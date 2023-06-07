import sqlite3
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import cooldown, BucketType
from sqlite3 import connect
import random
import math
import datetime
import asyncio
import asqlite
from asyncio import sleep
from typing import Literal, Optional, Union

class Economy(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog: "Economy" loaded.')

#-----------------------------------------------------------

    #For adding balance
    @commands.command(hidden=True)
    @commands.is_owner()
    async def addBalance(self,ctx,member : discord.Member, amount : int):
        """
        Add or remove Thonks to or from a user's account.

        :param ctx: The context of the message
        :param discord.Member member: The member to which you are altering the account of
        :param int amount: The amount to add or remove from the account
        """
        if ctx.author.id == 222224934359793674:
            async with asqlite.connect("./databases/user_info.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""UPDATE user_info SET balance = balance + ? WHERE user_id = ?""", (amount, member.id))
                    await connection.commit()
            embedAddedThonks = discord.Embed(colour=discord.Colour.blurple(),title=f"Successfully added {amount} <:Thonks:768191131820883978> thonks to {member.display_name}'s account")
            await ctx.send(embed=embedAddedThonks)

#-----------------------------------------------------------

    #For balance commands
    @app_commands.command(description="Shows the current balance of you or another user.")
    @app_commands.describe(member="The user you want the balance of. Leave blank for yourself.")
    async def balance(self, interaction : discord.Interaction, member: Union[None,discord.Member]):
        """
        Shows the current balance of you or another user.

        :param discord.Interaction interaction: The interaction context of the message
        :param Union[None, discord.Member] member: The member you wish to see the balance of. Set to None if no one is given
        """
        if member == None:
            member = interaction.user
        authorID = member.id
        authorName = member.display_name
        result = await MemberHasAccount(member)
        async with asqlite.connect("./databases/user_info.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""UPDATE user_info SET username = ? WHERE user_id = ?""",(authorName, authorID))
                await connection.commit()
        embed_balance = discord.Embed(
            colour= discord.Colour.green(),
            title= f"{authorName}'s Balance"
        )
        formatted = (f'{result[2]:,}').replace(","," ")
        embed_balance.add_field(name="Balance",value=f"{formatted} <:Thonks:768191131820883978> thonks")
        await interaction.response.send_message(embed=embed_balance)

#-----------------------------------------------------------

    #For beg command
    @app_commands.command(description="Beg for some money.")
    @app_commands.checks.cooldown(rate=1, per=7200)
    async def beg(self, interaction : discord.Interaction):
        """
        Beg for some money.

        :param discord.Interaction interaction: The interaction context of the message
        
        :raises app_commands.CommandOnCooldown: When the command has been used recently and is on a cooldown
        """
        authorID = interaction.user.id
        authorName = interaction.user.display_name
        userAcc = await UserHasAccount(interaction)
        earned = GenerateRandomNumber(0,100)
        if earned == 0:
            embed_beg = discord.Embed(
                colour= discord.Colour.red(),
                title= f"{authorName}. You begged and earned nothing!"
            )
            await interaction.response.send_message(embed=embed_beg)
        else:
            async with asqlite.connect("./databases/user_info.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("UPDATE user_info SET balance = ? + balance, username = ? WHERE user_id = ?",(earned, authorName, authorID))
                    await connection.commit()
            embed_beg = discord.Embed(
                colour= discord.Colour.green())
            embed_beg.title = f"{authorName}. You begged and earned {earned}<:Thonks:768191131820883978> thonks!"
        await interaction.response.send_message(embed=embed_beg)
    @beg.error
    async def beg_error(self,interaction,error):
        if isinstance(error,app_commands.CommandOnCooldown):
            time = error.retry_after
            formatted_time = str(datetime.timedelta(seconds=time))
            hours,minutes,seconds = formatted_time.split(":",2)
            seconds = str(math.floor(float(seconds)))
            out_time = ''
            if int(hours) > 0:
                out_time += f"{hours} hours, {minutes} minutes and {seconds} seconds"
            elif int(hours) == 0 and int(minutes) > 0:
                out_time += f"{minutes} minutes and {seconds} seconds"
            elif int(hours) == 0 and int(minutes) == 0:
                out_time += f"{seconds} seconds"
            embed_on_cooldown = discord.Embed(
                colour= discord.Colour.red(),
                title= f"That command is curently on cooldown. Try again in {out_time}"
            )
            await interaction.response.send_message(embed=embed_on_cooldown)

#-----------------------------------------------------------

    #For leaderboard command
    @app_commands.command(description="Shows the leaderboard for the highest amount of thonks")
    async def leaderboard(self, interaction : discord.Interaction):
        """Check the leaderboard for who has the highest amount of Thonks
        
        :param discord.Interaction interaction: The interaction context of the message
        """
        serverObject = interaction.guild
        async with asqlite.connect("./databases/user_info.db") as connection:
            async with connection.cursor() as c:
                leaderboard = []
                for member in serverObject.members:
                    await c.execute("""SELECT * from user_info WHERE user_id = ?""",(member.id,))
                    account = await c.fetchone()
                    if account != None:
                        leaderboard.append(account)
                embedLeaderboard = discord.Embed(colour=discord.Colour.random(),title=f"Leaderboard for {serverObject.name}")
                for i in range(len(leaderboard) - 1):
                    for j in range(i + 1, len(leaderboard)):
                        if leaderboard[i][2] < leaderboard[j][2]:
                            hold = leaderboard[i]
                            leaderboard[i] = leaderboard[j]
                            leaderboard[j] = hold
        print(leaderboard)
        outStr = ""
        for i in range(len(leaderboard)):
            if i <= 10:
                if i == 0:
                    topUser = await serverObject.fetch_member(leaderboard[i][0])
                    embedLeaderboard.set_thumbnail(url=topUser.avatar.url)
                temp = "**#" + str(i + 1) + "** - " + str(leaderboard[i][1]) + " - " + str(leaderboard[i][2]) + "<:Thonks:768191131820883978>"
                outStr += temp + "\n"
        outStr.rstrip("\n")
        embedLeaderboard.add_field(name="Placements",value=outStr)
        await interaction.response.send_message(embed=embedLeaderboard)       

#-----------------------------------------------------------

    #For give command
    @app_commands.command(description="Give someone some money. Well aren't you charitable.")
    @app_commands.describe(member="The member you wish to give <:Thonks:768191131820883978> thonks to", amount="The amount of <:Thonks:768191131820883978> thonks to give.")
    async def give(self, interaction : discord.Interaction, member : discord.Member, amount : int):
        """
        Give someone some money. Well aren't you charitable.

        :param discord.Interaction interaction: The interaction context of the message
        :param discord.Member member: The person you wish to give Thonks to
        :param int amount: The amount of Thonks you wish to give
        """
        authorID = interaction.user.id
        authorName = interaction.user.display_name
        memberID = member.id
        memberName = member.display_name


        if amount < 0:
            print("Under 0 money")
            embed_negative = discord.Embed(
                colour= discord.Colour.blue(),
                title= "Cannot use negative <:Thonks:768191131820883978> thonks."
            )
            await interaction.response.send_message(embed=embed_negative)
            return
        
        if authorName == member.display_name or authorID == memberID:
            embed_same_user = discord.Embed(
                colour= discord.Colour.blue(),
                title= "Cannot give to yourself. Baka"  #<:PikachuFacePalm:1018876989089792131>
            )
            embed_same_user.set_image(url="https://cdn.discordapp.com/emojis/1018876989089792131.webp")
            await interaction.response.send_message(embed=embed_same_user)
            return


        print(f"Name: {authorName}\nID: {authorID}\nMember Name: {memberName}\nMember ID: {memberID}")

        userResult = await UserHasAccount(interaction)
        memberResult = await MemberHasAccount(member)

        if userResult[2] < amount:
            embed_not_enough = discord.Embed(
                colour= discord.Colour.blue(),
                title= "You cannot give more than you have, dummy!"
            )
            await interaction.response.send_message(embed=embed_not_enough)
            return

        await RemoveBalanceUser(interaction,amount)
        await AddBalanceMember(member, amount)

        embed_give = discord.Embed(
            colour= discord.Colour.blue(),
            title= f"**{authorName}** gave **{memberName}** {str(amount)}<:Thonks:768191131820883978> thonks"
        )
        await interaction.response.send_message(embed=embed_give)

#-----------------------------------------------------------

    #For steal command
    def StealReset(interaction : discord.Interaction):
        return app_commands.Cooldown(1,3600)

    @app_commands.command(description="Try and steal some money from someone. Ooo he stealin'!")
    @app_commands.describe(member="The member you wish to steal from.")
    @app_commands.checks.dynamic_cooldown(factory=StealReset, key=lambda i: (i.guild_id, i.user.id))
    async def steal(self, interaction : discord.Interaction, member : discord.Member):
        """
        Try and steal some money from someone. Ooo he stealin'!

        :param discord.Interaction interaction: The interaction context of the message
        :param discord.Member member: The persony you wish to steal from

        :raises app_commands.CommandOnCooldown: When the command has already been used recently and is on cooldown
        """
        def check(m):
            return m.author == member and m.content.upper() == "STOP! THIEF"

        def has_been_stolen_from(member):
            if member.id in lastStolenFrom:
                return True
            return False

        def check_same_user(user_id,member):
            if user_id == member.id:
                return True
            return False

        def backfired():
            backfire_chance = random.randint(0,100)
            # if flag_has_trap:
            #     backfire_chance += 5
            # if flag_has_golden_trap:
            #     backfire_chance += 8
            if backfire_chance <= 40:
                return True
            return False

        # def remove_item_uses(item,servers,server,user_id,):
        #     item[1] = item[1] - 1
        #     amount_left = item[1]
        #     if item[1] == 0:
        #         servers[str(server)]["Equipped"][str(user_id)].clear()
        #     else:
        #         servers[str(server)]["Equipped"][str(user_id)] = item
        #     with open("./inventory.json","w") as f:
        #         json.dump(servers,f,indent=4)
        #     return amount_left

        authorID = interaction.user.id
        authorName = interaction.user.display_name
        memberID = member.id
        memberName = member.display_name
        serverID = interaction.guild.id

        percent_steals = [0.14,0.15,0.152,0.154,0.156,0.158,0.16,0.162,0.164,0.17,0.18,0.19,0.2]

        if has_been_stolen_from(member):
            embed_stolen_from = discord.Embed(
                colour= int("f2873a",16),
                title=f"{member.display_name} has been stolen from recently and has immunity"
            )
            await interaction.response.send_message(embed=embed_stolen_from)
            stealCooldown.reset()
            return

        if check_same_user(authorID,member):
            embed_same_user = discord.Embed(
                colour= discord.Colour.red(),
                title= "Cannot steal from yourself, dummy!"
            )
            await interaction.response.send_message(embed=embed_same_user)
            stealCooldown.reset()
            return

        authorResult = await UserHasAccount(interaction)
        memberResult = await MemberHasAccount(member)

        print(memberResult)
        print(authorResult)

        if memberResult[2] <= 0:
            embed_has_no_money = discord.Embed(
                colour= discord.Colour.red(),
                title= f"{memberName} has no thonks <:Thonks:768191131820883978> to steal"
            )
            await interaction.response.send_message(embed=embed_has_no_money)
            stealCooldown.reset()
            return
        embed_steal = discord.Embed(
            colour= int('eb9534',16),
            title= f"{authorName} is trying to steal some of your thonks<:Thonks:768191131820883978>!\nRespond with 'Stop! Thief' within the next 30 seconds to stop them!"
        )
        print("trying to send")
        await interaction.response.send_message(member.mention)
        followup = interaction.followup
        message = await followup.send(embed=embed_steal)
        print(type(message))
        try:
            await self.client.wait_for('message',timeout=30.0,check=check)
            embed_stopped = discord.Embed(
                colour= int('33e85a',16),
                title= f"{authorName} has been stopped! Your thonks are safe"
            )
            await message.edit(embed=embed_stopped)
            if backfired():
                fine_amount = random.randint(5,10)
                fine_amount /= 100
                amount_lost = math.floor(authorResult[2] * fine_amount)
                async with asqlite.connect("./databases/user_info.db") as connection:
                    async with connection.cursor() as c:
                        await c.execute("""UPDATE user_info SET balance = balance - ? WHERE user_id = ?""",(amount_lost, authorID))
                        await connection.commit()
                embed_backfire = discord.Embed(
                    colour= discord.Colour.blurple(),
                    title=f"{interaction.user.display_name} you were caught and had to pay {str(amount_lost)} thonks<:Thonks:768191131820883978> bail to be released from jail"
                    )
                await sleep(3)
                await message.edit(embed=embed_backfire)
        except asyncio.TimeoutError:
            steal_percent = random.choice(percent_steals)
            amount_stolen = math.floor(memberResult[2] * steal_percent)
            async with asqlite.connect("./databases/user_info.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""UPDATE user_info SET balance = balance - ? WHERE user_id = ?""",(amount_stolen, memberID))
                    await c.execute("""UPDATE user_info SET balance = balance + ? WHERE user_id = ?""",(amount_stolen, authorID))
                    await connection.commit()
            embed_stolen = discord.Embed(
                colour= int('ed2147',16),
                title= f"{interaction.user.name} has stolen {amount_stolen}<:Thonks:768191131820883978> from {member.name}"
            )
            lastStolenFrom.append(member.id)
            if len(lastStolenFrom) > 2:
                lastStolenFrom.pop(0)
            await message.edit(embed=embed_stolen)
    @steal.error
    async def steal_error(self,interaction,error):
        if isinstance(error,app_commands.CommandOnCooldown):
            time = error.retry_after
            formatted_time = str(datetime.timedelta(seconds=time))
            hours,minutes,seconds = formatted_time.split(":",2)
            seconds = str(math.floor(float(seconds)))
            out_time = ''
            if int(hours) > 0:
                out_time += f"{hours} hours, {minutes} minutes and {seconds} seconds"
            elif int(hours) == 0 and int(minutes) > 0:
                out_time += f"{minutes} minutes and {seconds} seconds"
            elif int(hours) == 0 and int(minutes) == 0:
                out_time += f"{seconds} seconds"
            embed_on_cooldown = discord.Embed(
                colour= discord.Colour.red(),
                title= f"That command is curently on cooldown. Try again in {out_time}"
            )
            await interaction.response.send_message(embed=embed_on_cooldown)
        else:
            raise error

# Side Functions

def GenerateRandomNumber(startNr, endNr):
    return random.randrange(startNr, endNr)
  
async def MakeUserAccount(c, authorID, authorName):
    await c.execute("""INSERT INTO user_info VALUES (?,?,0)""",(authorID, authorName))

async def UserHasAccount(ctx):
    authorID = ctx.user.id
    authorName = ctx.user.display_name
    async with asqlite.connect("./databases/user_info.db") as connection:
        async with connection.cursor() as c:
            await c.execute(f"SELECT * FROM user_info WHERE user_id = {authorID}")
            result = await c.fetchone()
            if result == None:
                await MakeUserAccount(c, authorID, authorName)
                await connection.commit()
            await c.execute(f"SELECT * FROM user_info WHERE user_id = {authorID}")
            result = await c.fetchone()
    return result

async def MemberHasAccount(member: discord.Member):
    authorID = member.id
    authorName = member.display_name
    async with asqlite.connect("./databases/user_info.db") as connection:
        async with connection.cursor() as c:
            await c.execute(f"SELECT * FROM user_info WHERE user_id = {authorID}")
            result = await c.fetchone()
            if result == None:
                await MakeUserAccount(c, authorID, authorName)
            await connection.commit()
            await c.execute(f"SELECT * FROM user_info WHERE user_id = {authorID}")
            result = await c.fetchone()
    return result

async def RemoveBalanceUser(ctx, amount):
    authorID = ctx.user.id
    authorName = ctx.user.display_name
    async with asqlite.connect("./databases/user_info.db") as connection:
        async with connection.cursor() as c:
            await c.execute("""UPDATE user_info SET username = ?, balance = balance - ? WHERE user_id = ?""", (authorName, amount, authorID))
            await connection.commit()

async def AddBalanceMember(member: discord.Member, amount):
    memberID = member.id
    memberName = member.display_name
    async with asqlite.connect("./databases/user_info.db") as connection:
        async with connection.cursor() as c:
            await c.execute("""UPDATE user_info SET username = ?, balance = balance + ? WHERE user_id = ?""", (memberName, amount, memberID))
            await connection.commit()

#-----------------------------------------------------------
# Side variables

stealCooldown = app_commands.Cooldown(1,3600)

lastStolenFrom = []

#-----------------------------------------------------------
# Setup

async def setup(client):
    await client.add_cog(Economy(client))