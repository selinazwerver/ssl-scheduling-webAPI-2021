DROP TABLE IF EXISTS schedule; -- drop already existing table

CREATE TABLE schedule (
    day varchar(255),
    teamA varchar(255),
    teamB varchar(255),
    starttime varchar(255),
    endtime varchar(255),
    scoreTeamA int(255),
    scoreTeamB int(255),
    field int(255),
)