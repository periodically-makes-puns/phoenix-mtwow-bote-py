from discord.ext import commands
from ..general import sqlutils
import sqlite3
conn = sqlite3.Connection("../data.db")



class MTwowAdministrator(commands.Cog):
    @commands.command(brief="Initialises database.")
    @commands.check(commands.is_owner)
    def init(self, ctx):
        sqlutils.handleSQLErrors(sqlutils.init(conn))

    @commands.command(brief="Wipes database.")
    @commands.check(commands.is_owner)
    def wipe(self, ctx):
        sqlutils.handleSQLErrors(sqlutils.wipe(conn))