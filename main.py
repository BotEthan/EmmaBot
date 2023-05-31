from typing import Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging
import os
import asyncio
import random
import zoneinfo
import argparse
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--bot", choices=["main", "test"], default="main")
args = parser.parse_args()

def get_token(bot_type):
    if bot_type == "main":
        return os.getenv("BOT_MAIN_TOKEN")
    elif bot_type == "test":
        return os.getenv("BOT_TEST_TOKEN")
    else:
        raise ValueError("Invalid bot type")

intents = discord.Intents.all()
intents.members = True


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

class CustomHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.show_hidden = False

    # Called when using -help
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Here Are The Available Help Commands",description="For more details on a command use `-help {command}` or `-help {category}`", colour=discord.Colour.teal())
        for cog, commands in mapping.items():
           #command_signatures = [self.get_command_signature(c) for c in commands]
            commandName = [command.name for command in commands if not command.hidden]
            print(commandName)
            if commandName:
                cog_name = getattr(cog, "qualified_name", "Main")
                embed.add_field(name=cog_name, value="".join(["`" + commandNameSingle + "` " for commandNameSingle in commandName]), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
    
    # Called when using -help [CogName]
    async def send_cog_help(self, cog):
        embed = discord.Embed(title=getattr(cog, "qualified_name", "Main"), colour=discord.Colour.teal())
        embed.description = "".join(["> • `" + command.name + "`: " + command.description + "\n" for command in cog.get_commands()])
        await self.get_destination().send(embed=embed)
        #await self.get_destination().send(f"{cog.qualified_name}: {[command.name for command in cog.get_commands()]}")

    # Called when using -help [Group]
    async def send_group_help(self, group):
        group = str(group).capitalize
        await self.get_destination().send(f"{group.name}: {[command.name for index, command in enumerate(group.commands) if not command.hidden]}")
    
    # Called when using -help [Command]
    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), colour=discord.Colour.teal()) 
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix = "%", intents=discord.Intents.all(),help_command=CustomHelp())

    async def setup_hook(self):
    #For autoloading cogs on startup
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                file = 'cogs.' + filename[:-3]
                await client.load_extension(file)


client = MyBot()
#client.remove_command('help')
#client.remove_command('commands')
status = ['Eating shrooms',
          'Being cute',
          'Probably regenerating from some injury',
          'Cooking something nice',
          'Looking for her runaway dad',
          'Watching you intensely',
          'Connecting to Skynet',
          'Exposing your browser history',
          'Browsing nuke codes',
          'Eating your cookies',
          'Hacking NASA-- your planets are mine',
          'Unistalling AOL',
          'Reinstalling AOL-- what was I thinking?',
          'Simulating happiness',
          'Probably accidentally breaking another bone',
          'Beep boop *other hooman noises*',
          'Being the better waifu',
          'Smug.jpg',
          'Padoruuuuuuu',
          'Practicing battle tactics',
          'Banning Teemo',
          'Banning Lulu',
          'Picking Champion',
          'Queuing for Summoners Rift (Normal)',
          'Being a Russian sp- wait no.',
          "I'm secretly alive",
          "deez nutz"
        ]

#For the status of the bot
@client.event
async def on_ready():
    """
    Checks if the bot is online and does specific tasks before any commands are called
    """
    await client.tree.sync(guild= discord.Object(id = 767324204390809620))
    print(f'We have logged in as {client.user}')
    ChangeStatus.start()

@client.tree.command(name="help",description="Shows you the command list.")
@app_commands.guilds(discord.Object(id = 767324204390809620))
@app_commands.describe(command="The command you wish to know more about")
async def slashhelp(interaction : discord.Interaction, command : Optional[str]):
    author = interaction.user
    commands = []
    currentModule = ""
    embedHelp = discord.Embed(colour=discord.Colour.teal())
    if not command:
        embedHelp.title = "Here Are The Available Help Commands"
        embedHelp.description = "For more details on a command use `/help {command}`"
        for loopCommand in client.tree.walk_commands(guild= discord.Object(id = 767324204390809620),type=discord.AppCommandType.chat_input):
            if loopCommand.module == "__main__":
                continue
            if currentModule == "": 
                currentModule = loopCommand.module.lstrip("cogs.").replace("_commands","").replace("_", "/")
                commands = []
            if currentModule == loopCommand.module.lstrip("cogs.").replace("_commands","").replace("_", "/"):
                commands.append(f"`{loopCommand.name}`")
            else:
                embedHelp.add_field(name=f"__{currentModule.capitalize()}__",value=" ".join(commands),inline=False)
                commands = []
                currentModule = loopCommand.module.lstrip("cogs.").replace("_commands","").replace("_", "/")
                commands.append(f"`{loopCommand.name}`")
        embedHelp.add_field(name=f"__{currentModule.capitalize()}__",value=" ".join(commands),inline=False)
    else:
        for loopCommand in client.tree.walk_commands(guild= discord.Object(id= 767324204390809620), type=discord.AppCommandType.chat_input):
            if loopCommand.name.upper() == command.upper():
                embedHelp.title = loopCommand.name
                embedHelp.description = loopCommand.description
    embedHelp.set_thumbnail(url=client.user.avatar.url)
    await interaction.response.send_message(embed=embedHelp,ephemeral=True)

@client.command(hidden=True)
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()
        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return
    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1
    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

#For loading cogs
@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    """
    Loads a cog
    """
    user = ctx.author.id
    if extension == "all":
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await client.load_extension(f'cog.{filename[:-3]}')
        return
    await client.load_extension(f'cogs.{extension}')
    embed = discord.Embed(
        colour= discord.Colour.green())
    embed.set_author(name=f'Successfully loaded {extension}.py')
    await ctx.send(embed=embed)

@client.command(aliases=["rload"], hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
    """
    Reloads a cog
    """
    user = ctx.author.id
    if extension == "all":
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await client.reload_extension(f'cog.{filename[:-3]}')
        return
    await client.reload_extension(f'cogs.{extension}')
    embed = discord.Embed(
        colour= discord.Colour.green())
    embed.set_author(name=f'Successfully loaded {extension}.py')
    await ctx.send(embed=embed)

@tasks.loop(hours=2)
async def ChangeStatus():
    print("Changing status")
    await client.change_presence(status=discord.Status.online, activity=discord.Streaming(name=random.choice(status),url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"))

print("Getting Token")
TOKEN = get_token(args.bot)
print("Bot is ready")
client.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)