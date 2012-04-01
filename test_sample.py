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

import cherrypy

from ajaxlogsbrowser import core, plugin_apachehttpdlogs, plugin_rsyslog_mysql


ajaxlogsbrowser_config = {
        "tabs": [
            { "template": "syslog_tab.html", "title": "Syslog",
              "plugin": plugin_rsyslog_mysql.SyslogModule({ 'db_params': { 'db': 'Syslog', 'user': 'ajaxlogsbrowser', 'passwd': 'xxxxxxxxxxxxxxxxxxxx' }})
            },
            { "template": "apachehttpdlogs_tab.html", "title": "Apache Httpd",
              "plugin": plugin_apachehttpdlogs.ApacheHttpdLogsModule({ 'connection_string': "dbname=logs" })
            }
        ]
    }

cherrypy.config.update({'server.socket_port': 8080})

core.standalone(ajaxlogsbrowser_config)
