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


class ApacheHttpdLogsModule(object):
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
        cursor.execute("SELECT DISTINCT logger_id FROM apache_httpd_access_log")
        output['logger_ids'] = [ row[0] for row in cursor.fetchall() ]
        
        cursor.execute("SELECT DISTINCT hostname FROM apache_httpd_access_log")
        output['hostnames'] = [ row[0] for row in cursor.fetchall() ]
        
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
        hostname = kwargs.get('hostname')
        logger_id = kwargs.get('logger_id')
        code_grp = kwargs.get('code_grp')
        path_prefix = kwargs.get('pathPrefix')
        
        all_days = kwargs.get('alldays', '').lower() in [ '1', 'yes', 'true' ]

        offset = from_page * page_size
        limit = page_count * page_size

        #
        # Getting the total number of rows for the requested day.
        #
        
        params = []
        query = " SELECT COUNT(id) FROM apache_httpd_access_log WHERE TRUE "
        
        if not all_days:
            if date:
                query += " AND DATE(event_datetime) = DATE(%s) "
                params.append(date)
            else:
                query += " AND DATE(event_datetime) = DATE(NOW()) "
        if logger_id:
            query += " AND logger_id = %s "
            params.append(logger_id)
        if hostname:
            query += " AND hostname = %s "
            params.append(hostname)
        if path_prefix:
            query += " AND path LIKE %s "
            params.append(path_prefix + '%')
        if code_grp:
            query += " AND status >= %s AND status < %s "
            if code_grp == "1xx":
                params.append(100)
                params.append(200)
            elif code_grp == "2xx":
                params.append(200)
                params.append(300)
            elif code_grp == "3xx":
                params.append(300)
                params.append(400)
            elif code_grp == "4xx":
                params.append(400)
                params.append(500)
            elif code_grp == "5xx":
                params.append(500)
                params.append(600)
            else:
                params.append(0)
                params.append(1000)

        total = 0
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            total = row[0]
        
        #
        # Getting the position of the row at the requested time.
        #
        
        params = []
        query = " SELECT COUNT(id) FROM apache_httpd_access_log WHERE TRUE "
        
        if not all_days:
            if date:
                query += " AND DATE(event_datetime) = DATE(%s) "
                params.append(date)
            else:
                query += " AND DATE(event_datetime) = DATE(NOW()) "
        if logger_id:
            query += " AND logger_id = %s "
            params.append(logger_id)
        if hostname:
            query += " AND hostname = %s "
            params.append(hostname)
        if path_prefix:
            query += " AND path LIKE %s "
            params.append(path_prefix + '%')
        if code_grp:
            query += " AND status >= %s AND status < %s "
            if code_grp == "1xx":
                params.append(100)
                params.append(200)
            elif code_grp == "2xx":
                params.append(200)
                params.append(300)
            elif code_grp == "3xx":
                params.append(300)
                params.append(400)
            elif code_grp == "4xx":
                params.append(400)
                params.append(500)
            elif code_grp == "5xx":
                params.append(500)
                params.append(600)
            else:
                params.append(0)
                params.append(1000)
                
        if date:
            query += " AND event_datetime <= %s::timestamptz "
            params.append(date)
        else:
            query += " AND event_datetime <= DATE(NOW()) "

        position = None
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            position = row[0]


        #
        # Getting the page of rows.
        #
        
        params = []
        query = """SELECT id, logger_id, hostname, ip_address, authuser, event_datetime::text, method, path, protocol,
    status, size, referer, useragent FROM apache_httpd_access_log WHERE TRUE""" 
        if not all_days:
            if date:
                query += " AND DATE(event_datetime) = DATE(%s) "
                params.append(date)
            else:
                query += " AND DATE(event_datetime) = DATE(NOW()) "
        if logger_id:
            query += " AND logger_id = %s "
            params.append(logger_id)
        if hostname:
            query += " AND hostname = %s "
            params.append(hostname)
        if path_prefix:
            query += " AND path LIKE %s "
            params.append(path_prefix + '%')
        if code_grp:
            query += " AND status >= %s AND status < %s "
            if code_grp == "1xx":
                params.append(100)
                params.append(200)
            elif code_grp == "2xx":
                params.append(200)
                params.append(300)
            elif code_grp == "3xx":
                params.append(300)
                params.append(400)
            elif code_grp == "4xx":
                params.append(400)
                params.append(500)
            elif code_grp == "5xx":
                params.append(500)
                params.append(600)
            else:
                params.append(0)
                params.append(1000)

        query += "  ORDER BY event_datetime LIMIT %s OFFSET %s";
        params.append(limit)
        params.append(offset)
        
        results = []
        
        cursor.execute(query, params)
        for row in cursor:
            results.append({
                "id": row[0],
                "logger_id": row[1],
                "hostname": row[2],
                "ip_addr": row[3],
                "authuser": row[4],
                "event_dt": row[5],
                "method": row[6],
                "path": row[7],
                "protocol": row[8],
                "status": row[9],
                "size": row[10],
                "referer": row[11],
                "useragent": row[12]
            })

        if position != None:
            output["position"] = position
        output["offset"] = offset
        output["count"] = limit
        output["total"] = total
        output["logs"] = results



