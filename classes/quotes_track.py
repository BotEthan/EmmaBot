import random
import asqlite

class ServerQuotes():

    def __init__(self, server_id : int, quotes : list) -> None:
        self.server_id = server_id
        self.used_quotes = []
        self.quotes = {}
        self.setup_dict(quotes)

    def setup_dict(self, quotes):
        for quotes_set in quotes:
            self.quotes[quotes_set[1]] = [quotes_set[0],quotes_set[2]]
        print(f"LOG: Quotes setup for {self.server_id}:\n{self.quotes}")

    def get_all_quotes(self):
        quotes_list = []
        for key,value in self.quotes.items():
            quotes_list.append([key, value[0], value[1]])
        return quotes_list

    def get_quote(self):
        if len(self.used_quotes) == len(self.quotes):
            self.used_quotes = []
            key_list = list(self.quotes)
            selected_key = random.choice(key_list)
            selected_quote = self.quotes[selected_key]
            self.used_quotes.append(selected_key)
            quote = [selected_quote[0], selected_key, selected_quote[1]]
            return quote
        else:
            key_list = list(self.quotes)
            selected_key = random.choice(key_list)
            while selected_key in self.used_quotes:
                selected_key = random.choice(key_list)
            selected_quote = self.quotes[selected_key]
            self.used_quotes.append(selected_key)
            quote = [selected_quote[0], selected_key, selected_quote[1]]
            return quote

    async def add_quote(self, author_id : int, new_quote : str, clip_link : str):
        self.quotes[new_quote] = [author_id, clip_link]
        async with asqlite.connect("./databases/server_quotes.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""INSERT INTO quotes VALUES (?,?,?,?)""", (self.server_id, author_id, new_quote, clip_link))
                await connection.commit()
        print("LOG: Added new quote")

    async def delete_quote(self, quote):
        print(f"Quote to delete {quote}")
        self.quotes.pop(quote)
        self.used_quotes.pop(quote)
        async with asqlite.connect("./databases/server_quotes.db") as connection:
            async with connection.cursor() as c:
                await c.execute("""DELETE FROM quotes WHERE quote = ?""", (quote,))
                await connection.commit()

    async def edit_quote(self, user_id : int, old_quote : str, new_quote : str, clip_link : str):
        old_index = self.quotes.index(old_quote)
        if clip_link == "skip":
            self.quotes[old_index] = [user_id, new_quote, None]
            async with asqlite.connect("./databases/server_quotes.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""UPDATE quotes SET quote = ?, submitter_id = ? WHERE quote = ? and server_id = ?""",(new_quote, user_id, old_quote, self.server_id))
                    await connection.commit()
        else:
            self.quotes[old_index] = [user_id, new_quote, clip_link]
            async with asqlite.connect("./databases/server_quotes.db") as connection:
                async with connection.cursor() as c:
                    await c.execute("""UPDATE quotes SET quote = ?, submitter_id = ?, clip_link = ? WHERE quote = ? and server_id = ?""",(new_quote, user_id, clip_link, old_quote, self.server_id))
                    await connection.commit()