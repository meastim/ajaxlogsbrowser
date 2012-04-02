#!/usr/bin/env python
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

# The getLogLineBNF() function comes from the pyparsing example licensed under:
#
# Copyright (c) 2003-2011  Paul T. McGuire
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

import sys
from pyparsing import alphas,nums, dblQuotedString, Combine, Word, Group, delimitedList, Suppress, removeQuotes
import string
import psycopg2




def getCmdFields(s, l, t):
    t["method"],t["requestURI"],t["protocolVersion"] = t[0].strip('"').split()
logLineBNF = None
def getLogLineBNF():
    global logLineBNF
    
    if logLineBNF is None:
        integer = Word( nums )
        ipAddress = delimitedList( integer, ".", combine=True )
        
        timeZoneOffset = Word("+-",nums)
        month = Word(string.uppercase, string.lowercase, exact=3)
        serverDateTime = Combine( Suppress("[") + 
                                Combine( integer + "/" + month + "/" + integer +
                                        ":" + integer + ":" + integer + ":" + integer + ' '  + timeZoneOffset) + 
                                Suppress("]") )
                         
        logLineBNF = ( ipAddress.setResultsName("ipAddr") + 
                       Suppress("-") +
                       ("-" | Word( alphas+nums+"@._" )).setResultsName("auth") +
                       serverDateTime.setResultsName("timestamp") + 
                       dblQuotedString.setResultsName("cmd").setParseAction(getCmdFields) +
                       (integer | "-").setResultsName("statusCode") + 
                       (integer | "-").setResultsName("numBytesSent")  + 
                       dblQuotedString.setResultsName("referrer").setParseAction(removeQuotes) +
                       dblQuotedString.setResultsName("clientSfw").setParseAction(removeQuotes) )
    return logLineBNF




conn = psycopg2.connect(database="logs")
conn.autocommit = True

query = """INSERT INTO apache_httpd_access_log (logger_id, hostname, ip_address, authuser, event_datetime, method, path,
		protocol, status, size, referer, useragent) VALUES (%s, %s, %s, %s, %s::timestamptz, %s, %s, %s, %s, %s, %s, %s)"""


cursor = conn.cursor()
try:
    logger_id = sys.argv[1] or None
    hostname = sys.argv[2] or None
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        fields = getLogLineBNF().parseString(line)
        fields['logger_id'] = logger_id
        fields['hostname'] = hostname

	cursor.execute(query, [ fields.get(x) for x in ['logger_id', 'hostname', 'ipAddr', 'auth', 'timestamp', 'method', 'requestURI', 'protocolVersion', 'statusCode', 'numBytesSent', 'referrer', 'clientSfw'] ])
finally:
    cursor.close()
    conn.close()



