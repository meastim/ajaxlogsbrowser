#!/usr/bin/python2.6
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


import sys

engine = None
try:
    #import site
    #site.addsitedir('/.../python-libs/lib/python2.6/site-packages')
    
    from ajaxlogsbrowser.plugin_apachehttpdlogs import ApacheHttpdLogsModule
    from ajaxlogsbrowser.plugin_rsyslog_mysql import SyslogModule
    
    ajaxlogsbrowser_config = {
        "tabs": [
            { "template": "syslog_tab.html", "title": "Syslog",
              "plugin": SyslogModule({ 'db_params': { 'db': 'Syslog', 'user': 'ajaxlogsbrowser', 'passwd': 'xxxxxxxxxxxxx' }})
            },
            { "template": "apachehttpdlogs_tab.html", "title": "Apache Httpd",
              "plugin": ApacheHttpdLogsModule({ 'connection_string': "dbname=logs" })
            }
        ]
    }
    
    import cherrypy
    from cherrypy.process import servers
    
    engine = cherrypy.engine
    
    if hasattr(engine, "signal_handler"):
        engine.signal_handler.subscribe()
    if hasattr(engine, "console_control_handler"):
        engine.console_control_handler.subscribe()
    
    
    cherrypy.config.update({
        'engine.autoreload_on': False,
        'server.log_to_screen': False,
        'server.logToScreen': False,
        'log.screen': False
    })
    cherrypy.server.unsubscribe()
    
    import ajaxlogsbrowser.core
    f = servers.FlupFCGIServer(application=ajaxlogsbrowser.core.application(ajaxlogsbrowser_config))
    
    s = servers.ServerAdapter(engine, httpserver=f)
    s.subscribe()

    engine.start()
except SystemExit:
    raise
except Exception, e:
    print 'Content-Type: text/plain\r\n\r\n'
    print
    print 'There was an internal error:'
    print
    print e
    print
    import traceback
    import StringIO
    tb = StringIO.StringIO()
    traceback.print_exc(file=tb)
    print tb.getvalue()
    sys.exit(1)
else:
    if engine:
        engine.block()

