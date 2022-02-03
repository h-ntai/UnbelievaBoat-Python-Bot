"""
START OF ROOULETTE
ROULETTE GAME SLOTS found on https://github.com/ntaliceo/roulette-simulator,
rest is done here
"""

import random, discord, time, asyncio


# what will be called to play the game
class roulette_discord_implementation:
	def __init__(self, bot, channel, currency_emoji):
		self.bot = bot
		self.channel = channel
		self.currency_symbol = currency_emoji
		self.first, self.second, self.third = ['1', '4', '7', '10', '13', '16', '19', '22', '25', '28', '31', '34'], ['2', '5', '8', '11', '14', '17', '20', '23', '26', '29', '32', '35'], ['3', '6', '9', '12', '15', '18', '21', '24', '27', '30', '33', '36']
		self.slots = {'00': 'green', '0': 'green', '1': 'red', '2': 'black',
             '3': 'red', '4': 'black', '5': 'red', '6': 'black', '7': 'red',
             '8': 'black', '9': 'red', '10': 'black', '11': 'black',
             '12': 'red', '13': 'black', '14': 'red', '15': 'black',
             '16': 'red', '17': 'black', '18': 'red', '19': 'red',
             '20': 'black', '21': 'red', '22': 'black', '23': 'red',
             '24': 'black', '25': 'red', '26': 'black', '27': 'red',
             '28': 'black', '29': 'black', '30': 'red', '31': 'black',
             '32': 'red', '33': 'black', '34': 'red', '35': 'black',
             '36': 'red'}
	"""
	
	not used but may be, if adding that multiple player can play the same roulette game at once
	
	async def get_user_input(self, message):
		# we want an answer from the guy who wants to give an answer
		answer = await self.bot.wait_for("message", check=lambda response: response.author == message.author)
		answer = answer.content
		# clean input
		answer = answer.lower().strip()
		# we only want hit or stand, nothing else, and still wait after that tho
		if answer not in ["hit", "stand"]:
			return "none"

		return answer
	"""

	async def play(self, bot, channel, username, user_pfp, bet, space, mention):
		self.bot = bot

		# get space type
		spaceType = "string"
		try:
			space = int(space)
			spaceType = "int"
		except:
			space = str(space)

		color = discord.Color.from_rgb(3, 169, 244)
		embed = discord.Embed(description=f"You have placed a bet of {str(self.currency_symbol)} {bet} on `{space}`.", color=color)
		embed.set_author(name=username, icon_url=user_pfp)
		embed.set_footer(text="Spinning ! ... time remaining: 10 seconds")
		await channel.send(embed=embed)

		# wait the 10 seconds
		await asyncio.sleep(10)

		win = lose = multiplicator = None

		if space in ["odd", "even", "black", "red", "1-18", "19-36"]:
			multiplicator = 2
		elif str(space).lower() in ["1st", "2nd", "3rd", "first", "second", "third", "1-12", "13-24", "25-36"]:
			multiplicator = 3
		elif spaceType == "int":
			multiplicator = 35

		result = random.choice(list(self.slots.keys()))
		print(self.slots[result], result)

		result_prompt = f"The ball landed on: **{self.slots[result]} {result}** !\n\n"

		if str(space).lower() == "black":
			win = 1 if self.slots[result] == "black" else 0

		elif str(space).lower() == "red":
			win = 1 if self.slots[result] == "red" else 0

		elif str(space).lower() == "even":
			win = 1 if (int(result) % 2) == 0 else 0

		elif str(space).lower() == "odd":
			win = 1 if (int(result) % 2) != 0 else 0

		elif str(space).lower() == "1st":
			win = 1 if str(result) in self.first else 0
		elif str(space).lower() == "first":
			win = 1 if str(result) in self.first else 0
		elif str(space).lower() == "2nd":
			win = 1 if str(result) in self.second else 0
		elif str(space).lower() == "second":
			win = 1 if str(result) in self.second else 0
		elif str(space).lower() == "3rd":
			win = 1 if str(result) in self.third else 0
		elif str(space).lower() == "third":
			win = 1 if str(result) in self.third else 0
		elif str(space).lower() == "1-12":
			win = 1 if int(result) in range (1, 13) else 0
		elif str(space).lower() == "13-24":
			win = 1 if int(result) in range (13, 25) else 0
		elif str(space).lower() == "25-36":
			win = 1 if int(result) in range (25, 37) else 0
		elif str(space).lower() == "1-18":
			win = 1 if int(result) in range (1, 19) else 0
		elif str(space).lower() == "19-36":
			win = 1 if int(result) in range (19, 37) else 0

		elif spaceType == "int":
			win = 1 if int(space) == int(result) else 0

		else:
			# shouldnt happen
			print(space)

		if win:
			result_prompt += f"**Winner:**\n{mention} won {str(self.currency_symbol)} {bet*multiplicator}"
		else:
			result_prompt += "**No Winner :(**"

		# inform user
		await channel.send(result_prompt)

		return win, multiplicator

