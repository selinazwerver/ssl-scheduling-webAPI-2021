DROP TABLE IF EXISTS posts; -- drop already existing table

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

--CREATE TABLE schedule (
--    id INTEGER PRIMARY KEY AUTOINCREMENT,
--    teamA varchar(255),
--    teamB varchar(255),
--    starttime varchar(255),
--    endtime varchar(255)
--)