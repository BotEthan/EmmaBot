from typing import Optional, Union
import discord
from discord.utils import get
import asyncio
import os
import yt_dlp
import json
from classes.imagecolourgetter import get_image_colour

class YTSongObject():

    def __init__(self, song_link, added_by, server_id):
        self.song_link = song_link
        self.added_by = added_by
        self.server_id = server_id
        self.ydl_opts = {'format': 'bestaudio/best', 'outtmpl': './music_queues/{0}/%(title)s.mp3'.format(self.server_id), 'default_search': 'auto'}
        self.__get_song_details__()
        self.thumbnail = self.info['thumbnail']

    def __get_song_details__(self):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            # Use the query as the search term or URL
            self.info = ydl.extract_info(self.song_link, download=False)
            if 'entries' in self.info:
                if self.info['id'] == self.info['title']:
                    self.song_link = self.info['entries'][0]['original_url']
                self.info = self.info['entries'][0]

    def download(self):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            # Use the query as the search term or URL
            self.info = ydl.extract_info(self.song_link, download=True)
            if 'entries' in self.info:
                self.info = self.info['entries'][0]
            self.path = self.info['requested_downloads'][0]['_filename']

    @property
    def song_name(self):
        """Returns the songs title"""
        return self.info["title"]
    
    @property
    def description(self):
        """Returns the songs description"""
        return self.info["description"]
    
    @property
    def duration(self):
        """Returns the songs duration"""
        return self.info["duration"]
    
    def __str__(self):
        return f"{self.song_name}"

class YTPlaylistObject():

    def __init__(self, videos, added_by):
        self.videos = videos
        self.added_by = added_by

    def __str__(self):
        return [video for video in self.videos]

class ServerMusic():

    def __init__(self, guild : discord.Guild):
        self.guild = guild
        self.music_queue = []
        self._is_paused = False
        self.is_playing = False
        self.volume = 0.5
        self.set_channel = None
        self.visual_queue = []
        self.voice = None
        self.loop = False


    @property
    def is_paused(self):
        return self.is_paused
    
    @property
    def get_queue(self):
        return self.music_queue
    
#------------ Methods --------------

    def add_to_queue(self, song : Union[YTSongObject,YTPlaylistObject]):
        self.music_queue.append(song)
        embed_added_to_queue = discord.Embed(colour=discord.Colour.green())
        if type(song) == YTSongObject:
            self.visual_queue.append([song.song_name, song.duration, song.added_by])
            embed_added_to_queue.title = f"Successfully added {song.song_name} to the queue."
        else:
            for video in song.videos:
                self.visual_queue.append([video['title'], video['duration'], song.added_by])
            embed_added_to_queue.title = f"Successfully added `{len(song.videos)}` songs to the queue"
        return embed_added_to_queue

    def change_loop_mode(self):
        self.loop = not self.loop
        embedLoopMode = discord.Embed(colour=discord.Colour.blurple(), title=":repeat: Loop mode now ")
        embedLoopMode.title += "Off :repeat:" if self.loop == False else "On :repeat:"
        return embedLoopMode

    def change_volume(self, new_vol : int):
        def check_vol_change(new_vol) -> str:
            print(f"source vol: {str(self.volume)}\nnew volume: {str(new_vol)}")
            if self.volume > new_vol:
                return "Decreasing"
            else:
                return "Increasing"
        
        new_vol = new_vol/100

        if new_vol > 2:
            embed_unsafe = discord.Embed(
                colour= discord.Colour.red(),
                title= "This is an unsafe volume. Please stay under 200%"
            )
            return embed_unsafe
        
        change = check_vol_change(new_vol)
        self.voice.source = discord.PCMVolumeTransformer(self.voice.source, new_vol)
        self.volume = new_vol

        embed_volume = discord.Embed(
            colour = discord.Colour.blue(),
            title= f"{change} bot's volume to {(new_vol*100):.0f}%" 
        )
        embed_volume.title = ":sound: " + embed_volume.title + " :sound:" if change == "Decreasing" else ":loud_sound: " + embed_volume.title + " :loud_sound:"
        return embed_volume

    async def end_of_queue(self):
        self.visual_queue = []
        self.music_queue = []
        embedEndOfQueue = discord.Embed(colour=discord.Colour.blurple(), title="All songs played. I've reached the end of the queue.")
        await self.set_channel.send(embed=embedEndOfQueue)

    async def join(self, interaction : discord.Interaction):
        try:
            if self.voice.channel == interaction.user.voice.channel:
                print("LOG: Already connected to channel with user")
                return 2
            elif self.voice.is_connected() == True and len(self.voice.channel.members) == 1:
                print(self.voice.channel + "\t" + interaction.user.voice.channel)
                self.voice = await interaction.user.voice.channel.connect(timeout=240, reconnect=True)   
                print("Set self.voice in elif 1")  
                return 2
        except discord.errors.ClientException as e:
            print("LOG: Already connected to channel with user. Client Exception")
            return 2
        except AttributeError as e:
            print("LOG: Voice client has not yet been made. See error below")
            print(e)
            print(f"LOG: Interaction User VC: {interaction.user.voice.channel}")
            channel = interaction.user.voice.channel
            self.voice = await channel.connect(timeout=240, reconnect=True)
            print("Set self.voice in attribute error")  
            self.set_channel = interaction.channel
            print(self.set_channel)
            return 0
        except Exception as e:
            print("LOG: Error occured leaving the voice channel. See error below:")
            print(e)
            return 1

    async def leave(self):
        try:
            await self.voice.disconnect()
            return 0
        except Exception as e:
            print("LOG: Error occured leaving the voice channel. See error below:")
            print(e)
            return 1
        
    def pause(self):
        print("LOG: Trying to pause")
        try:
            self.voice.pause()
            return 0
        except Exception as e:
            print("LOG: Error when attempting to pause the voice client. See error below:")
            print(e)
            return 1
        
    async def play(self):
        self.get_queue[0].download()
        source = discord.PCMVolumeTransformer(original=discord.FFmpegPCMAudio(source=self.get_queue[0].path),volume=self.volume)
        self.is_playing = True
        self.voice.play(source,after=self.next)
        #self.voice.source = discord.PCMVolumeTransformer(self.voice.source, self.volume)
        embedNowPlaying = discord.Embed(colour=get_image_colour(self.get_queue[0].thumbnail),url= self.get_queue[0].song_link,title=f":musical_note: Now Playing {self.get_queue[0].song_name} `[{self.music_queue[0].duration//60}:{self.music_queue[0].duration%60:02d}]` :musical_note:")
        embedNowPlaying.set_thumbnail(url=self.get_queue[0].thumbnail)
        await self.set_channel.send(embed=embedNowPlaying)

    def resume(self):
        try:
            self.voice.resume()
            return 0
        except Exception as e:
            print("LOG: Error when attempting to resume. See error below:")
            print(e)
            return 1

    def next(self,error):
        self.is_playing = False
        print("LOG: Loading Next Song")
        print(f"LOG: Loop mode: {self.loop}")
        print(f"Length of queue: {len(self.music_queue)}")
        print(f"Visual Queue: {self.visual_queue}")
        if self.loop:
            self.music_queue.append(self.music_queue[0])
            self.visual_queue.append([self.music_queue[0].song_name, self.music_queue[0].duration, self.music_queue[0].added_by])
            print(f"Visual Queue After Loop: {self.visual_queue}")
        if len(self.get_queue) > 1:
            self.visual_queue.pop(0)
            print(str(self.music_queue[0]))
            if type(self.music_queue[1]) == YTPlaylistObject:
                print("Playlist object found")
                song = YTSongObject(self.music_queue[1].videos[0]['url'],self.music_queue[1].added_by,self.guild.id)
                self.music_queue.pop(0)
                self.music_queue.insert(0, song)
                print(str(self.music_queue[0]))
                self.music_queue[1].videos.pop(0)
                asyncio.run_coroutine_threadsafe(self.play(), self.voice.loop)
            else:
                self.music_queue.pop(0)
                asyncio.run_coroutine_threadsafe(self.play(), self.voice.loop)    
        else:
            print("LOG: End of queue")
            asyncio.run_coroutine_threadsafe(self.end_of_queue(), self.voice.loop)

    def skip(self):
        if len(self.get_queue) >= 1:
            currentSong = [self.get_queue[0].song_name, self.get_queue[0].duration, self.get_queue[0].song_link]
            colour = get_image_colour(self.get_queue[0].thumbnail)
            self.voice.stop()
            return (currentSong, colour)
        else:
            return None
    
    def skip_specific(self, song_index : int):
        pass

    def stop(self):
        if self.voice.is_playing():
            self.music_queue = []
            self.visual_queue = []
            self.voice.stop()
            embed_stopped = discord.Embed(colour=discord.Colour.blurple(),title=":stop_button: Music has been stopped and queue has been cleared :stop_button:")
            return embed_stopped
        else:
            embed_nothing_playing = discord.Embed(colour=discord.Colour.red(),title="Nothing currently playing to stop")
            return embed_nothing_playing

class YTPlaylistUnwrapper():

    def __init__(self, playlist_link, server_music_object : ServerMusic, added_by : discord.User):
        self.playlist_link = playlist_link
        self.server_music_object = server_music_object  
        self.added_by = added_by
        self.__get_songs__()

    def __get_songs__(self):
        ydl_opts = {
        'extract_flat': 'in_playlist',
        'format': 'bestaudio/best',
        'noplaylist': False,
        'geturl': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(self.playlist_link, download=False)
    
        videos = playlist_info['entries']
        self.server_music_object.add_to_queue(YTSongObject(videos[0]['url'],self.added_by,self.server_music_object.guild.id))
        self.embed_amount_added = self.server_music_object.add_to_queue(YTPlaylistObject(videos[1:], self.added_by))