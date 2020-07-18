import asyncio, discord, json, requests ,pycountry, us, traceback
from discord.ext import commands
from datetime import datetime, timedelta, date
from os import listdir
from os.path import isfile, join

class Misc(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

# Graph (will be custom later)
    @commands.command()
    async def graph(self,ctx):
        embed = discord.Embed()
        embed.set_image(url="https://covid19.mathdro.id/api/og")
        await ctx.send(embed=embed)

# FAQ
    @commands.command()
    async def faq(self,ctx):
        embed = discord.Embed(title="Frequently Asked Questions", color=0xff80ff)
        embed.add_field(
            name="Who does the virus affect?",
            value="The virus is capable of infecting anyone, but effects will vary from person to person. For one, " +
            "the mortality rate for those under the age of 40 is approximately 0.2% while those over the age of 80 " +
            "is approximately 15%. Generally, people who have pre-existing major health complications, mainly " +
            "those with compromised immune systems, are significantly more likely to experience severe effects or " +
            "even death compared to those in good health.",
            inline=False)
        embed.add_field(name="How can I protect myself?",
            value="Make sure to wash your hands regularly and avoid touching your eyes, nose and mouth with unwashed " +
            "hands. Avoid close contact with people who are sick, and avoid travelling to countries that have been hit " +
            "particularly hard by the virus. Make sure to use a face mask whenever you venture outside, and if you will be in "+
            "especially dangerous areas consider using an N95 filter mask.",
            inline=False)
        embed.add_field(name="Who made this bot?",
            value="COVID-BOT was created by [cosmopath](https://github.com/cosmopath) using data from [Johns Hopkins CSSE](https://coronavirus.jhu.edu/map.html) " +
            "provided by an API authored by Github user [mathdroid.](https://github.com/mathdroid/covid-19-api)\n\n" +
            "If you have any questions about COVID-BOT [please PM me on Reddit here](https://reddit.com/u/cosmopath). " +
            "Additionally, COVID-BOT costs money to host and time " +
            "to maintain so if you appreciate the work I've done on it [please consider dropping me a few bucks on " +
            "my Ko-fi page.](https://ko-fi.com/cosmo)",
            inline=False)
        embed.add_field(name="How do I invite this bot to my server?",
            value="[**Click here to invite COVID-BOT to your server!**](https://discordapp.com/oauth2/authorize?client_id=685987072858652761&scope=bot&permissions=3072)" +
            "\nAlternatively, if you'd like an easy link to share, [cosmopath.com/covid](http://cosmopath.com/covid) will get you there too."
            "\n\nThe bot only asks for permission to read, write and embed messages in your server in order to function. Thanks for your interest!",
            inline=False)
        await ctx.send(embed=embed)

# Invite
    @commands.command()
    async def invite(self, ctx):
        embed=discord.Embed(
            title="Invite COVID-BOT", 
            description="[**Click here to invite COVID-BOT to your server!**](https://discordapp.com/oauth2/authorize?client_id=685987072858652761&scope=bot&permissions=3072)" +
            "\nAlternatively, if you'd like an easy link to share, [cosmopath.com/covid](http://cosmopath.com/covid) will get you there too."
            "\n\nThe bot only asks for permission to read, write and embed messages in your server in order to function. Thanks for your interest!",
            color=0x4af2a1)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Misc(bot))