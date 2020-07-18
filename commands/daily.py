import asyncio, discord, json, requests ,pycountry, us, traceback
from discord.ext import commands
from datetime import datetime, timedelta, date
from os import listdir
from os.path import isfile, join

class Daily(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

# Daily update command
    @commands.command(aliases=['world'])
    async def daily(self,ctx):
        print("Incoming !!world")
        total_url = "https://covid19.mathdro.id/api"
        r = requests.get(total_url)

        total_confirmed = r.json()['confirmed']['value']
        total_deaths = r.json()['deaths']['value']
        total_recovered = r.json()['recovered']['value']
        last_dt = datetime.strptime(r.json()['lastUpdate'], "%Y-%m-%dT%X.%fZ")

    # Yesterday
        yesterday = (last_dt - timedelta(1)).strftime('%Y-%m-%d')
        yesterday_url = "https://covid19.mathdro.id/api/daily/" + yesterday
        r = requests.get(yesterday_url)

        i = 0
        yesterday_confirmed = 0
        yesterday_recovered = 0
        yesterday_deaths = 0

        for x in r.json():
            yesterday_confirmed += int(x['confirmed'])
            yesterday_recovered += int(x['recovered'])
            yesterday_deaths += int(x['deaths'])
            i += 1

    # Calc trend
        trend_confirmed = total_confirmed - yesterday_confirmed
        trend_recovered = total_recovered - yesterday_recovered
        trend_deaths = total_deaths - yesterday_deaths


    # Lazy fix for bug
        if yesterday_confirmed == 0: trend_confirmed = 0
        if yesterday_recovered == 0: trend_recovered = 0
        if yesterday_deaths == 0: trend_deaths = 0

        if (trend_confirmed >= 0):
         trend_confirmed_str = "(up " + str("{:,}".format(trend_confirmed)) + " today)"
        else: trend_confirmed_str = "(adj." + str("{:,}".format(trend_confirmed)) + " today)"

        if (trend_recovered >= 0):
            trend_recovered_str = "(up " + str("{:,}".format(trend_recovered)) + " today)"
        else: trend_recovered_str = "(adj. " + str("{:,}".format(trend_recovered)) + " today)"

        if (trend_deaths >= 0):
            trend_deaths_str = "(up " + str("{:,}".format(trend_deaths)) + " today)"
        else: trend_deaths_str = "(adj. " + str("{:,}".format(trend_deaths)) + " today)"

    # Death rate
        death_rate = total_deaths/total_confirmed * 100
        recovery_rate = total_recovered/total_confirmed * 100

        embed = discord.Embed(
            title="Worldwide data (last updated " + last_dt.strftime("%Y-%m-%d %H:%M") +"):",color=0x8f0114
    )
        embed.add_field(name='Confirmed cases', 
                    value = str("{:,}".format(total_confirmed)) + "\n" + trend_confirmed_str)
        embed.add_field(name='Deaths', 
                    value = str("{:,}".format(total_deaths)) + "\n" +  trend_deaths_str)
        embed.add_field(name='Recoveries', 
                    value = str("{:,}".format(total_recovered)) + "\n" + trend_recovered_str)

        embed.add_field(name='Death rate', value = str(round(death_rate,2)) + "%  ")
        embed.add_field(name='Recovery rate', value = str(round(recovery_rate,2)) + "%  ")

        embed.set_footer(text="COVID-19 data from Johns Hopkins CSSE\nConsider donating to keep COVID-BOT afloat at ko-fi.com/cosmo")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Daily(bot))