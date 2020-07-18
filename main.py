# Importing necessary libraries
import asyncio, discord, json, requests ,pycountry, us, traceback
from discord.ext import commands
from datetime import datetime, timedelta, date
from os import listdir
from os.path import isfile, join

# Creating Discord bot object and removing the default !!help
bot = commands.Bot(command_prefix='!!')
bot.remove_command('help')

# Log-in confirmation to console
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="in " + str(len(bot.guilds)) + " servers"))

if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in listdir('commands') if isfile(join('commands', f))]:
        try:
            bot.load_extension('commands' + "." + extension)
        except (discord.ClientException, ModuleNotFoundError):
            print(f'Failed to load extension {extension}.')
            traceback.print_exc()

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

@commands.is_owner()
@bot.command(pass_context=True)
async def load(ctx, extension):
    try:    
        bot.load_extension('commands' + "." + extension)
        await ctx.send("Sucessfully loaded `{}`".format(extension))
    except Exception as error:
        await ctx.send("Error loading {0}, consult console for more information. [{1}]".format(extension,error))

@commands.is_owner()
@bot.command(pass_context=True)
async def unload(ctx, extension):
    try:    
        bot.unload_extension('commands' + "." + extension)
        await ctx.send("Sucessfully unloaded `{}`".format(extension))
    except Exception as error:
        await ctx.send("Error unloading {0}, consult console for more information. [{1}]".format(extension,error))

# Update status when the bot joins a new server
@bot.event
async def on_guild_join(guild):
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="in " + str(len(bot.guilds)) + " servers"))


bot.run("TOKEN")
