import discord
from discord import app_commands
from discord.ext import commands,tasks
import redditeasy as rEZ
import asyncio
from asyncio import sleep
import random
from typing import Union
import os
from dotenv import load_dotenv

load_dotenv()

class Reddit(commands.Cog):

    def __init__(self, client):
        self.client = client
        
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog: "Reddit Commands" loaded.')

    @app_commands.command(description="mmmmmmm yes meme.....")
    async def meme(self, interaction : discord.Interaction, subreddit : Union[None,str]):
        """
        Hey kid, you wanna buy some memes?

        **Usage:**
            `-meme Optional[Subreddit]`
        
        **Arguments:**
            `subreddit`: The subreddit you want to get a meme from. If none is given it will pick one at random.
            Subreddit choices:
             > `comedycemetery`
             > `memes`
             > `dankmemes`
             > `terriblefacebookmemes`
             > `funny`
             > `dndmemes`
        """
        def CheckSubreddit(subreddit):
            allowed_subreddits = ["comedycemetery","memes","dankmemes","terriblefacebookmemes","funny","dndmemes"]
            if subreddit.lower() in allowed_subreddits:
                return True
            return False

        await interaction.response.defer()

        reddit = await GetRedditInstance()

        if subreddit == None:
            allowed_subreddits = ["comedycemetery","memes","dankmemes","terriblefacebookmemes","funny"]
            subreddit = random.choice(allowed_subreddits)
        elif not CheckSubreddit(subreddit):
            embedIncorrectSubreddit = discord.Embed(colour=discord.Colour.red(), title=f"{subreddit} is"\
                " not one of the allowed meme subreddits. Please use `-help meme`"\
                    " for the list of available subreddits")
            await interaction.followup.send(embed=embedIncorrectSubreddit)
            return
        elif "r/" in subreddit:
            subreddit = subreddit[2:]        
        
        post = await reddit.get_post(subreddit)
        
        if post.content_type != rEZ.ContentType.IMAGE or post.stickied:
            while post.content_type != rEZ.ContentType.IMAGE or post.stickied:
                post = await reddit.get_post(subreddit)

        print(post.content_type)
        print(post.content)
        print(post.score)
        print(post.is_media)
        print(post.subreddit_name)
        
        embed_meme = discord.Embed(colour=discord.Colour.random())
        embed_meme.set_image(url=post.content)
        embed_meme.set_author(url=post.post_url,name=post.title)
        embed_meme.title = f"<:upvote:798056851559415829>{post.score}<:downvote:798056851576979466>"
        embed_meme.set_footer(text=f'Posted by u/{post.author} in r/{subreddit}')
        await interaction.followup.send(embed=embed_meme)

#----------------------------------
#Side Functions

async def GetRedditInstance():
    reddit = rEZ.AsyncSubreddit(
                client_id = os.getenv("REDDIT_CLIENT_ID"),
                client_secret = os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent = os.getenv("REDDIT_USER_AGENT")
            )
    return reddit

#----------------------------------
#Setup
async def setup(client):
    await client.add_cog(Reddit(client))