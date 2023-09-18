import asyncio
from math import ceil
import os
from PIL import Image,ImageDraw
import asqlite
from zoneinfo import ZoneInfo
import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import date, datetime, time, timedelta
from typing import Optional, Union
import pygal
from pygal.style import *
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import ast

class Utility(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.my_loop.start()
        self.UpdatePolls.start()
        self.amount_per_page = 5

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog: "Utility Commands" loaded.')
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        serverID = guild.id
        async with asqlite.connect("./databases/user_birthdays.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""INSERT INTO settings VALUES (?, 0, 0)""", (serverID,))
                await connection.commit()
        print(f"Created birthday settings entry for {guild.name}({serverID}).")
        async with asqlite.connect("./databases/polls.db") as connection:
            async with connection.cursor() as c:
                command = f"CREATE TABLE a{serverID} (server_id INT, channel_id INT, message_id INT, poll_id INT, poll_title TEXT, charttype TEXT, choices BLOB, votes BLOB, style TEXT"
                await c.execute(command)
                await connection.commit()
                
    
    @commands.Cog.listener()
    async def on_member_join(self,member : discord.Member):
        serverID = member.guild.id
        serverObject = member.guild
        async with asqlite.connect("./databases/reaction_info.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM join_roles WHERE server_id = ?""", (serverID,))
                results = await c.fetchall()
        if results:
            for result in results:
                role = serverObject.get_role(result[1])
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        print("saw a reaction in add")
        async with asqlite.connect("./databases/reaction_info.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM reactions WHERE server_id = ?""",(payload.guild_id,))
                result = await c.fetchall()
        for reactionRole in result:
            reaction_emoji = reactionRole[3]
            print(str(payload.message_id))
            if ":" in reactionRole[3]:
                reaction_emoji = str(reactionRole[3].split(":")[2])
                reaction_emoji = reaction_emoji[:-1]
            if reactionRole[2] == payload.message_id:
                print("Found the message")
                try:
                    print(f"{reaction_emoji}\n{reactionRole[3] == payload.emoji.name}")
                    if reaction_emoji == payload.emoji.name:
                        print("Found the emoji in emoji.name")
                        if reactionRole[5] == 0 or reactionRole[5] == 2:
                            guildObject = self.client.get_guild(payload.guild_id)
                            roleToAdd = guildObject.get_role(reactionRole[4])
                            await payload.member.add_roles(roleToAdd)
                            embedAddedRole = discord.Embed(colour=discord.Colour.teal())
                            embedAddedRole.title = f"Successfully gave you the {roleToAdd.name} role."
                            await payload.member.send(embed=embedAddedRole)
                        elif reactionRole[5] == 1:
                            guildObject = self.client.get_guild(payload.guild_id)
                            roleToRemove = guildObject.get_role(reactionRole[4])
                            await payload.member.remove_roles(roleToRemove)
                            embedRemovedRole = discord.Embed(colour=discord.Colour.teal())
                            embedRemovedRole.title = f"Successfully removed the {roleToRemove.name} role."
                            await payload.member.send(embed=embedRemovedRole)
                    elif int(reaction_emoji) == payload.emoji.id:
                        print("Found the emoji")
                        if reactionRole[5] == 0 or reactionRole[5] == 2:
                            guildObject = self.client.get_guild(payload.guild_id)
                            roleToAdd = guildObject.get_role(reactionRole[4])
                            await payload.member.add_roles(roleToAdd)
                            embedAddedRole = discord.Embed(colour=discord.Colour.teal())
                            embedAddedRole.title = f"Successfully gave you the {roleToAdd.name} role."
                            await payload.member.send(embed=embedAddedRole)
                        elif reactionRole[5] == 1:
                            guildObject = self.client.get_guild(payload.guild_id)
                            roleToRemove = guildObject.get_role(reactionRole[4])
                            await payload.member.remove_roles(roleToRemove)
                            embedRemovedRole = discord.Embed(colour=discord.Colour.teal())
                            embedRemovedRole.title = f"Successfully removed the {roleToRemove.name} role."
                            await payload.member.send(embed=embedRemovedRole)
                except Exception as e:
                    print("LOG: There was a problem giving the role")
                    print(f"ERROR: Role Error:\n{e}")
        try:
            async with asqlite.connect("./databases/polls.db") as connection:
                async with connection.cursor() as c:
                    query = f"SELECT * FROM a{payload.guild_id}"
                    await c.execute(query)
                    results = await c.fetchall()
            for poll in results:
                if poll[2] == payload.message_id:
                    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
                    choices = poll[6].split(",")
                    print(choices)
                    if poll[5].lower() == "line":
                        votes = ast.literal_eval(poll[7])
                        for i in range(len(choices)):
                            if str(payload.emoji) == reactions[i]:
                                print(votes[i])
                                votes[i].append(votes[i][len(votes[i]) - 1] + 1)
                                print(f"Adding 1 to {choices[i]}")
                        async with asqlite.connect("./databases/polls.db") as connection:
                            async with connection.cursor() as c:
                                query = f"UPDATE a{payload.guild_id} SET votes = ? WHERE poll_id = ?"
                                await c.execute(query,(",".join(str(v) for v in votes),poll[3]))
                                await connection.commit()
                    else:
                        votes = poll[7].split(",")
                        print(votes)
                        for i in range(len(choices)):
                            if str(payload.emoji) == reactions[i]:
                                votes[i] = str(int(votes[i]) + 1)
                                print(f"Adding 1 to {choices[i]}")
                        print(f"Before join {votes}")
                        votes = ",".join(votes)
                        print(f"after join {votes}")
                        async with asqlite.connect("./databases/polls.db") as connection:
                            async with connection.cursor() as c:
                                query = f"UPDATE a{payload.guild_id} SET votes = ? WHERE poll_id = ?"
                                await c.execute(query,(votes,poll[3]))
                                await connection.commit()
        except:
            print("LOG: No poll table found for the server")   
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload : discord.RawReactionActionEvent):
        print("saw a reaction in remove")
        async with asqlite.connect("./databases/reaction_info.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM reactions WHERE server_id = ?""",(payload.guild_id,))
                result = await c.fetchall()
        print(result)
        for reactionRole in result:
            reaction_emoji = reactionRole[3]
            if ":" in reactionRole[3]:
                reaction_emoji = str(reactionRole[3].split(":")[2])
                reaction_emoji = reaction_emoji[:-1]
            print(str(payload.message_id))
            if reactionRole[2] == payload.message_id:
                print("Found the message")
                try:
                    if reaction_emoji == payload.emoji.name:
                        print("Found the emoji")
                        if reactionRole[5] == 1 or reactionRole[5] == 2:
                            guildObject = self.client.get_guild(payload.guild_id)
                            memberObject = guildObject.get_member(payload.user_id)
                            roleToRemove = guildObject.get_role(reactionRole[4])
                            await memberObject.remove_roles(roleToRemove)
                            embedRemovedRole = discord.Embed(colour=discord.Colour.teal())
                            embedRemovedRole.title = f"Successfully removed the {roleToRemove.name} role."
                            await memberObject.send(embed=embedRemovedRole)
                    elif int(reaction_emoji) == payload.emoji.id:
                        print("Found the emoji")
                        if reactionRole[5] == 1 or reactionRole[5] == 2:
                            guildObject = self.client.get_guild(payload.guild_id)
                            memberObject = guildObject.get_member(payload.user_id)
                            roleToRemove = guildObject.get_role(reactionRole[4])
                            await memberObject.remove_roles(roleToRemove)
                            embedRemovedRole = discord.Embed(colour=discord.Colour.teal())
                            embedRemovedRole.title = f"Successfully removed the {roleToRemove.name} role."
                            await memberObject.send(embed=embedRemovedRole)
                except:
                    print("There was an error removing the role")
        try:
            async with asqlite.connect("./databases/polls.db") as connection:
                async with connection.cursor() as c:
                    query = f"SELECT * FROM a{payload.guild_id}"
                    await c.execute(query)
                    results = await c.fetchall()
            for poll in results:
                if poll[2] == payload.message_id:
                    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
                    choices = poll[6].split(",")
                    print(choices)
                    if poll[5].lower() == "line":
                        votes = ast.literal_eval(poll[7])
                        for i in range(len(choices)):
                            if str(payload.emoji) == reactions[i]:
                                print(votes[i])
                                votes[i].append(votes[i][len(votes[i]) - 1] - 1)
                                print(f"Adding 1 to {choices[i]}")
                        async with asqlite.connect("./databases/polls.db") as connection:
                            async with connection.cursor() as c:
                                query = f"UPDATE a{payload.guild_id} SET votes = ? WHERE poll_id = ?"
                                await c.execute(query,(",".join(str(v) for v in votes),int(poll[3])))
                                await connection.commit()
                    else:
                        votes = poll[7].split(",")
                        print(votes)
                        for i in range(len(choices)):
                            if str(payload.emoji) == reactions[i]:
                                votes[i] = str(int(votes[i]) - 1)
                                print(f"Adding 1 to {choices[i]}")
                        print(f"Before join {votes}")
                        votes = ",".join(votes)
                        print(f"after join {votes}")
                        async with asqlite.connect("./databases/polls.db") as connection:
                            async with connection.cursor() as c:
                                query = f"UPDATE a{payload.guild_id} SET votes = ? WHERE poll_id = ?"
                                await c.execute(query,(votes,int(poll[3])))
                                await connection.commit()
        except:
            print("LOG: No poll table found for the server")                        

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):
        if not message.guild == None:
            serverID = message.guild.id
            print(serverID)
            channelID = message.channel.id
            print(channelID)
            user = message.author
            guildObject = message.guild
            async with asqlite.connect("./databases/reaction_info.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""SELECT * FROM message_reactions WHERE server_id = ? and channel_id = ?""",(serverID,channelID))
                    results = await c.fetchone()
            print(results)
            print(message.content.lower())
            if results != None:
                role = guildObject.get_role(results[3])
                if role in user.roles:
                    if results[5]:
                        print(results[5])
                        await message.add_reaction(results[5])
                    return
                if results[2] in message.content.lower() or results[2] == None:
                    print(role.name)
                    await user.add_roles(role)
                    if results[4]:
                        print(results[4])
                        print(user.display_name)
                        print(discord.Permissions.manage_nicknames)
                        nickname = user.display_name
                        print(nickname)
                        await user.edit(nick=f"{results[4]} {nickname}")
                    if results[5]:
                        print(results[5])
                        await message.add_reaction(results[5])

#-----------------------------------------------------------

    #For adding birthdays
    @app_commands.command(name= "addbirthday", description="Add a birthday to the calendar.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.describe(birthdaydate = "Your birthday date in 'YYYY-MM-DD' format", member = "A member you are setting the birthday of. If you aren't stating a member then it will set it as your birthday")
    async def addbirthday(self, interaction : discord.Interaction, birthdaydate : str, member : Union[None,discord.Member],):
        """
        Add a birthday to the calendar.

        **Usage:**
            `-addbirthday [Birthday Date] Optional[Member]`
        
        **Arguments:**
            `birthday date`: The date you were born in the format `yyyy-mm-dd`.
            `member`: A person that you mention
        """
        if member == None:
            member = interaction.user
        try:
            dates = birthdaydate.split("-")
            if len(dates) == 3 and len(dates[0]) == 4 and int(dates[0]) > 1950 and int(dates[0]) < 2022 and len(dates[1]) == 2 and int(dates[1]) > 0 and int(dates[1]) < 13 \
                and len(dates[2]) == 2 and int(dates[2]) > 0 and int(dates[2]) < 32 :
                            print("Date is good")
            else:
                embedIncorrectDate = discord.Embed(colour=discord.Colour.red(),title="Incorrect birthday date formate. Please input it as YYYY-MM-DD")
                await interaction.response.send_message(embed=embedIncorrectDate)
                return
        except:
            embedIncorrectDate = discord.Embed(colour=discord.Colour.red(),title="Incorrect birthday date formate. Please input it as YYYY-MM-DD")
            await interaction.response.send_message(embed=embedIncorrectDate)
            return
        memberID = member.id
        memberName = member.display_name
        serverID = interaction.guild.id
        async with asqlite.connect("./databases/user_birthdays.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""INSERT INTO users VALUES (?,?,?)""", (serverID,memberID,birthdaydate))
                await connection.commit()
        embedAddedBirthday = discord.Embed(title=f"Woohoo! {memberName}'s Birthday has been added to the calendar!")
        await interaction.response.send_message(embed=embedAddedBirthday)

#-----------------------------------------------------------

    #Show birthdays
    @app_commands.command(description="Show all the birthdays currently on the calendar.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.describe(viewmode="The specific month you wish to see the birthdays of. If none is given it will default to all of the months.")
    async def birthdays(self,interaction : discord.Interaction,viewmode : str = 'ALL'):
        """
        Show all the birthdays currently on the calendar.

        **Usage:**
            `-birthdays Optional[Scope]`
        
        **Arguments:**
            `scope`: The specific month you wish to see. Defaults to all
        """
        serverID = interaction.guild.id
        async with asqlite.connect("./databases/user_birthdays.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM users WHERE server_id = ?""",(serverID,))
                results = await c.fetchall()
        embedBirthdays = discord.Embed(colour=discord.Colour.gold())
        embedBirthdays.title = 'Birthdays'
        
        months = ['Placefiller','January','February','March',
                    'April','May',
                    'June','July',
                    'August','September',
                    'October','November','December']
        if len(results) > 0:
            if (viewmode.upper() == 'ALL'):
                embedBirthdays.description = f"*These are the birthdays for the entire year!* :cake:"
                for month in range(1,13):
                    birthdayString = ''
                    for birthday in results:
                        if birthday[2][5:7] == '0' + str(month) or birthday[2][5:7] == str(month):
                            user = await self.client.fetch_user(birthday[1])
                            birthdayString += f'{user.display_name} - {birthday[2][8:]}\n'
                    if birthdayString == '':
                        birthdayString = 'None'
                    embedBirthdays.add_field(name=months[month],value=birthdayString)
                await interaction.response.send_message(embed=embedBirthdays)
            elif (viewmode.capitalize() not in months):
                embedBadMonth = discord.Embed(colour=discord.Colour.red())
                embedBadMonth.title = "Incorrect input for scope of search. Please use a month"
                await interaction.response.send_message(embed=embedBadMonth)
            elif (viewmode.capitalize() in months):
                birthdayString = ''
                for month in range(1,13):
                    if viewmode.capitalize() == months[month]:
                        embedBirthdays.description = f"*These are the birthdays for {months[month]}* :cake:"
                        for birthday in results:
                            if birthday[2][5:7] == '0' + str(month) or birthday[2][5:7] == str(month):
                                user = await self.client.fetch_user(birthday[1])
                                birthdayString += f'{user.display_name} - {birthday[2][8:]}\n'
                        if len(birthdayString) == 0:
                            birthdayString = 'None'
                        embedBirthdays.add_field(name=months[month],value=birthdayString)
                await interaction.response.send_message(embed=embedBirthdays)
            else:
                for birthday in results:
                    currentUserName = await self.client.fetch_user(birthday[1])
                    embedBirthdays.add_field(name=currentUserName.display_name,value=birthday[2])
                await interaction.response.send_message(embed=embedBirthdays)
        else:
            embedBirthdays.title = "No birthdays found. Add some for them to be shown"
            await interaction.response.send_message(embed=embedBirthdays)
    
#-----------------------------------------------------------

    # For checking bday notifications
    @app_commands.command(description="Lets you know if the birthday announcements are enabled.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def birthdaystatus(self,interaction : discord.Interaction):
        """
        Lets you know if the birthday announcements are enabled.

        **Usage:**
            `-birthdaystatus`
        """
        serverID = interaction.guild.id
        async with asqlite.connect("./databases/user_birthdays.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM settings WHERE server_id = ?""", (serverID,))
                result = await c.fetchone()
                embedStatus = discord.Embed(colour=discord.Colour.blurple())
                embedStatus.title = "Birthday Notification Status"
                if result == None:
                    await c.execute("""INSERT INTO settings (server_id, channel_id, activated) VALUES (?,?,?)""",(serverID,0,0))
                    await connection.commit()
                    print("")
                    embedStatus.description = "Currently the notifications are disabled."\
                        " You can enable them by calling `enablebirthdays [channelMention]`"
                elif result[2] == 0:
                    embedStatus.description = "Currently the notifications are disabled."\
                        " You can enable them by calling `enablebirthdays [channelMention]`"
                elif result[2] == 1:
                    sendingChannel = self.client.get_channel(result[1])
                    embedStatus.description = "Notifications are enabled!"\
                        f" They will be sent to {sendingChannel.mention}."
        await interaction.response.send_message(embed=embedStatus)

#-----------------------------------------------------------

    #For removing birthdays
    @app_commands.command(description="Delete a members birthday from the calendar.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.describe(member= "The member's birthday you wish to delete. Leave blank for yourself")
    async def deletebirthday(self, interaction : discord.Interaction, member : Union[None,discord.Member]):
        """
        Delete a members birthday from the calendar.

        **Usage:**
            `-deletebirthday Optional[Member]`
        
        **Arguments:**
            `member`: A person that you mention. Defaults to you if none is given.
        """
        if member == None:
            member = commands.Author
        memberID = member.id
        memberName = member.display_name
        serverID = interaction.guild.id
        print("ID : " + str(memberID))
        async with asqlite.connect("./databases/user_birthdays.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""DELETE FROM users WHERE user_id = ? AND server_id = ?""", (memberID,serverID))
                await connection.commit()
        embedRemovedBirthday = discord.Embed(title=f"Darn. {memberName}'s Birthday has been removed from the calendar")
        await interaction.response.send_message(embed=embedRemovedBirthday)

#-----------------------------------------------------------

    @app_commands.command(description="Disables the birthday announcements. By default they are disabled.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.checks.has_permissions(administrator=True)
    async def disablebirthdays(self, interaction : discord.Interaction):
        """
        Disables the birthday announcements. By default they are disabled.

        **Usage:**
            `-disablebirthdays`
        """
        serverID = interaction.guild.id
        async with asqlite.connect("./databases/user_birthdays.db") as connection:
            async with connection.cursor() as c:
                c.execute("""UPDATE settings SET activated = 0 WHERE server_id = ?""", (serverID,))
                connection.commit()
        embedEnableBirthdays = discord.Embed(colour=discord.Colour.blurple())
        embedEnableBirthdays.title = f"Birthday notifications are now disabled"
        await interaction.response.send_message(embed=embedEnableBirthdays)

#-----------------------------------------------------------

    @app_commands.command(description="Enable birthday announcements in a given channel.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.describe(channel= "The channel you wish to have birthday announcements in.")
    @app_commands.checks.has_permissions(administrator=True)
    async def enablebirthdays(self, interaction : discord.Interaction, channel : discord.TextChannel):
        """
        Enable birthday announcements in a given channel.

        **Usage:**
            `-enablebirthdays [Channel]`
        
        **Arguments:**
            `channel`: A text channel that you have mentioned.
        """
        channelID = channel.id
        serverID = interaction.guild.id
        async with asqlite.connect("./databases/user_birthdays.db") as connection:
            async with connection.cursor() as c:
                c.execute("""SELECT * FROM settings WHERE server_id = ?""",(serverID,))
                results = c.fetchone()
                if results == None:
                    c.execute("""INSERT INTO settings (server_id, channel_id, activated) VALUES (?,?,?))""",(serverID,channelID,1))
                    connection.commit()
                else:
                    c.execute("""UPDATE settings SET channel_id = ?, activated = 1 WHERE server_id = ?""", (channelID,serverID))
                    connection.commit()
        embedEnableBirthdays = discord.Embed(colour=discord.Colour.blurple())
        embedEnableBirthdays.title = "Success!"
        embedEnableBirthdays.description = f"Birthday notifications are now enabled and will be sent to {channel.mention}!"
        await interaction.response.send_message(embed=embedEnableBirthdays)

#-----------------------------------------------------------

    #For creating an event
    @app_commands.command(description="Create an event to automate channel hiding on various stages")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.describe(eventname= "The specific name of the event",stage1="The list of channels to be available on the first stage",stage2="The list of channels to be available on the second stage",stage3="The list of channels to be available on the third stage")
    @app_commands.checks.has_permissions(administrator=True)
    async def eventcreate(self, interaction : discord.Interaction, eventname : str, stage1 : str, stage2 : Union[None,str], stage3 : Union[None,str]):
        """
        Create an event to allow you to automate hiding channels at different stages. You can have up to three different stages.

        **Usage:**
            `-eventcreate [Event Name] [Stage 1 Channels] Optional[Stage 2 Channels] Optional[Stage 3 Channels]`
        
        **Arguments:**
            `event name`: The name of the event you are creating.
            `stage 1 channels`: A list of channel IDs seperated by only a ",".
            `stage 2 channels`: A list of channel IDs seperated by only a ",".
            `stage 3 channels`: A list of channel IDs seperated by only a ",".
        """
        serverID = interaction.guild.id
        async with asqlite.connect("./databases/server_events.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""INSERT INTO events VALUES (?,?,?,?,?)""", (serverID, eventname, stage1, stage2, stage3))
                await c.execute("""SELECT * FROM preferences WHERE server_id = ?""", (serverID,))
                preferences = await c.fetchone()
                if preferences == None:
                    await c.execute("""INSERT INTO preferences VALUES (?,?,?)""", (serverID,eventname,0))
                    embedEventCreated = discord.Embed(colour=discord.Colour.random(),title=f"Successfully created event: {eventname} and set it as the current event,")
                    await connection.commit()
                    await interaction.response.send_message(embed=embedEventCreated)
                    return
                elif preferences[1] == None:
                    await c.execute("""UPDATE preferences SET current_event = ?, current_stage = ? WHERE server_id = ?""", (eventname,0,serverID))
                    embedEventCreated = discord.Embed(colour=discord.Colour.random(),title=f"Successfully created event: {eventname} and set it as the current event.")
                    await connection.commit()
                    await interaction.response.send_message(embed=embedEventCreated)
                    return
                await connection.commit()
        embedEventCreated = discord.Embed(colour=discord.Colour.random(),title=f"Successfully created event: {eventname}")
        await interaction.response.send_message(embed=embedEventCreated)

#-----------------------------------------------------------

    #For end of event
    @app_commands.command(description="End the current event")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @commands.has_permissions(administrator=True)
    async def eventend(self, interaction : discord.Interaction):
        """
        End the current event. This will also give you option to delete the event or if you want to keep it for later use.

        **Usage:**
            `-eventend`
        """
        def check(m):
            return m.author == interaction.user
        serverID = interaction.guild.id
        await interaction.response.defer()
        async with asqlite.connect("./databases/server_events.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM preferences WHERE server_id = ?""",(serverID,))
                preferences = await c.fetchone()
                if preferences == None:
                    embedNoEvent = discord.Embed(colour=discord.Colour.red(),title="There is currently no active event. Please select an event with `-eventset [Event Name]`")
                    await interaction.followup.send(embed=embedNoEvent)
                    return
                await c.execute("""SELECT * FROM events WHERE server_id = ? and event_name = ?""",(serverID,preferences[1]))
                eventDetails = await c.fetchone()
                if eventDetails == None:
                    embedCantFindEvent = discord.Embed(colour=discord.Colour.red(),title="Cannot find the current event's details. Perhaps it was removed?")
                    await interaction.followup.send(embed=embedCantFindEvent)
                    await c.execute("""UPDATE preferences SET current_event = ?,current_stage = ? WHERE server_id = ?""", (None,0,serverID))
                    await connection.commit()
                    return
        for i in range(2,5):
            if eventDetails[i] != None:
                channels = eventDetails[i].split(",")
                for channelID in channels:
                    channel = await self.client.fetch_channel(channelID)
                    guild = await self.client.fetch_guild(serverID)
                    await channel.set_permissions(guild.default_role, view_channel=False)
        embedDeleteEvent = discord.Embed(colour=discord.Colour.blurple(),title=f"Do you want to delete event: {eventDetails[1]}? Y/N")
        message = await interaction.followup.send(embed=embedDeleteEvent)
        reply = await self.client.wait_for('message', check=check)
        async with asqlite.connect("./databases/server_events.db") as connection:
            async with connection.cursor() as c:
                if reply.content.upper() == "Y" or reply.content.upper() == "YES":
                    await c.execute("""DELETE FROM events WHERE event_name = ? and server_id = ?""", (preferences[1], serverID))
                await c.execute("""UPDATE preferences SET current_event = ?, current_stage = ? WHERE server_id = ?""", (None,0,serverID))
                await connection.commit()
        embedEndEvent = discord.Embed(colour=discord.Colour.blurple(),title=f"Successfully ended event: {preferences[1]}.")
        await message.edit(embed=embedEndEvent)

#-----------------------------------------------------------

    #For listing events
    @app_commands.command(description="See the events for the server.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def eventlist(self, interaction : discord.Interaction):
        """
        See the current event as well as all the others available for the server. This will also show the stages channels that are assigned to them.

        **Usage:**
            `-eventlist`
        """
        serverID = interaction.guild.id
        serverName = interaction.guild.name
        async with asqlite.connect("./databases/server_events.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM preferences WHERE server_id = ?""",(serverID,))
                preferences = await c.fetchone()
                await c.execute("""SELECT * FROM events WHERE server_id = ?""",(serverID,))
                events = await c.fetchall()
        embedEventList = discord.Embed(colour=discord.Colour.random(),title=f"Events for {serverName}")
        if preferences[1] != None:
            embedEventList.add_field(name="Current Event:",value=f"{preferences[1]}\nStage {preferences[2]}",inline=False)
        else: 
            embedEventList.add_field(name="No Event Currently Active:",value=f"Set an event to be active with `/eventset [Event Name]`")
        if events != None:
            for event in events:
                channelMentions1 = []
                if event[2] != None:
                    channels = event[2].split(",")
                    for channelID in channels:
                        channel = await self.client.fetch_channel(channelID)
                        channelMentions1.append(channel.mention)
                channelMentions2 = []
                if event[3] != None:
                    channels = event[3].split(",")
                    for channelID in channels:
                        channel = await self.client.fetch_channel(channelID)
                        channelMentions2.append(channel.mention)
                channelMentions3 = []
                if event[4] != None:
                    channels = event[4].split(",")
                    for channelID in channels:
                        channel = await self.client.fetch_channel(channelID)
                        channelMentions3.append(channel.mention)
                embedEventList.add_field(name=event[1],value="Stage 1 Channels: %s\nStage 2 Channels: %s\nStage 3 Channels: %s" % (", ".join(channelMentions1),", ".join(channelMentions2),", ".join(channelMentions3)),inline=True)
            else:
                embedEventList.add_field(name=None,value="There are currently no events saved. Create one with `/eventcreate`")
            await interaction.response.send_message(embed=embedEventList)

#-----------------------------------------------------------

    #For next event stage
    @app_commands.command(description="Go to the next stage of the event.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.checks.has_permissions(administrator=True)
    async def eventnext(self, interaction : discord.Interaction):
        """
        Go to the next stage of the event.

        **Usage:**
            `-eventnext`
        """
        serverID = interaction.guild.id
        await interaction.response.defer()
        async with asqlite.connect("./databases/server_events.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM preferences WHERE server_id = ?""",(serverID,))
                preferences = await c.fetchone()
        if preferences == None:
            embedNoEvent = discord.Embed(colour=discord.Colour.red(),title="There is currently no active event. Please select an event with `-eventset [Event Name]`")
            await interaction.followup.send(embed=embedNoEvent)
            return
        elif preferences[2] == 0:
            embedEventNotStarted = discord.Embed(colour=discord.Colour.red(),title="Event hasn't been started yet. Start it with `-eventstart`")
            await interaction.followup.send(embed=embedEventNotStarted)
            return
        elif preferences[2] == 3 or preferences[2] == None:
            embedEndOfEvent = discord.Embed(colour=discord.Colour.red(),title="Reached the end of the event, time to close the event with `-eventend`")
            await interaction.followup.send(embed=embedEndOfEvent)
            return
        async with asqlite.connect("./databases/server_events.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM events WHERE server_id = ? and event_name = ?""",(serverID,preferences[1]))
                eventDetails = await c.fetchone()
        if eventDetails == None:
            embedCantFindEvent = discord.Embed(colour=discord.Colour.red(),title="Cannot find the current event's details. Perhaps it was removed?")
            await interaction.followup.send(embed=embedCantFindEvent)
            async with asqlite.connect("./databases/server_events.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""UPDATE preferences SET current_event = ?,current_stage = ? WHERE server_id = ?""", (None,0,serverID))
                    await connection.commit()
            return
        if eventDetails[preferences[2] + 2] != None:
            channels = eventDetails[preferences[2] + 2].split(",")
            for channelID in channels:
                channel = await self.client.fetch_channel(channelID)
                guild = await self.client.fetch_guild(serverID)
                await channel.set_permissions(guild.default_role, view_channel=True)
            channels = eventDetails[preferences[2] + 1].split(",")
            for channelID in channels:
                channel = await self.client.fetch_channel(channelID)
                guild = await self.client.fetch_guild(serverID)
                await channel.set_permissions(guild.default_role, view_channel=False)
        else:
            embedEndOfEvent = discord.Embed(colour=discord.Colour.red(),title="Reached the end of the event, time to close the event with `-eventend`")
            await interaction.followup.send(embed=embedEndOfEvent)
            return 
        async with asqlite.connect("./databases/server_events.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""UPDATE preferences SET current_stage = current_stage + 1 WHERE server_id = ?""",(serverID,))
                await connection.commit()
        embedNextStage = discord.Embed(colour=discord.Colour.green(),title=f"Successfully moved to stage {preferences[2] + 1} for event: {eventDetails[1]}")
        await interaction.followup.send(embed=embedNextStage)
        
#-----------------------------------------------------------

    #For setting the event
    @app_commands.command(description="Set the current event for the server.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.describe(eventname= "The name of the event to set as active.")
    @app_commands.checks.has_permissions(administrator=True)
    async def eventset(self, interaction : discord.Interaction, eventname : str):
        """
        Set the current event for the server.
        Note that this overwrites the progress of another. This means that if you select the event again it will need to be started again.

        **Usage:**
            `-eventset [Event Name]`
        
        **Arguments:**
            `event name`: The name of the event you wish to change to.
        """
        serverID = interaction.guild.id
        await interaction.response.defer()
        async with asqlite.connect("./databases/server_events.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM events WHERE server_id = ? and event_name = ?""",(serverID, eventname))
                results = await c.fetchall()
                if results == None:
                    embedEventDoesNotExist = discord.Embed(colour=discord.Colour.red(),title=f"Event: {eventname} does not exist.")
                    await interaction.followup.send(embed=embedEventDoesNotExist)
                    return
                await c.execute("""SELECT * FROM preferences WHERE server_id = ?""", (serverID,))
                results = await c.fetchone()
                if results == None:
                    await c.execute("""INSERT INTO preferences VALUES (?,?,?)""", (serverID, eventname, 0))
                else:
                    await c.execute("""UPDATE preferences SET current_event = ?, current_stage = ?""",(eventname,0))
                await connection.commit()
        embedEventSet = discord.Embed(colour=discord.Colour.green(),title=f"Successfully set the current event to: {eventname}")
        await interaction.followup.send(embed=embedEventSet)

#-----------------------------------------------------------

    #For starting the event
    @app_commands.command(description="Kickoff your event by allowing the first stage channels to be visible!")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.checks.has_permissions(administrator=True)
    async def eventstart(self, interaction : discord.Interaction):
        """
        Kickoff your event by allowing the first stage channels to be visible!

        **Usage:**
            `-eventstart`
        """
        serverID = interaction.guild.id
        await interaction.response.defer()
        async with asqlite.connect("./databases/server_events.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM preferences WHERE server_id = ?""",(serverID,))
                preferences = await c.fetchone()
                if preferences == None:
                    embedNoEvent = discord.Embed(colour=discord.Colour.red(),title="There is currently no active event. Please select an event with `-eventset [Event Name]`")
                    await interaction.followup.send(embed=embedNoEvent)
                    return
                print(preferences)
                await c.execute("""SELECT * FROM events WHERE server_id = ? and event_name = ?""",(serverID,preferences[1]))
                eventDetails = await c.fetchone()
                if eventDetails == None:
                    embedCantFindEvent = discord.Embed(colour=discord.Colour.red(),title="Cannot find the current event's details. Perhaps it was removed?")
                    await interaction.followup.send(embed=embedCantFindEvent)
                    await c.execute("""UPDATE preferences SET current_event = ?, current_stage = ?""", (None,0))
                    await connection.commit()
                    return
        for i in range(2,5):
            if eventDetails[i] != None:
                channels = eventDetails[i].split(",")
                for channelID in channels:
                    channel = await self.client.fetch_channel(channelID)
                    guild = await self.client.fetch_guild(serverID)
                    await channel.set_permissions(guild.default_role, view_channel=False)
        channels1 = eventDetails[2].split(",")
        for channelID in channels1:
            channel = await self.client.fetch_channel(channelID)
            guild = await self.client.fetch_guild(serverID)
            await channel.set_permissions(guild.default_role, view_channel=True)
            async with asqlite.connect("./databases/server_events.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""UPDATE preferences SET current_stage = current_stage + 1 WHERE server_id = ?""",(serverID,))
                    await connection.commit()
        embedEventStarted = discord.Embed(colour=discord.Colour.green(),title=f"Successfully started event: {eventDetails[1]}")
        await interaction.followup.send(embed=embedEventStarted)

#-----------------------------------------------------------

    #For join role
    @app_commands.command(description="Setup users to receive a role on joining")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.describe(role="The role for the user to receieve when joining")
    async def joinroles(self,interaction : discord.Interaction, role : Optional[discord.Role]):
        serverID = interaction.guild_id
        async with asqlite.connect("./databases/reaction_info.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""CREATE TABLE IF NOT EXISTS join_roles (server_id INT, role_id INT)""")
                await connection.commit()
        if role:
            async with asqlite.connect("./databases/reaction_info.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""SELECT * FROM join_roles WHERE server_id =?""", (serverID,))
                    results = await c.fetchall()
            if results:
                for result in results:
                    if result[1] == role.id:
                        async with asqlite.connect("./databases/reaction_info.db") as connection:
                            async with connection.cursor() as c:
                                await c.execute("""DELETE FROM join_roles WHERE role_id = ?""", (role.id,))
                                await connection.commit()
                        embedRemovedRole = discord.Embed(colour=discord.Colour.green(), title=f'Successfully removed {role.name} from the join roles.')
                        await interaction.response.send_message(embed=embedRemovedRole)
                        return
            async with asqlite.connect("./databases/reaction_info.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""INSERT INTO join_roles VALUES (?, ?)""", (serverID, role.id))
                    await connection.commit()
            embedAddedJoinRole = discord.Embed(colour=discord.Colour.green(), title= f'Succesfully added "{role.name}" to the roles to be given on joining.')
            await interaction.response.send_message(embed=embedAddedJoinRole)
        else:
            async with asqlite.connect("./databases/reaction_info.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""SELECT * FROM join_roles WHERE server_id =?""", (serverID,))
                    results = await c.fetchall()
            if results:
                embedJoinRoles = discord.Embed(colour=discord.Colour.random(),title=f"Join Roles For {interaction.guild.name}")
                guildObject = interaction.guild
                outString = ''
                for result in results:
                    role = guildObject.get_role(result[1])
                    outString += role.mention + "\n"
                outString.rstrip("\n")
                embedJoinRoles.add_field(name="Roles",value=outString)
                await interaction.response.send_message(embed=embedJoinRoles)
            else:
                embedNoRoles = discord.Embed(colour=discord.Colour.red(),title="There are currently no join roles active")
                await interaction.response.send_message(embed=embedNoRoles)

#-----------------------------------------------------------

    @app_commands.command(description="List all of the emojis that the server has along with it's id")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def listemojis(self, interaction : discord.Interaction):
        await interaction.response.defer()
        serverObject = interaction.guild
        embedCurrentEmoji = discord.Embed(colour=discord.Colour.random(),title=f"Emojis for {serverObject.name}")
        currentEmoji = ""
        page = 1
        amountOfPages = ceil(len(serverObject.emojis) / self.amount_per_page)

        async def buttonLeftCallback(interaction : discord.Interaction):
            currentEmoji = ""
            nonlocal page
            nonlocal amountOfPages
            nonlocal embedCurrentEmoji
            if page == 1:
                page = amountOfPages
                startIndex = (amountOfPages - 1) * self.amount_per_page
                for i in range(startIndex,len(serverObject.emojis)):
                    currentEmoji += f"{serverObject.emojis[i].name}: {serverObject.emojis[i]}\nID: {serverObject.emojis[i].id}\nItem ID: \{serverObject.emojis[i]}" + "\n"
            else:
                page -= 1
                endIndex = (page * self.amount_per_page)
                startIndex = endIndex - self.amount_per_page
                for i in range(startIndex,endIndex):
                    currentEmoji += f"{serverObject.emojis[i].name}: {serverObject.emojis[i]}\nID: {serverObject.emojis[i].id}\nItem ID: \{serverObject.emojis[i]}" + "\n"
                
            embedCurrentEmoji.remove_field(0)
            embedCurrentEmoji.add_field(name="Emoji",value=currentEmoji)
            embedCurrentEmoji.set_footer(text=f"Page {page} of {amountOfPages}")
            await interaction.response.edit_message(embed=embedCurrentEmoji)
        
        async def buttonRightCallback(interaction : discord.Interaction):
            currentEmoji = ""
            nonlocal page
            nonlocal amountOfPages
            nonlocal embedCurrentEmoji
            if page == amountOfPages:
                print("Going to page 1")
                page = 1
                startIndex = 0
                endIndex = startIndex + self.amount_per_page
                for i in range(startIndex,endIndex):
                    currentEmoji += f"{serverObject.emojis[i].name}: {serverObject.emojis[i]}\nID: {serverObject.emojis[i].id}\nItem ID: \{serverObject.emojis[i]}" + "\n"
            elif page == amountOfPages - 1:
                print("Going to last page")
                page += 1
                startIndex = (page - 1) * self.amount_per_page
                for i in range(startIndex,len(serverObject.emojis)):
                    currentEmoji += f"{serverObject.emojis[i].name}: {serverObject.emojis[i]}\nID: {serverObject.emojis[i].id}\nItem ID: \{serverObject.emojis[i]}" + "\n"
            else:
                print("Going to else")
                page += 1
                endIndex = page * self.amount_per_page
                startIndex = endIndex - self.amount_per_page
                for i in range(startIndex,endIndex):
                    currentEmoji += f"{serverObject.emojis[i].name}: {serverObject.emojis[i]}\nID: {serverObject.emojis[i].id}\nItem ID: \{serverObject.emojis[i]}" + "\n"
            
            embedCurrentEmoji.remove_field(0)
            embedCurrentEmoji.add_field(name="Emoji",value=currentEmoji)
            embedCurrentEmoji.set_footer(text=f"Page {page} of {amountOfPages}")
            await interaction.response.edit_message(embed=embedCurrentEmoji)

        for i in range(len(serverObject.emojis)):
            if i < self.amount_per_page:
                currentEmoji += f"{serverObject.emojis[i].name}: {serverObject.emojis[i]}\nID: {serverObject.emojis[i].id}\nItem ID: \{serverObject.emojis[i]}" + "\n"
            else:
                break

        currentEmoji.rstrip("\n")
        embedCurrentEmoji.add_field(name="Emoji",value=currentEmoji)
        embedCurrentEmoji.set_footer(text=f"Page {page} of {amountOfPages}")
        if amountOfPages > 1:
            print("More than one page")
            leftButton = discord.ui.Button(style=discord.ButtonStyle.grey, label="Previous Page")
            leftButton.callback = buttonLeftCallback
            rightButton = discord.ui.Button(style=discord.ButtonStyle.grey, label="Next Page")
            rightButton.callback = buttonRightCallback
            view = discord.ui.View()
            view.add_item(leftButton)
            view.add_item(rightButton)
            message = await interaction.followup.send(embed=embedCurrentEmoji,view=view)
        else:
            message = await interaction.followup.send(embed=embedCurrentEmoji)

#-----------------------------------------------------------

    #For list roles
    @app_commands.command(description="List all of the roles in the server along with it's id")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.checks.has_permissions(administrator=True)
    async def listroles(self, interaction : discord.Interaction):
        await interaction.response.defer()
        serverObject = interaction.guild
        embedCurrentRoles = discord.Embed(colour=discord.Colour.random(),title=f"Roles for {serverObject.name}")
        currentRole = ""
        page = 1
        amountOfPages = ceil(len(serverObject.roles) / self.amount_per_page)

        async def buttonLeftCallback(interaction : discord.Interaction):
            currentRole = ""
            nonlocal page
            nonlocal amountOfPages
            nonlocal embedCurrentRoles
            if page == 1:
                page = amountOfPages
                startIndex = (amountOfPages - 1) * self.amount_per_page
                for i in range(startIndex,len(serverObject.roles)):
                    currentRole += f"{serverObject.roles[i].name}: {serverObject.roles[i].mention}\nID: {serverObject.roles[i].id}\nItem ID: \{serverObject.roles[i].mention}" + "\n"
            else:
                page -= 1
                endIndex = (page * self.amount_per_page)
                startIndex = endIndex - self.amount_per_page
                for i in range(startIndex,endIndex):
                    currentRole += f"{serverObject.roles[i].name}: {serverObject.roles[i].mention}\nID: {serverObject.roles[i].id}\nItem ID: \{serverObject.roles[i].mention}" + "\n"                
            embedCurrentRoles.remove_field(0)
            embedCurrentRoles.add_field(name="Emoji",value=currentRole)
            embedCurrentRoles.set_footer(text=f"Page {page} of {amountOfPages}")
            await interaction.response.edit_message(embed=embedCurrentRoles)
        
        async def buttonRightCallback(interaction : discord.Interaction):
            currentRole = ""
            nonlocal page
            nonlocal amountOfPages
            nonlocal embedCurrentRoles
            if page == amountOfPages:
                print("Going to page 1")
                page = 1
                startIndex = 0
                endIndex = startIndex + self.amount_per_page
                for i in range(startIndex,endIndex):
                    currentRole += f"{serverObject.roles[i].name}: {serverObject.roles[i].mention}\nID: {serverObject.roles[i].id}\nItem ID: \{serverObject.roles[i].mention}" + "\n"                
            elif page == amountOfPages - 1:
                print("Going to last page")
                page += 1
                startIndex = (page - 1) * self.amount_per_page
                for i in range(startIndex,len(serverObject.roles)):
                    currentRole += f"{serverObject.roles[i].name}: {serverObject.roles[i].mention}\nID: {serverObject.roles[i].id}\nItem ID: \{serverObject.roles[i].mention}" + "\n"                
            else:
                print("Going to else")
                page += 1
                endIndex = page * self.amount_per_page
                startIndex = endIndex - self.amount_per_page
                for i in range(startIndex,endIndex):
                    currentRole += f"{serverObject.roles[i].name}: {serverObject.roles[i].mention}\nID: {serverObject.roles[i].id}\nItem ID: \{serverObject.roles[i].mention}" + "\n"                
            
            embedCurrentRoles.remove_field(0)
            embedCurrentRoles.add_field(name="Emoji",value=currentRole)
            embedCurrentRoles.set_footer(text=f"Page {page} of {amountOfPages}")
            await interaction.response.edit_message(embed=embedCurrentRoles)

        for i in range(len(serverObject.roles)):
            if i < self.amount_per_page:
                currentRole += f"{serverObject.roles[i].name}: {serverObject.roles[i].mention}\nID: {serverObject.roles[i].id}\nItem ID: \{serverObject.roles[i].mention}" + "\n"                
            else:
                break

        currentRole.rstrip("\n")
        embedCurrentRoles.add_field(name="Emoji",value=currentRole)
        embedCurrentRoles.set_footer(text=f"Page {page} of {amountOfPages}")
        if amountOfPages > 1:
            print("More than one page")
            leftButton = discord.ui.Button(style=discord.ButtonStyle.grey, label="Previous Page")
            leftButton.callback = buttonLeftCallback
            rightButton = discord.ui.Button(style=discord.ButtonStyle.grey, label="Next Page")
            rightButton.callback = buttonRightCallback
            view = discord.ui.View()
            view.add_item(leftButton)
            view.add_item(rightButton)
            message = await interaction.followup.send(embed=embedCurrentRoles,view=view)
        else:
            message = await interaction.followup.send(embed=embedCurrentRoles)

#-----------------------------------------------------------

    #For message react
    @app_commands.command(description="Set up users to get a role based on a message that was sent")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel = "The channel you're looking for the message in", messagecontent = "The message to look for. Leave none for any message", role = "The role you wish to give to a user.")
    async def messageroleadd(self, interaction : discord.Interaction, channel : discord.TextChannel, messagecontent : Union[None,str], role : discord.Role, nicknamechange : Optional[str], confirmationemoji : Optional[str]):
        serverID = interaction.guild_id
        channelID = channel.id
        roleID = role.id
        async with asqlite.connect("./databases/reaction_info.db") as connection:
            async with connection.cursor() as c:
                query = f"CREATE TABLE if NOT EXISTS message_reactions (server_id INT, channel_id INT, message_content TEXT, role_id INT, nickname_change TEXT, confirmation_emoji TEXT)"
                await c.execute(query)
                await c.execute("""INSERT INTO message_reactions VALUES (?,?,?,?,?,?)""",(serverID,channelID,messagecontent.lower(),roleID,nicknamechange,confirmationemoji))
                await connection.commit()
        embedAddedMessageRole = discord.Embed(colour=discord.Colour.green(),title=f'Successfully added {role.name} to be given when using the phrase {messagecontent} in {channel.name}')
        await interaction.response.send_message(embed=embedAddedMessageRole)

#-----------------------------------------------------------

    #For message react list
    @app_commands.command(description="List all the messages the bot is listening for.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.checks.has_permissions(administrator=True)
    async def messagerolelist(self,interaction : discord.Interaction):
        serverID = interaction.guild_id
        guildObject = interaction.guild
        async with asqlite.connect("./databases/reaction_info.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM message_reactions WHERE server_id = ?""", (serverID,))
                results = await c.fetchall()
        if results == None:
            embedNoReactions = discord.Embed(colour=discord.Colour.blurple(),title="There are currently no messages that the bot is listening for. Add some with `/messageroleadd`.")
            await interaction.response.send_message(embed=embedNoReactions)
            return
        else:
            outStr = ''
            currentChannel = results[0][1]
            embedMessageList = discord.Embed(colour=discord.Colour.random(),title=f"Current Message Reactions For {guildObject.name}")
            for reaction in results:
                print(reaction[2])
                if reaction[1] == currentChannel:
                    role = guildObject.get_role(reaction[3])
                    outStr += f'> Message - "{reaction[2]}"\n> Role - {role.mention}\n> Nickname Addition - "{reaction[4]}"\n> Confirmation Emoji - {reaction[5]}\n\n'
                else:
                    channelObject = guildObject.get_channel(currentChannel)
                    embedMessageList.add_field(name="Active Reaction",value=f"Messages in {channelObject.mention}\n{outStr}")
                    outStr = ''
                    currentChannel = reaction[1]
                    outStr += f'> Message - "{reaction[2]}"\n> Role - {role.mention}\n> Nickname Addition - "{reaction[4]}"\n> Confirmation Emoji - {reaction[5]}\n\n'
            channelObject = guildObject.get_channel(currentChannel)
            embedMessageList.add_field(name="Active Reaction",value=f"Messages in {channelObject.mention}\n{outStr}")
            await interaction.response.send_message(embed=embedMessageList)

                
#-----------------------------------------------------------

    #For message react removal
    @app_commands.command(description="Remove a message role")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.checks.has_permissions(administrator=True)
    async def messageroleremove(self,interaction : discord.Interaction, channel : discord.TextChannel, role : discord.Role):
        serverID = interaction.guild_id
        async with asqlite.connect("./databases/reaction_info.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM message_reactions WHERE server_id = ? and channel_id = ? and role_id = ?""",(serverID,channel.id,role.id))
                results = await c.fetchone()
                if results:
                    await c.execute("""DELETE FROM message_reactions WHERE server_id = ? and channel_id = ? and role_id = ?""",(serverID,channel.id,role.id))
                    embedRoleRemove = discord.Embed(colour=discord.Colour.green(),title=f"Successfully removed message role for *{role.name}* in the *{channel.name}* channel")
                    await connection.commit()
                else:
                    embedRoleRemove = discord.Embed(colour=discord.Colour.red(),title="No message role found for this combination of channel and role.")
        await interaction.response.send_message(embed=embedRoleRemove)
        

#-----------------------------------------------------------

    #For ping
    @app_commands.command(description="Shows the current ping of the bot.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def ping(self, interaction : discord.Interaction):
        """
        Shows the current ping of the bot.

        **Usage:**
            `-ping`
        """
        await interaction.response.send_message(f'Pong! {round (self.client.latency * 1000)}ms', ephemeral=True)

#-----------------------------------------------------------

    #For poll creation
    @app_commands.command(description="Create a new poll for the server")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.describe(charttype="Line, Bar, Pie")
    async def pollcreate(self, interaction : discord.Interaction, channel : discord.TextChannel, charttype : str, polltitle : str, style : Optional[str], choice1 : str, choice2 : str, choice3 : Optional[str], choice4 : Optional[str], choice5 : Optional[str], choice6 : Optional[str], choice7 : Optional[str], choice8 : Optional[str]):
        serverID = interaction.guild_id
        async with asqlite.connect("./databases/polls.db") as connection:
            async with connection.cursor() as c:
                query = f"CREATE TABLE IF NOT EXISTS a{serverID} (server_id INT, channel_id INT, message_id INT, poll_id INT, poll_title TEXT, charttype TEXT, choices BLOB, votes BLOB, style TEXT)"
                await c.execute(query)
                await connection.commit()
        discordStyle = Style(
            background='#36393f',
            plot_background='#23272a',
            foreground='#99aab5',
            foreground_strong='#ffffff',
            foreground_subtle='#99aab5',
            opacity='.6',
            opacity_hover='.9',
            title_font_size=25,
            legend_font_size=15,
            transition='400ms ease-in',
            colors=('#7289da', '#ffffff', '#b9bbbe', '#7289da', '#ffffff', '#b9bbbe', '#7289da', '#ffffff', '#b9bbbe',)
        )
        reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
        choicesTemp = [choice1,choice2,choice3,choice4,choice5,choice6,choice7,choice8]
        choices = []
        for choice in choicesTemp:
            if choice != None:
                choices.append(choice)
        print(f"{choices}")
        match charttype.lower():
            case 'line':
                chart = pygal.Line(print_values=True,style=discordStyle,title=polltitle)
            case 'bar':
                if not style:
                    style = "nothing"
                match style.lower():
                    case "basic":
                        chart = pygal.Bar(print_values=True,style=discordStyle,title=polltitle)
                    case "stacked":
                        chart = pygal.StackedBar(print_values=True,style=discordStyle,title=polltitle)
                    case "horizontal":
                        chart = pygal.HorizontalBar(print_values=True,style=discordStyle,title=polltitle)
                    case _:
                        chart = pygal.Bar(print_values=True,style=discordStyle,title=polltitle)
            case 'pie':
                if style:
                    chart = pygal.Pie(print_values=True,style=discordStyle,title=polltitle,inner_radius=float(style))
                else:
                    chart = pygal.Pie(print_values=True,style=discordStyle,title=polltitle)
            case _:
                chart = pygal.Bar(print_values=True,style=discordStyle,title=polltitle)
                await interaction.channel.send(content="Unknown chart type. Defaulting to a bar graph")
        numbersList = []
        if charttype.lower() == "line":
            for i in range(len(choices)):
                numbersList.append([0])
                chart.add(choices[i],[0])
        else:
            for i in range(len(choices)):
                numbersList.append(0)
                chart.add(choices[i],[0])
        if not os.path.isdir(f"./polls/{serverID}/"):
            os.makedirs(f"./polls/{serverID}/")
        nrOfActivePolls = len(os.listdir(f"./polls/{serverID}/"))
        await interaction.response.send_message(content=f"Made poll with id: `{nrOfActivePolls + 1}`")
        fileDirectory = f'./polls/{serverID}/{nrOfActivePolls+1}.svg'
        chart.render_to_file(fileDirectory)
        drawing = svg2rlg(fileDirectory)
        os.remove(fileDirectory)
        pngDirectory = f'./polls/{serverID}/{nrOfActivePolls+1}.png'
        renderPM.drawToFile(drawing, pngDirectory, fmt='PNG')
        img = Image.open(pngDirectory)
        I1 = ImageDraw.Draw(img)
        I1.text((610,590),"Poll Updates Every: 5 Minutes",fill=(153, 170, 181))
        img.save(pngDirectory)
        url = await self.GetSendChannel(pngDirectory)
        message = await channel.send(content=url)
        for i in range(len(choices)):
            await message.add_reaction(reactions[i])
        async with asqlite.connect("./databases/polls.db") as connection:
            async with connection.cursor() as c:
                query = f"INSERT INTO a{serverID} VALUES (?,?,?,?,?,?,?,?,?)"
                await c.execute(query, (serverID, channel.id, message.id,nrOfActivePolls+1,polltitle,charttype,",".join(choices),",".join(str(v) for v in numbersList),style))
                await connection.commit()

#-----------------------------------------------------------

    @app_commands.command(description="End a poll and show the final result.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.checks.has_permissions(administrator=True)
    async def pollend(self, interaction : discord.Interaction, pollid : int):
        await interaction.response.defer()
        async def MakePoll():
            discordStyle = Style(
                            background='#36393f',
                            plot_background='#23272a',
                            foreground='#99aab5',
                            foreground_strong='#ffffff',
                            foreground_subtle='#99aab5',
                            opacity='.6',
                            opacity_hover='.9',
                            title_font_size=25,
                            legend_font_size=15,
                            transition='400ms ease-in',
                            colors=('#7289da', '#ffffff', '#b9bbbe', '#7289da', '#ffffff', '#b9bbbe', '#7289da', '#ffffff', '#b9bbbe',)
                        )
            match poll[5].lower():
                case 'line':
                    chart = pygal.Line(print_values=True,style=discordStyle,title=poll[4])
                case 'bar':
                    match poll[8].lower():
                        case "basic":
                            chart = pygal.Bar(print_values=True,style=discordStyle,title=poll[4])
                        case "stacked":
                            chart = pygal.StackedBar(print_values=True,style=discordStyle,title=poll[4])
                        case "horizontal":
                            chart = pygal.HorizontalBar(print_values=True,style=discordStyle,title=poll[4])
                        case _:
                            chart = pygal.Bar(print_values=True,style=discordStyle,title=poll[4])
                case 'pie':
                    if poll[8]:
                        chart = pygal.Pie(print_values=True,style=discordStyle,title=poll[4],inner_radius=float(poll[8]))
                    else:
                        chart = pygal.Pie(print_values=True,style=discordStyle,title=poll[4])
                case _:
                    chart = pygal.Bar(print_values=True,style=discordStyle,title=poll[4])
            print(poll[6])
            choices = poll[6].split(",")
            print(choices)
            if poll[5].lower() == "line":
                votes = ast.literal_eval(poll[7])
                for i in range(len(choices)):
                    print(votes[i])
                    chart.add(choices[i], votes[i])
            else:
                votes = poll[7].split(",")
                print(votes)
                for i in range(len(choices)):
                    chart.add(choices[i], [int(votes[i])])
            fileDirectory = f'./polls/{poll[0]}/{poll[3]}.svg'
            chart.render_to_file(fileDirectory)
            drawing = svg2rlg(fileDirectory)
            os.remove(fileDirectory)
            pngDirectory = f'./polls/{poll[0]}/{poll[3]}.png'
            renderPM.drawToFile(drawing, pngDirectory, fmt='PNG')
            return pngDirectory

        serverID = interaction.guild_id
        async with asqlite.connect("./databases/polls.db") as connection:
            async with connection.cursor() as c:
                query = f"SELECT * FROM a{serverID} WHERE poll_id = ?"
                await c.execute(query, (pollid,))
                poll = await c.fetchone()
                if poll:
                    query = f"DELETE FROM a{serverID} WHERE poll_id = ?"
                    await c.execute(query, (pollid,))
                else:
                    embedMissingPoll = discord.Embed(colour=discord.Colour.red(), title="No poll with that id found")
                    await interaction.response.send_message(embed=embedMissingPoll)
                    return
        guildObject = await self.client.fetch_guild(poll[0])
        channel = await guildObject.fetch_channel(poll[1])
        message = await channel.fetch_message(poll[2])
        choices = poll[6].split(",")
        votes = ast.literal_eval(poll[7])
        votes = list(votes)
        biggestVote = max(votes)
        if votes.count(biggestVote) > 1:
            indices = [i for i,x in enumerate(votes) if x == biggestVote]
            outStr = "Poll Results:\nWe have a tie between "
            if len(indices) > 2:
                for i in range(0,len(indices)-1):
                    outStr += f"{choices[i]}, "
                outStr += f"and {choices[indices[len(indices)]]} with {biggestVote} votes."
            else:
                outStr += f"{choices[0]} and {choices[1]} with {biggestVote} votes."
        else:
            index = votes.index(biggestVote)
            outStr = f"Poll Results:\nThe winning selection is **{choices[index]}** with **{biggestVote}** votes."

        pngDirectory = await MakePoll()
        await message.delete()
        await channel.send(content=outStr,file=discord.File(pngDirectory))
        await interaction.followup.send(content=f"Successfully ended poll with id of {pollid}")

#-----------------------------------------------------------

    @app_commands.command(description="List all the currently active polls")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def polllist(self, interaction : discord.Interaction):
        serverID = interaction.guild_id
        async with asqlite.connect("./databases/polls.db") as connection:
            async with connection.cursor() as c:
                query = f"SELECT * FROM a{serverID}"
                await c.execute(query)
                polls = await c.fetchall()
        if not polls:
            embedNoPolls = discord.Embed(colour=discord.Colour.blurple(), title=f"Polls for {interaction.guild.name}",description="No Polls Currently Active")
            await interaction.response.send_message(embed=embedNoPolls)
            return
        embedCurrentPolls = discord.Embed(colour=discord.Colour.random(),title=f"Polls for {interaction.guild.name}")
        counter = 1
        for poll in polls:
            embedCurrentPolls.add_field(name=f"Poll {counter}",value=f'ID: **{poll[3]}**\nTitle: **"{poll[4]}"**\nChart Type: **{poll[5]}**\nChoices: **{poll[6]}**')
        await interaction.response.send_message(embed=embedCurrentPolls)

#-----------------------------------------------------------

    #For adding reactions
    @app_commands.command(description="Add a reaction that the bot must listen for in order to assign roles.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.describe(channel="The channel in which the message is sent", messageid= "The ID of the reaction message", emoji="The emoji required for this reaction", role="The discord role to be received",mode="The mode of the reaction. (Toggle,Add,Remove)")
    @app_commands.checks.has_permissions(administrator=True)
    async def reactionroleadd(self, interaction : discord.Interaction, channel : discord.TextChannel, messageid : str, emoji : str, role : discord.Role, mode : str):
        """
        Add a reaction that the bot must listen for in order to assign roles.

        ### Usage:
            `-reactionadd [Channel] [Message ID] [Emoji] [Role]`
        
        ### Arguments:
            `channel`: A channel that you mention
            `message id`: The ID of the message that you want the bot to listen to
            `emoji`: The emoji you want the bot to listen for
            `role`: A role that you mention
            `mode`: The mode that the reaction role will play.
             > `add`: Only allows the role to be added.
             > `remove`: Only allows the role to be removed.
             > `toggle`: Allows the role to be added and removed.
        """
        serverID = interaction.guild.id
        channelID = channel.id
        roleID = role.id
        embedAddedRole = discord.Embed(colour=discord.Colour.green(),title=f"Successfully added {role.name} to the reaction {emoji}")
        match mode.upper():
            case 'ADD': type = 0
            case 'REMOVE': type = 1
            case 'TOGGLE': type = 2
        if type == None:
            embedFailed = discord.Embed(colour=discord.Colour.red(),title="Incorrect mode. Please try again")
            await interaction.response.send_message(embed=embedFailed)
            return()
        async with asqlite.connect("./databases/reaction_info.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""INSERT INTO reactions VALUES (?, ?, ?, ?, ?, ?)""",(serverID,channelID, messageid,emoji,roleID, type))
                await connection.commit()
        await interaction.response.send_message(embed=embedAddedRole)

#-----------------------------------------------------------

    #For showing all reactions currently active
    @app_commands.command(description="Shows all the messages and reactions that the bot is listening for")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.checks.has_permissions(administrator=True)
    async def reactionrolelist(self, interaction : discord.Interaction):
        """
        Shows all the messages and reactions that the bot is listening for

        **Usage:**
            `-reactionall`
        """
        def GetEmoji(emojiID):
            try:
                emoji = self.client.get_emoji(int(emojiID))
            except:
                emoji = reaction[3]
            return emoji
        
        def GetMode(mode):
            if mode == 0:
                return 'Add'
            elif mode == 1:
                return 'Remove'
            elif mode == 2:
                return 'Toggle'
            else: return 'Add'

        serverID = interaction.guild.id
        async with asqlite.connect("./databases/reaction_info.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM reactions WHERE server_id = ?""",(serverID,))
                results = await c.fetchall()
        embedCurrentReactions = discord.Embed(colour=discord.Colour.green())
        embedCurrentReactions.title = "These are the current reactions that are active"
        if len(results) == 0:
            embedNoReactions = discord.Embed(colour=discord.Colour.red(), title="There are currently no message that the bot is listening to right now.")
            await interaction.response.send_message(embed=embedNoReactions)
            return
        currentChannelID = results[0][1]
        currentMessageID = results[0][2]
        currentEmoji = results[0][3]
        currentRole = results[0][4]
        outString = ""
        for reaction in results:
            if currentMessageID == reaction[2] and reaction == results[len(results) - 1]:
                serverObject = self.client.get_guild(reaction[0])
                channelObject = await self.client.fetch_channel(reaction[1])
                message = await channelObject.fetch_message(reaction[2])
                messageUrl = message.jump_url
                emoji = GetEmoji(reaction[3])
                role = serverObject.get_role(reaction[4])
                type = GetMode(reaction[5])
                print(f"Adding {emoji} - {role.name} in if 1\n")
                outString += f"> {emoji} - {role.mention} ({type})\n"
                embedCurrentReactions.add_field(name="Active Reaction",value=f"Message in {channelObject.mention}. [Jump to message]({messageUrl})\n" + outString)
                outString = ""
                continue
            elif currentMessageID == reaction[2]:
                serverObject = self.client.get_guild(reaction[0])
                emoji = GetEmoji(reaction[3])
                role = serverObject.get_role(reaction[4])
                type = GetMode(reaction[5])
                print(f"Adding {emoji} - {role.name} in if 2\n")
                outString += f"> {emoji} - {role.mention} ({type})\n"
            elif currentMessageID != reaction[2] and reaction == results[len(results) - 1]:
                serverObject = self.client.get_guild(reaction[0])
                channelObject = await self.client.fetch_channel(currentChannelID)
                message = await channelObject.fetch_message(currentMessageID)
                messageUrl = message.jump_url
                emoji = GetEmoji(currentEmoji)
                role = serverObject.get_role(currentRole)
                #outString += f"> {emoji} - {role.mention}\n"
                embedCurrentReactions.add_field(name="Active Reaction",value=f"Message in {channelObject.mention}. [Jump to message]({messageUrl})\n" + outString)
                outString = ""
                serverObject = self.client.get_guild(int(reaction[0]))
                channelObject = await self.client.fetch_channel(reaction[1])
                message = await channelObject.fetch_message(reaction[2])
                messageUrl = message.jump_url
                emoji = GetEmoji(reaction[3])
                role = serverObject.get_role(reaction[4])
                type= GetMode(reaction[5])
                print(f"Adding {emoji} - {role.name} in if 3\n")
                outString += f"> {emoji} - {role.mention} ({type})\n"
                embedCurrentReactions.add_field(name="Active Reaction",value=f"Message in {channelObject.mention}. [Jump to message]({messageUrl})\n" + outString)
                continue
            elif currentMessageID != reaction[2]:
                serverObject = self.client.get_guild(reaction[0])
                channelObject = await self.client.fetch_channel(currentChannelID)
                message = await channelObject.fetch_message(currentMessageID)
                messageUrl = message.jump_url
                emoji = GetEmoji(currentEmoji)
                role = serverObject.get_role(currentRole)
                embedCurrentReactions.add_field(name="Active Reaction",value=f"Message in {channelObject.mention}. [Jump to message]({messageUrl})\n" + outString)
                outString = ""
                serverObject = self.client.get_guild(reaction[0])
                emoji = GetEmoji(reaction[3])
                role = serverObject.get_role(reaction[4])
                type = GetMode(reaction[5])
                outString += f"> {emoji} - {role.mention} ({type})\n"
                currentChannelID = reaction[1]
                currentMessageID = reaction[2]
                currentEmoji = reaction[3]
                currentRole = reaction[4]                
        await interaction.response.send_message(embed=embedCurrentReactions)

#-----------------------------------------------------------

    #For removing reactions
    @app_commands.command(description="Stop the bot from listening to a message for a reaction")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    @app_commands.describe(messageid = "The ID of the message listening for reactions or 'all' to remove all", emoji= "The emoji to remove the reaction of")
    @app_commands.checks.has_permissions(administrator=True)
    async def reactionroleremove(self, interaction : discord.Interaction, messageid : str, emoji :str = None):
        """
        Stop the bot from listening to a message for a reaction

        **Usage:**
            `-reactionremove [Message ID] Optional[Emoji]`
        
        **Arguments:**
            `message id`: The ID of the message that has the reaction
            `emoji`: The emoji that the bot is listening for. If none is given it defaults to remove all.
        """
        serverID = interaction.guild.id
        async with asqlite.connect("./databases/reaction_info.db") as connection:
            async with connection.cursor() as c:
                embedRemovedReaction = discord.Embed(colour=discord.Colour.green())
                if messageid.upper() == "ALL":
                    print("removing all")
                    await c.execute("""DELETE FROM reactions WHERE server_id = ?""", (serverID,))
                    await connection.commit()
                    await interaction.response.send_message(embed=embedRemovedReaction)
                    embedRemovedReaction.title = "Successfully removed all reactions for the server"
                    return
                if emoji:
                    if len(emoji) > 1:
                        newEmoji = (emoji.split(":")[2]).strip(">")
                        emoji = self.client.get_emoji(int(newEmoji))
                        emoji = emoji.id
                    try:
                        await c.execute("""DELETE FROM reactions WHERE server_id = ? and emoji_id = ? and message_id = ?""",(serverID,emoji,messageid))
                        await connection.commit()
                        embedRemovedReaction.title = "Successfully removed the reaction to do with that emoji"
                    except:
                        embedRemovedReaction.title = "No reaction listener found for that emoji."
                else:
                    await c.execute("""DELETE FROM reactions WHERE server_id = ? and message_id = ?""",(serverID,messageid))
                    await connection.commit()
                    embedRemovedReaction.title = "Successfully removed all reactions on that message"
        await interaction.response.send_message(embed=embedRemovedReaction)

#-----------------------------------------------------------

    #For version of bot
    @app_commands.command(description="Shows the current version of the bot.")
    @app_commands.guilds(discord.Object(id = 767324204390809620))
    async def version(self, interaction : discord.Interaction):
        """
        Shows the current version of the bot.

        **Usage:**
            `-version`
        """
        await interaction.response.send_message("Currently version 0.0.9")

#-----------------------------------------------------------

    @tasks.loop(minutes=5)
    async def UpdatePolls(self):
        async with asqlite.connect("./databases/polls.db") as connection:
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
                    for poll in results:
                        reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
                        discordStyle = Style(
                            background='#36393f',
                            plot_background='#23272a',
                            foreground='#99aab5',
                            foreground_strong='#ffffff',
                            foreground_subtle='#99aab5',
                            opacity='.6',
                            opacity_hover='.9',
                            title_font_size=25,
                            legend_font_size=15,
                            transition='400ms ease-in',
                            colors=('#7289da', '#ffffff', '#b9bbbe', '#7289da', '#ffffff', '#b9bbbe', '#7289da', '#ffffff', '#b9bbbe',)
                        )
                        match poll[5].lower():
                            case 'line':
                                chart = pygal.Line(print_values=True,style=discordStyle,title=poll[4])
                            case 'bar':
                                match poll[8].lower():
                                    case "basic":
                                        chart = pygal.Bar(print_values=True,style=discordStyle,title=poll[4])
                                    case "stacked":
                                        chart = pygal.StackedBar(print_values=True,style=discordStyle,title=poll[4])
                                    case "horizontal":
                                        chart = pygal.HorizontalBar(print_values=True,style=discordStyle,title=poll[4])
                                    case _:
                                        chart = pygal.Bar(print_values=True,style=discordStyle,title=poll[4])
                            case 'pie':
                                if poll[8]:
                                    chart = pygal.Pie(print_values=True,style=discordStyle,title=poll[4],inner_radius=float(poll[8]))
                                else:
                                    chart = pygal.Pie(print_values=True,style=discordStyle,title=poll[4])
                            case _:
                                chart = pygal.Bar(print_values=True,style=discordStyle,title=poll[4])
                        print(poll[6])
                        choices = poll[6].split(",")
                        print(choices)
                        if poll[5].lower() == "line":
                            votes = ast.literal_eval(poll[7])
                            for i in range(len(choices)):
                                print(votes[i])
                                chart.add(choices[i], votes[i])
                        else:
                            votes = poll[7].split(",")
                            print(votes)
                            for i in range(len(choices)):
                                chart.add(choices[i], [int(votes[i])])
                        fileDirectory = f'./polls/{poll[0]}/{poll[3]}.svg'
                        chart.render_to_file(fileDirectory)
                        drawing = svg2rlg(fileDirectory)
                        os.remove(fileDirectory)
                        pngDirectory = f'./polls/{poll[0]}/{poll[3]}.png'
                        renderPM.drawToFile(drawing, pngDirectory, fmt='PNG')
                        img = Image.open(pngDirectory)
                        I1 = ImageDraw.Draw(img)
                        I1.text((610,590),"Poll Updates Every: 5 Minutes",fill=(153, 170, 181))
                        img.save(pngDirectory)
                        guildObject = await self.client.fetch_guild(poll[0])
                        channel = await guildObject.fetch_channel(poll[1])
                        message = await channel.fetch_message(poll[2])
                        url = await self.GetSendChannel(pngDirectory)
                        await message.edit(content=url)

    @tasks.loop(time=time(10,00,00,tzinfo=ZoneInfo("Africa/Johannesburg")))
    async def my_loop(self):
        print('Checking Birthdays')
        async with asqlite.connect("./databases/user_birthdays.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""SELECT * FROM settings WHERE activated = 1""")
                resultsActive = await c.fetchall()
                if len(resultsActive) > 0:
                    for activeServer in resultsActive:
                        await c.execute("""SELECT * FROM users WHERE server_id = ?""",(activeServer[0],))
                        results = await c.fetchall()
                        currentDate = date.today().strftime("%m-%d")
                        for result in results:
                            print(result[2][5:] == currentDate)
                            if result[2][5:] == currentDate:
                                birthdayChannel = self.client.get_channel(activeServer[1])
                                print(birthdayChannel)
                                user = await self.client.fetch_user(result[1])
                                embedBirthday = discord.Embed(colour=user.accent_colour)
                                embedBirthday.title = f"It is currently {user.display_name}'s birthday!"
                                embedBirthday.description = "Please wish them a happy birthday!"
                                embedBirthday.set_image(url=user.avatar.url)
                                await birthdayChannel.send(embed=embedBirthday)
    
    async def GetSendChannel(self,png):
        serverObject = await self.client.fetch_guild(767324204390809620)
        channelObject = await serverObject.fetch_channel(1048277257115930634)
        message = await channelObject.send(file=discord.File(png))
        url = message.attachments[0].url
        print(url)
        return url

#-----------------------------------------------------------
# Side Function

#-----------------------------------------------------------
# Setup

async def setup(client):
    await client.add_cog(Utility(client))