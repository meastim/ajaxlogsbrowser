CREATE TABLE logging_event (
    timestmp BIGINT NOT NULL,
    formatted_message TEXT NOT NULL,
    logger_name TEXT NOT NULL,
    level_string TEXT NOT NULL,
    thread_name TEXT,
    reference_flag SMALLINT,
    arg0 TEXT,
    arg1 TEXT,
    arg2 TEXT,
    arg3 TEXT,
    caller_filename TEXT NOT NULL,
    caller_class TEXT NOT NULL,
    caller_method TEXT NOT NULL,
    caller_line TEXT NOT NULL,
    event_id BIGSERIAL PRIMARY KEY
);

CREATE TABLE logging_event_property (
    event_id BIGINT NOT NULL,
    mapped_key TEXT NOT NULL,
    mapped_value TEXT,
    PRIMARY KEY(event_id, mapped_key),
    FOREIGN KEY (event_id) REFERENCES logging_event(event_id)
);

CREATE TABLE logging_event_exception (
    event_id BIGINT NOT NULL,
    i SMALLINT NOT NULL,
    trace_line TEXT NOT NULL,
    PRIMARY KEY(event_id, i),
    FOREIGN KEY (event_id) REFERENCES logging_event(event_id)
);

-- This should be the JDBC user configured in the logback config file.
GRANT SELECT, UPDATE ON logging_event_event_id_seq TO logback;
GRANT SELECT, INSERT ON logging_event TO logback;
GRANT SELECT, INSERT ON logging_event_property TO logback;
GRANT SELECT, INSERT ON logging_event_exception TO logback;


GRANT SELECT ON TABLE logging_event TO "www-data";
GRANT SELECT ON TABLE logging_event_property TO "www-data";
GRANT SELECT ON TABLE logging_event_exception TO "www-data";