import asyncio, discord, json, requests ,pycountry, us, traceback
from discord.ext import commands
from datetime import datetime, timedelta, date
from os import listdir
from os.path import isfile, join

class Country(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(pass_context = True)
    async def country(self, ctx, *, country_name):
        print("Incoming !!country")
        if (country_name.lower() == 'uk'.lower()): country_name = 'gbr'
        if (country_name.lower() == 'south korea'.lower()): country_name = 'kor'
        if (country_name.lower() == 'iran'.lower()): country_name = 'irn'
        if (country_name.lower() == 'russia'.lower()): country_name = 'rus'
        if (country_name.lower() == 'america'.lower()): country_name = 'US'

        # Weird exception in pycountry
        if (country_name.lower() == 'kosovo'.lower()):
            country_formatted_name = "Kosovo"
            country_code = "XKX"
        else:
            country_code = pycountry.countries.lookup(country_name).alpha_3
            country_formatted_name = pycountry.countries.lookup(country_name).name

        # Hacky API workaround
        if (country_formatted_name == 'United States'): 
            country_formatted_name = 'US'

        if (country_formatted_name =='Korea, Republic of'): 
            country_formatted_name = 'Korea, South'

        if (country_formatted_name == 'Viet Nam'): 
            country_formatted_name = 'Vietnam'

        if (country_formatted_name == "Iran, Islamic Republic of"): 
            country_formatted_name = "Iran"

        if (country_formatted_name == "Czechia"): 
            country_code = "Czechia"

        # Getting country data
        country_url = "https://covid19.mathdro.id/api/countries/" + country_code
        r = requests.get(country_url)
        total_confirmed = r.json()['confirmed']['value']
        total_deaths = r.json()['deaths']['value']
        total_recovered = r.json()['recovered']['value']
        last_dt = datetime.strptime(r.json()['lastUpdate'], "%Y-%m-%dT%X.%fZ")

        # Awful workaround for API limitation, pt. 1
        counter = 0
        while (counter <= 1):
            # Yesterday
            yesterday = (last_dt - timedelta(1 + counter)).strftime('%Y-%m-%d')
            yesterday_url = "https://covid19.mathdro.id/api/daily/" + yesterday
            r = requests.get(yesterday_url)

            i = 0
            yesterday_confirmed = 0
            yesterday_recovered = 0
            yesterday_deaths = 0

            for x in r.json():
                if str(x['countryRegion']) == country_formatted_name:
                    yesterday_confirmed += int(x['confirmed'])
                    yesterday_recovered += int(x['recovered'])
                    yesterday_deaths += int(x['deaths'])
                i += 1

            # Stupid API shit
            if (country_formatted_name == "Czechia" or country_code == "CZE"): 
                country_formatted_name = "Czech Republic"

            # Calc trend
            trend_confirmed = total_confirmed - yesterday_confirmed
            trend_recovered = total_recovered - yesterday_recovered
            trend_deaths = total_deaths - yesterday_deaths

            # Lazy fix for bug
            if yesterday_confirmed == 0: trend_confirmed = 0
            if yesterday_recovered == 0: trend_recovered = 0
            if yesterday_deaths == 0: trend_deaths = 0

            # Awful workaround for API limitation, pt. 2
            if (trend_confirmed == 0) and (trend_recovered == 0) and (trend_deaths == 0) and (counter == 0):
                counter += 1
            else:
                break

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
        embed = discord.Embed(title="Data for " + country_formatted_name + " (last updated " + last_dt.strftime("%Y-%m-%d %H:%M") +")",color=0x8f0114)
        embed.add_field(name='Confirmed cases', value = str("{:,}".format(total_confirmed)) + "\n" + trend_confirmed_str)
        embed.add_field(name='Deaths', value = str("{:,}".format(total_deaths)) + "\n" +  trend_deaths_str)
        embed.add_field(name='Recoveries', value = str("{:,}".format(total_recovered)) + "\n" + trend_recovered_str)
        embed.add_field(name='Death rate', value = str(round(death_rate,2)) + "%  ")
        embed.add_field(name='Recovery rate', value = str(round(recovery_rate,2)) + "%  ")
    
        embed.set_footer(text=("COVID-19 data from Johns Hopkins CSSE\nConsider donating to keep COVID-BOT afloat at ko-fi.com/cosmo"))
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Country(bot))
