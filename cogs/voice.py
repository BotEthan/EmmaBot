import asyncio
import asqlite
from math import ceil
from typing import Optional
import discord
from discord import app_commands
from discord.utils import get
from discord.ext import commands, tasks
import os
import json
from classes.music import *
import threading

class Voice(commands.Cog):

    name="Voice"

    def __init__(self,client : commands.Bot) -> None:
        self.client = client
        self.lock = threading.Lock()
        self.servers_dict = {}
        self.amount_per_page = 5

    async def join_voice(self, interaction : discord.Interaction):
        if interaction.user.voice.channel == None:
            embed_member_not_in_vc = discord.Embed(colour=discord.Colour.red(), title="Unable to find channel to connect to. Please ensure that you are in a voice channel")
            await interaction.channel.send(embed=embed_member_not_in_vc)
            return None
        print(self.servers_dict)
        #Checking if the guild is already in the dict and making a fresh one
        if str(interaction.guild.id) not in self.servers_dict:
            self.servers_dict[str(interaction.guild.id)] = ServerMusic(interaction.guild)
        elif str(interaction.guild.id) in self.servers_dict and self.servers_dict[str(interaction.guild.id)].voice.is_playing == False:
            del self.servers_dict[str(interaction.guild.id)]
            self.servers_dict[str(interaction.guild.id)] = ServerMusic(interaction.guild)
        elif str(interaction.guild.id) in self.servers_dict and self.servers_dict[str(interaction.guild.id)].voice.is_playing == True:
            pass

        
        print(self.servers_dict)

        #Trying to connect to the VC and reporting if an error occured
        print(f"Voice: {self.servers_dict[str(interaction.guild.id)].voice}")
        outcome = await self.servers_dict[str(interaction.guild.id)].join(interaction)
        print("LOG: Checking join outcome")
        if outcome == 0:
            embedJoin = discord.Embed(
            colour= discord.Colour.blue(),
            title= f":musical_note: Joined {interaction.user.voice.channel} :musical_note:"
            )
            return embedJoin
        elif outcome == 1:
            embedFailedJoin = discord.Embed(
            colour= discord.Colour.blue(),
            title= f"Failed to join {interaction.user.voice.channel}. Possibly because I am in another voice channel or do not have the correct permissions"
            )
            return embedFailedJoin
        else:
            return None

    @commands.Cog.listener()
    async def on_voice_client_error(error, *args, **kwargs):
        print(f"Voice client error: {error}")

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog: "Voice Commands" loaded.')

    @commands.Cog.listener()
    async def on_guild_join(self, guild : discord.Guild):
        async with asqlite.connect("./databases/music_queue.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM music_settings WHERE server_id = ?""", (guild.id))
                results = await c.fetchone()
                if results == None:
                    await c.execute("""INSERT INTO music_settings VALUES (?,?,?,?)""", (guild.id,100,0,None))
                    await connection.commit()

#-----------------------------------------------------------

    @app_commands.command(description="Make Emma join the voice channel")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def join(self, interaction : discord.Interaction):
        await interaction.response.defer()
        embed = await self.join_voice(interaction)
        if not embed == None:
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(content="Failed to join")

#-----------------------------------------------------------

    #For the leave command
    @app_commands.command(description="Kick Emma out of the voice channel")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def leave(self, interaction : discord.Interaction):
        #Defer the response for a followup to allow time to process
        await interaction.response.defer()
        with self.lock:
            #Checking if the guild is already in the dict and if not meaning there is no active bot
            if str(interaction.guild.id) in self.servers_dict:
                #Trying to make the bot leave and seeing what it returns with
                if await self.servers_dict[str(interaction.guild.id)].leave() == 0:
                    embed_leave = discord.Embed(
                    colour= discord.Colour.blue(),
                    title= f":mute: Left {interaction.user.voice.channel} :mute:"
                )
                    await interaction.followup.send(embed=embed_leave)    
                    #Delete the server reference from the dictionary
                    del self.servers_dict[str(interaction.guild.id)]
                    os.remove(path=f"./music_queues/{interaction.guild.id}/")
            else:
                embed_leave = discord.Embed(
                    colour= discord.Colour.blue(),
                    title= "I am not currently in a voice channel or not in a voice channel with you"
                )
                await interaction.followup.send(embed=embed_leave)

#-----------------------------------------------------------

    #For looping the playlist
    @app_commands.command(description="Toggle looping so that you can hear the same thing over and over.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def loop(self, interaction : discord.Interaction):
        try:
            with self.lock:
                embed_loop = self.servers_dict[str(interaction.guild.id)].change_loop_mode()
            await interaction.response.send_message(embed=embed_loop)
        except:
            embed_no_object = discord.Embed(colour=discord.Colour.red(),title="I cannot turn loop mode on/off yet because I am not in a call")
            await interaction.response.send_message(embed=embed_no_object)

#-----------------------------------------------------------

    #For pausing the music
    @app_commands.command(description="Pause the music")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def pause(self,interaction : discord.Interaction):
        #Defer response to process
        await interaction.response.defer()

        with self.lock:
            if str(interaction.guild.id) in self.servers_dict:
                outcome = self.servers_dict[str(interaction.guild.id)].pause()
                if outcome == 0:
                    embedPausedMusic = discord.Embed(colour=discord.Colour.random(),title="I'm now paused.")
                    await interaction.followup.send(embed=embedPausedMusic)
                elif outcome == 1:
                    embedNotPlaying = discord.Embed(colour=discord.Colour.red(),title="The bot is not currently playing anything")
                    await interaction.followup.send(embedNotPlaying)
            
#-----------------------------------------------------------

    @app_commands.command(description="Play something or add it queue")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def play(self,interaction : discord.Interaction, search : str):
        #Get the bot into the channel
        embed = await self.join_voice(interaction)
        #If there is an embed returned meaning it joined the channel send the embed
        if not embed == None:
            await interaction.response.send_message(embed=embed)
        #If there was no embed returned
        else:
            #Check that the user is in voice channel
            if interaction.user.voice.channel == None:
                return
            else:
                await interaction.response.defer()

        with self.lock:
            #Create the k,v pair if its not in the dict
            if str(interaction.guild.id) not in self.servers_dict:
                self.servers_dict[str(interaction.guild.id)] = ServerMusic(interaction.guild)
            
            #Check what the search type is
            if "playlist" in search or "&list" in search:
                #Create a playlist unwrapper object to add all of the songs to the queue
                embed = YTPlaylistUnwrapper(search,self.servers_dict[str(interaction.guild.id)],interaction.user).embed_amount_added
                #Send an embed to the channel stating how many songs were added
                await interaction.followup.send(embed=embed)
                #If this is the first entry into the bot, begin playing the playlist
                if len(self.servers_dict[str(interaction.guild.id)].get_queue) == 2:
                    asyncio.create_task(self.servers_dict[str(interaction.guild.id)].play())
            #If it's not a playlist
            else:
                #Add a song object to the server's queue
                embed = self.servers_dict[str(interaction.guild.id)].add_to_queue(YTSongObject(search, interaction.user, str(interaction.guild.id)))
                print(f"Visual Queue length: {len(self.servers_dict[str(interaction.guild.id)].visual_queue)}")
                #If there are songs in the queue already then say the songs been added to the queue
                if len(self.servers_dict[str(interaction.guild.id)].visual_queue) > 1:
                    await interaction.followup.send(embed=embed)
                #If this is the first entry into the bot, begin playing the song
                if len(self.servers_dict[str(interaction.guild.id)].get_queue) == 1:
                    asyncio.create_task(self.servers_dict[str(interaction.guild.id)].play())

#-----------------------------------------------------------

    #For the queue
    @app_commands.command(description="Shows the current queue for the music.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def queue(self, interaction : discord.Interaction):
        await interaction.response.defer()
        with self.lock:
            embedQueue = discord.Embed(colour=discord.Colour.random(),title=f'Music Queue For {interaction.guild.name}')
            embedQueue.add_field(name="Currently Playing",value=f"{self.servers_dict[str(interaction.guild.id)].visual_queue[0][0]} `[{self.servers_dict[str(interaction.guild.id)].visual_queue[0][1]//60}:{self.servers_dict[str(interaction.guild.id)].visual_queue[0][1]%60:02d}]` - Added by: {self.servers_dict[str(interaction.guild.id)].visual_queue[0][2].mention}",inline=False)
            temp_music_queue = [song for song in self.servers_dict[str(interaction.guild.id)].visual_queue]
            temp_music_queue.pop(0)
        currentQueue = ""
        page = 1
        amountOfPages = 1 if ceil(len(temp_music_queue) / self.amount_per_page) == 0 else ceil(len(temp_music_queue) / self.amount_per_page)

        async def buttonLeftCallback(interaction : discord.Interaction):
            currentQueue = ""
            nonlocal page
            nonlocal amountOfPages
            nonlocal embedQueue
            if page == 1:
                page = amountOfPages
                startIndex = (amountOfPages - 1) * self.amount_per_page
                for i in range(startIndex,len(temp_music_queue)):
                    currentQueue += "**#" + str(i + 1) + "** " + temp_music_queue[i][0] + " `[" + f"{temp_music_queue[i][1]//60}:{temp_music_queue[i][1] % 60:02d}" + "]`" + " - Added by: " + temp_music_queue[i][2].mention + "\n"
            else:
                page -= 1
                endIndex = (page * self.amount_per_page)
                startIndex = endIndex - self.amount_per_page
                for i in range(startIndex,endIndex):
                    currentQueue += "**#" + str(i + 1) + "** " + temp_music_queue[i][0] + " `[" + f"{temp_music_queue[i][1]//60}:{temp_music_queue[i][1] % 60:02d}" + "]`" + " - Added by: " + temp_music_queue[i][2].mention + "\n"
                
            embedQueue.remove_field(1)
            embedQueue.add_field(name="Queue",value=currentQueue)
            embedQueue.set_footer(text=f"Page {page} of {amountOfPages}")
            await interaction.response.edit_message(embed=embedQueue)
        
        async def buttonRightCallback(interaction : discord.Interaction):
            currentQueue = ""
            nonlocal page
            nonlocal amountOfPages
            nonlocal embedQueue
            if page == amountOfPages:
                print("Going to page 1")
                page = 1
                startIndex = 0
                endIndex = startIndex + self.amount_per_page
                for i in range(startIndex,endIndex):
                    print(temp_music_queue[i][2])
                    currentQueue += "**#" + str(i + 1) + "** " + temp_music_queue[i][0] + " `[" + f"{temp_music_queue[i][1]//60}:{temp_music_queue[i][1] % 60:02d}" + "]`" + " - Added by: " + temp_music_queue[i][2].mention + "\n"
            elif page == amountOfPages - 1:
                print("Going to last page")
                page += 1
                startIndex = (page - 1) * self.amount_per_page
                for i in range(startIndex,len(temp_music_queue)):
                    currentQueue += "**#" + str(i + 1) + "** " + temp_music_queue[i][0] + " `[" + f"{temp_music_queue[i][1]//60}:{temp_music_queue[i][1] % 60:02d}" + "]`" + " - Added by: " + temp_music_queue[i][2].mention + "\n"
            else:
                print("Going to else")
                page += 1
                endIndex = page * self.amount_per_page
                startIndex = endIndex - self.amount_per_page
                for i in range(startIndex,endIndex):
                    currentQueue += "**#" + str(i + 1) + "** " + temp_music_queue[i][0] + " `[" + f"{temp_music_queue[i][1]//60}:{temp_music_queue[i][1] % 60:02d}" + "]`" + " - Added by: " + temp_music_queue[i][2].mention + "\n"
                
            embedQueue.remove_field(1)
            embedQueue.add_field(name="Queue",value=currentQueue,inline=False)
            embedQueue.set_footer(text=f"Page {page} of {amountOfPages}")
            await interaction.response.edit_message(embed=embedQueue)
        
        for i in range(len(temp_music_queue)):
            if i < self.amount_per_page:
                currentQueue += "**#" + str(i + 1) + "** " + temp_music_queue[i][0] + " `[" + f"{temp_music_queue[i][1]//60}:{temp_music_queue[i][1] % 60:02d}" + "]`" + " - Added by: " + temp_music_queue[i][2].mention + "\n"
            else:
                break
        currentQueue.rstrip("\n")
        if len(currentQueue) == 0:
            embedQueue.add_field(name="Queue",value="Empty")
        else:
            embedQueue.add_field(name="Queue",value=currentQueue)
        embedQueue.set_footer(text=f"Page {page} of {amountOfPages}")
        if amountOfPages > 1:
            print("More than one page")
            leftButton = discord.ui.Button(style=discord.ButtonStyle.grey, label="Previous Page")
            leftButton.callback = buttonLeftCallback
            rightButton = discord.ui.Button(style=discord.ButtonStyle.grey, label="Next Page")
            rightButton.callback = buttonRightCallback
            view = discord.ui.View()
            view.add_item(leftButton)
            view.add_item(rightButton)
            message = await interaction.followup.send(embed=embedQueue,view=view)
        else:
            message = await interaction.followup.send(embed=embedQueue)

#-----------------------------------------------------------

    @app_commands.command(description="Skip the current song")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def skip(self, interaction : discord.Interaction):
        await interaction.response.defer()
        with self.lock:
            #Call the skip method and get the details of the song skipped
            details = self.servers_dict[str(interaction.guild.id)].skip()
        #If no song was skipped, let the user know
        if details == None:
            embed_nothing_playing = discord.Embed(colour=discord.Colour.red(), title="There is nothing currently playing to skip.")
            await interaction.followup.send(embed=embed_nothing_playing)
        #Send an embed of the song that was skipped
        else:
            embed_skipped = discord.Embed(colour=details[1], url=details[0][2], title=f":track_next: Skipped Song: {details[0][0]} `[{details[0][1]//60}:{details[0][1] % 60:02d}]` :track_next:")
            await interaction.followup.send(embed=embed_skipped)

#-----------------------------------------------------------

    #For resuming the music
    @app_commands.command(description="Resumes the music. Keep the vibes going.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def resume(self,interaction : discord.Interaction):
        with self.lock:
            #Get the outcome of trying to resume the music
            outcome = self.servers_dict[str(interaction.guild.id)].resume()
        #If the outcome is 0, meaning success, print the resuming embed
        if outcome == 0:
            embedResuming = discord.Embed(colour=discord.Colour.red(),title="Resuming the action!")
            await interaction.response.send_message(embed=embedResuming)
        #If the outcome is not 0, meaning failure, print the failed embed
        else:
            embedNotPlaying = discord.Embed(colour=discord.Colour.red(),title="The bot is not currently playing anything")
            await interaction.response.send_message(embed=embedNotPlaying)

#-----------------------------------------------------------

    #For the stop command
    @app_commands.command(description="Stop the music and clear the queue")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def stop(self,interaction : discord.Interaction):
        with self.lock:
            #Call the stop command for the server object and get the embed
            embed_stop = self.servers_dict[str(interaction.guild.id)].stop()
        #Send the embed to the channel
        await interaction.response.send_message(embed=embed_stop)

#-----------------------------------------------------------

    #For the volume command
    @app_commands.command(description="Change the volume of the bot")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.describe(vol = "The volume you wish it to be set at between 0-200.")
    async def volume(self,interaction : discord.Interaction,vol : int):
        #Deferring response
        await interaction.response.defer()
        #Check if the bot is in a channel
        if str(interaction.guild.id) not in self.servers_dict:
            embed_no_bot = discord.Embed(colour=discord.Colour.red(),title="There is currently no instance of the bot active. Please make the bot join a channel first")
            await interaction.followup.send(embed=embed_no_bot)
            return
        #Changing volume and printing response
        await interaction.followup.send(embed=self.servers_dict[str(interaction.guild.id)].change_volume(vol))

async def setup(client):
    await client.add_cog(Voice(client))