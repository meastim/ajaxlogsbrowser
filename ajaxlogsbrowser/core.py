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


import os

from pkg_resources import resource_filename #IGNORE:E0611 #@UnresolvedImport

import cherrypy
from cherrypy._cptree import Application
from genshi.template import TemplateLoader


class Root(object):
    def __init__(self, ajaxlogsbrowser_config):
        self.ajaxlogsbrowser_config = ajaxlogsbrowser_config
                
        self.genshi_loader = TemplateLoader(
            os.path.join(resource_filename(__name__, 'templates')),
            auto_reload = self.ajaxlogsbrowser_config.get('dev_mode', False)
        )
        
        self.script_locations = [ 
            "3rdparty/jquery-1.7.1.min.js",
            "3rdparty/jquery-ui/js/jquery-ui-1.8.18.custom.min.js",
            "3rdparty/jquery-ui-timepicker-addon.js",
            "3rdparty/jquery.ba-bbq.min.js",
            "3rdparty/spin.min.js",
            "3rdparty/SlickGrid/lib/jquery.event.drag-2.0.min.js",
            "3rdparty/SlickGrid/slick.core.js",
            "3rdparty/SlickGrid/slick.grid.js",
            "3rdparty/SlickGrid/plugins/slick.rowselectionmodel.js",
            
            # TODO: Move to config / plugin
            "js/ajaxlogsbrowser.syslogremotemodel.js",
            "js/ajaxlogsbrowser.apachehttpdlogsremotemodel.js",
            "js/ajaxlogsbrowser.logback.remotemodel.js"
         ]
        self.css_locations = [
            "3rdparty/jquery-ui/css/pepper-grinder/jquery-ui-1.8.18.custom.css",
            "3rdparty/jquery-ui-timepicker-addon.css",
            "3rdparty/SlickGrid/slick.grid.css",
            "3rdparty/SlickGrid/examples/examples.css"
        ]
        
        # TODO: Move to config / plugin
        self.head_included_templates = [
            "syslog_style.html",
            "apachehttpdlogs_style.html",
            "syslog_javascript_head.html",
            "logback_style.html"
        ]

    @cherrypy.expose
    def index(self):
        tmpl = self.genshi_loader.load('index.html')
        tmpl_tabs = []
        i = 0
        for tab_config in self.ajaxlogsbrowser_config.get('tabs', []):
            tmpl_tabs.append({
                'tab_index': i,
                'tab_template': tab_config.get('template', ''),
                'tab_title': tab_config.get('title', '')
            })
            i += 1
        tmpl_data = {
            "script_locations": self.script_locations,
            "css_locations": self.css_locations,
            "head_included_templates": self.head_included_templates,
            "tabs": tmpl_tabs
        }
        return tmpl.generate(**tmpl_data).render('html', doctype='xhtml')
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def ajax(self, **kwargs):
        try:
            tab_plugin = self.ajaxlogsbrowser_config['tabs'][int(kwargs['tabindex'])]['plugin']
            return tab_plugin.produce_output(kwargs)
        except Exception, e:
            return "An error occurred: %s" % (e,)
        return {}

cherrypy.config.update({
    'tools.encode.on': True,
    'tools.encode.encoding': 'utf-8',
    'tools.decode.on': True,
    'tools.trailing_slash.on': True
})

def application(ajaxlogsbrowser_config):
    return Application(Root(ajaxlogsbrowser_config), None, config={
        '/3rdparty': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': resource_filename(__name__, '3rdparty')
        },
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': resource_filename(__name__, 'js')
        }
    })

def mount(target, ajaxlogsbrowser_config):
    cherrypy.tree.mount(Root(ajaxlogsbrowser_config), target, config={
        '/3rdparty': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': resource_filename(__name__, '3rdparty')
        },
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': resource_filename(__name__, 'js')
        }
    })

def standalone(ajaxlogsbrowser_config):
    cherrypy.quickstart(Root(ajaxlogsbrowser_config), '/', {
        '/3rdparty': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': resource_filename(__name__, '3rdparty')
        },
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': resource_filename(__name__, 'js')
        }
    })
