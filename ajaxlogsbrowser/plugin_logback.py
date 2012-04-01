#
# Copyright (c) 2012  Meastim
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import psycopg2


class LogbackModule(object):
    def __init__(self, config):
        self.config = config
        
    def produce_output(self, args):
        connect_string = self.config.get('connection_string', '')
        
        output = {}
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(connect_string)
            try:
                cursor = conn.cursor()
                self.get_options(cursor, output)
                self.get_entries(cursor, output, args)
            finally:
                if cursor:
                    cursor.close()
        finally:
            if conn:
                conn.close()
            
        return output
    
    def get_options(self, cursor, output):
        cursor.execute("SELECT DISTINCT mapped_value FROM logging_event_property WHERE mapped_key='LOGGER_ID'")
        output['logger_ids'] = [ row[0] for row in cursor.fetchall() ]
        
        return output
    
    def get_entries(self, cursor, output, kwargs):
        try:
            from_page = int(kwargs.get('fromPage'))
        except (ValueError, TypeError):
            from_page = 0
        try:
            page_count = int(kwargs.get('pageCount'))
        except (ValueError, TypeError):
            page_count = 1
        try:
            page_size = int(kwargs.get('pageSize'))
        except (ValueError, TypeError):
            page_size = 50
        
        date = kwargs.get('date')
        logger_id = kwargs.get('logger_id')
        log_level = kwargs.get('loglevel', 'INFO')
        if log_level:
            log_level = log_level.upper()
        class_name_prefix = kwargs.get('classPrefix')
        method_prefix = kwargs.get('methodPrefix')
        
        all_days = kwargs.get('alldays', '').lower() in [ '1', 'yes', 'true' ]

        offset = from_page * page_size
        limit = page_count * page_size

        #
        # Getting the total number of rows for the requested day.
        #
        
        params = []
        query = " SELECT COUNT(le.event_id) FROM logging_event le"
        if logger_id:
            query += """INNER JOIN logging_event_property logger_id
    ON le.event_id=logger_id.event_id AND logger_id.mapped_key='LOGGER_ID' WHERE logger_id.mapped_value=%s """
            params.append(logger_id)
        else:
            query += " WHERE TRUE "
        
        if not all_days:
            if date:
                query += " AND DATE(TIMESTAMP WITH TIME ZONE 'epoch' + le.timestmp/1000 * INTERVAL '1 second') = DATE(%s) "
                params.append(date)
            else:
                query += " AND DATE(TIMESTAMP WITH TIME ZONE 'epoch' + le.timestmp/1000 * INTERVAL '1 second') = DATE(NOW()) "
        if log_level:
            query += " AND le.level_string IN "
            if log_level == 'ERROR':
                query += " ('ERROR') "
            elif log_level == 'WARN':
                query += " ('WARN','ERROR') "
            elif log_level == 'INFO':
                query += " ('INFO','WARN','ERROR') "
            elif log_level == 'DEBUG':
                query += " ('DEBUG','INFO','WARN','ERROR') "
            else:
                query += " ('TRACE','DEBUG','INFO','WARN','ERROR') "
        if class_name_prefix:
            query += " AND le.caller_class LIKE %s "
            params.append(class_name_prefix + '%')
        if method_prefix:
            query += " AND le.caller_method LIKE %s "
            params.append(method_prefix + '%')

        total = 0
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            total = row[0]
        
        #
        # Getting the position of the row at the requested time.
        #
        
        params = []
        query = " SELECT COUNT(le.event_id) FROM logging_event le"
        if logger_id:
            query += """INNER JOIN logging_event_property logger_id
    ON le.event_id=logger_id.event_id AND logger_id.mapped_key='LOGGER_ID' WHERE logger_id.mapped_value=%s """
            params.append(logger_id)
        else:
            query += " WHERE TRUE "
        
        if not all_days:
            if date:
                query += " AND DATE(TIMESTAMP WITH TIME ZONE 'epoch' + le.timestmp/1000 * INTERVAL '1 second') = DATE(%s) "
                params.append(date)
            else:
                query += " AND DATE(TIMESTAMP WITH TIME ZONE 'epoch' + le.timestmp/1000 * INTERVAL '1 second') = DATE(NOW()) "
        if log_level:
            query += " AND le.level_string IN "
            if log_level == 'ERROR':
                query += " ('ERROR') "
            elif log_level == 'WARN':
                query += " ('WARN','ERROR') "
            elif log_level == 'INFO':
                query += " ('INFO','WARN','ERROR') "
            elif log_level == 'DEBUG':
                query += " ('DEBUG','INFO','WARN','ERROR') "
            else:
                query += " ('TRACE','DEBUG','INFO','WARN','ERROR') "
        if class_name_prefix:
            query += " AND le.caller_class LIKE %s "
            params.append(class_name_prefix + '%')
        if method_prefix:
            query += " AND le.caller_method LIKE %s "
            params.append(method_prefix + '%')
                
        if date:
            query += " AND (TIMESTAMP WITH TIME ZONE 'epoch' + le.timestmp/1000 * INTERVAL '1 second') <= %s::timestamptz "
            params.append(date)
        else:
            query += " AND (TIMESTAMP WITH TIME ZONE 'epoch' + le.timestmp/1000 * INTERVAL '1 second') <= DATE(NOW()) "

        position = None
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            position = row[0]


        #
        # Getting the page of rows.
        #
        
        params = []
        query = """ SELECT (TIMESTAMP WITH TIME ZONE 'epoch' + le.timestmp/1000 * INTERVAL '1 second')::text,
            le.formatted_message, le.logger_name, le.level_string, le.thread_name, le.reference_flag,
            le.arg0, le.arg1, le.arg2, le.arg3, le.caller_filename, le.caller_class, le.caller_method, le.caller_line, le.event_id
            FROM logging_event le """
        if logger_id:
            query += """INNER JOIN logging_event_property logger_id
    ON le.event_id=logger_id.event_id AND logger_id.mapped_key='LOGGER_ID' WHERE logger_id.mapped_value=%s """
            params.append(logger_id)
        else:
            query += " WHERE TRUE "
        
        if not all_days:
            if date:
                query += " AND DATE(TIMESTAMP WITH TIME ZONE 'epoch' + le.timestmp/1000 * INTERVAL '1 second') = DATE(%s) "
                params.append(date)
            else:
                query += " AND DATE(TIMESTAMP WITH TIME ZONE 'epoch' + le.timestmp/1000 * INTERVAL '1 second') = DATE(NOW()) "
        if log_level:
            query += " AND le.level_string IN "
            if log_level == 'ERROR':
                query += " ('ERROR') "
            elif log_level == 'WARN':
                query += " ('WARN','ERROR') "
            elif log_level == 'INFO':
                query += " ('INFO','WARN','ERROR') "
            elif log_level == 'DEBUG':
                query += " ('DEBUG','INFO','WARN','ERROR') "
            else:
                query += " ('TRACE','DEBUG','INFO','WARN','ERROR') "
        if class_name_prefix:
            query += " AND le.caller_class LIKE %s "
            params.append(class_name_prefix + '%')
        if method_prefix:
            query += " AND le.caller_method LIKE %s "
            params.append(method_prefix + '%')

        query += "  ORDER BY le.timestmp LIMIT %s OFFSET %s";
        params.append(limit)
        params.append(offset)
        
        results = []
        
        cursor.execute(query, params)
        for row in cursor:
            results.append({
                "logger_id": logger_id,
                "id": row[14],
                "event_dt": row[0],
                "message": row[1],
                "logger": row[2],
                "level": row[3],
                "thread": row[4],
                "refflag": row[5],
                "arg0": row[6],
                "arg1": row[7],
                "arg2": row[8],
                "arg3": row[9],
                "filename": row[10],
                "class": row[11],
                "method": row[12],
                "line": row[13]
            })
        
        query = "SELECT mapped_key, mapped_value FROM logging_event_property WHERE event_id=%s"
        for result_row in results:
            cursor.execute(query, [ result_row['id'] ])
            for row in cursor:
                result_row["prop_%s" % (row[0],)] = row[1]
                
        query = "SELECT i, trace_line FROM logging_event_exception WHERE event_id=%s ORDER BY i"
        for result_row in results:
            cursor.execute(query, [ result_row['id'] ])
            exception = ""
            for row in cursor:
                exception += row[1] + "\n"
            result_row['exception'] = exception


        if position != None:
            output["position"] = position
        output["offset"] = offset
        output["count"] = limit
        output["total"] = total
        output["logs"] = results



