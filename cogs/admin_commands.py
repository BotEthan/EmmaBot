import discord
from discord import app_commands
from typing import Optional, Union
import typing
from discord.ext import commands, tasks
from discord.ext.commands import Greedy
from asyncio import sleep

class Admin(commands.Cog):
    
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog: "Admin Commands" loaded.')

#-----------------------------------------------------------

    #For purge chat
    @app_commands.command(name="clear",description="Clear some messages away.")
    @app_commands.describe(amount="The amount of messages you want to remove.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.checks.has_permissions(administrator=True)
    async def _clear(self, interaction : discord.Interaction, amount : int = 3):
        """
        Clear some messages away.

        **Usage:**
            `-clear [amount]`
        
        **Arguments:**
            `amount`: The amount of messages you want to clear. Default is 3.
        """
        await interaction.response.send_message(content=f"Deleted {amount} messages from {interaction.channel.mention}",ephemeral=True)
        await interaction.channel.purge(limit=(amount+1))
        #string = f'Deleted {amount} messages from {interaction.channel.mention}'
        #await sleep(10)
        #await interaction.delete_original_response()

#-----------------------------------------------------------
    
    #For move members
    @app_commands.command(description="Move a large amount of people to another vc")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.describe(voicechannel="The voice channel you wish to move all to",members="A list of people you specifically want to move")
    @app_commands.checks.has_permissions(administrator=True)
    async def movevoicechannel(self,interaction : discord.Interaction,voicechannel : discord.VoiceChannel,*, members : Optional[str]):
        currentChannel = interaction.user.voice.channel
        if members:
            try:
                members = members.split(" ")
                for member in members:
                    print(member)
                    member = member.lstrip("<@")
                    member = member.rstrip(">")
                    print(member)
                    member = await interaction.guild.fetch_member(member)
                    print(member)
                    if member in currentChannel.members:
                        await member.move_to(voicechannel)
            except:
                embedIncorrectUsage = discord.Embed(colour=discord.Colour.red(),title=f"Incorrect usage. List of users must be `@[User]` separated by a space")
                await interaction.response.send_message(embed=embedIncorrectUsage)
                return
        else:
            for member in currentChannel.members:
                print(member.display_name)
                await member.move_to(voicechannel)
        embedMovedUsers = discord.Embed(colour=discord.Colour.green(),title=f"Success!",description=f"Moved members to {voicechannel.mention}")
        await interaction.response.send_message(embed=embedMovedUsers)

#-----------------------------------------------------------
# Setup
async def setup(client):
    await client.add_cog(Admin(client))