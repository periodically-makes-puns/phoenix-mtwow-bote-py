import sqlite3
from typing import List
from utils import data

def isContestant(conn: sqlite3.Connection, uid: int) -> bool:
    return isinstance(conn.cursor().execute("SELECT * FROM Contestants WHERE uid = ?;", uid).fetchone(), sqlite3.Row)

def isDead(conn: sqlite3.Connection, uid: int) -> bool:
    return bool(conn.cursor().execute("SELECT alive FROM Contestants WHERE uid=?;").fetchone()["alive"])

def addContestant(conn: sqlite3.Connection, uid: int):
    conn.execute("INSERT INTO Contestants (uid, alive) VALUES (?, 1);")

def phase(conn: sqlite3.Connection) -> str:
    return conn.execute("SELECT phase FROM Status;").fetchone()["phase"]

def roundNum(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT roundNum FROM Status;").fetchone()["roundNum"]

def editResponse(conn: sqlite3.Connection, uid: int, responseNumber: int, response: str):
    conn.execute("UPDATE Responses SET response=? WHERE uid=? AND rid=?;", (uid, responseNumber, response))

def addResponse(conn: sqlite3.Connection, uid: int, responseNumber: int, response: str):
    conn.execute("INSERT INTO Responses (uid, rid, response) VALUES (?, ?, ?);", (uid, responseNumber, response))


def getResponseByUID(conn: sqlite3.Connection, uid: int, responseNumber: int) -> sqlite3.Row:
    return conn.execute("SELECT * FROM Responses WHERE uid = ? AND rid = ?;", (uid, responseNumber)).fetchone()

def getResponseByID(conn: sqlite3.Connection, id: int) -> sqlite3.Row:
    return conn.execute("SELECT * FROM Responses WHERE id = ?;", id).fetchone()

def allowedResponses(conn: sqlite3.Connection, uid: int) -> int:
    return conn.execute("SELECT allowedResponses FROM Contestants WHERE uid = ?;", uid).fetchone()["allowedResponses"]

def getAllResponsesButOwn(conn: sqlite3.Connection, uid: int) -> List[sqlite3.Row]:
    return conn.execute("SELECT * FROM Responses WHERE uid != ?;", uid).fetchall()

def getAllResponsesButOne(conn: sqlite3.Connection, uid: int, responseNumber: int) -> List[sqlite3.Row]:
    return conn.execute("SELECT * FROM Responses WHERE uid != ? OR rid != ?;", (uid, responseNumber)).fetchall()


def getAllResponses(conn: sqlite3.Connection) -> List[sqlite3.Row]:
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