from discord.ext import commands
from ..general import sqlutils, admin
from ...generic.utils import parse_time, data
import sqlite3
import logging
conn = sqlite3.Connection("./package/mtwow/data.db")
discord_logger = logging.getLogger("discord")


class MTwowAdministrator(commands.Cog):
    @commands.command(brief="Initialises database.")
    @commands.check(commands.is_owner())
    async def init(self, ctx: commands.Context):
        sqlutils.init(conn)

    @commands.command(brief="Wipes database.")
    @commands.check(commands.is_owner())
    async def wipe(self, ctx: commands.Context):
        sqlutils.wipe(conn)

    @commands.command(brief="Starts signups.")
    @commands.check(commands.is_owner())
    async def start_signups(self, ctx: commands.Context, time: parse_time):
        if time[0] == 0:
            ret = admin.start_signups(conn, time[1])
            if ret is not None:
                await ctx.send("Error: " + ret[1])
            else:
                await ctx.send("Started signups!")
        else:
            await ctx.send("Error: " + time[1])
    

def setup(bot: commands.Bot):
    discord_logger.info("Loading extension mtwow.discord.admin")
    bot.add_cog(MTwowAdministrator())

def teardown(bot: commands.Bot):
    discord_logger.info("Unloading extension mtwow.discord.admin")
    bot.remove_cog("MTwowAdministrator")