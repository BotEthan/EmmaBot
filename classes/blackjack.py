import asyncio
import discord
import random
import asqlite

card_emoji_ids = ["<:1ofspades:1082365568750993428>", "<:2ofspades:1082365583712075848>", "<:3ofspades:1082365596873785436>", "<:4ofspades:1082365612606636202>", "<:5ofspades:1082365624614928444>", "<:6ofspades:1082365638078648430>", "<:7ofspades:1082365655388524544>", "<:8ofspades:1082365670903271524>", "<:9ofspades:1082365686560600114>", "<:10ofspades:1082365708228362360>", "<:11ofspades:1082365732337221683>", "<:12ofspades:1082365757045874769>", "<:13ofspades:1082617047688679475>", "<:1ofclubs:1082365556805619762>", "<:2ofclubs:1082365573691871293>", "<:3ofclubs:1082365587642142760>", "<:4ofclubs:1082365599558139995>", "<:5ofclubs:1082365614754123927>", "<:6ofclubs:1082365628503031818>", "<:7ofclubs:1082365641090142359>", "<:8ofclubs:1082365660530753618>", "<:9ofclubs:1082365675240165547>", "<:10ofclubs:1082365692755591241>", "<:11ofclubs:1082365714293325925>", "<:12ofclubs:1082617441584173137>", "<:13ofclubs:1082617670979043428>", "<:1ofhearts:1082365563122225162>", "<:2ofhearts:1082365580234997771>", "<:3ofhearts:1082365593174417500>", "<:4ofhearts:1082365608601063555>", "<:5ofhearts:1082365620793921536>", "<:6ofhearts:1082365634559606814>", "<:7ofhearts:1082365650980307015>", "<:8ofhearts:1082365668596383754>", "<:9ofhearts:1082365681649070080>", "<:10ofhearts:1082365703375552543>", "<:11ofhearts:1082365726863667230>", "<:12ofhearts:1082365750213357649>", "<:13ofhearts:1082618359826350140>", "<:1ofdiamonds:1082365560630812733>", "<:2ofdiamonds:1082365577974259792>", "<:3ofdiamonds:1082365589273727118>", "<:4ofdiamonds:1082365604167680062>", "<:5ofdiamonds:1082365618684178482>", "<:6ofdiamonds:1082365630835081297>", "<:7ofdiamonds:1082365645620006922>", "<:8ofdiamonds:1082365664574050354>", "<:9ofdiamonds:1082365679132487791>", "<:10ofdiamonds:1082365698044608582>", "<:11ofdiamonds:1082365719871750285>", "<:12ofdiamonds:1082365743385030656>", "<:13ofdiamonds:1082618048235700234>"]

class Card:
    def __init__(self, suit, value, emoji_id):
        self.suit = suit
        self.value = value
        self.emoji_id = emoji_id

    def __repr__(self):
        return f"{self.value} of {self.suit}"

class Deck:
    def __init__(self):
        self.cards = []
        counter = -1
        for s in ["Spades", "Clubs", "Hearts", "Diamonds"]:
            for v in range(1, 14):
                print(f"On {v} of {s} and giving ID {card_emoji_ids[v + counter]}")
                e = card_emoji_ids[v + counter]
                self.cards.append(Card(s, v, e))
            counter += 13

    def shuffle(self):
        if len(self.cards) > 1:
            random.shuffle(self.cards)

    def deal_card(self):
        print(f"LOG: Length of cards in deck {len(self.cards)}")
        if len(self.cards) > 1:
            return self.cards.pop(0)

class Blackjack:
    '''
    The class for the blackjack game
    '''
    def __init__(self, interaction : discord.Interaction, bet : int):
        self.interaction = interaction
        self.bet = bet
        self.deck = Deck()
        self.deck.shuffle()
        self.player_cards = []
        self.dealer_cards = []
        self.player_score = 0
        self.dealer_score = 0
        self.message = None
        self.result = None
        self.game_owner = self.interaction.user.id

    async def start(self):
        for i in range(2):
            self.player_cards.append(self.deck.deal_card())
            self.dealer_cards.append(self.deck.deal_card())
        

    async def print_current(self):

        self.update_score()

        embed = discord.Embed(colour=discord.Colour.random(),title="Game Details",description=f"On-going game for {self.interaction.user.mention}")
        embed.add_field(name=f"Dealer's cards `[{self.dealer_cards[0].value} + ?]`:", value=f"{self.dealer_cards[0].emoji_id} and [hidden]")
        embed.add_field(name=f"Player's cards `[{self.player_score}]`:",value="".join([card.emoji_id for card in self.player_cards]))
        embed.set_footer(text="Do you want to hit or stand?")

        hitButton = discord.ui.Button(style=discord.ButtonStyle.blurple, label="Hit")
        hitButton.callback = self.hit
        standButton = discord.ui.Button(style=discord.ButtonStyle.red, label="Stand")
        standButton.callback = self.stand
        self.view = discord.ui.View()
        self.view.add_item(hitButton)
        self.view.add_item(standButton)
        
        if self.message == None:
            self.message = await self.interaction.followup.send(embed=embed, view=self.view)
        else:
            await self.interaction.edit(embed=embed, view=self.view)

    async def hit(self, interaction : discord.Interaction):
        if interaction.user.id == self.game_owner:
            print("LOG: Hitting")
            self.player_cards.append(self.deck.deal_card())
            self.update_score()
            embed_hit = discord.Embed(colour=discord.Colour.random(),title="Game Details",description=f"On-going game for {self.interaction.user.mention}")
            embed_hit.add_field(name=f"Dealer's cards `[{self.dealer_cards[0].value} + ?]`:", value=f"{self.dealer_cards[0].emoji_id} and [hidden]")
            embed_hit.add_field(name=f"Player's cards `[{self.player_score}]`:",value="".join([card.emoji_id for card in self.player_cards]))
            await interaction.response.edit_message(embed=embed_hit, view=self.view)

    async def stand(self, interaction : discord.Interaction):
        if interaction.user.id == self.game_owner:
            print("LOG: Standing")
            self.dealer_score = sum([card.value for card in self.dealer_cards])
            self.update_score()
            while self.dealer_score < 17:
                self.dealer_cards.append(self.deck.deal_card())
                self.dealer_score = sum([card.value for card in self.dealer_cards])
                print(f"LOG: Dealer Cards {self.dealer_cards}")
                print(f"LOG: Dealer Score{self.dealer_score}")
            self.update_score()
            embed = discord.Embed(colour=discord.Colour.random(),title="Game Details",description=f"On-going game for {self.interaction.user.mention}")
            embed.add_field(name=f"Dealer's cards `[{self.dealer_cards[0].value} + ?]`:", value=f"{self.dealer_cards[0].emoji_id} and [hidden]")
            embed.add_field(name=f"Player's cards `[{self.player_score}]`:",value="".join([card.emoji_id for card in self.player_cards]))
            await self.calculate_score(interaction)

    async def calculate_score(self, interaction : discord.Interaction):
        print("LOG: Calculating Score")
        self.update_score()
        embed_end = discord.Embed(colour=discord.Colour.random(),title="Game Details",description=f"End of game for {self.interaction.user.mention}")
        embed_end.add_field(name=f"Dealer's cards `[{self.dealer_score}]`:", value=f"".join([card.emoji_id for card in self.dealer_cards]))
        embed_end.add_field(name=f"Player's cards `[{self.player_score}]`:",value="".join([card.emoji_id for card in self.player_cards]))
        if self.player_score > 21:
            embed_end.set_footer(text="Player busts. Dealer wins.")
            self.result = "Loss"
        elif self.dealer_score > 21:
            embed_end.set_footer(text="Dealer busts. Player wins.")
            self.result = "Win"
        elif self.player_score == self.dealer_score:
            embed_end.set_footer(text="It's a tie!")
        elif self.player_score > self.dealer_score:
            embed_end.set_footer(text="Player wins!")
            self.result = "Win"
        else:
            embed_end.set_footer(text="Dealer wins.")
            self.result = "Loss"
        await interaction.response.edit_message(embed=embed_end)

        if self.bet and self.result == "Loss":
            async with asqlite.connect("./databases/user_info.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""UPDATE user_info SET balance = balance - ? WHERE user_id = ?""",(self.bet, self.game_owner))
                    await connection.commit()
            embed_loss = discord.Embed(colour=discord.Colour.blurple(), title=f"You lost {self.bet}<:Thonks:768191131820883978> Thonks in the blackjack game")
            await interaction.channel.send(embed=embed_loss)
        elif self.bet and self.result == "Win":
            async with asqlite.connect("./databases/user_info.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""UPDATE user_info SET balance = balance + ? WHERE user_id = ?""",(self.bet, self.game_owner))
                    await connection.commit()
            embed_win = discord.Embed(colour=discord.Colour.blurple(), title=f"You won {self.bet}<:Thonks:768191131820883978> Thonks in the blackjack game")
            await interaction.channel.send(embed=embed_win)
    
    def update_score(self):
        self.player_score = sum([card.value for card in self.player_cards])
        self.dealer_score = sum([card.value for card in self.dealer_cards])