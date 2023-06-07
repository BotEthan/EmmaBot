from math import ceil
from sqlite3 import connect
from typing import Union, Optional
import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import asyncio
from asyncio import sleep
import asqlite
from classes.blackjack import Blackjack
from classes.hangman import Hangman
from classes.quotes_track import ServerQuotes

class Fun(commands.Cog):

    def __init__(self,client):
        self.client = client
        self.server_quotes = {}
        self.amount_per_page = 10
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog: "Fun Commands" loaded.')


    async def check_server_quote_exists(self, server_id):
        if not server_id in self.server_quotes:
            print("LOG: Creating server quotes object")
            await self.create_server_quote_object(server_id)
        else:
            print("LOG: Server quotes object already exists")

    async def create_server_quote_object(self,server_id):
        async with asqlite.connect("./databases/server_quotes.db") as connection:
            async with connection.cursor() as c:
                await c.execute("SELECT * FROM quotes WHERE server_id = ?",(server_id,))
                results = await c.fetchall()
            print(len(results))
            if len(results) == 0:
                raise Exception
            quotes_sets = []
            for quote_data in results:
                print(quote_data)
                quotes_sets.append((quote_data[1],quote_data[2],quote_data[3]))
            self.server_quotes[server_id] = ServerQuotes(server_id, quotes_sets)

#-----------------------------------------------------------

    #For add quote command
    @app_commands.command(description="Add a new quote to the server.")
    @app_commands.describe(newquote=R"The quote that you wish to add. Use '\n' to add a new line")
    async def addquote(self,interaction : discord.Interaction, newquote : str, clip_link : Optional[str]):
        """
        Add a new quote to the server.

        **Usage:**
            `-quote [Quote]`
        
        **Arguments:**
            `quote`: The quote that you wish to add.
        """
        serverID = interaction.guild.id
        authorID = interaction.user.id
        await self.check_server_quote_exists(serverID)
        await self.server_quotes[serverID].add_quote(authorID, newquote, clip_link)
        embedAddQuote = discord.Embed(colour=discord.Colour.random())
        embedAddQuote.title = f"Added quote '{newquote}' to the list of available quotes"
        await interaction.response.send_message(embed=embedAddQuote)

#-----------------------------------------------------------
    @app_commands.command(description="Play some blackjack.")
    async def blackjack(self, interaction : discord.Interaction, bet : Optional[int]):        
        embed_met_bet = await self.check_bet(interaction, bet)
        if not embed_met_bet[0]:
            await interaction.response.send_message(embed=embed_met_bet[1])
            return
        await interaction.response.defer()

        game = Blackjack(interaction, bet)
        await game.start()
        await game.print_current()

#-----------------------------------------------------------

    @app_commands.command(description="Delete a quote")
    async def deletequote(self, interaction : discord.Interaction):
        await interaction.response.defer()
        serverID = interaction.guild_id
        await self.create_server_quote_object(interaction.guild_id)
        quotes = self.server_quotes[serverID].get_all_quotes()
        embedCurrentQuotes = discord.Embed(colour=discord.Colour.random(),title=f"Quotes added to {interaction.guild.name}",description="Respond with the number of the quote to delete or type cancel to, well, cancel. Make sure you are either an admin or the user that submitted the quote.")
        currentQuotes = ""
        page = 1
        amountOfPages = ceil(len(quotes) / self.amount_per_page)
        
        async def buttonLeftCallback(interaction : discord.Interaction):
            currentQuotes = ""
            nonlocal page
            nonlocal amountOfPages
            nonlocal embedCurrentQuotes
            if page == 1:
                page = amountOfPages
                startIndex = (amountOfPages - 1) * self.amount_per_page
                for i in range(startIndex,len(quotes)):
                    currentQuotes += "**#" + str(i + 1) + "** - " + quotes[i][0] + "\n"
            else:
                page -= 1
                endIndex = (page * self.amount_per_page)
                startIndex = endIndex - self.amount_per_page
                for i in range(startIndex,endIndex):
                    currentQuotes += "**#" + str(i + 1) + "** - " + quotes[i][0] + "\n"
                
            embedCurrentQuotes.remove_field(0)
            embedCurrentQuotes.add_field(name="Quote",value=currentQuotes)
            embedCurrentQuotes.set_footer(text=f"Page {page} of {amountOfPages}")
            await interaction.response.edit_message(embed=embedCurrentQuotes)
        
        async def buttonRightCallback(interaction : discord.Interaction):
            currentQuotes = ""
            nonlocal page
            nonlocal amountOfPages
            nonlocal embedCurrentQuotes
            if page == amountOfPages:
                print("Going to page 1")
                page = 1
                startIndex = 0
                endIndex = startIndex + self.amount_per_page
                for i in range(startIndex,endIndex):
                    print(quotes[i][2])
                    currentQuotes += "**#" + str(i + 1) + "** - " + quotes[i][0] + "\n"
            elif page == amountOfPages - 1:
                print("Going to last page")
                page += 1
                startIndex = (page - 1) * self.amount_per_page
                for i in range(startIndex,len(quotes)):
                    currentQuotes += "**#" + str(i + 1) + "** - " + quotes[i][0] + "\n"
            else:
                print("Going to else")
                page += 1
                endIndex = page * self.amount_per_page
                startIndex = endIndex - self.amount_per_page
                for i in range(startIndex,endIndex):
                    currentQuotes += "**#" + str(i + 1) + "** - " + quotes[i][0] + "\n"
                
            embedCurrentQuotes.remove_field(0)
            embedCurrentQuotes.add_field(name="Quote",value=currentQuotes)
            embedCurrentQuotes.set_footer(text=f"Page {page} of {amountOfPages}")
            await interaction.response.edit_message(embed=embedCurrentQuotes)

        for i in range(len(quotes)):
            if i < self.amount_per_page:
                currentQuotes += "**#" + str(i + 1) + "** - " + quotes[i][0] + "\n"
            else:
                break
        currentQuotes.rstrip("\n")
        embedCurrentQuotes.add_field(name="Quotes",value=currentQuotes)
        embedCurrentQuotes.set_footer(text=f"Page {page} of {amountOfPages}")
        if amountOfPages > 1:
            print("More than one page")
            leftButton = discord.ui.Button(style=discord.ButtonStyle.grey, label="Previous Page")
            leftButton.callback = buttonLeftCallback
            rightButton = discord.ui.Button(style=discord.ButtonStyle.grey, label="Next Page")
            rightButton.callback = buttonRightCallback
            view = discord.ui.View()
            view.add_item(leftButton)
            view.add_item(rightButton)
            message = await interaction.followup.send(embed=embedCurrentQuotes,view=view)
        else:
            message = await interaction.followup.send(embed=embedCurrentQuotes)

        def check(m):
            return m.author == interaction.user

        reply = await self.client.wait_for('message', check=check)
        response = reply.content
        response = str(response)
        if response.lower() == "quit" or response.lower() == "stop" or response.lower() == "cancel":
            await interaction.followup.send("Cancelled listening for changing a quote")
            return
        if not response.isdigit():
            while not response.isdigit():
                await interaction.followup.send("Incorrect input, please reply with a number corresponding to the quotes list")
                reply = await self.client.wait_for('message', check=check)
                response = reply.content
                response = str(response)
        quoteChangeNumber = int(response)
        print()
        await self.server_quotes[serverID].delete_quote(quotes[quoteChangeNumber - 1][2])
        embedChangedQuote = discord.Embed(colour=discord.Colour.green(),title=f"Succesfully deleted the quote to {quotes[quoteChangeNumber - 1][2]}")
        await interaction.followup.send(embed=embedChangedQuote)

#-----------------------------------------------------------

    #For edit quote command
    @app_commands.command(description="Edit a quote that was added to the server.")
    async def editquote(self, interaction : discord.Interaction):
        await interaction.response.defer()
        serverID = interaction.guild_id
        await self.check_server_quote_exists(interaction.guild_id)
        quotes = self.server_quotes[serverID].get_all_quotes()
        embedCurrentQuotes = discord.Embed(colour=discord.Colour.random(),title=f"Quotes added to {interaction.guild.name}",description="Respond with the number of the quote to edit or type cancel to, well, cancel. Make sure you are either an admin or the user that submitted the quote.")
        currentQuotes = ""
        page = 1
        amountOfPages = ceil(len(quotes) / self.amount_per_page)
        
        async def buttonLeftCallback(interaction : discord.Interaction):
            currentQuotes = ""
            nonlocal page
            nonlocal amountOfPages
            nonlocal embedCurrentQuotes
            if page == 1:
                page = amountOfPages
                startIndex = (amountOfPages - 1) * self.amount_per_page
                for i in range(startIndex,len(quotes)):
                    currentQuotes += "**#" + str(i + 1) + "** - " + quotes[i][0] + "\n"
            else:
                page -= 1
                endIndex = (page * self.amount_per_page)
                startIndex = endIndex - self.amount_per_page
                for i in range(startIndex,endIndex):
                    currentQuotes += "**#" + str(i + 1) + "** - " + quotes[i][0] + "\n"
                
            embedCurrentQuotes.remove_field(0)
            embedCurrentQuotes.add_field(name="Quote",value=currentQuotes)
            embedCurrentQuotes.set_footer(text=f"Page {page} of {amountOfPages}")
            await interaction.response.edit_message(embed=embedCurrentQuotes)
        
        async def buttonRightCallback(interaction : discord.Interaction):
            currentQuotes = ""
            nonlocal page
            nonlocal amountOfPages
            nonlocal embedCurrentQuotes
            if page == amountOfPages:
                print("Going to page 1")
                page = 1
                startIndex = 0
                endIndex = startIndex + self.amount_per_page
                for i in range(startIndex,endIndex):
                    print(quotes[i][2])
                    currentQuotes += "**#" + str(i + 1) + "** - " + quotes[i][0] + "\n"
            elif page == amountOfPages - 1:
                print("Going to last page")
                page += 1
                startIndex = (page - 1) * self.amount_per_page
                for i in range(startIndex,len(quotes)):
                    currentQuotes += "**#" + str(i + 1) + "** - " + quotes[i][0] + "\n"
            else:
                print("Going to else")
                page += 1
                endIndex = page * self.amount_per_page
                startIndex = endIndex - self.amount_per_page
                for i in range(startIndex,endIndex):
                    currentQuotes += "**#" + str(i + 1) + "** - " + quotes[i][0] + "\n"
                
            embedCurrentQuotes.remove_field(0)
            embedCurrentQuotes.add_field(name="Quote",value=currentQuotes)
            embedCurrentQuotes.set_footer(text=f"Page {page} of {amountOfPages}")
            await interaction.response.edit_message(embed=embedCurrentQuotes)

        for i in range(len(quotes)):
            if i < self.amount_per_page:
                currentQuotes += "**#" + str(i + 1) + "** - " + quotes[i][0] + "\n"
            else:
                break
        currentQuotes.rstrip("\n")
        embedCurrentQuotes.add_field(name="Quotes",value=currentQuotes)
        embedCurrentQuotes.set_footer(text=f"Page {page} of {amountOfPages}")
        if amountOfPages > 1:
            print("More than one page")
            leftButton = discord.ui.Button(style=discord.ButtonStyle.grey, label="Previous Page")
            leftButton.callback = buttonLeftCallback
            rightButton = discord.ui.Button(style=discord.ButtonStyle.grey, label="Next Page")
            rightButton.callback = buttonRightCallback
            view = discord.ui.View()
            view.add_item(leftButton)
            view.add_item(rightButton)
            message = await interaction.followup.send(embed=embedCurrentQuotes,view=view)
        else:
            message = await interaction.followup.send(embed=embedCurrentQuotes)

        def check(m):
            return m.author == interaction.user

        reply = await self.client.wait_for('message', check=check)
        response = reply.content
        response = str(response)
        if response.lower() == "quit" or response.lower() == "stop" or response.lower() == "cancel":
            await interaction.followup.send("Cancelled listening for changing a quote")
            return
        if not response.isdigit():
            while not response.isdigit():
                await interaction.followup.send("Incorrect input, please reply with a number corresponding to the quotes list")
                reply = await self.client.wait_for('message', check=check)
                response = reply.content
                response = str(response)
        quoteChangeNumber = int(response)
        await interaction.followup.send("What would you like to change the quote to")
        reply = await self.client.wait_for('message', check=check)
        response = reply.content
        await interaction.followup.send(content="Do you have a clip link to add? Type 'skip' to not add anything")
        link_reply = await self.client.wait_for('message', check=check)
        link_response = link_reply.content
        userID = interaction.user.id
        await self.server_quotes[serverID].edit_quote(userID, quotes[quoteChangeNumber - 1][2], response, link_response)
        embedChangedQuote = discord.Embed(colour=discord.Colour.green(),title=f"Succesfully changed the quote to {response}")
        await interaction.followup.send(embed=embedChangedQuote)

#-----------------------------------------------------------

    #For hangman command
    @app_commands.command(description="Wanna play some hangman? You can bet on it and play with a second player!")
    @app_commands.describe(player2="A member that you wish to play with",bet="The amount of thonks you want to bet")
    async def hangman(self,interaction : discord.Interaction, player2 : Optional[discord.Member], bet : Optional[int]):
        """
        Wanna play some hangman? You can bet on it and play with a second player!

        **Usage:**
            `-hangman Optional[Player2] Optional[Bet]`
        
        **Arguments:**
            `player 2`: A member that you wish to play with.
            `bet`: The amount of thonks you want to bet. Get double when you win. *Max 2000<:Thonks:768191131820883978> Thonks*
        """
        metBetRequirements = await self.check_bet(interaction,bet)
        if not metBetRequirements[0]:
            await interaction.response.send_message(embed=metBetRequirements[1])
            return

        await interaction.response.defer()

        hangman_game = Hangman(interaction, bet, player2)
        await hangman_game.start()

#-----------------------------------------------------------

    @app_commands.command(description="Let the bot tell you a joke.")
    async def joke(self, interaction : discord.Interaction):
        """
        Let the bot tell you a joke.

        **Usage:**
            `-joke`
        """
        await interaction.response.defer()
        with open("./jokes.txt","r") as f:
            jokes = f.readlines()
            chosenJoke = random.choice(jokes)
            joke = chosenJoke.split("%")
            colour = "%06x" % random.randint(0, 0xFFFFFF)
            embedJoke = discord.Embed(colour=int(colour,16))
            embedJoke.title = joke[0]
            message = await interaction.followup.send(embed=embedJoke)
            await sleep(3)
            embedJoke.description = joke[1]
            await message.edit(embed=embedJoke)

#-----------------------------------------------------------

    #For quote command
    @app_commands.command(description="Show a random quote that has been said in this server.")
    async def quote(self, interaction : discord.Interaction):
        """
        Show a random quote that has been said in this server.

        **Usage:**
            `-quote`
        """
        serverID = interaction.guild.id
        try:
            await self.check_server_quote_exists(serverID)
        except:
            await interaction.response.send_message("No quotes found.\nYou can add quotes with the command `/addquote` followed by the quote.")
            return
        quote = self.server_quotes[serverID].get_quote()
        user = await self.client.fetch_user(quote[0])
        embedQuote = discord.Embed(colour=discord.Colour.random())
        quote_text = quote[1].replace(R"\n", "\n")
        embedQuote.title = quote_text
        if not quote[2] == None:
            embedQuote.add_field(name="Clip", value=quote[2])
        embedQuote.set_footer(icon_url=user.avatar.url,text=f"Submitted by: {user.display_name}")
        await interaction.response.send_message(embed=embedQuote)

#-----------------------------------------------------------
# Side Functions
    async def check_bet(self, interaction, bet):
        if bet != None:
            async with asqlite.connect("./databases/user_info.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""SELECT * FROM user_info WHERE user_id = ?""",(interaction.user.id,))
                    result = await c.fetchone()
            if result[2] < int(bet):
                embed_not_enough = discord.Embed(
                    colour= discord.Colour.blue(),
                    title= "You do not have enough <:Thonks:768191131820883978> Thonks to make this bet"
                )
                return False, embed_not_enough
            elif int(bet) < 0:
                embed_negative_bet = discord.Embed(
                    colour= discord.Colour.blue(),
                    title= "Cannot bet negative numbers"
                )
                return False, embed_negative_bet
            elif int(bet) > 2000:
                embed_bet_too_high = discord.Embed(colour=discord.Colour.blurple(),title=f"Bet too high. You can only bet a max of 2000 <:Thonks:768191131820883978> Thonks")
                return False,embed_bet_too_high
        return True, None

#-----------------------------------------------------------
# Setup

async def setup(client):
    await client.add_cog(Fun(client))