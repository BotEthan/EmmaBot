import asyncio
from typing import Optional
import discord
import random

import asqlite

class Hangman():
    
    def __init__(self, interaction : discord.Interaction, bet : int, player2 : Optional[discord.Member]):
        self.interaction = interaction
        self.bet = bet
        self.game_owner = interaction.user.id
        self.player2 = player2
        self.guessed_letters = []
        self.selected_word = self.read_file('hangman_words.txt')
        self.current_answer = self.random_fill_word(self.selected_word)
        self.remaining_guesses = 6
        self.buttons = []

    async def start(self):
        embed_hangman = self.create_embed()
        string = self.hangman_image()
        embed_hangman.title = f"{string}\nGuess the a missing letter: {str(self.current_answer)}"
        self.view = discord.ui.View()
        self.create_buttons()
        await self.interaction.followup.send(embed=embed_hangman, view=self.view)

    async def guess_button(self, interaction : discord.Interaction):
        if self.check(interaction):
            for i in range(len(self.view.children)):
                if self.view.children[i].custom_id == interaction.data['custom_id']:
                    button = self.view.children[i]
            if button.label.lower() not in self.guessed_letters:
                    embed_hangman = self.create_embed()
                    self.guessed_letters.append(button.label.lower())
                    str_guessed_letters = ", ".join(self.guessed_letters)
                    if self.is_missing_char(button.label.lower()):
                        self.fill_in_char(button.label.lower())
                        string = self.hangman_image()
                        embed_hangman.title = f"Nice Guess!\n{string}{self.current_answer}\nLetters guessed: {str_guessed_letters}\nGuess a missing letter: "
                        self.view.remove_item(button)
                        await interaction.response.edit_message(embed=embed_hangman, view=self.view)              
                    else:
                        self.remaining_guesses -= 1
                        string = self.hangman_image()
                        embed_hangman.title = f"Wrong!\n{string}{self.current_answer}\nLetters guessed: {str_guessed_letters}\nGuess a missing letter: "
                        self.view.remove_item(button)
                        await interaction.response.edit_message(embed=embed_hangman, view= self.view)
                    
                    if self.remaining_guesses == 0:
                        await asyncio.sleep(1.5)
                        await interaction.message.delete()
                        string = self.hangman_image()
                        if self.bet == None:
                            embed_hangman.title = f"Sorry, you are out of guesses. The word was: {self.selected_word}"
                            await interaction.channel.send(embed=embed_hangman)
                        else:
                            async with asqlite.connect("./databases/user_info.db") as connection:
                                async with connection.cursor() as c:
                                    await c.execute("""UPDATE user_info SET balance = balance - ? WHERE user_id = ?""",(self.bet, self.game_owner))
                                    await connection.commit()
                            embed_hangman.title = f"Sorry, are out of guesses. You have lost {self.bet}<:Thonks:768191131820883978> thonks\nThe word was: {self.selected_word}"
                            await interaction.channel.send(embed=embed_hangman)
                    if self.current_answer == self.selected_word:
                        await asyncio.sleep(1.5)
                        await interaction.message.delete()
                        if self.bet == None:
                            embed_hangman.title = f"Congradulations! You won!\nThe word was {self.selected_word}"
                            await interaction.channel.send(embed=embed_hangman)
                        else:
                            async with asqlite.connect("./databases/user_info.db") as connection:
                                async with connection.cursor() as c:
                                    if self.player2:
                                        await c.execute("""UPDATE user_info SET balance = balance + (? * 2) WHERE user_id = ?/2""",(self.bet, self.game_owner))
                                        await c.execute("""UPDATE user_info SET balance = balance + (? * 2) WHERE user_id = ?/2""",(self.bet, self.player2))
                                    else:
                                        await c.execute("""UPDATE user_info SET balance = balance + (? * 2) WHERE user_id = ?""",(self.bet, self.game_owner))
                                    await connection.commit()
                            embed_hangman.title = f"Congradulations! You won! You got {2*(int(self.bet))}<:Thonks:768191131820883978> thonks\nThe word was {self.selected_word}"
                            await interaction.channel.send(embed=embed_hangman)

    def create_embed(self):
        embed_hangman = discord.Embed(colour=discord.Colour.random())
        if self.player2:
            embed_hangman.set_footer(icon_url=self.interaction.user.avatar.url,text=f"Game running for: {self.interaction.user.name} and {self.player2.display_name}")
        else:
            embed_hangman.set_footer(icon_url=self.interaction.user.avatar.url,text=f"Game running for: {self.interaction.user.name}")
        return embed_hangman

    def create_buttons(self):
        for letter in "abcdefghijklmnopqrstuvwxyz":
            if letter != self.kept_letter:
                print("LOG: Letter != ", self.kept_letter)
                button = discord.ui.Button(style=discord.ButtonStyle.blurple, label=letter.upper(), disabled=False)
                button.callback = self.guess_button
                self.buttons.append(button)
        for button in self.buttons:
            self.view.add_item(button)

    def read_file(self, file_name):
            file = open(file_name, 'r')
            words = file.readlines()
            return self.select_random_word(words)
            
    def check(self, interaction : discord.Interaction):
        if self.player2:
            return self.game_owner == interaction.user.id or self.player2.id == interaction.user.id
        else:
            return self.game_owner == interaction.user.id
    
    def select_random_word(self, words):
        random_index = random.randint(0, len(words) - 1)
        word = words[random_index].strip()
        return word
    
    def random_fill_word(self, word):
        blanked_out_word = list(word)
        random_kept_letter = random.randint(0, len(word) - 1)
        self.kept_letter = word[random_kept_letter]
        for letters in range(0, len(blanked_out_word)):
            if not blanked_out_word[letters] == word[random_kept_letter]:
                blanked_out_word[letters] = '-'
        return "".join(blanked_out_word)

    def is_missing_char(self, char):
        if char in self.selected_word:
            if char not in self.current_answer:
                return True
            else:
                return False
        return False
    
    def fill_in_char(self, char):
        word = list(self.selected_word)
        answer = list(self.current_answer)
        for letters in range(0, len(word)):
            if char == word[letters]:
                answer[letters] = word[letters]
        self.current_answer = "".join(answer)
    
    def hangman_image(self):
        if (self.remaining_guesses == 6):
            return f"Number of guesses left: {str(self.remaining_guesses)}\n/----" + "\n" + "|\n" * 4 + "-" * 7+"\n"                
        if (self.remaining_guesses == 5):
            return f"Number of guesses left: {str(self.remaining_guesses)}\n/----" + "\n" + "|    0" + "\n" + "|\n" * 3 + "-" * 7+"\n"
        if (self.remaining_guesses == 4):
            return f"Number of guesses left: {str(self.remaining_guesses)}\n/----" + "\n|    0" + "\n|   |" + "\n|   |" + "\n|" + "\n" +"-" * 7+"\n"
        if (self.remaining_guesses == 3):
            return f"Number of guesses left: {str(self.remaining_guesses)}\n/----" + "\n|    0" + "\n|  /|" + "\n|    |" + "\n|" + "\n" +"-" * 7+"\n"
        if (self.remaining_guesses == 2):
            return f"Number of guesses left: {str(self.remaining_guesses)}\n/----" + "\n|    0" + "\n|  /|\\" + "\n|    |" + "\n|" + "\n" +"-" * 7+"\n"
        if (self.remaining_guesses == 1):
            return f"Number of guesses left: {str(self.remaining_guesses)}\n/----" + "\n|    0" + "\n|  /|\\" + "\n|    |" + "\n|  / " + "\n" +"-" * 7+"\n"
        if (self.remaining_guesses == 0):
            return f"Number of guesses left: {str(self.remaining_guesses)}\n/----" + "\n|    0" + "\n|  /|\\" + "\n|    |" + "\n|  / \\" + "\n" +"-" * 7+"\n"