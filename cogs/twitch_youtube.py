import discord
from discord.ext import commands, tasks
import os
import asyncio
import requests
import json
from googleapiclient.discovery import build
from discord import app_commands
import asqlite
from dotenv import load_dotenv

load_dotenv()

class TwitchYoutube(commands.Cog):
    
    def __init__(self, client : discord.Client):
        self.client = client
        # Set up the Twitch API access token
        self.twitch_client_id = os.getenv("TWITCH_CLIENT_ID")
        self.twitch_client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        self.twitch_access_url = os.getenv("TWITCH_ACCESS_URL")
        self.twitch_access_token = self.get_twitch_access_token()
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.last_announcement = {}
        self.saved_yt_ids = {}
        self.check_channels.start()
    
    def get_twitch_access_token(self):
        data = {
            'client_id': self.twitch_client_id,
            'client_secret': self.twitch_client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(self.twitch_access_url, data=data)
        json_data = json.loads(response.text)
        return json_data['access_token']

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog: "Twitch/Youtube Commands" loaded.')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        async with asqlite.connect("./databases/polls.db") as connection:
            async with connection.cursor() as c:
                command = f"CREATE TABLE a{guild.id} (server_id INT, channel_id INT, channel_link TEXT)"
                await c.execute(command)
                await connection.commit()

#-----------------------------------------------------------

    @app_commands.command(description="Add a Youtube channel to be notified about")
    @app_commands.describe(send_channel="The channel to send the notification to", channel_link="The link to the channel. Only Youtube or Twitch", notification_message="The message to send. Use '{author}' to send the name of the channel")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def addchannel(self, interaction : discord.Interaction, send_channel : discord.TextChannel, channel_link : str, notification_message : str):
        print("youtube" in channel_link)
        if "youtube" in channel_link or "youtu.be" in channel_link or "twitch.tv" in channel_link:
            try:
                async with asqlite.connect("./databases/twitchyoutube.db") as connection:
                    async with connection.cursor() as c:
                        await c.execute(f'INSERT INTO a{interaction.guild.id} VALUES ({send_channel.id}, "{channel_link}", "{notification_message}")')
                        await connection.commit()
                embed_added = discord.Embed(colour=discord.Colour.green(),title=f"Successfully added. I will now listen for anything from: {channel_link}")
                await interaction.response.send_message(embed=embed_added)
            except Exception as e:
                await interaction.response.send_message(content="Failed to add")
                print("LOG: Failed to add channel. See error below")
                print(e)
        else:
            embed_unacceptable_link = discord.Embed(colour=discord.Colour.red(),title="Unacceptable channel link. Please use a Youtube or Twitch link")
            await interaction.response.send_message(embed=embed_unacceptable_link)
            return

#-----------------------------------------------------------

    @app_commands.command(description="Delete a channel from the subscribed channels")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def deletechannel(self, interaction : discord.Interaction, channel_link : str):
        async with asqlite.connect("./databases/twitchyoutube.db") as connection:
            async with connection.cursor() as c:
                await c.execute(f'SELECT * FROM a{interaction.guild.id} WHERE channel_link = "{channel_link}"')
                result = await c.fetchone()

        if result == None:
            embed_no_channel = discord.Embed(colour=discord.Colour.red(),title=f"No channel with link {channel_link} found.")
            await interaction.response.send_message(embed=embed_no_channel)
        else:
            async with asqlite.connect("./databases/twitchyoutube.db") as connection:
                async with connection.cursor() as c:
                    await c.execute(f'DELETE FROM a{interaction.guild.id} WHERE channel_link = "{channel_link}"')
                    await connection.commit()
            embed_removed_channel = discord.Embed(colour=discord.Colour.green(),title=f"Successfully unsubscribed from {channel_link}")
            await interaction.response.send_message(embed=embed_removed_channel)

#-----------------------------------------------------------

    @app_commands.command(description="Show all channels currently being listened for")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def subscribedchannels(self, interaction : discord.Interaction):
        async with asqlite.connect("./databases/twitchyoutube.db") as connection:
            async with connection.cursor() as c:
                await c.execute(f'SELECT * FROM a{interaction.guild.id}')
                results = await c.fetchall()
        embed_subscribed_channels = discord.Embed(colour=discord.Colour.random(),title=f"Subscribed Channels For {interaction.guild.name}")
        for result in results:
            channel_object = await interaction.guild.fetch_channel(result[0])
            channel_name = result[1].split("/")[-1]
            embed_subscribed_channels.add_field(name=f"{channel_name}:",value=f"Send Channel:{channel_object.mention}\nChannel Link: {result[1]}\nNotification Message: {result[2]}")
        await interaction.response.send_message(embed=embed_subscribed_channels)

    
    @tasks.loop(minutes=10)
    async def check_channels(self):
        async with asqlite.connect("./databases/twitchyoutube.db") as connection:
            async with connection.cursor() as c:
                tables = []
                await c.execute("""SELECT name FROM sqlite_master WHERE type = 'table'""")
                temp = await c.fetchall()
                for table in temp:
                    tables.append(table)
                for x in tables:
                    query = f"SELECT * FROM {x[0]}"
                    await c.execute(query)
                    results = await c.fetchall()
                    if results == None:
                        continue
                    else:
                        print(f"LOG: Server ID: {x[0][1:]}")
                        print(f"LOG: Length of results: {len(results)}")
                        for entry in results:
                            print(f"{entry[0]}, {entry[1]}, {entry[2]}")
                            server_id = x[0][1:]
                            channel_id = entry[0]
                            channel_link = entry[1]
                            notification_message = entry[2]
                            # Check if the link is a YouTube channel
                            if "youtube" in channel_link:
                                print("Youtube Channel Detected")
                                print(self.saved_yt_ids)
                                try:
                                    # Extract the channel ID from the link
                                    yt_channel_id = channel_link.split("/")[-1]
                                    if channel_link in self.saved_yt_ids:
                                        yt_channel_name = self.saved_yt_ids[channel_link]["items"][0]["snippet"]["channelId"]
                                        yt_channel_thumbnail = self.saved_yt_ids[channel_link]["items"][0]["snippet"]["thumbnails"]["high"]["url"]
                                    if not channel_link in self.saved_yt_ids:
                                        raise Exception
                                    # Make a request to the YouTube API to get the channel's latest video
                                    response = requests.get(f"https://www.googleapis.com/youtube/v3/search?key={self.youtube_api_key}&channelId={yt_channel_id}&part=snippet,id&order=date&type=video&maxResults=1")
                                    #response = requests.get(f"https://www.googleapis.com/youtube/v3/search?key={self.youtube_api_key}&channelId={yt_channel_id}&part=snippet,id&order=date&maxResults=1", headers={'Cache-Control': 'no-cache'})
                                    if response.status_code != 200:
                                        raise Exception
                                except Exception:
                                    print("Exception")
                                    custom_url_name = channel_link.split("/")[-1].replace("@", "")
                                    response = requests.get(f"https://www.googleapis.com/youtube/v3/search?key={self.youtube_api_key}&part=snippet&type=channel&q={custom_url_name}")
                                    if response.status_code == 200:
                                        user_data = response.json()
                                        yt_channel_id = user_data["items"][0]["snippet"]["channelId"]
                                        print("LOG: " + yt_channel_id)
                                        if not channel_link in self.saved_yt_ids:
                                            self.saved_yt_ids[channel_link] = user_data
                                        yt_channel_name = user_data["items"][0]["snippet"]["channelTitle"]
                                        yt_channel_thumbnail = user_data["items"][0]["snippet"]["thumbnails"]["high"]["url"]
                                        response = requests.get(f"https://www.googleapis.com/youtube/v3/search?key={self.youtube_api_key}&channelId={yt_channel_id}&part=snippet,id&order=date&type=video&maxResults=1")
                                        #response = requests.get(f"https://www.googleapis.com/youtube/v3/search?key={self.youtube_api_key}&channelId={yt_channel_id}&part=snippet,id&order=date&maxResults=1", headers={'Cache-Control': 'no-cache'})
                                        #response = requests.get(f"https://www.googleapis.com/youtube/v3/search?key={self.youtube_api_key}&channelId={yt_channel_id}&part=snippet,id&order=date&maxResults=1")
                                print(response.status_code)
                                print(response.text)
                                if response.status_code == 200:
                                    # Parse the response JSON to get the video ID and title
                                    response_json = response.json()
                                    print(response_json)
                                    video_details = response_json["items"][0]["snippet"]
                                    video_id = response_json["items"][0]["id"]["videoId"]
                                    video_title = response_json["items"][0]["snippet"]["title"]
                                    
                                    # Check if the latest video is different from the last announcement
                                    if channel_link not in self.last_announcement or self.last_announcement[channel_link] != video_id:
                                        self.last_announcement[channel_link] = video_id
                                        
                                        # Send a message to the Discord channel announcing the new video
                                        guild_object = await self.client.fetch_guild(int(server_id))
                                        channel = await guild_object.fetch_channel(int(channel_id))
                                        embed_now_live = discord.Embed(colour=discord.Colour.from_rgb(255, 0, 0),url=f"https://youtube.com/watch?v={video_id}",title=video_title)
                                        embed_now_live.set_image(url=video_details['thumbnails']["high"]["url"])
                                        embed_now_live.set_thumbnail(url=yt_channel_thumbnail)
                                        embed_now_live.set_author(name=yt_channel_name,icon_url=yt_channel_thumbnail)
                                        await channel.send(content=notification_message.replace("{author}", channel_name),embed=embed_now_live)
                                        
                            # Check if the link is a Twitch channel
                            elif "twitch.tv/" in channel_link:
                                print("Twitch Channel Detected")
                                # Extract the channel name from the link
                                channel_name = channel_link.split("/")[-1]
                                
                                # Make a request to the Twitch API to get the channel's stream information
                                headers = {"Client-ID": f"{self.twitch_client_id}", "Authorization": f"Bearer {self.twitch_access_token}"}
                                response = requests.get(f"https://api.twitch.tv/helix/streams?user_login={channel_name}", headers=headers)
                                
                                if response.status_code == 200:
                                    # Parse the response JSON to get the stream information
                                    response_json = response.json()
                                    print(f"Response\n{response_json['data']}")
                                    if response_json["data"]:
                                        # The channel is currently live
                                        stream_title = response_json["data"][0]["title"]
                                        stream_info = response_json['data'][0]
                                        
                                        user_response = requests.get(f"https://api.twitch.tv/helix/users?login={stream_info['user_name']}", headers=headers)
                                        user_data = user_response.json()["data"][0]
                                        # Check if the stream is different from the last announcement
                                        if channel_link not in self.last_announcement or self.last_announcement[channel_link] != stream_title:
                                            self.last_announcement[channel_link] = stream_title
                                            
                                            # Send a message to the Discord channel announcing the live stream
                                            guild_object = await self.client.fetch_guild(int(server_id))
                                            print(type(guild_object))
                                            channel = await guild_object.fetch_channel(int(channel_id))
                                            embed_now_live = discord.Embed(colour=discord.Colour.from_rgb(145, 70, 255),url=channel_link,title=stream_info['title'], description=f"**Viewers**\n{stream_info['viewer_count']}")
                                            embed_now_live.set_image(url=stream_info['thumbnail_url'].replace("{width}", "1920").replace("{height}", "1080"))
                                            embed_now_live.set_thumbnail(url=user_data['profile_image_url'])
                                            embed_now_live.set_author(name=stream_info['user_name'],icon_url=user_data['profile_image_url'])
                                            await channel.send(content=notification_message.replace("{author}", stream_info['user_name']), embed=embed_now_live)
                                            
                                    else:
                                        # The channel is not currently live
                                        if channel_link in self.last_announcement:
                                            self.last_announcement.pop(channel_link)

async def setup(client):
    await client.add_cog(TwitchYoutube(client))