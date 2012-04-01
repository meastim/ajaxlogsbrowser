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

import pymysql


class SyslogModule(object):
    def __init__(self, config):
        self.config = config
        
    def produce_output(self, args):
        output = {}
        conn = None
        cursor = None
        try:
            db_params = self.config.get('db_params') or {}
            conn = pymysql.connect(**db_params)
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
        cursor.execute("SELECT DISTINCT FromHost FROM SystemEvents")
        output['hosts'] = [ row[0] for row in cursor.fetchall() ]
        
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
        try:
            priority_threshold = int(kwargs.get('thres'))
        except (ValueError, TypeError):
            priority_threshold = 10
        try:
            facility = int(kwargs.get('facility'))
        except (ValueError, TypeError):
            facility = None
        host = kwargs.get('host')
        syslog_tag_prefix = kwargs.get('tagprefix')
        
        all_days = kwargs.get('alldays', '').lower() in [ '1', 'yes', 'true' ]

        offset = from_page * page_size
        limit = page_count * page_size

        #
        # Getting the total number of rows for the requested day.
        #
        
        params = []
        query = " SELECT COUNT(ID) FROM SystemEvents WHERE TRUE  "
        
        if not all_days:
            if date:
                query += " AND ReceivedAtDate = DATE(%s) "
                params.append(date)
            else:
                query += " AND ReceivedAtDate = DATE(NOW()) "
        if host:
            query += " AND FromHost = %s "
            params.append(host)
        if facility != None:
            query += " AND Facility = %s "
            params.append(facility)
        if priority_threshold:
            query += " AND Priority <= %s "
            params.append(priority_threshold)
        if syslog_tag_prefix:
            query += " AND SysLogTag LIKE %s "
            params.append(syslog_tag_prefix + "%")

        total = 0
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            total = row[0]
        
        #
        # Getting the position of the row at the requested time.
        #
        
        params = []
        query = " SELECT COUNT(ID) FROM SystemEvents WHERE TRUE  "
        
        if not all_days:
            if date:
                query += " AND ReceivedAtDate = DATE(%s) "
                params.append(date)
            else:
                query += " AND ReceivedAtDate = DATE(NOW()) "
        if host:
            query += " AND FromHost = %s "
            params.append(host)
        if facility != None:
            query += " AND Facility = %s "
            params.append(facility)
        if priority_threshold:
            query += " AND Priority <= %s "
            params.append(priority_threshold)
        if syslog_tag_prefix:
            query += " AND SysLogTag LIKE %s "
            params.append(syslog_tag_prefix + "%")
                
        if date:
            query += " AND ReceivedAt < TIMESTAMP(%s) "
            params.append(date)
        else:
            query += " AND ReceivedAt <= DATE(NOW()) "

        position = None
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            position = row[0]


        #
        # Getting the page of rows.
        #
        
        params = []
        query = """SELECT ID, DeviceReportedTime, ReceivedAt, Facility, Priority, FromHost, SysLogTag, Message
    FROM SystemEvents WHERE TRUE""" 
        if not all_days:
            if date:
                query += " AND ReceivedAtDate = DATE(%s) "
                params.append(date)
            else:
                query += " AND ReceivedAtDate = DATE(NOW()) "
        if host:
            query += " AND FromHost = %s "
            params.append(host)
        if facility != None:
            query += " AND Facility = %s "
            params.append(facility)
        if priority_threshold:
            query += " AND Priority <= %s "
            params.append(priority_threshold)
        if syslog_tag_prefix:
            query += " AND SysLogTag LIKE %s "
            params.append(syslog_tag_prefix + "%")

        query += "  ORDER BY ReceivedAt LIMIT %s OFFSET %s";
        params.append(limit)
        params.append(offset)
        
        results = []
        
        cursor.execute(query, params)
        for row in cursor:
            results.append({
                "id": row[0],
                "device_dt": row[1].strftime('%Y-%m-%d %H:%M:%S') if row[1] else '', 
                "received_dt": row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else '', 
                "facility": row[3],
                "severity": row[4],
                "fromhost": row[5],
                "syslogtag": row[6],
                "message": row[7],
            })

        if position != None:
            output["position"] = position
        output["offset"] = offset
        output["count"] = limit
        output["total"] = total
        output["logs"] = results



