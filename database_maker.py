import sqlite3

connection = sqlite3.connect("./databases/server_quotes.db")
c = connection.cursor()

# c.execute("""INSERT INTO music_settings VALUES(518721840865214484,100,0,?)""",(None,))
# c.execute("""DROP TABLE a767324204390809620""")

# c.execute("""CREATE TABLE quotes (
#     server_id INT,
#     submitter_id INT,
#     quote TEXT,
#     clip_link TEXT
# )""")

#query = f"DELETE FROM a{767324204390809620} WHERE channel_link = 'https://youtube.com/@jacksepticeye'"
#c.execute(query)

# KEY FUNCTIONS
# DELETE FROM {table} // Deletes all from a table
# UPDATE {table} SET {queries} WHERE {conditions} // Edits a table to change things based on certain conditions

# c.execute("""CREATE TABLE preferences (
#     server_id INT,
#     current_event Text,
#     current_stage INT
# )""")

#c.execute("""ALTER TABLE music_settings ADD COLUMN channel_id INT""")

#c.execute("""DROP TABLE message_reacions""")
# c.execute("""ALTER TABLE reactions ADD toggle INT DEFAULT 0""")
#c.execute("""DELETE FROM birthdays WHERE server_id = 767324204390809620	""")
#c.execute("""UPDATE user_info SET balance = 0 WHERE user_id = 296668203571085312""")
#c.execute("DELETE FROM reactions WHERE server_id = 767324204390809620")
#c.execute("""INSERT INTO quotes VALUES (767324204390809620, 296668203571085312, "Don't let your dreams be dreams - Shia Labeouf")""")
#c.execute("""INSERT INTO quotes VALUES (767324204390809620, 439078090937729034, "Y'see this shovel? I'mma put it right up yo bootyho. SIDEWAYS. Then I'mma spin chu like a beyblade. - Jack")""")
#c.execute("""INSERT INTO quotes VALUES (767324204390809620, 222224934359793674, "This is a quote! - Ethan")""")
#c.execute("INSERT INTO user_info VALUES (222224934359793674,'Bot Ethan',0)")
#c.execute("""INSERT INTO settings VALUES (819667478158114816, 0, False)""")
#c.execute("""ALTER TABLE birthdays RENAME TO users""")

# with sqlite3.connect("server_quotes.db") as connection:
#     c = connection.cursor()
#     insert_query = "ALTER TABLE quotes ADD COLUMN clip_link TEXT DEFAULT None"
#     c.execute(insert_query)
#     connection.commit()

# with sqlite3.connect("./databases/temp_quotes.db") as connection:
#     c = connection.cursor()
#     for quote in results:
#         c.execute("INSERT INTO quotes VALUES (?, ?, ?, ?)", (quote[0], quote[1], quote[2], None))

c.execute("""DELETE FROM reactions WHERE role_id = 1115986688527839243""")
connection.commit()

# connection.close()