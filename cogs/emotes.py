from pydoc import describe
from typing import Optional, Union
import discord
from discord import app_commands
import os
import random
from discord.ext import commands

class Emotes(commands.Cog):

    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog: "Emote Commands" loaded')
    
    @app_commands.command(description="Let people know you are mad with this command.")
    @app_commands.describe(member="A person that you mention")
    async def angry(self, interaction : discord.Interaction, member : Optional[discord.Member]):
        """
        Let people know you are mad with this command.

        :param discord.Interaction interaction: The interaction context of the message
        :param Optional[discord.Member] member: The person that you're angry at
        """
        username = interaction.user.display_name
        files = ["https://media.giphy.com/media/PjhjAtBWgWfg7Uuewj/giphy.gif",
                "https://media.giphy.com/media/qKce8CkhmQj0eox6nh/giphy.gif",
                "https://media.giphy.com/media/nHQUx3EuzwHJsJReHQ/giphy.gif",
                "https://media.giphy.com/media/v9pWKZIjzPGpZ03D9l/giphy.gif",
                "https://media.giphy.com/media/uBhOptavYKDdcV3kJs/giphy.gif"]
        
        embed_angry = discord.Embed(colour= discord.Colour.blue())
        if member:
            embed_angry.set_author(name=f'{username} is angry with {member.display_name}')
        else:
            embed_angry.set_author(name=f'{username} is angry')
        embed_angry.set_image(url=random.choice(files))
        await interaction.response.send_message(embed=embed_angry)


    @app_commands.command(description="Let people know you are blushing with this command.")
    async def blush(self, interaction : discord.Interaction):
        """
        Let people know you are blushing with this command.

        :param discord.Interaction interaction: The interaction context of the message
        """
        username = interaction.user.display_name
        files = ["https://media.giphy.com/media/LrjU8kGYXDAV9kTZqV/giphy.gif",
                "https://media.giphy.com/media/70RXxna7GdlAq69qY1/giphy.gif",
                "https://media.giphy.com/media/kmD3y0fhsO0TNEQfy8/giphy.gif",
                "https://media.giphy.com/media/5vG6aDYSN78h2rMCvl/giphy.gif"]                

        embed_blush = discord.Embed(colour= discord.Colour.blue())
        embed_blush.set_author(name=f'{username} is blushing')
        embed_blush.set_image(url=random.choice(files))
        await interaction.response.send_message(embed=embed_blush)


    @app_commands.command(description="Let people know you are confused with this command.")
    async def confused(self,interaction : discord.Interaction):
        """
        Let people know you are confused with this command.

        :param discord.Interaction interaction: The interaction context of the message
        """
        username = interaction.user.display_name
        files = ["https://media.giphy.com/media/kxwswQcCHd8khvE5YB/giphy.gif",
                "https://media.giphy.com/media/XTP0x2WfzV15OOpPM6/giphy.gif"]
        
        embed_confused = discord.Embed(colour= discord.Colour.blue())
        embed_confused.set_author(name=f'{username} is confused')
        embed_confused.set_image(url=random.choice(files))
        await interaction.response.send_message(embed=embed_confused)


    @app_commands.command(description="Let people know you are crying with this command.")
    async def cry(self,interaction : discord.Interaction):
        """
        Let people know you are crying with this command.

        :param discord.Interaction interaction: The interaction context of the message
        """
        username = interaction.user.display_name
        files = ["https://media.giphy.com/media/2JVkxXoEamKPpvHYlP/giphy.gif",
                "https://media.giphy.com/media/V9LTDeEXSena0Ew1K3/giphy.gif"]
        
        embed_cry = discord.Embed(colour= discord.Colour.blue())
        embed_cry.set_author(name=f'{username} is crying')
        embed_cry.set_image(url=random.choice(files))
        await interaction.response.send_message(embed=embed_cry)


    @app_commands.command(description="Let people know you are fighting with someone with this command.")
    @app_commands.describe(member="A person that you mention")
    async def hit(self, interaction : discord.Interaction, member : discord.Member):
        """
        Let people know you are fighting with someone with this command.

        :param discord.Interaction interaction: The interaction context of the message
        :param discord.Member member: The person that you wish to hit
        """
        username = interaction.user.display_name
        files = ["https://media.giphy.com/media/Lc0P5azCK0JbaywNp1/giphy.gif",
                "https://media.giphy.com/media/Fjag5IT747Da0SxROS/giphy.gif",
                "https://media.giphy.com/media/CjpvIMamM8aNu0tttC/giphy.gif",
                "https://media.giphy.com/media/443EGHY9ypaQdpzql7/giphy.gif",
                "https://media.giphy.com/media/7tnVNW3MUuRrsMevy9/giphy.gif",
                "https://media.giphy.com/media/5EWKozaaCytyxYyGdU/giphy.gif"]

        embed_hit = discord.Embed(colour= discord.Colour.blue())
        embed_hit.set_author(name=f'{username} hits {member.display_name}')
        embed_hit.set_image(url=random.choice(files))
        await interaction.response.send_message(embed=embed_hit)    


    @commands.command(description="Let people know you are hugging someone with this command.")
    @app_commands.describe(member="A person that you mention")
    async def hug(self, interaction : discord.Interaction, member : discord.Member):
        """
        Let people know you are hugging someone with this command.

        :param discord.Interaction interaction: The interaction context of the message
        :param Optional[discord.Member] member: The person that you wish to hug
        """
        username = interaction.user.display_name
        files = ["https://media.giphy.com/media/HaAbFJBM6kqzoYeNpS/giphy.gif",
                "https://media.giphy.com/media/NFf1EeMk1m8wzTQALT/giphy.gif",
                "https://media.giphy.com/media/4LOG4frft43k2ATPSG/giphy.gif",
                "https://media.giphy.com/media/xNdBscibKMHrmQZMYn/giphy.gif",
                "https://media.giphy.com/media/IMHXCXmuE3Fir9Bf0a/giphy.gif"]
        
        embed_hug = discord.Embed(colour= discord.Colour.blue())
        embed_hug.set_author(name=f'{username} hugs {member.display_name}')
        embed_hug.set_image(url=random.choice(files))
        await interaction.response.send_message(embed=embed_hug)   


    @commands.command(description="Let people know you are laughing with this command.")
    @app_commands.describe(member="A person that you mention")
    async def laugh(self, interaction : discord.Interaction, member : Optional[discord.Member]):
        """
        Let people know you are laughing with this command.

        :param discord.Interaction interaction: The interaction context of the message
        :param Optional[discord.Member] member: The person that you're laughing at or with
        """
        username = interaction.user.display_name
        files = ["https://media.giphy.com/media/stI3O70wGemn0B8SFS/giphy.gif",
                "https://media.giphy.com/media/0L0eT7Fhs7TJGQhgw3/giphy.gif",
                "https://media.giphy.com/media/Lebf0yEcxDT0q81Uyb/giphy.gif"]

        embed_laugh = discord.Embed(colour= discord.Colour.blue())
        if member:
            embed_laugh.set_author(name=f'{username} laughs at {member.display_name}')
        else:
            embed_laugh.set_author(name=f'{username} laughs')
        embed_laugh.set_image(url=random.choice(files))
        await interaction.response.send_message(embed=embed_laugh)


    @app_commands.command(description="Let people know you are thinking lewd thoughts with this command.")
    @app_commands.describe(member="A person that you mention")
    async def lewd(self,interaction : discord.Interaction,member : Optional[discord.Member]):
        """
        Let people know you are thinking lewd thoughts with this command.

        :param discord.Interaction interaction: The interaction context of the message
        :param Optional[discord.Member] member: The person that you're being lewd with
        """
        username = interaction.user.display_name
        files = ["https://media.giphy.com/media/IRTWvrl0OX0vBI81kz/giphy.gif",
                "https://media.giphy.com/media/bluyPrNSjdLbHKdiYi/giphy.gif",
                "https://media.giphy.com/media/ulrYrRNEmsjxVZKywS/giphy.gif",
                "https://media.giphy.com/media/NVEQpwtfNLlDy6v5jE/giphy.gif",
                "https://media.giphy.com/media/468yTVZX7YflyEyuoM/giphy.gif"]
        
        embed_lewd = discord.Embed(colour= discord.Colour.blue())
        if member:
            embed_lewd.set_author(name=f'{username} is doing lewd things with {member.display_name}')
        else:
            embed_lewd.set_author(name=f'{username} is doing lewd things')
        embed_lewd.set_image(url=random.choice(files))
        await interaction.response.send_message(embed=embed_lewd)


    @app_commands.command(description="Let people know you are petting someone with this command.")
    @app_commands.describe(member="A person that you mention")
    async def pet(self, interaction : discord.Interaction, member : discord.Member):
        """
        Let people know you are petting someone with this command.

        :param discord.Interaction interaction: The interaction context of the message
        :param discord.Member member: The person that you're petting
        """
        username = interaction.user.display_name
        files = ["https://media.giphy.com/media/kx044uERaEJ18AyuxO/giphy.gif",
                "https://media.giphy.com/media/HHV8YHufSeN6irJiFM/giphy.gif",
                "https://media.giphy.com/media/6tpsFIaEaKdxX8MULa/giphy.gif",
                "https://media.giphy.com/media/vVjSL8xzhi953ydr12/giphy.gif",
                "https://media.giphy.com/media/eGGtRrrwuLtRFEgGO1/giphy.gif",
                "https://media.giphy.com/media/fhRZhJbmyesDz9ZHHU/giphy.gif",
                "https://media.giphy.com/media/S69DBX8JhmN4cePsA8/giphy.gif",
                "https://media.giphy.com/media/5yFm5FUJP6UmjvCRpL/giphy.gif",
                "https://media.giphy.com/media/1fmoMsQNkYXstrllVn/giphy.gif"]

        embed_pet = discord.Embed(colour= discord.Colour.blue())
        embed_pet.set_author(name=f'{username} pets {member.display_name}')
        embed_pet.set_image(url=random.choice(files))
        await interaction.response.send_message(embed=embed_pet)  


    @app_commands.command(description="Let people know you are pouting with this command.")
    async def pout(self,interaction : discord.Interaction):
        """
        Let people know you are pouting with this command.

        :param discord.Interaction interaction: The interaction context of the message
        """
        username = interaction.user.display_name
        files = ["https://media.giphy.com/media/8puKwJmGeryCAsPSI6/giphy.gif",
                "https://media.giphy.com/media/5ByhqKfDw0VghSbFSH/giphy.gif",
                "https://media.giphy.com/media/R7t1erNnebxdhSqjYH/giphy.gif"]

        embed_pout = discord.Embed(colour= discord.Colour.blue())
        embed_pout.set_author(name=f'{username} is pouting')
        embed_pout.set_image(url=random.choice(files))
        await interaction.response.send_message(embed=embed_pout)        


    @app_commands.command(description="Let people know you are smiling with this command.")
    @app_commands.describe(member="A person that you mention")
    async def smile(self,interaction : discord.Interaction,member : Optional[discord.Member]):
        """
        Let people know you are smiling with this command.

        :param discord.Interaction interaction: The interaction context of the message
        :param Optional[discord.Member] member: The person that you're smiling at
        """
        username = interaction.user.display_name
        files = ["https://media.giphy.com/media/6q0WShKRhW2EbfwjOx/giphy.gif",
                "https://media.giphy.com/media/dcHdNKZ10OrKzeO5qx/giphy.gif",
                "https://media.giphy.com/media/6pH1kRgrAcHSoCDKnR/giphy.gif",
                "https://media.giphy.com/media/hZgOXPnHNZRJSUBlBg/giphy.gif",
                "https://media.giphy.com/media/ZFznJsbCP83D6cNf4n/giphy.gif",
                "https://media.giphy.com/media/kQLHIx1mm0xni0Ip3V/giphy.gif",
                "https://media.giphy.com/media/3NUFq5pJNn2IvVLAUw/giphy.gif",
                "https://media.giphy.com/media/omd8cOKyqaFvbc5I0B/giphy.gif",
                "https://media.giphy.com/media/iBfX6Ed2tAGt2aA2wH/giphy.gif",
                "https://media.giphy.com/media/RtnkHwB0H6wrv1CiuH/giphy.gif",
                "https://media.giphy.com/media/j3p5WNxmIaDrjnr9sd/giphy.gif"]
        
        embed_smile = discord.Embed(colour= discord.Colour.blue())
        if member:
            embed_smile.set_author(name=f'{username} smiles at {member.display_name}')
        else:
            embed_smile.set_author(name=f'{username} smiles')
        embed_smile.set_image(url=random.choice(files))
        await interaction.response.send_message(embed=embed_smile)


    @app_commands.command(description="Let people know you are waving with this command.")
    @app_commands.describe(member="A person that you mention")
    async def wave(self,interaction : discord.Interaction,member : Optional[discord.Member]):
        """
        Let people know you are waving with this command.

        :param discord.Interaction interaction: The interaction context of the message
        :param Optional[discord.Member] member: The person that you're waving to
        """
        username = interaction.user.display_name
        files = ["https://media.giphy.com/media/iuvRKADgBMXfqrfgdI/giphy.gif",
                "https://media.giphy.com/media/NL0mgMZDBuBugJQ1ti/giphy.gif"]

        embed_wave = discord.Embed(colour= discord.Colour.blue())
        if member:
            embed_wave.set_author(name=f'{username} waves to {member.display_name}')
        else:
            embed_wave.set_author(name=f'{username} waves')
        embed_wave.set_image(url=random.choice(files))
        await interaction.response.send_message(embed=embed_wave)


async def setup(client):
    await client.add_cog(Emotes(client))