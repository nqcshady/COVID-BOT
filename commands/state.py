import asyncio, discord, json, requests ,pycountry, us, traceback
from discord.ext import commands
from datetime import datetime, timedelta, date
from os import listdir
from os.path import isfile, join

class State(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

# State lookup
    @commands.command(aliases=['province', 'region'])
    async def state(self, ctx, *, state_name):
        print("Incoming !!state")
    # Getting state data
        state_url = "https://covid19.mathdro.id/api/confirmed"
        r = requests.get(state_url)

        i = 0
        state_formatted_name = ""
        total_confirmed = 0
        total_recovered = 0
        total_deaths = 0

    # US states by acronym
        if (len(state_name) == 2):
            state_name = us.states.lookup(state_name).name

        for x in r.json():
            if str(x['provinceState']).lower() == state_name.lower():
                state_formatted_name = x['provinceState']
                total_confirmed += int(x['confirmed'])
                total_recovered += int(x['recovered'])
                total_deaths += int(x['deaths'])
                state_last_epoch = int(x['lastUpdate'])
            i += 1

        if state_formatted_name != "":
            state_last_dt = datetime.fromtimestamp(state_last_epoch/1000.0)

        # Yesterday
            yesterday = (state_last_dt - timedelta(1)).strftime('%Y-%m-%d')
            yesterday_url = "https://covid19.mathdro.id/api/daily/" + yesterday
            r = requests.get(yesterday_url)

            i = 0
            yesterday_confirmed = 0
            yesterday_recovered = 0
            yesterday_deaths = 0

            for x in r.json():
                if str(x['provinceState']) == state_formatted_name:
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

        # Embed
            embed = discord.Embed(
            title="Data for " + state_formatted_name + " (last updated " +state_last_dt.strftime("%Y-%m-%d %H:%M") +")",color=0x8f0114
        )
            embed.add_field(name='Confirmed cases', value = str("{:,}".format(total_confirmed)) + "\n" + trend_confirmed_str)
            embed.add_field(name='Deaths', value = str("{:,}".format(total_deaths)) + "\n" +  trend_deaths_str)
            embed.add_field(name='Recoveries', 
                        value = str("{:,}".format(total_recovered)) + "\n" + trend_recovered_str)

            embed.add_field(name='Death rate', value = str(round(death_rate,2)) + "%  ")
            embed.add_field(name='Recovery rate', value = str(round(recovery_rate,2)) + "%  ")
            embed.set_footer(text="COVID-19 data from Johns Hopkins CSSE\nConsider donating to keep COVID-BOT afloat at ko-fi.com/cosmo")
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Data not found.",
                color=0x8f0114
        )
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(State(bot))