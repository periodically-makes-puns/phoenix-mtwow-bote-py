"""
Defines the functions needed for the common user.
"""
from . import sqlutils
from ...generic.utils import data
import sqlite3
import random
import logging
from typing import Tuple, Union, List, Callable
sql_logger = logging.getLogger("sqlite3")

@sqlutils.handleSQLErrors
def signup(conn: sqlite3.Connection, uid: int) -> Tuple[int, str]:
    if sqlutils.isContestant(conn, uid):
        return (2, "You are already signed up.")
    if data["owner"] == uid:
        return (2, "You are an administrator. You may not sign up.")
    if sqlutils.phase(conn) != "signups" and (sqlutils.phase(conn) != "responding" or sqlutils.roundNum(conn) != 1):
        return (2, "Not in signup phase.")
    sqlutils.addContestant(conn, uid)
    return (0, "You have been signed up.")
    
@sqlutils.handleSQLErrors
def respond(conn: sqlite3.Connection, uid: int, responseNumber: int, response: str) -> Tuple[int, str]:
    responseNumber -= 1
    if not sqlutils.isContestant(conn, uid):
        return (2, "You are not a contestant!")
    if sqlutils.isDead(conn, uid):
        return (2, "You are eliminated!")
    if sqlutils.phase(conn) != "respond":
        return (2, "Not in responding phase.")
    if sqlutils.allowedResponses(conn, uid) <= responseNumber:
        return (2, "You are not allowed to submit a response with that ID.")
    status = 0
    if sqlutils.getResponseByUID(conn, uid, responseNumber):
        sqlutils.editResponse(conn, uid, responseNumber, response)
        message = "Your response has been edited!"
    else:
        sqlutils.addResponse(conn, uid, responseNumber, response)    
        message = "Your response has been submitted!"
    response = sqlutils.removeDisallowedChars(response)
    if sqlutils.wordCount(response) > 10:
        status = 1
        message = "Your word count is over 10 words!"
    elif sqlutils.wordCount(response) < 10:
        message = "Your word count is under 10 words."
    return (status, message)

@sqlutils.handleSQLErrors
def newScreen(conn: sqlite3.Connection, uid: int, voteNumber: int, screenSize: int) -> Tuple[int, Union[List[sqlite3.Row], str]]:
    # our pool of responses
    allowedResponses = []
    # weights per response
    weights = []
    # confirmed in our screen
    screen = []
    if data["voteConfig"]["giveContestantsOwnResponses"]:
        resp = sqlutils.getResponseByUID(conn, uid, voteNumber)
        if resp is not None:
            screen.append(resp)
            allowedResponses = sqlutils.getAllResponsesButOwn(conn, uid)
            if screenSize > len(allowedResponses) + 1:
                # we won't have enough responses!
                # allow own responses
                allowedResponses = sqlutils.getAllResponsesButOne(conn, uid, voteNumber)
                if screen > len(allowedResponses) + 1:
                    # screen size too large >:(
                    return (2, "Screen size requested too large.")
        else:
            allowedResponses = sqlutils.getAllResponses(conn)
            if screenSize > len(allowedResponses):
                return (2, "Screen size requested too large.")
    scheme = data["voteConfig"]["voteBalacingScheme"]
    if scheme == "equal":
        # All responses are treated equally.
        # Implemented by weighting all responses with weight 1
        weights = [1 for i in allowedResponses]
    if scheme == "pareto":
        # Responses are weighted by 1 / (voteCount + 1)
        for resp in allowedResponses:
            weights.append(10 / (sqlutils.expectedVoteCount(resp) + 1)) # 10 is on top so the randomisation range isn't too small
    if scheme == "linear":
        # Responses are weighted by maxVoteCount - thisVoteCount + 1
        maxWeight = 0
        for resp in allowedResponses:
            maxWeight = max(sqlutils.expectedVoteCount(resp), maxWeight)
        for resp in allowedResponses:
            weights.append(maxWeight - sqlutils.expectedVoteCount(resp) + 1)
    if scheme == "strict":
        # Responses with less votes ALWAYS go first.
        # Implemented by limiting response sample to lowest N responses as requested
        # then allowing randomizer to select all N in whatever order.
        allowedResponses.sort(key=sqlutils.expectedVoteCount)
        numResps = screenSize - int(data["voteConfig"]["giveContestantsOwnResponses"])
        allowedResponses = allowedResponses[0:numResps]
        weights = [1 for i in allowedResponses]
    # Fills the screen
    while len(screen) < screenSize:
        sumWeights = sum(weights) # sum weights
        cumulativeWeights = [0]
        for i in range(len(weights)):
            cumulativeWeights.append(cumulativeWeights[i] + weights[i])
        val = random.random() * sumWeights
        # I could binary search but it's already O(n ^ 2) soooooo
        for i in range(1, len(cumulativeWeights)):
            if cumulativeWeights[i] > val:
                ind = i
                break
        screen.append(allowedResponses[i-1])
        del weights[ind]
        del allowedResponses[ind]
    """
     Idea for possible weighted randomiser that runs in O(N log N): 
     - N is the number of responses.
     - Use a Fenwick Tree to find and update segment sums in O(log N).
     - Generate a random float in the range indicated by [0, sum(0, N)], that's the sum of all the weights. We'll call this number "random".
       - That's done in O(log N) time since Fenwick Tree queries are O(log N).
     - Binary search to find the smallest index i such that: A[i] != 0, and sum(0, i) >= random.
     - The first condition is to ensure that deletions are handled nicely.
     - To handle deletions, we simply set A[i] = 0. 
     This is pretty complicated and I won't use it since it's unlikely I'll get more than 100 responses
     """
    return (0, screen)


def getGSeed(screen: List[sqlite3.Row]) -> str:
    pass

def getScreen(gseed: str) -> List[sqlite3.Row]:
    pass