import sqlite3
from typing import List, Callable
from ...generic.utils import data
import logging
sql_logger = logging.getLogger("sqlite3")

def handleSQLErrors(func: Callable):
    def handler(*args, **kwargs):
        if not isinstance(args[0], sqlite3.Connection):
            return (2, "No connection provided.")
        try:
            with args[0]:
                res = func(*args, **kwargs)
            return res
        except sqlite3.Error as e:
            sql_logger.error(str(e))
            return (2, "SQL Error occurred.")
    return handler


def init(conn: sqlite3.Connection):
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

    CREATE TABLE IF NOT EXISTS Votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        uid INTEGER NOT NULL,
        vid INTEGER NOT NULL,
        gseed TEXT UNIQUE NOT NULL,
        vote TEXT
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

def wipe(conn: sqlite3.Connection):
    conn.executescript("""
        DROP TABLE IF EXISTS Members;
        DROP TABLE IF EXISTS Contestants;
        DROP TABLE IF EXISTS Responses;
        DROP TABLE IF EXISTS Votes;
        DROP TABLE IF EXISTS Status;
        DROP TABLE IF EXISTS ResponseArchive;
    """)

def isContestant(conn: sqlite3.Connection, uid: int) -> bool:
    sql_logger.debug("Checking if {:d} is a contestant.".format(uid))
    return isinstance(conn.execute("SELECT * FROM Contestants WHERE uid = ?;", uid).fetchone(), sqlite3.Row)

def isDead(conn: sqlite3.Connection, uid: int) -> bool:
    sql_logger.debug("Checking if {:d} is alive.".format(uid))
    return bool(conn.execute("SELECT alive FROM Contestants WHERE uid=?;").fetchone()["alive"])

def addContestant(conn: sqlite3.Connection, uid: int):
    sql_logger.debug("Adding contestant with ID {:d}".format(uid))
    conn.execute("INSERT INTO Contestants (uid, alive) VALUES (?, 1);")

def phase(conn: sqlite3.Connection) -> str:
    sql_logger.debug("Getting current phase")
    return conn.execute("SELECT phase FROM Status;").fetchone()["phase"]

def roundNum(conn: sqlite3.Connection) -> int:
    sql_logger.debug("Getting round number")
    return conn.execute("SELECT roundNum FROM Status;").fetchone()["roundNum"]

def editResponse(conn: sqlite3.Connection, uid: int, responseNumber: int, response: str):
    sql_logger.debug("Editing response {:d} of contestant {:d} to:\n{:s}".format(responseNumber, uid, response))
    conn.execute("UPDATE Responses SET response=? WHERE uid=? AND rid=?;", (uid, responseNumber, response))

def addResponse(conn: sqlite3.Connection, uid: int, responseNumber: int, response: str):
    sql_logger.debug("Adding response {:d} of contestant {:d}:\n{:s}".format(responseNumber, uid, response))
    conn.execute("INSERT INTO Responses (uid, rid, response) VALUES (?, ?, ?);", (uid, responseNumber, response))


def getResponseByUID(conn: sqlite3.Connection, uid: int, responseNumber: int) -> sqlite3.Row:
    sql_logger.debug("Getting response {:d} submitted by {:d}".format(responseNumber, uid))
    return conn.execute("SELECT * FROM Responses WHERE uid = ? AND rid = ?;", (uid, responseNumber)).fetchone()

def getResponseByID(conn: sqlite3.Connection, id: int) -> sqlite3.Row:
    sql_logger.debug("Getting response with ID {:d}".format(id))
    return conn.execute("SELECT * FROM Responses WHERE id = ?;", id).fetchone()

def allowedResponses(conn: sqlite3.Connection, uid: int) -> int:
    sql_logger.debug("Getting number of responses for contestant {:d}".format(uid))
    return conn.execute("SELECT allowedResponses FROM Contestants WHERE uid = ?;", uid).fetchone()["allowedResponses"]

def getAllResponsesButOwn(conn: sqlite3.Connection, uid: int) -> List[sqlite3.Row]:
    sql_logger.debug("Getting all responses except those of {:d}".format(uid))
    return conn.execute("SELECT * FROM Responses WHERE uid != ?;", uid).fetchall()

def getAllResponsesButOne(conn: sqlite3.Connection, uid: int, responseNumber: int) -> List[sqlite3.Row]:
    sql_logger.debug("Getting all responses except response {:d} submitted by {:d}".format(responseNumber, uid))
    return conn.execute("SELECT * FROM Responses WHERE uid != ? OR rid != ?;", (uid, responseNumber)).fetchall()


def getAllResponses(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    sql_logger.debug("Getting all responses.")
    return conn.execute("SELECT * FROM Responses;").fetchall()

def wordCount(string: str) -> int:
    return len(string.split())

def removeDisallowedChars(string: str) -> str:
    res = ""
    for c in string:
        # filter out:
        #    - ZWSPs
        #    - Newlines
        # don't make me have to add more
        if c not in "\u200b\n":
            res += c
    return res

def expectedVoteCount(resp: sqlite3.Row) -> float:
    return resp["confirmedVoteCount"] + resp["pendingVoteCount"] * data["voteConfig"]["pendingWeight"]

def lessExpectedVotes(a: sqlite3.Row, b: sqlite3.Row) -> float:
    return expectedVoteCount(a) - expectedVoteCount(b)