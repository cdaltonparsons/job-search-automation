CREATE TABLE IF NOT EXISTS jobs (
    id          TEXT        PRIMARY KEY,
    title       TEXT        NOT NULL,
    company     TEXT        NOT NULL,
    url         TEXT        NOT NULL,
    location    TEXT        NOT NULL,
    posted_date TEXT        NOT NULL,
    description TEXT        NOT NULL,
    source      TEXT        NOT NULL,
    remote      INTEGER     NOT NULL DEFAULT 0,
    seen        INTEGER     NOT NULL DEFAULT 0,
    applied     INTEGER     NOT NULL DEFAULT 0,
    salary      TEXT,
    notes       TEXT
);
