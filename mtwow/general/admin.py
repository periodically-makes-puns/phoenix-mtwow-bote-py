"""
Defines the functions needed for the administrator.
"""
import sqlutils
import sqlite3
conn = sqlite3.connect("data.db")
init()

def init():
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS Members (
        uid INTEGER PRIMARY KEY NOT NULL,
        aggregateVoteCount INTEGER DEFAULT 0,
        roundVoteCount INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS Contestants (
        uid INTEGER PRIMARY KEY NOT NULL,
        alive BOOLEAN DEFAULT 0,
        allowedResponseCount INTEGER DEFAULT 1,
        responseCount INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS Responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        uid INTEGER NOT NULL,
        rid INTEGER NOT NULL,
        response TEXT,
        confirmedVoteCount INTEGER DEFAULT 0,
        pendingVoteCount INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS Status (
        roundNum INTEGER,
        prompt TEXT,
        phase TEXT,
        deadline INTEGER
    );

    CREATE TABLE IF NOT EXISTS Status (
        roundNum INTEGER,
        prompt TEXT,
        phase TEXT,
        deadline INTEGER
    );

    CREATE TABLE IF NOT EXISTS ResponseArchive (
        roundNum INTEGER NOT NULL,
        id INTEGER NOT NULL,
        uid INTEGER NOT NULL,
        rid INTEGER NOT NULL,
        rank INTEGER NOT NULL,
        response TEXT NOT NULL,
        score DOUBLE NOT NULL,
        skew DOUBLE NOT NULL
    );
    """)
    conn.commit()