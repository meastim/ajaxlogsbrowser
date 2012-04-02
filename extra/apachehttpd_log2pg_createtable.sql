CREATE TABLE apache_httpd_access_log (
    id BIGSERIAL PRIMARY KEY,
    logger_id TEXT,
    hostname TEXT,
    ip_address TEXT,
    authuser TEXT,
    event_datetime TIMESTAMPTZ,
    method TEXT,
    path TEXT,
    protocol TEXT,
    status INTEGER,
    size INTEGER,
    referer TEXT, -- It isn't spelt properly in the HTTP specification...
    useragent TEXT
);


-- Assuming root is a PostgreSQL user accessible via ident (for example), not necessarily a PG superuser.

GRANT SELECT, UPDATE ON apache_httpd_access_log_id_seq TO root;
GRANT INSERT ON apache_httpd_access_log TO root;


GRANT SELECT ON TABLE apache_httpd_access_log TO "www-data";