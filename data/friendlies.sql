DROP TABLE IF EXISTS friendlies; -- drop already existing table

CREATE TABLE friendlies (
    day int(255),
    field varchar(255),
    teamA varchar(255),
    teamB varchar(255),
    starttime varchar(255),
    status varchar(255),
    timestamp varchar(255)
)