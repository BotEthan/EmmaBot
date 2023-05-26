# EmmaBot, the multipurpose Discord bot
Welcome. This is a bot that I've been building for around 3-4 years. She has changed many times in that time
frame and has undergone several reworks and refactorings.

EmmaBot is something that I made for my friends and close communities to enjoy. I started developing her when I was just starting out with Python. This does mean there is still a bit of spaghetti visible from when I really didn't know what I was doing. I'm just going to say that that adds character and leave it at that. *I'm not too lazy to fix it I swear*

The bot was designed to do many things that I thought I would need to add for my friend's to use in their servers. It's packed with features such as:


I have no issue with people wanting to use EmmaBot for research on how to scuff your own bot together but I do not want people taking this and claiming it to be their own code. Unfortunately that falls under something called plagiarism, which is pretty bad.

# Table of Contents

* [Installation](https://github.com/BotEthan/EmmaBot/#installation)

* [Usage](https://github.com/BotEthan/EmmaBot/#usage)

* [Features](https://github.com/BotEthan/EmmaBot/#features)

# Installation
In order to install EmmaBot you need to have a **valid bot application** created on the Discord Developr Application portal. You can see how to so [here](https://discordpy.readthedocs.io/en/stable/discord.html). The client token created there will be needed to run the bot.

In terms of a few other cogs in the bot some extra API keys will be needed. You can see which cog will need API keys based on the cog title in the [features](https://github.com/BotEthan/EmmaBot/#features) section. Should you not have the API for this cog then it is advised you remove the cog from the cogs folder

Once all API keys have been gathered you'll need to create a **.env** file to hold all of your keys in a safe place.

The order in which the keys are does not matter. It is crucial however that the bot's token is inside this **.env** file with a specific name.

Here is the layout of what all should be in the **.env** file if you have retrieved all the API keys needed. The <u>underlined</u> tokens are the ones necessary to run the bot. If you do not have all of the ones that are <u>underlined</u> then please remove the cog that would use them from the **./cogs** file:
<u>BOT_MAIN_TOKEN='your-bots-token'</u>  
BOT_TEST_TOKEN='if-you-have-another-bot-for-testings-token'  
TWITCH_CLIENT_ID='your-twitch-client-id'  
TWITCH_CLIENT_SECRET='your-twitch-client-secret'  
TWITCH_ACCESS_URL=https://id.twitch.tv/oauth2/token  
YOUTUBE_API_KEY='your-youtube-api-key'  
REDDIT_CLIENT_ID='your-reddit-client-id'  
REDDIT_CLIENT_SECRET='your-reddit-client-secret'  
REDDIT_USER_AGENT='your-reddit-user-agent'  

Once you have all the keys you need all that needs to happen is for you to install all the packages in the requirements.txt file into either your global python or virtual environment. Once all that is done try it out by running the `Run Bot.bat` file. This will run your bot with the `BOT_MAIN_TOKEN`. In the same way the `Run Bot Test.bat` will instead use the `BOT_TEST_TOKEN` if you have another bot application to use for testing with code while the other one remain on to keep using

# Usage
From here all that needs to happen is grabbing an invite link for your bot from the Discord Developer Application portal, adding it to a server you have admin permissions in and putting it in your server. **NB!!!** Make sure in the developer application portal when creating an invite link to tick the box that says **Administrator**. This will make sure the bot joins with administrator permissions. Open up that link in a new tab and you can invite your bot to a server.

Once the bot is online you have to give it some time to sync all of the slash commands to the server. This process can take between 5 minutes and an hour depending on how many servers the bot is in.

Once the slash commands have been synced, you can check this by typing `/` in the discord server and see if your bot's commands or icon appears in the selection box that pops up, then you know you can start using your commands!

# Features
## Main Bot (Bot API Key Required)
* Custom rotating statuses that change after a set amount of time
* Custom help command
* Slash commands for ease of use
## Admin Commands
* Clearing chats in channels
* Moving mass amounts of people to a different voice channel
## Economy Commands
* Begging for the bot's unique currency (Thonks)
* Checking the leaderboard for who has the most Thonks
* Giving Thonks to other people
* Attempting to steal Thonks from other people
## Emote Commands
* Sharing your current actions or emotes with the other people in chat
## Fun Commands
* Adding quotes, they could be smart phrases or funny things said that you want to remember
* Reading quotes, get a random quote everytime the command is used
* Delete quotes that you don't want to see anymore
* Play Blackjack
* Play Hangman
* Make EmmaBot tell a horrible dad joke
## Reddit Commands (Reddit API Keys Required)
* Get a funny meme off of Reddit from a select choice of subreddits
## Twitch/Youtube Commands (Google/Twitch API Keys Required)
* Add a Twitch or Youtube channel for the bot to lookout for update from
* Set the channel to send these updates to
## Utility Commands
* Add a birthday to EmmaBot for her to look out for
* List all the added birthdays
* Removed a birthday from EmmaBot
* Set which channel to send the birthday notifications to
* Create events which can hide or show different channels based on stages of up to 3 stages
* Set the role a user gets from EmmaBot when joining the server
* List all the emoji's and roles added to the server with some extra data on each
* Add a role and nickname to add to a user when sending a message with a specific keyword in it
* Create polls that update regularly with a fancy graph to show it's current data
* Add reaction roles which give the user a certain role when reacting on a message with a specific emoji
## Voice Commands
* Tell the bot to join the voice call you're currently in
* Add a song to the bot to play, if it's playing something it will instead add it to a queue
* Tell the bot to change the volume it's playing music at
* Tell the bot to pause, play, or skip the current song