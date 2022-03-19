CREATE TABLE crawldb.ips (
    ip varchar(15),
    accessed_time timestamp,
    CONSTRAINT unq_ip UNIQUE ( ip )
);