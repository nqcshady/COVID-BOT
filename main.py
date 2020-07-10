# Importing necessary libraries
import asyncio
import discord
from discord.ext import commands
import json
import requests
from datetime import datetime, timedelta, date
import pycountry
import us

# Creating Discord bot object and removing the default !!help
bot = commands.Bot(command_prefix='!!')
bot.remove_command('help')

# Global variables
footer_text = "COVID-19 data from Johns Hopkins CSSE\nConsider donating to keep COVID-BOT afloat at ko-fi.com/cosmo"

# Log-in confirmation to console
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="in " + str(len(bot.guilds)) + " servers"))

# Daily update command
@bot.command(aliases=['world'])
async def daily(ctx):
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
        trend_confirmed_str = "(up " + \
                                 str("{:,}".format(trend_confirmed)) + " today)"
    else: trend_confirmed_str = "(adj." + str("{:,}".format(trend_confirmed)) + " today)"

    if (trend_recovered >= 0):
        trend_recovered_str = "(up " + \
                                 str("{:,}".format(trend_recovered)) + " today)"
    else: trend_recovered_str = "(adj. " + str("{:,}".format(trend_recovered)) + " today)"

    if (trend_deaths >= 0):
        trend_deaths_str = "(up " + str("{:,}".format(trend_deaths)) + " today)"
    else: trend_deaths_str = "(adj. " + str("{:,}".format(trend_deaths)) + " today)"

    # Death rate
    death_rate = total_deaths/total_confirmed * 100
    recovery_rate = total_recovered/total_confirmed * 100

    embed = discord.Embed(
        title="Worldwide data (last updated " +
            last_dt.strftime("%Y-%m-%d %H:%M") +
            "):",
        color=0x8f0114
    )
    embed.add_field(name='Confirmed cases', 
                    value = str("{:,}".format(total_confirmed)) + "\n" + trend_confirmed_str)
    embed.add_field(name='Deaths', 
                    value = str("{:,}".format(total_deaths)) + "\n" +  trend_deaths_str)
    embed.add_field(name='Recoveries', 
                    value = str("{:,}".format(total_recovered)) + "\n" + trend_recovered_str)

    embed.add_field(name='Death rate', value = str(round(death_rate,2)) + "%  ")
    embed.add_field(name='Recovery rate', value = str(round(recovery_rate,2)) + "%  ")

    embed.set_footer(text=footer_text)
    await ctx.send(embed=embed)

# Country update command
@bot.command()
async def country(ctx, *, country_name):
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
        trend_confirmed_str = "(up " + \
                                 str("{:,}".format(trend_confirmed)) + " today)"
    else: trend_confirmed_str = "(adj." + str("{:,}".format(trend_confirmed)) + " today)"

    if (trend_recovered >= 0):
        trend_recovered_str = "(up " + \
                                 str("{:,}".format(trend_recovered)) + " today)"
    else: trend_recovered_str = "(adj. " + str("{:,}".format(trend_recovered)) + " today)"

    if (trend_deaths >= 0):
        trend_deaths_str = "(up " + str("{:,}".format(trend_deaths)) + " today)"
    else: trend_deaths_str = "(adj. " + str("{:,}".format(trend_deaths)) + " today)"

    # Death rate
    death_rate = total_deaths/total_confirmed * 100
    recovery_rate = total_recovered/total_confirmed * 100

    # Embed
    embed = discord.Embed(
        title="Data for " + country_formatted_name + " (last updated " +
        last_dt.strftime("%Y-%m-%d %H:%M") +
        ")",
        color=0x8f0114
    )
    embed.add_field(name='Confirmed cases', 
                    value = str("{:,}".format(total_confirmed)) + "\n" + trend_confirmed_str)
    embed.add_field(name='Deaths', 
                    value = str("{:,}".format(total_deaths)) + "\n" +  trend_deaths_str)
    embed.add_field(name='Recoveries', 
                    value = str("{:,}".format(total_recovered)) + "\n" + trend_recovered_str)

    embed.add_field(name='Death rate', value = str(round(death_rate,2)) + "%  ")
    embed.add_field(name='Recovery rate', value = str(round(recovery_rate,2)) + "%  ")
    
    embed.set_footer(text=footer_text)
    await ctx.send(embed=embed)

# State lookup
@bot.command(aliases=['province', 'region'])
async def state(ctx, *, state_name):
    print("Incoming !!state")
    # Getting state data
    state_url = "https://covid19.mathdro.id/api/confirmed"
    r = requests.get(state_url)

    i = 0
    state_formatted_name = ""
    total_confirmed = 0
    total_recovered = 0
    total_deaths = 0
    total_last_epoch = 0

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
            trend_confirmed_str = "(up " + \
                                    str("{:,}".format(trend_confirmed)) + " today)"
        else: trend_confirmed_str = "(adj." + str("{:,}".format(trend_confirmed)) + " today)"

        if (trend_recovered >= 0):
            trend_recovered_str = "(up " + \
                                    str("{:,}".format(trend_recovered)) + " today)"
        else: trend_recovered_str = "(adj. " + str("{:,}".format(trend_recovered)) + " today)"

        if (trend_deaths >= 0):
            trend_deaths_str = "(up " + str("{:,}".format(trend_deaths)) + " today)"
        else: trend_deaths_str = "(adj. " + str("{:,}".format(trend_deaths)) + " today)"

        # Death rate
        death_rate = total_deaths/total_confirmed * 100
        recovery_rate = total_recovered/total_confirmed * 100

        # Embed
        embed = discord.Embed(
            title="Data for " + state_formatted_name + " (last updated " +
            state_last_dt.strftime("%Y-%m-%d %H:%M") +
            ")",
            color=0x8f0114
        )
        embed.add_field(name='Confirmed cases', 
                        value = str("{:,}".format(total_confirmed)) + "\n" + trend_confirmed_str)
        embed.add_field(name='Deaths', 
                        value = str("{:,}".format(total_deaths)) + "\n" +  trend_deaths_str)
        embed.add_field(name='Recoveries', 
                        value = str("{:,}".format(total_recovered)) + "\n" + trend_recovered_str)

        embed.add_field(name='Death rate', value = str(round(death_rate,2)) + "%  ")
        embed.add_field(name='Recovery rate', value = str(round(recovery_rate,2)) + "%  ")
        embed.set_footer(text=footer_text)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Data not found.",
            color=0x8f0114
        )
        await ctx.send(embed=embed)

# County lookup
@bot.command()
async def county(ctx, *, county_name):
    print("Incoming !!county")

    # Getting state data
    today = str(date.today() - timedelta(1))
    county_url = "https://covid19.mathdro.id/api/daily/" + today
    r = requests.get(county_url)
    print (county_url)

    i = 0
    county_formatted_name = ""
    total_confirmed = 0
    total_recovered = 0
    total_deaths = 0

    for x in r.json():
        if str(x["admin2"]).lower() == county_name.lower():
            county_formatted_name = x['combinedKey']
            total_confirmed = int(x['confirmed'])
            total_recovered = int(x['recovered'])
            total_deaths = int(x['deaths'])
            county_last_dt = datetime.strptime(
                x['lastUpdate'], "%Y-%m-%d %H:%M:%S")
        i += 1

    trend_confirmed_str = ""
    trend_recovered_str = ""
    trend_deaths_str = ""

    if county_formatted_name != "":

        # Yesterday
        yesterday = (county_last_dt - timedelta(1)).strftime('%Y-%m-%d')
        yesterday_url = "https://covid19.mathdro.id/api/daily/" + yesterday
        r = requests.get(yesterday_url)

        i = 0
        yesterday_confirmed = 0
        yesterday_recovered = 0
        yesterday_deaths = 0

        for x in r.json():
            if str(x['combinedKey']) == county_formatted_name:
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
            trend_confirmed_str = "(up " + \
                                    str("{:,}".format(trend_confirmed)) + " today)"
        else: trend_confirmed_str = "(adj." + str("{:,}".format(trend_confirmed)) + " today)"

        if (trend_recovered >= 0):
            trend_recovered_str = "(up " + \
                                    str("{:,}".format(trend_recovered)) + " today)"
        else: trend_recovered_str = "(adj. " + str("{:,}".format(trend_recovered)) + " today)"

        if (trend_deaths >= 0):
            trend_deaths_str = "(up " + str("{:,}".format(trend_deaths)) + " today)"
        else: trend_deaths_str = "(adj. " + str("{:,}".format(trend_deaths)) + " today)"

        # Death rate
        death_rate = total_deaths/total_confirmed * 100
        recovery_rate = total_recovered/total_confirmed * 100

        # Embed
        embed = discord.Embed(
            title="Data for " + county_formatted_name + " (last updated " +
            county_last_dt.strftime("%Y-%m-%d %H:%M") +
            ")",
            color=0x8f0114
        )
        embed.add_field(name='Confirmed cases', 
                        value = str("{:,}".format(total_confirmed)) + "\n" + trend_confirmed_str)
        embed.add_field(name='Deaths', 
                        value = str("{:,}".format(total_deaths)) + "\n" +  trend_deaths_str)
        embed.add_field(name='Recoveries', 
                        value = str("{:,}".format(total_recovered)) + "\n" + trend_recovered_str)

        embed.add_field(name='Death rate', value = str(round(death_rate,2)) + "%  ")
        embed.add_field(name='Recovery rate', value = str(round(recovery_rate,2)) + "%  ")
        # embed.add_field(name='⠀', value = '⠀')
        embed.set_footer(text=footer_text)
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Data not found.",
            color=0x8f0114
        )
        await ctx.send(embed=embed)

# Graph (will be custom later)
@bot.command()
async def graph(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://covid19.mathdro.id/api/og")
    await ctx.send(embed=embed)

# FAQ
@bot.command()
async def faq(ctx):
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

# Help command
@bot.command()
async def help(ctx):
	embed = discord.Embed(title="COVID-BOT Help", color=0xff80ff)
	embed.add_field(name="!!world", value="Overview of the worldwide stats. Can also be called with `!!daily`.", inline=False)
	embed.add_field(name="!!country location", value="Country-specific stats lookup.\n`Example: !!country Japan`", inline=False)
	embed.add_field(name="!!state location", value="State/province/region-specific stats lookup. Can also be called with !!province or !!region.\n`Example: !!state Texas`", inline=False)
	embed.add_field(name="!!faq", value="More information about COVID-19 and the bot, including how to add the bot to your server.", inline=False)
	embed.set_footer(text="Help COVID-BOT stay up by donating at ko-fi.com/cosmo")
	await ctx.send(embed=embed)

# Update status when the bot joins a new server
@bot.event
async def on_guild_join(guild):
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="in " + str(len(bot.guilds)) + " servers"))

# Invite
@bot.command()
async def invite(ctx):
    embed=discord.Embed(
        title="Invite COVID-BOT", 
        description="[**Click here to invite COVID-BOT to your server!**](https://discordapp.com/oauth2/authorize?client_id=685987072858652761&scope=bot&permissions=3072)" +
            "\nAlternatively, if you'd like an easy link to share, [cosmopath.com/covid](http://cosmopath.com/covid) will get you there too."
            "\n\nThe bot only asks for permission to read, write and embed messages in your server in order to function. Thanks for your interest!",
        color=0x4af2a1)
    await ctx.send(embed=embed)

bot.run("TOKEN", bot=True)