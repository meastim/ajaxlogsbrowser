Plugins
=======

There are 4 (pseudo) plugins that can be used:

  - Rsyslog logs in a MySQL database,
  - Rsyslog logs in a PostgreSQL database,
  - Apache Httpd logs in a PostgreSQL database,
  - Logback (Java) logs in a PostgreSQL database.


Dependencies
============

The following lists the commands you need to use to install the dependencies
in `INSTALL_DIR`.
`psycopg2` is only required when using PostgreSQL and `pymysql` is only 
required when using MySQL.
The following assumes you're using Python 2.6 and have installed setuptools.


    INSTALL_DIR=/path/where/you/want/to/install
    
    export PYTHONPATH="$INSTALL_DIR"/python-libs/lib/python2.6/site-packages
    mkdir -p "$PYTHONPATH"
    easy_install-2.6 --prefix="$INSTALL_DIR"/python-libs CherryPy
    easy_install-2.6 --prefix="$INSTALL_DIR"/python-libs Genshi
    easy_install-2.6 --prefix="$INSTALL_DIR"/python-libs FormEncode
    easy_install-2.6 --prefix="$INSTALL_DIR"/python-libs flup
    easy_install-2.6 --prefix="$INSTALL_DIR"/python-libs pymysql
    easy_install-2.6 --prefix="$INSTALL_DIR"/python-libs psycopg2


This was mainly tested on Debian/Ubuntu, but shouldn't need much adaptation
for other platforms.


If you have not started to use PostgreSQL yet, it is probably better to allow
for a UTF-8 encoding (if it's not already the case). You can delete and 
rebuild your cluser using (NOTE THAT THIS WILL DELETE YOUR EXISTING DATA):

    pg_dropcluster --stop 8.4 main
    pg_createcluster --locale=en_GB.utf8 --start 8.4 main



Usage / Installation
====================

Configuration
-------------

This system uses one tab (in the jQuery UI sense) per plugin.
Pending a better plugin system, you need to configure where the python code and 
which templates is to be used as follows, for example:


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



Please refer to the `psycopg2` and the `pymysql` documentations to get more
details about the connection strings and parameters.


Standalone
----------

`test_sample.py` is a sample standalone server. Make sure PYTHONPATH is set 
correctly to be able to run it.


Fcgid
-----

`cherryd_sample.fcgi` shows a sample FCGI script.
You may need to adapt the path to the python interpreter as well as the
path to the site directory using `site.addsitedir`.

You should then be able to use this in your Apache Httpd configuration:

    ScriptAlias /logs/ /path/to/ajaxlogsbrowser/cherryd.fcgi/
    
    # If you want to use mod_rewrite for the trailing slash:
    # RewriteEngine On
    # RewriteRule ^/logs$ /logs/ [R]


Rsyslog
=======

On Debian/Ubuntu, install rsyslog-mysql or rsyslog-pgsql. It will create
the required tables.

Rsyslog with MySQL
------------------

	ALTER TABLE SystemEvents ADD COLUMN ReceivedAtDate DATE;
	CREATE TRIGGER SystemEventsReceivedAtDateInsert BEFORE INSERT ON SystemEvents
	    FOR EACH ROW SET NEW.ReceivedAtDate = DATE(NEW.ReceivedAt);
	UPDATE SystemEvents SET ReceivedAtDate = DATE(ReceivedAt);
	CREATE INDEX SystemEventsFacilityIdx ON SystemEvents(Facility);
	CREATE INDEX SystemEventsPriorityIdx ON SystemEvents(Priority);
	CREATE INDEX SystemEventsReceivedAtDateIdx ON SystemEvents(ReceivedAtDate);

Rsyslog with PostgreSQL
-----------------------

Create indices:

	CREATE INDEX SystemEventsFacilityIdx ON SystemEvents(Facility);
	CREATE INDEX SystemEventsPriorityIdx ON SystemEvents(Priority);
	CREATE INDEX SystemEventsReceivedAtDateIdx ON SystemEvents(date_trunc('day', ReceivedAt));

Create a user (e.g. using ident authentication for the `www-data` user):

    createuser -D -R -S www-data

Grant access:

    GRANT SELECT ON SystemEvents TO "www-data";
    GRANT SELECT ON SystemEventsProperties TO "www-data";
    


Apache Httpd logs
=================


The `apachehttpd_log2pg.py` script relies on the `pyparsing` module, which 
must be installed.

`apachehttpd_log2pg_createtable.sql` contains the required statements to 
create the table in PostgreSQL.

In the Apache Httpd configuration use:

    CustomLog "|/path/to/apachehttpd_log2pg.py LoggerID MachineName" combined

If you are collecting logs from multiple sources into the same database, 
LoggerID and MachineName are parameters to help you distinguish those sources.

Adapt the `connect` parameters as needed to authenticate. You can also create
a PostgreSQL user called `root` which will be able to authenticate via ident.
Grant table access accordingly. For example:

    GRANT SELECT, UPDATE ON apache_httpd_access_log_id_seq TO root;
    GRANT INSERT ON apache_httpd_access_log TO root;


Logback
=======

The `logback_createtables.sql` files can be used to create the tables in 
PostgreSQL. `logback-jetty-example.xml` is an example configuration file.

