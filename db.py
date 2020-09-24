import sqlite3
import asyncio
import pandas as pd

class Database:
	"""
		CREATE TABLE OlxUsers (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_id VARCHAR (255) NOT NULL,
			user_name VARCHAR (255) NOT NULL,
			status BOOLEAN,
			url VARCHAR (300) NOT NULL
		);
	"""
	@classmethod
	def connect(self, db: str):
		self = Database()
		self.connection = sqlite3.connect(db)
		self.cursor = self.connection.cursor()
		
		return self

	async def get_all_users(self, status: bool = True):
		with self.connection:
			return self.cursor.execute("SELECT * FROM `OlxUsers`").fetchall()
	
	async def get_users(self, status: bool = True):
		with self.connection:
			return self.cursor.execute("SELECT * FROM `OlxUsers` WHERE `status` = ?", (status,)).fetchall()

	async def user_exists(self, user_id):
		with self.connection:
			result = self.cursor.execute("SELECT * FROM `OlxUsers` WHERE `user_id` = ?", (user_id,)).fetchall()
			return bool(len(result))

	async def add_user(self, user_id, user_name, status = True, url = ''):
		with self.connection:
			return self.cursor.execute("INSERT INTO `OlxUsers` (`user_id`, `user_name`, `status`, `url`) VALUES (?,?,?,?)", (user_id, user_name,status, url))

	async def update_user(self, user_id, status):
		return self.cursor.execute("UPDATE `OlxUsers` SET `status` = ? WHERE `user_id` = ?", (status	, user_id))
	
	async def update_url(self, user_id, url):
		return self.cursor.execute("UPDATE `OlxUsers` SET `url` = ? WHERE `user_id` = ?", (url, user_id))

	async def close(self):
		self.connection.close()

async def main():
	database = Database.connect('db.db')
	users = await database.get_all_users()
	users = pd.DataFrame(users)
	users.rename(columns = {
		0:'ID',
		1:'User_id',
		2:'User_name',
		3: 'Active',
		4: 'Url'
	}, inplace=True)
	
	print(users.head())

if __name__ == "__main__":
	asyncio.run(main())