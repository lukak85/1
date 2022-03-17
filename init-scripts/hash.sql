CREATE TABLE crawldb.html_hash (
    hash integer,
    CONSTRAINT unq_hash UNIQUE ( hash ),
    CONSTRAINT fk_url FOREIGN KEY ( url ) REFERENCES crawldb.page( id ) ON DELETE RESTRICT
 );