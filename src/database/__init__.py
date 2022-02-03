import json, os, time, random, math, sys, discord, math
from datetime import datetime, timezone, timedelta
from random import randint
# custom blackjack game thing
from game_libs.blackjack import blackjack_discord_implementation
# custom roulette game thing
from game_libs.roulette import roulette_discord_implementation

"""

	the database handler of the unbelievaboat-python discord bot
	// is imported by ../main.py

"""


class pythonboat_database_handler:
    # always called when imported in main.py
    def __init__(self, client):
        # we do the path from the main.py file, so we go into the db folder, then select
        self.pathToJson = "database/database.json"
        self.client = client
        # for the json "variables", dont want to make a whole function to find index for variables
        # wont be many anyways. so making it manually
        self.variable_dict = {
            "slut": 0,
            "crime": 1,
            "work": 2,
            "daily": 3,
            "rob": 4
        }

        # for colors
        self.discord_error_rgb_code = discord.Color.from_rgb(239, 83, 80)
        self.discord_blue_rgb_code = discord.Color.from_rgb(3, 169, 244)
        self.discord_success_rgb_code = discord.Color.from_rgb(102, 187, 106)

        # check if file is created, else create it
        if not os.path.exists(self.pathToJson):
            creating_file = open(self.pathToJson, "w")
            # adding default json config into the file if creating new
            # all the users will get created automatically in the function self.find_index_in_db()
            # but for the different jobs etc the program needs configs for variables and symbols
            creating_file.write("""{\n\t"userdata": [], 
        										"variables":[
        											{"name":"slut","delay":15,"min_revenue":50,"max_revenue":400,"proba":50,"win_phrases":["You made","Your dad likes it so much he gives you"],"lose_phrases":["You were fined","Your uncle didn't like the encounter. You pay"],"min_lose_amount_percentage":2,"max_lose_amount_percentage":5},
        											{"name":"crime","delay":60,"min_revenue":100,"max_revenue":1200,"proba":30,"win_phrases":["You commited a crime and got","You robbed a bank and got"],"lose_phrases":["You were fined","MacGyver finds you, you pay"],"min_lose_amount_percentage":10,"max_lose_amount_percentage":20},
        											{"name":"work","delay":10,"min_revenue":50,"max_revenue":200,"win_phrases":["You worked at SubWay and made","You helped someone do his homework and got"]},
        											{"name":"rob","delay":45,"proba":50,"min_gain_amount_percentage":10,"max_gain_amount_percentage":20,"min_lose_amount_percentage":10,"max_lose_amount_percentage":20,"win_phrases":["You robbed and got"],"lose_phrases":["You were caught robbing and have to pay"]}], 
        										"symbols": [
        											{"name":"currency_symbol","symbol_emoji":":dollar:"}				
        										],
        										"items": [
        											{}				
        										],
        										"income_roles": [
        											{}				
        										]
        										\n}""")
            creating_file.close()

        #

        # check if json file is corrupted
        #  -> in self.check_json()
        # called from main.py

    def get_currency_symbol(self, test=False, value="unset"):
        if not test:
            # get currency symbol to use
            temp_json_opening = open(self.pathToJson, "r")
            temp_json_content = json.load(temp_json_opening)
            # the currency symbol is always at position 0 in the "symbols" part
            currency_symbol = temp_json_content["symbols"][0]["symbol_emoji"]
            self.currency_symbol = discord.utils.get(self.client.emojis, id=int(currency_symbol))
        else:
            try:
                self.currency_symbol = discord.utils.get(self.client.emojis, id=int(value))
                print(str(self.currency_symbol))
                if self.currency_symbol == None:
                    return "error"
            except:
                return "error"

        # if we handle a already created file, we need certain variables

    async def check_json(self):
        temp_json_opening = open(self.pathToJson, "r")
        temp_json_content = json.load(temp_json_opening)
        """
        possibly to add : 
            improve the error system, raising specific errors with a "error_info"
            for example : "userdata missing", or "slut missing", or even "slut min_revenue missing"
        """
        try:
            check_content = temp_json_content
            # userdata space
            userdata = check_content["userdata"]
            # variables
            variables = check_content["variables"]
            slut = variables[self.variable_dict["slut"]]
            crime = variables[self.variable_dict["crime"]]
            work = variables[self.variable_dict["work"]]
            daily = variables[self.variable_dict["daily"]]
            rob = variables[self.variable_dict["rob"]]

            # symbol
            currency_symbol = check_content["symbols"][0]
            items = check_content["items"]
            roles = check_content["income_roles"]

            # didnt fail, so we're good
            temp_json_opening.close()
        except Exception as e:
            # something is missing, inform client
            return "error"

    """
    GLOBAL FUNCTIONS
    """

    # need to overwrite the whole json when updating, luckily the database won't be enormous
    def overwrite_json(self, content):
        self.json_db = open(self.pathToJson, "w")
        self.clean_json = json.dumps(content, indent=4, separators=(",", ": "))
        self.json_db.write(self.clean_json)
        self.json_db.close()

    # find the user in the database
    def find_index_in_db(self, data_to_search, user_to_find, fail_safe=False):
        print(data_to_search)
        user_to_find = int(user_to_find)
        for i in range(len(data_to_search)):
            if data_to_search[i]["user_id"] == user_to_find:
                print("\nfound user\n")
                return int(i), "none"

        # in this case, this isnt a user which isnt yet registrated
        # but someone who doesnt exist on the server
        # or at least thats what is expected when calling with this parameter
        if fail_safe:
            return 0, "error"

        print("\ncreating user\n")
        # we did NOT find him, which means he doesn't exist yet
        # so we automatically create him
        data_to_search.append({
            "user_id": int(user_to_find),
            "cash": 0,
            "bank": 0,
            # "balance" : cash + bank
            # "roles": "None" ; will be checked when calculating weekly auto-role-income
            "items": "none",
            "last_slut": "none",
            "last_work": "none",
            "last_crime": "none",
            "last_rob": "none",
            "last_daily": "none",
            "rate": 50,
            "work_mult": 1.0,
            "crime_mult": 1.0,
            "slut_mult": 1.0,
            "daily_mult": 1.0
        })
        """
            POSSIBLE ISSUE :
                that we need to create user by overwrite, then problem of doing that while another command is
                supposed to have it open etc. hopefully it works just as such
        """
        # now that the user is created, re-check and return int

        for i in range(len(data_to_search)):
            if data_to_search[i]["user_id"] == user_to_find:
                return i, data_to_search

    """
    CLIENT-DB HANDLING
    """

    async def blackjack(self, user, bet, bot, channel, username, user_pfp, message):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]

        # get user stuff
        user_cash = json_user_content["cash"]
        if bet == "half":
            bet = round((user_cash / 2))
        elif bet == "all":
            bet = user_cash
        else:
            bet = bet
        print("cash", user_cash)
        if user_cash < int(float(bet)):
            self.overwrite_json(json_content)
            return "error", f"You don't have enough money for this bet.\nYou currently have {str(self.currency_symbol)} **{'{:,}'.format(int(user_cash))}** in cash."
        json_user_content["cash"] -= int(float(bet))
        json_content["userdata"][user_index] = json_user_content
        self.overwrite_json(json_content)

        # the actual game
        # start it
        startInstance = blackjack_discord_implementation(bot, channel, self.currency_symbol)
        bjPlay = await startInstance.play(bot, channel, username, user_pfp, message, int(float(bet)))
        json_file = open(self.pathToJson, "r")
        json_cnt = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_cnt["userdata"], user)
        json_user_cnt = json_cnt["userdata"][user_index]

        if bjPlay == "win":
            json_user_cnt["cash"] += int(float(bet)) * 2
        elif bjPlay == "loss":
            pass
            # json_user_content["cash"] -= int(float(bet))
        elif bjPlay == "bust":
            json_user_cnt["cash"] += int(float(bet))
        else:
            return "error", "error unknown, contact admin"

        # overwrite, end
        json_cnt["userdata"][user_index] = json_user_cnt
        self.overwrite_json(json_cnt)

        return "success", "success"

    async def cockfight(self, user, bet, channel, username, user_pfp):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]
        proba = json_user_content["rate"]
        cash = json_user_content["cash"]
        if bet == "half":
            bet = round((cash / 2))
        elif bet == "all":
            bet = cash
        else:
            bet = bet

        if cash >= bet:
            """
                    ACTUAL FUNCTION
                    """
            # so, explanation :
            # not actually using probabilites or so, just a random number between 1 and 2
            # and if for example probability is 50%, then the random num should be > 1.5 in order to win
            cf_success = random.randint(0, 100)

            if proba < cf_success:
                # LOST

                loss = bet  # balance * (lose_percentage / 100)
                # round up, no floats
                color = self.discord_error_rgb_code
                embed = discord.Embed(
                    description=f"Your Chicken died and you lost {str(self.currency_symbol)} **{'{:,}'.format(int(loss))}**",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                embed.set_footer(text="r.i.p")
                json_user_content["cash"] -= loss
                # update last slut time
                json_user_content["rate"] = 50
                # overwrite, end
                json_content["userdata"][user_index] = json_user_content
                self.overwrite_json(json_content)
                await channel.send(embed=embed)
                return "success", "success"
            else:
                # SUCCESS
                gain = bet
                if proba < 75:
                    newrate = proba + 1
                else:
                    newrate = proba
                color = self.discord_success_rgb_code
                embed = discord.Embed(
                    description=f"Your Chicken won and made you {str(self.currency_symbol)} **{'{:,}'.format(int(gain))}** richer! 🐓",
                    color=color)
                embed.set_author(name=username, icon_url=user_pfp)
                embed.set_footer(text=f"Chicken Strenght: {newrate}%")
                json_user_content["cash"] += gain
                # update last slut time
                json_user_content["rate"] = newrate
                # overwrite, end
                json_content["userdata"][user_index] = json_user_content
                self.overwrite_json(json_content)
                await channel.send(embed=embed)
                return "success", "success"
        else:
            return "error", f"You don't have enough money for this bet.\nYou currently have {str(self.currency_symbol)} **{'{:,}'.format(int(cash))}** in cash."

    async def upgrade(self, user, channel, username, user_pfp, item_name, amount):
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        json_items = ["work", "crime", "slut", "daily", "w", "c", "s", "d"]
        item_found = item_index = 0
        if item_name.lower() in json_items:
            item_found = True
        if not item_found:
            return "error", f"{item_name} not found.\nYou can upgrade work, crime, slut and daily"
        # get variables
        if item_name == "w":
            item_name = "work"
        if item_name == "d":
            item_name = "daily"
        if item_name == "c":
            item_name = "crime"
        if item_name == "s":
            item_name = "slut"
        item_name = item_name
        item_price = 10000

        # 4. check if enough money
        sum_price = item_price * int(float(amount))
        sum_price = round(sum_price, 0)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)
        user_content = json_content["userdata"][user_index]
        user_cash = user_content["cash"]
        if user_cash < sum_price:
            return "error", f"Error! Not enough money in cash to purchase.\nto pay: {sum_price}; in cash: {round(user_cash, 0)}"

        # 8. rem money, substract stock, print message, add to inventory
        user_content["cash"] -= sum_price
        before = user_content[f"{item_name}_mult"]
        after = before + 0.1 * amount
        after = round(after, 1)

        color = self.discord_blue_rgb_code
        higher_name = f"{item_name} multiplicator".upper()
        embed = discord.Embed(
            description=f"You have bought {amount} {item_name} uprgade(s) and paid {str(self.currency_symbol)} **{'{:,}'.format(int(sum_price))}**\n\n\n__**{higher_name}**__\n\n*x{before}* ➡️ *x{after}*",
            color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        embed.set_footer(text=f"let\'s goo")
        await channel.send(embed=embed)
        mult = user_content[f"{item_name}_mult"]
        user_content[f"{item_name}_mult"] = round((mult + 0.1 * amount), 1)

        # overwrite, end
        json_content["userdata"][user_index] = user_content
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # ROULETTE
    #

    async def roulette(self, user, bet, space, bot, channel, username, user_pfp, mention):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]

        # get user stuff
        user_cash = json_user_content["cash"]
        if bet == "half":
            bet = round((user_cash / 2))
        elif bet == "all":
            bet = user_cash
        else:
            bet = bet
        print("cash", user_cash)
        if user_cash < int(float(bet)):
            self.overwrite_json(json_content)
            return "error", f"You don't have enough money for this bet.\nYou currently have {str(self.currency_symbol)} **{'{:,}'.format(int(user_cash))}** in cash."

        # the actual game
        # start it
        json_user_content["cash"] -= int(float(bet))
        json_content["userdata"][user_index] = json_user_content
        self.overwrite_json(json_content)
        startInstance = roulette_discord_implementation(bot, channel, self.currency_symbol)
        roulettePlay, multiplicator = await startInstance.play(bot, channel, username, user_pfp, int(float(bet)), space,
                                                               mention)
        # roulettePlay will be 1 for won, 0 for lost
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]

        # get user stuff
        json_file = open(self.pathToJson, "r")
        json_bet = json.load(json_file)
        if roulettePlay:
            json_user_content["cash"] += int(float(bet) * multiplicator)
        elif roulettePlay == 0:
            pass
        else:
            return "error", "error unknown, contact admin"

        # overwrite, end
        json_bet["userdata"][user_index] = json_user_content
        self.overwrite_json(json_bet)

        return "success", "success"

    #
    # SLUT
    #

    async def slut(self, user, channel, username, user_pfp):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]
        multiplicator = json_user_content["slut_mult"]

        """
        SPECIFIC TIME ETC
        """
        # grep values
        slut_data = json_content["variables"][self.variable_dict["slut"]]

        # delay will ALWAYS be in MINUTES
        delay = slut_data["delay"]
        proba = slut_data["proba"]

        time_check = False
        now = datetime.now()
        if json_user_content["last_slut"] == "none":
            # never done it, so go ahead
            time_check = True
        # else, gotta check if enough time passed since last slut
        else:
            last_slut_string = json_user_content["last_slut"]
            last_slut = datetime.strptime(last_slut_string, '%Y-%m-%d %H:%M:%S.%f')
            print(last_slut)
            passed_time = now - last_slut
            passed_time_minutes = passed_time.total_seconds() // 60 - 1
            seconds = passed_time.total_seconds()
            seconds = float(f"{seconds:.0f}")
            hours_remaining = delay // 60 - seconds // 3600
            delay_remaining = delay - passed_time_minutes
            if hours_remaining - 1 < 1:
                if passed_time_minutes <= 0:
                    passed_time_minutes = 1
                # show_secs = True
                else:
                    pass
                # show_secs = False
                if seconds > delay * 60:
                    time_check = True
                else:
                    time_check = False
                    delay_remaining = delay - passed_time_minutes
                    dl_remaining = delay * 60 - seconds
                    if dl_remaining <= 60:
                        show_secs = True
                    else:
                        show_secs = False
                    if show_secs == True:
                        wait = f"{dl_remaining:.0f} seconds"
                    elif show_secs == False:
                        wait = f"{delay_remaining:.0f} minutes"
            else:
                short_hours = float(f"{hours_remaining:.0f}") - 1
                short_hours_in_min = short_hours * 60
                delay_remaining = delay - passed_time_minutes - short_hours_in_min
                mins = delay_remaining
                wait = f"{short_hours:.0f} hours and {mins:.0f} minutes"
            # calculate difference, see if it works
            if seconds > delay * 60:
                time_check = True
            else:
                time_check = False
                delay_remaining = delay - passed_time_minutes
                splitted = last_slut_string.split(" ")
                splitted_two = splitted[0].split("-")
                splitted_three = splitted[1].split(":")
                splitted_four = splitted_three[2].split(".")
                year = int(splitted_two[0])
                day = int(splitted_two[2])
                hour = int(splitted_three[0])
                minute = int(splitted_three[1])
                month = int(splitted_two[1])
                second = int(splitted_four[0])
        if time_check == False:
            dt = datetime(year, month, day, hour, minute, second, 0, timezone(timedelta(hours=0)))
            dt = dt + timedelta(0, 0, 0, 0, delay, 0, 0)
            unix = int(dt.timestamp())
            color = self.discord_blue_rgb_code
            embed = discord.Embed(description=f"⏱ ️You cannot be a slut for {wait}.",
                                  color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            embed.set_footer(text=f"Slut multiplicator: x{multiplicator}")
            await channel.send(embed=embed)
            return "success", "success"
        else:
            print("he can do it")

        """
        ACTUAL FUNCTION
        """
        # so, explanation :
        # not actually using probabilites or so, just a random number between 1 and 2
        # and if for example probability is 50%, then the random num should be > 1.5 in order to win
        slut_success = random.randint(0, 100)

        if proba < slut_success:
            # LOST

            lose_phrases = random.choice(slut_data["lose_phrases"])
            lose_percentage = random.randint(slut_data["min_lose_amount_percentage"],
                                             slut_data["max_lose_amount_percentage"])
            balance = json_user_content["cash"] + json_user_content["bank"]
            loss = random.randint(300, 800)  # balance * (lose_percentage / 100)
            # round up, no floats
            loss = loss * multiplicator
            loss = round(loss, 0)
            print(lose_phrases, balance, loss)
            color = self.discord_error_rgb_code
            embed = discord.Embed(
                description=f"{lose_phrases} {str(self.currency_symbol)} **{'{:,}'.format(int(loss))}**", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            embed.set_footer(text="r.i.p")
            await channel.send(embed=embed)
            json_user_content["cash"] -= loss
            # update last slut time
            json_user_content["last_slut"] = str(now)
            # overwrite, end
            json_content["userdata"][user_index] = json_user_content
            self.overwrite_json(json_content)

            return "success", "success"

        else:
            # SUCCESS
            win_phrases = random.choice(slut_data["win_phrases"])
            gain = random.randint(slut_data["min_revenue"], slut_data["max_revenue"])
            gain = gain * multiplicator
            # round up, no floats
            gain = round(gain, 0)
            color = self.discord_success_rgb_code
            embed = discord.Embed(
                description=f"{win_phrases} {str(self.currency_symbol)} **{'{:,}'.format(int(gain))}**", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            embed.set_footer(text=f"Slut multiplicator: x{multiplicator}")
            await channel.send(embed=embed)
            json_user_content["cash"] += gain
            # update last slut time
            json_user_content["last_slut"] = str(now)
            # overwrite, end
            json_content["userdata"][user_index] = json_user_content
            self.overwrite_json(json_content)

            return "success", "success"

    # we never reach this part of the code

    #
    # CRIME
    #

    async def crime(self, user, channel, username, user_pfp):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]
        multiplicator = json_user_content["crime_mult"]

        """
        SPECIFIC TIME ETC
        """
        # grep values
        crime_data = json_content["variables"][self.variable_dict["crime"]]

        # delay will ALWAYS be in MINUTES
        delay = crime_data["delay"]
        proba = crime_data["proba"]

        time_check = False
        now = datetime.now()
        if json_user_content["last_crime"] == "none":
            # never done it, so go ahead
            time_check = True
        # else, gotta check if enough time passed since last slut
        else:
            last_slut_string = json_user_content["last_crime"]
            last_slut = datetime.strptime(last_slut_string, '%Y-%m-%d %H:%M:%S.%f')
            print(last_slut)
            passed_time = now - last_slut
            passed_time_minutes = passed_time.total_seconds() // 60 - 1
            seconds = passed_time.total_seconds()
            seconds = float(f"{seconds:.0f}")
            hours_remaining = delay // 60 - seconds // 3600
            delay_remaining = delay - passed_time_minutes
            if hours_remaining - 1 < 1:
                if passed_time_minutes <= 0:
                    passed_time_minutes = 1
                # show_secs = True
                else:
                    pass
                # show_secs = False
                if seconds > delay * 60:
                    time_check = True
                else:
                    time_check = False
                    delay_remaining = delay - passed_time_minutes
                    dl_remaining = delay * 60 - seconds
                    if dl_remaining <= 60:
                        show_secs = True
                    else:
                        show_secs = False
                    if show_secs == True:
                        wait = f"{dl_remaining:.0f} seconds"
                    elif show_secs == False:
                        wait = f"{delay_remaining:.0f} minutes"
            else:
                short_hours = float(f"{hours_remaining:.0f}") - 1
                short_hours_in_min = short_hours * 60
                delay_remaining = delay - passed_time_minutes - short_hours_in_min
                mins = delay_remaining
                wait = f"{short_hours:.0f} hours and {mins:.0f} minutes"
            # calculate difference, see if it works
            if seconds > delay * 60:
                time_check = True
            else:
                time_check = False
                delay_remaining = delay - passed_time_minutes
                splitted = last_slut_string.split(" ")
                splitted_two = splitted[0].split("-")
                splitted_three = splitted[1].split(":")
                splitted_four = splitted_three[2].split(".")
                year = int(splitted_two[0])
                day = int(splitted_two[2])
                hour = int(splitted_three[0])
                minute = int(splitted_three[1])
                month = int(splitted_two[1])
                second = int(splitted_four[0])
        if time_check == False:
            dt = datetime(year, month, day, hour, minute, second, 0, timezone(timedelta(hours=0)))
            dt = dt + timedelta(0, 0, 0, 0, delay, 0, 0)
            unix = int(dt.timestamp())
            color = self.discord_blue_rgb_code
            embed = discord.Embed(description=f"⏱ ️You cannot commit a crime for {wait}.",
                                  color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            embed.set_footer(text=f"Crime multiplicator: x{multiplicator}")
            await channel.send(embed=embed)
            return "success", "success"
        else:
            print("he can do it")

        """
        ACTUAL FUNCTION
        """
        # so, explanation :
        # not actually using probabilites or so, just a random number between 1 and 2
        # and if for example probability is 50%, then the random num should be > 1.5 in order to win
        crime_success = random.randint(0, 100)

        if proba < crime_success:
            # LOST

            lose_phrases = random.choice(crime_data["lose_phrases"])
            lose_percentage = random.randint(crime_data["min_lose_amount_percentage"],
                                             crime_data["max_lose_amount_percentage"])
            balance = json_user_content["cash"] + json_user_content["bank"]
            loss = random.randint(500, 1000)  # balance * (lose_percentage / 100)
            loss = loss * multiplicator
            # round up, no floats
            loss = round(loss, 0)
            print(lose_phrases, balance, loss)
            color = self.discord_error_rgb_code
            embed = discord.Embed(
                description=f"{lose_phrases} {str(self.currency_symbol)} **{'{:,}'.format(int(loss))}**", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            embed.set_footer(text="r.i.p")
            await channel.send(embed=embed)
            json_user_content["cash"] -= loss
            # update last slut time
            json_user_content["last_crime"] = str(now)
            # overwrite, end
            json_content["userdata"][user_index] = json_user_content
            self.overwrite_json(json_content)

            return "success", "success"

        else:
            # SUCCESS
            win_phrases = random.choice(crime_data["win_phrases"])
            gain = random.randint(crime_data["min_revenue"], crime_data["max_revenue"])
            gain = gain * multiplicator
            # round up, no floats
            gain = round(gain, 0)
            color = self.discord_success_rgb_code
            embed = discord.Embed(
                description=f"{win_phrases} {str(self.currency_symbol)} **{'{:,}'.format(int(gain))}**", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            embed.set_footer(text=f"Crime multiplicator: x{multiplicator}")
            await channel.send(embed=embed)
            json_user_content["cash"] += gain
            # update last slut time
            json_user_content["last_crime"] = str(now)
            # overwrite, end
            json_content["userdata"][user_index] = json_user_content
            self.overwrite_json(json_content)

            return "success", "success"

    # we never reach this part of the code

    #
    # WORK
    #

    async def work(self, user, channel, username, user_pfp):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]
        multiplicator = json_user_content["work_mult"]

        """
        SPECIFIC TIME ETC
        """
        # grep values
        work_data = json_content["variables"][self.variable_dict["work"]]

        # delay will ALWAYS be in MINUTES
        delay = work_data["delay"]

        time_check = False
        now = datetime.now()
        if json_user_content["last_work"] == "none":
            # never done it, so go ahead
            time_check = True
        # else, gotta check if enough time passed since last slut
        else:
            last_slut_string = json_user_content["last_work"]
            last_slut = datetime.strptime(last_slut_string, '%Y-%m-%d %H:%M:%S.%f')
            print(last_slut)
            passed_time = now - last_slut
            passed_time_minutes = passed_time.total_seconds() // 60 - 1
            seconds = passed_time.total_seconds()
            seconds = float(f"{seconds:.0f}")
            hours_remaining = delay // 60 - seconds // 3600
            delay_remaining = delay - passed_time_minutes
            if hours_remaining - 1 < 1:
                if passed_time_minutes <= 0:
                    # because of // division it might display 0
                    passed_time_minutes = 1
                # show_secs = True
                else:
                    pass
                # show_secs = False
                if seconds > delay * 60:
                    time_check = True
                else:
                    time_check = False
                    delay_remaining = delay - passed_time_minutes
                    dl_remaining = delay * 60 - seconds
                    if dl_remaining <= 60:
                        show_secs = True
                    else:
                        show_secs = False
                    if show_secs == True:
                        wait = f"{dl_remaining:.0f} seconds"
                    else:
                        wait = f"{delay_remaining:.0f} minutes"
            else:
                short_hours = float(f"{hours_remaining:.0f}") - 1
                short_hours_in_min = short_hours * 60
                delay_remaining = delay - passed_time_minutes - short_hours_in_min
                mins = delay_remaining
                wait = f"{short_hours:.0f} hours and {mins:.0f} minutes"
            # calculate difference, see if it works
            if seconds > delay * 60:
                time_check = True
            else:
                time_check = False
                splitted = last_slut_string.split(" ")
                splitted_two = splitted[0].split("-")
                splitted_three = splitted[1].split(":")
                splitted_four = splitted_three[2].split(".")
                year = int(splitted_two[0])
                day = int(splitted_two[2])
                hour = int(splitted_three[0])
                minute = int(splitted_three[1])
                month = int(splitted_two[1])
                second = int(splitted_four[0])
        # moving the block here for cleaner code
        if time_check == False:
            dt = datetime(year, month, day, hour, minute, second, 0, timezone(timedelta(hours=0)))
            dt = dt + timedelta(0, 0, 0, 0, delay, 0, 0)
            unix = int(dt.timestamp())
            color = self.discord_blue_rgb_code
            embed = discord.Embed(description=f"⏱ ️You cannot work for {wait}.",  # \nNext work: <t:{unix}:T>",
                                  color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            embed.set_footer(text=f"Work multiplicator: x{multiplicator}")
            await channel.send(embed=embed)
            return "success", "success"
        else:
            print("he can do it")

        """
        ACTUAL FUNCTION
        """

        # work is always a success
        win_phrases = random.choice(work_data["win_phrases"])
        gain = random.randint(work_data["min_revenue"], work_data["max_revenue"])
        gain = gain * multiplicator
        # round up, no floats
        gain = round(gain, 0)
        color = self.discord_success_rgb_code
        embed = discord.Embed(description=f"{win_phrases} {str(self.currency_symbol)} **{'{:,}'.format(int(gain))}**",
                              color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        embed.set_footer(text=f"Work multiplicator: x{multiplicator}")
        await channel.send(embed=embed)
        json_user_content["cash"] += gain
        # update last slut time
        json_user_content["last_work"] = str(now)
        # overwrite, end
        json_content["userdata"][user_index] = json_user_content
        self.overwrite_json(json_content)

        return "success", "success"

    async def daily(self, user, channel, username, user_pfp):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]
        multiplicator = json_user_content["daily_mult"]

        """
        SPECIFIC TIME ETC
        """
        # grep values
        work_data = json_content["variables"][self.variable_dict["daily"]]

        # delay will ALWAYS be in MINUTES
        delay = work_data["delay"]

        time_check = False
        now = datetime.now()
        if json_user_content["last_daily"] == "none":
            # never done it, so go ahead
            time_check = True
        # else, gotta check if enough time passed since last slut
        else:
            last_slut_string = json_user_content["last_daily"]
            last_slut = datetime.strptime(last_slut_string, '%Y-%m-%d %H:%M:%S.%f')
            print(last_slut)
            passed_time = now - last_slut
            passed_time_minutes = passed_time.total_seconds() // 60 - 1
            seconds = passed_time.total_seconds()
            seconds = float(f"{seconds:.0f}")
            hours_remaining = delay // 60 - seconds // 3600
            delay_remaining = delay - passed_time_minutes
            if hours_remaining - 1 < 1:
                if passed_time_minutes <= 0:
                    passed_time_minutes = 1
                # show_secs = True
                else:
                    pass
                # show_secs = False
                if seconds > delay * 60:
                    time_check = True
                else:
                    time_check = False
                    delay_remaining = delay - passed_time_minutes
                    dl_remaining = delay * 60 - seconds
                    if dl_remaining <= 60:
                        show_secs = True
                    else:
                        show_secs = False
                    if show_secs == True:
                        wait = f"{dl_remaining:.0f} seconds"
                    elif show_secs == False:
                        wait = f"{delay_remaining:.0f} minutes"
            else:
                short_hours = float(f"{hours_remaining:.0f}") - 1
                short_hours_in_min = short_hours * 60
                delay_remaining = delay - passed_time_minutes - short_hours_in_min
                mins = delay_remaining
                wait = f"{short_hours:.0f} hours and {mins:.0f} minutes"
            # calculate difference, see if it works
            if seconds > delay * 60:
                time_check = True
            else:
                time_check = False
                delay_remaining = delay - passed_time_minutes
                splitted = last_slut_string.split(" ")
                splitted_two = splitted[0].split("-")
                splitted_three = splitted[1].split(":")
                splitted_four = splitted_three[2].split(".")
                year = int(splitted_two[0])
                day = int(splitted_two[2])
                hour = int(splitted_three[0])
                minute = int(splitted_three[1])
                month = int(splitted_two[1])
                second = int(splitted_four[0])
        # moving the block here for cleaner code
        # moving the block here for cleaner code
        if time_check == False:
            dt = datetime(year, month, day, hour, minute, second, 0, timezone(timedelta(hours=0)))
            dt = dt + timedelta(0, 0, 0, 0, delay, 0, 0)
            unix = int(dt.timestamp())
            color = self.discord_blue_rgb_code
            embed = discord.Embed(description=f"⏱ ️You cannot do daily for {wait}!",
                                  color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            embed.set_footer(text=f"Daily multiplicator: x{multiplicator}")
            await channel.send(embed=embed)
            return "success", "success"
        else:
            print("he can do it")

        """
        ACTUAL FUNCTION
        """

        # work is always a success
        win_phrases = random.choice(work_data["win_phrases"])
        gain = random.randint(work_data["min_revenue"], work_data["max_revenue"])
        gain = gain * multiplicator
        # round up, no floats
        gain = round(gain, 0)
        color = self.discord_success_rgb_code
        embed = discord.Embed(description=f"{win_phrases} {str(self.currency_symbol)} **{'{:,}'.format(int(gain))}**",
                              color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        embed.set_footer(text=f"sheesh - Daily multiplicator: {multiplicator}")
        await channel.send(embed=embed)
        json_user_content["cash"] += gain
        # update last slut time
        json_user_content["last_daily"] = str(now)
        # overwrite, end
        json_content["userdata"][user_index] = json_user_content
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # ROB
    #

    async def rob(self, user, channel, username, user_pfp, user_to_rob):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]

        """
        SPECIFIC TIME ETC
        """
        # grep values
        rob_data = json_content["variables"][self.variable_dict["rob"]]

        # delay will ALWAYS be in MINUTES
        delay = rob_data["delay"]
        proba = rob_data["proba"]

        time_check = False
        now = datetime.now()
        if json_user_content["last_rob"] == "none":
            # never done it, so go ahead
            time_check = True
        # else, gotta check if enough time passed since last slut
        else:
            last_slut_string = json_user_content["last_rob"]
            last_slut = datetime.strptime(last_slut_string, '%Y-%m-%d %H:%M:%S.%f')
            print(last_slut)
            passed_time = now - last_slut
            passed_time_minutes = passed_time.total_seconds() // 60 - 1
            seconds = passed_time.total_seconds()
            seconds = float(f"{seconds:.0f}")
            hours_remaining = delay // 60 - seconds // 3600
            delay_remaining = delay - passed_time_minutes
            if hours_remaining - 1 < 1:
                if passed_time_minutes <= 0:
                    passed_time_minutes = 1
                # show_secs = True
                else:
                    pass
                # show_secs = False
                if seconds > delay * 60:
                    time_check = True
                else:
                    time_check = False
                    delay_remaining = delay - passed_time_minutes
                    dl_remaining = delay * 60 - seconds
                    if dl_remaining <= 60:
                        show_secs = True
                    else:
                        show_secs = False
                    if show_secs == True:
                        wait = f"{dl_remaining:.0f} seconds"
                    elif show_secs == False:
                        wait = f"{delay_remaining:.0f} minutes"
            else:
                short_hours = float(f"{hours_remaining:.0f}") - 1
                short_hours_in_min = short_hours * 60
                delay_remaining = delay - passed_time_minutes - short_hours_in_min
                mins = delay_remaining
                wait = f"{short_hours:.0f} hours and {mins:.0f} minutes"
            # calculate difference, see if it works
            if seconds > delay * 60:
                time_check = True
            else:
                time_check = False
                delay_remaining = delay - passed_time_minutes
                splitted = last_slut_string.split(" ")
                splitted_two = splitted[0].split("-")
                splitted_three = splitted[1].split(":")
                splitted_four = splitted_three[2].split(".")
                year = int(splitted_two[0])
                day = int(splitted_two[2])
                hour = int(splitted_three[0])
                minute = int(splitted_three[1])
                month = int(splitted_two[1])
                second = int(splitted_four[0])
        # moving the block here for cleaner code
        if time_check == False:
            dt = datetime(year, month, day, hour, minute, second, 0, timezone(timedelta(hours=0)))
            dt = dt + timedelta(0, 0, 0, 0, delay, 0, 0)
            unix = int(dt.timestamp())
            color = self.discord_blue_rgb_code
            embed = discord.Embed(description=f"⏱ ️You cannot rob someone for {wait}.",
                                  color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return "success", "success"
        else:
            print("he can do it")

        """
        ACTUAL FUNCTION
        """

        # check if user you want to rob exists
        robbed_user, status = self.find_index_in_db(json_content["userdata"], user_to_rob, fail_safe=True)
        if (robbed_user == 0 and status == "error"):
            # we didnt find him
            color = self.discord_error_rgb_code
            embed = discord.Embed(description=f"❌ Invalid `<user>` argument given.\n\nUsage:\n`rob <user>`",
                                  color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return "success", "success"

        if str(user).strip() == str(user_to_rob).strip():
            # you cannot rob yourself
            color = self.discord_error_rgb_code
            embed = discord.Embed(description=f"❌ You cannot rob yourself!", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)
            return "success", "success"

        print(robbed_user)
        # you cannot rob from people who have less money than you
        robbed_user_data = json_content["userdata"][robbed_user]
        robbed_balance = robbed_user_data["cash"] + robbed_user_data["bank"]
        user_balance = json_user_content["cash"] + json_user_content["bank"]
        if robbed_balance < user_balance:
            lose_percentage = random.randint(rob_data["min_lose_amount_percentage"],
                                             rob_data["max_lose_amount_percentage"])
            balance = json_user_content["cash"] + json_user_content["bank"]
            loss = random.randint(1000, 7000)  # balance * (lose_percentage / 100)
            # round up, no floats
            loss = round(loss, 0)

            color = self.discord_error_rgb_code
            embed = discord.Embed(
                description=f"❌ You've been fined {str(self.currency_symbol)} **{'{:,}'.format(int(loss))}** for trying to rob a person more poor than you.",
                color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            await channel.send(embed=embed)

            return "success", "success"

        #
        # Normal robbing now
        #

        # so, explanation :
        # not actually using probabilites or so, just a random number between 1 and 2
        # and if for example probability is 50%, then the random num should be > 1.5 in order to win
        crime_success = random.randint(0, 100)

        if proba < crime_success:
            # LOST

            lose_phrases = random.choice(rob_data["lose_phrases"])
            lose_percentage = random.randint(rob_data["min_lose_amount_percentage"],
                                             rob_data["max_lose_amount_percentage"])
            balance = json_user_content["cash"] + json_user_content["bank"]
            loss = random.randint(10, 100)  # balance * (lose_percentage / 100)
            # round up, no floats
            loss = robbed_user_data["cash"] / 1000 * loss
            loss = round(loss, 0)
            print(lose_phrases, balance, loss)
            color = self.discord_error_rgb_code
            embed = discord.Embed(
                description=f"❌ {lose_phrases} {str(self.currency_symbol)} **{'{:,}'.format(int(loss))}**", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            embed.set_footer(text="robbing isn't cool")
            await channel.send(embed=embed)
            json_user_content["cash"] -= loss
            # update last slut time
            json_user_content["last_rob"] = str(now)
            # overwrite, end
            json_content["userdata"][user_index] = json_user_content
            self.overwrite_json(json_content)

            return "success", "success"

        else:
            # SUCCESS

            win_phrases = random.choice(rob_data["win_phrases"])
            gain_percentage = random.randint(rob_data["min_gain_amount_percentage"],
                                             rob_data["max_gain_amount_percentage"])

            robbed_cash = robbed_user_data["cash"]
            gain = robbed_cash * (gain_percentage / 100)

            # round up, no floats
            gain = round(gain, 0)
            color = self.discord_success_rgb_code
            embed = discord.Embed(
                description=f"✅ {win_phrases} {str(self.currency_symbol)} **{'{:,}'.format(int(gain))}**", color=color)
            embed.set_author(name=username, icon_url=user_pfp)
            embed.set_footer(text="lucky")
            await channel.send(embed=embed)
            json_user_content["cash"] += gain
            robbed_user_data["cash"] -= gain
            # update last slut time
            json_user_content["last_rob"] = str(now)
            # overwrite, end
            json_content["userdata"][user_index] = json_user_content
            self.overwrite_json(json_content)
            json_content["userdata"][robbed_user] = robbed_user_data
            self.overwrite_json(json_content)

            return "success", "success"

    # this code is never reached

    #
    # BALANCE
    #

    async def balance(self, user, channel, userbal_to_check, username_to_check, userpfp_to_check):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)
        # check if user exists
        # no need for fail_safe option because that is already checked in main.py before calling this function
        checked_user, status = self.find_index_in_db(json_content["userdata"], userbal_to_check)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][checked_user]
        check_cash = "{:,}".format(int(json_user_content["cash"]))
        check_bank = "{:,}".format(int(json_user_content["bank"]))
        check_bal = "{:,}".format(int(json_user_content["cash"] + json_user_content["bank"]))

        if datetime.now().minute < 10:
            min = "0"
        else:
            min = ""
        if datetime.now().hour < 10:
            hr = "0"
        else:
            hr = ""
        formatted_time = str(f"{hr}{datetime.now().hour}:{min}{datetime.now().minute}")

        color = self.discord_blue_rgb_code
        embed = discord.Embed(color=color)
        embed.add_field(name="**Cash**", value=f"{str(self.currency_symbol)} {check_cash}", inline=True)
        embed.add_field(name="**Bank**", value=f"{str(self.currency_symbol)} {check_bank}", inline=True)
        embed.add_field(name="**Net Worth:**", value=f"{str(self.currency_symbol)} {check_bal}", inline=True)
        embed.set_author(name=username_to_check, icon_url=userpfp_to_check)
        embed.set_footer(text=f"today at {formatted_time}")
        await channel.send(embed=embed)

        return

    async def stats(self, user, channel, userbal_to_check, username_to_check, userpfp_to_check):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)
        # check if user exists
        # no need for fail_safe option because that is already checked in main.py before calling this function
        checked_user, status = self.find_index_in_db(json_content["userdata"], userbal_to_check)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][checked_user]
        work_mult = json_user_content["work_mult"]
        crime_mult = json_user_content["crime_mult"]
        daily_mult = json_user_content["daily_mult"]
        slut_mult = json_user_content["slut_mult"]
        last_work = json_user_content["last_work"]
        last_crime = json_user_content["last_crime"]
        last_slut = json_user_content["last_slut"]
        last_daily = json_user_content["last_daily"]
        last_rob = json_user_content["last_rob"]
        chicken_rate = json_user_content["rate"]
        if last_crime != "none":
            splitted = last_crime.split(" ")
            splitted_two = splitted[0].split("-")
            splitted_three = splitted[1].split(":")
            splitted_four = splitted_three[2].split(".")
            year = int(splitted_two[0])
            day = int(splitted_two[2])
            hour = int(splitted_three[0])
            minute = int(splitted_three[1])
            month = int(splitted_two[1])
            second = int(splitted_four[0])
            dt = datetime(year, month, day, hour, minute, second, 0, timezone(timedelta(hours=0)))
            last_crime = f"<t:{int(dt.timestamp())}>"
        if last_slut != "none":
            splitted = last_slut.split(" ")
            splitted_two = splitted[0].split("-")
            splitted_three = splitted[1].split(":")
            splitted_four = splitted_three[2].split(".")
            year = int(splitted_two[0])
            day = int(splitted_two[2])
            hour = int(splitted_three[0])
            minute = int(splitted_three[1])
            month = int(splitted_two[1])
            second = int(splitted_four[0])
            dt = datetime(year, month, day, hour, minute, second, 0, timezone(timedelta(hours=0)))
            last_slut = f"<t:{int(dt.timestamp())}>"
        if last_work != "none":
            splitted = last_work.split(" ")
            splitted_two = splitted[0].split("-")
            splitted_three = splitted[1].split(":")
            splitted_four = splitted_three[2].split(".")
            year = int(splitted_two[0])
            day = int(splitted_two[2])
            hour = int(splitted_three[0])
            minute = int(splitted_three[1])
            month = int(splitted_two[1])
            second = int(splitted_four[0])
            dt = datetime(year, month, day, hour, minute, second, 0, timezone(timedelta(hours=0)))
            last_work = f"<t:{int(dt.timestamp())}>"
        if last_daily != "none":
            splitted = last_daily.split(" ")
            splitted_two = splitted[0].split("-")
            splitted_three = splitted[1].split(":")
            splitted_four = splitted_three[2].split(".")
            year = int(splitted_two[0])
            day = int(splitted_two[2])
            hour = int(splitted_three[0])
            minute = int(splitted_three[1])
            month = int(splitted_two[1])
            second = int(splitted_four[0])
            dt = datetime(year, month, day, hour, minute, second, 0, timezone(timedelta(hours=0)))
            last_daily = f"<t:{int(dt.timestamp())}>"
        if last_rob != "none":
            splitted = last_rob.split(" ")
            splitted_two = splitted[0].split("-")
            splitted_three = splitted[1].split(":")
            splitted_four = splitted_three[2].split(".")
            year = int(splitted_two[0])
            day = int(splitted_two[2])
            hour = int(splitted_three[0])
            minute = int(splitted_three[1])
            month = int(splitted_two[1])
            second = int(splitted_four[0])
            dt = datetime(year, month, day, hour, minute, second, 0, timezone(timedelta(hours=0)))
            last_rob = f"<t:{int(dt.timestamp())}>"

        if datetime.now().minute < 10:
            min = "0"
        else:
            min = ""
        if datetime.now().hour < 10:
            hr = "0"
        else:
            hr = ""
        formatted_time = str(f"{hr}{datetime.now().hour}:{min}{datetime.now().minute}")

        color = self.discord_blue_rgb_code
        embed = discord.Embed(color=color)
        embed.add_field(name="**Chicken Rate 🐓**", value=f"{chicken_rate}%", inline=False)
        embed.add_field(name="**Multiplicators**",
                        value=f"**Slut:** *x{slut_mult}*\n**Work:** *x{work_mult}*\n**Daily:** *x{daily_mult}*\n**Crime:** *x{crime_mult}*",
                        inline=False)
        embed.add_field(name="**Last Done:**",
                        value=f"**Slut:** {last_slut}\n**Work:** {last_work}\n**Daily:** {last_daily}\n**Crime:** {last_crime}\n**Rob:** {last_rob}",
                        inline=False)
        embed.set_author(name=username_to_check, icon_url=userpfp_to_check)
        embed.set_footer(text=f"today at {formatted_time}")
        await channel.send(embed=embed)

        return

    #
    # DEPOSIT
    #

    async def deposit(self, user, channel, username, user_pfp, amount):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]

        user_cash = json_user_content["cash"]

        if amount == "all":
            amount = user_cash
            if amount < 0:
                return "error", "❌ No negative values."
        elif amount == "half":
            amount = round((user_cash / 2))
            if amount < 0:
                return "error", "❌ No negative values."
        else:
            amount = int(float(amount))
            if amount > user_cash:
                return "error", f"❌ You don't have that much money to deposit. You currently have {str(self.currency_symbol)} {'{:,}'.format(user_cash)} on hand."

        json_user_content["cash"] -= amount
        json_user_content["bank"] += amount

        color = self.discord_success_rgb_code
        embed = discord.Embed(
            description=f"✅ Deposited {str(self.currency_symbol)} {'{:,}'.format(int(amount))} to your bank!",
            color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        await channel.send(embed=embed)

        # overwrite, end
        json_content["userdata"][user_index] = json_user_content
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # WITHDRAW
    #

    async def withdraw(self, user, channel, username, user_pfp, amount):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]

        user_bank = json_user_content["bank"]

        if amount == "all":
            amount = user_bank
            if amount < 0:
                return "error", "❌ No negative values."
        elif amount == "half":
            amount = round((user_bank / 2))
            if amount < 0:
                return "error", "❌ No negative values."
        else:
            amount = int(float(amount))
            if amount > user_bank:
                return "error", f"❌ You don't have that much money to withdraw. You currently have {str(self.currency_symbol)} {'{:,}'.format(user_bank)} in the bank."

        json_user_content["cash"] += amount
        json_user_content["bank"] -= amount

        color = self.discord_success_rgb_code
        embed = discord.Embed(
            description=f"✅ Withdrew {str(self.currency_symbol)} {'{:,}'.format(int(amount))} from your bank!",
            color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        await channel.send(embed=embed)

        # overwrite, end
        json_content["userdata"][user_index] = json_user_content
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # GIVE
    #

    async def give(self, user, channel, username, user_pfp, reception_user, amount, recept_uname):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)
        reception_user_index, new_data = self.find_index_in_db(json_content["userdata"], reception_user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]
        json_recept_content = json_content["userdata"][reception_user_index]

        user_cash = json_user_content["cash"]
        recept_cash = json_recept_content["cash"]

        if amount == "all":
            amount = user_cash
            if amount < 0:
                return "error", "❌ No negative values."
        elif amount == "half":
            amount = round((user_cash / 2))
            if amount < 0:
                return "error", "❌ No negative values."
        else:
            amount = int(amount)
            if amount > user_cash:
                return "error", f"❌ You don't have that much money to give. You currently have {str(self.currency_symbol)} {'{:,}'.format(int(user_cash))} in the bank."

        json_user_content["cash"] -= amount
        json_recept_content["cash"] += amount

        # inform user
        color = self.discord_success_rgb_code
        embed = discord.Embed(
            description=f"✅ <@{recept_uname.id}> has received your {str(self.currency_symbol)} {'{:,}'.format(int(amount))}",
            color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        await channel.send(embed=embed)

        # overwrite, end
        json_content["userdata"][user_index] = json_user_content
        json_content["userdata"][reception_user_index] = json_recept_content
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # LEADERBOARD
    #

    async def leaderboard(self, user, channel, username, full_name, page_number, mode_type, client):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_user_content = json_content["userdata"][user_index]

        """
        sorting algorithm
        """
        # yes, i could use a dict
        all_users = []
        all_bal = []
        i = 0
        for i in range(len(json_content["userdata"])):
            all_users.append(json_content["userdata"][i]["user_id"])
            if mode_type == "-cash":
                all_bal.append(int(json_content["userdata"][i]["cash"]))
            elif mode_type == "-bank":
                all_bal.append(int(json_content["userdata"][i]["bank"]))
            else:  # elif mode_type == "-total":
                print(json_content["userdata"][i]["cash"] + json_content["userdata"][i]["bank"])
                all_bal.append(int(json_content["userdata"][i]["cash"] + json_content["userdata"][i]["bank"]))
        print(all_bal)
        # so, data is set, now sort
        i = -1
        while i <= len(all_bal):
            i += 1
            try:
                if all_bal[i] < all_bal[i + 1]:
                    # save the higher stats one into buffer
                    saved = all_bal[i]
                    # this one has lower stats, so move him right
                    all_bal[i] = all_bal[i + 1]
                    # the higher one (saved) takes that position
                    all_bal[i + 1] = saved
                    # repeat process, but for the player-names
                    saved = all_users[i]
                    all_users[i] = all_users[i + 1]
                    all_users[i + 1] = saved
                    i = -1
            except:
                pass

        i = 0
        # use names instead of just ID, except if we cannot find names
        # so for example if someone left the server
        for i in range(len(all_users)):
            try:
                name_object = await client.fetch_user(int(all_users[i]))
                print(i, all_users[i], name_object)
                actual_name = str(name_object)
                if all_users[i] == user:
                    user_lb_position = i + 1
            except:
                actual_name = str(all_users[i])
            # update
            all_users[i] = actual_name

        i = 0
        # making nice number formats
        for i in range(len(all_bal)):
            all_bal[i] = '{:,}'.format(all_bal[i])

        # making the formatted output description
        # number of pages which will be needed :
        # we have 10 ranks per page
        ranks_per_page = 10
        page_count = len(all_bal) / ranks_per_page
        if ".0" in str(page_count): page_count = int(page_count)
        if not isinstance(page_count, int):
            page_count += 1
        # page_count = (len(all_bal) + ranks_per_page - 1)
        # round number up
        total_pages = round(page_count)

        # our selection !
        index_start = (page_number - 1) * ranks_per_page
        index_end = index_start + ranks_per_page
        user_selection = all_users[index_start: index_end]
        bal_selection = all_bal[index_start: index_end]

        # making the formatted !
        i = 0
        leaderboard_formatted = f""
        for i in range(len(user_selection)):
            leaderboard_formatted += f"\n**{str(i + 1)}.** {user_selection[i]} • {str(self.currency_symbol)} {bal_selection[i]}"

        # making a nice output
        if total_pages == 1:
            page_number = 1
        elif page_number > total_pages:
            page_number = 1

        # inform user
        color = self.discord_blue_rgb_code
        embed = discord.Embed(description=f"\n\n{leaderboard_formatted}", color=color)
        # same pfp as unbelievaboat uses
        embed.set_author(name=full_name,
                         icon_url="https://media.discordapp.net/attachments/506838906872922145/506899959816126493/h5D6Ei0.png")
        if user_lb_position == 1:
            pos_name = "st"
        elif user_lb_position == 2:
            pos_name = "nd"
        elif user_lb_position == 3:
            pos_name = "rd"
        pos_name = "th"
        embed.set_footer(
            text=f"Page {page_number}/{total_pages}  •  Your leaderboard rank: {user_lb_position}{pos_name}")
        await channel.send(embed=embed)

        return "success", "success"

    #
    # MODULE INFO
    #

    async def module(self, user, channel, module):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        """
        variable_dict = {
            "slut": 0,
            "crime": 1,
            "work": 2,
            "rob": 3
        }
        """

        if module not in self.variable_dict.keys() and module not in ["symbols", "currency_symbol"]:
            possible = "slut, crime, work, rob, symbols"
            return "error", f"Module not found. Possibilites : {possible}"

        if module in ["symbols", "currency_symbol"]:
            info_output = f"""Symbol:\nname: {json_content['symbols'][0]['name']}, value: emoji "{json_content['symbols'][0]['symbol_emoji']}" """
        else:
            module_index = self.variable_dict[module]
            info_output = f"Module: **{module}** info:\nOutput as : <variable name> ; <value>\n```"
            mod = json_content["variables"][module_index]
            module_content = json_content["variables"][module_index]
            for i in range(len(module_content)):
                module_content_vars = list(json_content["variables"][module_index].keys())[i]

                info_output += f'\n"{module_content_vars}" ; {mod[module_content_vars]}'
            info_output += "\n```\n**Note**: Delay is in minutes, proba is x%, percentages are in % too"
        await channel.send(info_output)

        return "success", "success"

    #
    # ADD-MONEY
    #

    async def add_money(self, user, channel, username, user_pfp, reception_user, amount, recept_uname):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        reception_user_index, new_data = self.find_index_in_db(json_content["userdata"], reception_user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_recept_content = json_content["userdata"][reception_user_index]

        json_recept_content["cash"] += int(amount)

        # inform user
        color = self.discord_success_rgb_code
        embed = discord.Embed(
            description=f"✅  Added {str(self.currency_symbol)} {'{:,}'.format(int(amount))} to <@{recept_uname.id}>'s cash balance",
            color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        await channel.send(embed=embed)

        # overwrite, end
        json_content["userdata"][reception_user_index] = json_recept_content
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # REMOVE-MONEY
    #

    async def remove_money(self, user, channel, username, user_pfp, reception_user, amount, recept_uname):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)
        reception_user_index, new_data = self.find_index_in_db(json_content["userdata"], reception_user)

        if new_data != "none":
            json_content["userdata"] = new_data

        json_recept_content = json_content["userdata"][reception_user_index]

        json_recept_content["cash"] -= int(amount)

        # inform user
        color = self.discord_success_rgb_code
        embed = discord.Embed(
            description=f"✅  Removed {str(self.currency_symbol)} {'{:,}'.format(int(amount))} from <@{recept_uname.id}>'s cash balance",
            color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        await channel.send(embed=embed)

        # overwrite, end
        json_content["userdata"][reception_user_index] = json_recept_content
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # EDIT VARIABLES
    #

    async def edit_variables(self, user, channel, username, user_pfp, module_name, variable_name, new_value):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        if module_name not in self.variable_dict.keys():
            return "error", "module not found"
        module_index = self.variable_dict[module_name]

        json_module_content = json_content["variables"][module_index]
        try:
            old_value = json_module_content[variable_name]
        except:
            return "error", f"variable name of module {module_name} not found"

        # changing value
        json_module_content[variable_name] = new_value

        # not asking for verification, would just have to reverse by another edit
        # inform user
        color = self.discord_success_rgb_code
        embed = discord.Embed(
            description=f"✅  Changed variable '{variable_name}' of module '{module_name}'\nBefore: '{old_value}'. Now: '{new_value}'",
            color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        await channel.send(embed=embed)

        # overwrite, end
        json_content["variables"][module_index] = json_module_content
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # EDIT CURRENCY SYMBOL
    #

    async def change_currency_symbol(self, user, channel, username, user_pfp, new_emoji_name):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        json_emoji = json_content["symbols"][0]

        old_value = json_emoji["symbol_emoji"]

        test_emoji = self.get_currency_symbol(True, new_emoji_name)
        if test_emoji == "error":
            return "error", "Emoji not found."

        # changing value
        json_emoji["symbol_emoji"] = new_emoji_name

        # not asking for verification, would just have to reverse by another edit
        # inform user
        color = self.discord_success_rgb_code
        embed = discord.Embed(description=f"✅  Changed emoji from '{old_value}' to '{new_emoji_name}'", color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        await channel.send(embed=embed)

        # overwrite, end
        json_content["symbols"][0] = json_emoji
        self.overwrite_json(json_content)

        return "success", "success"

    """
    ITEM HANDLING
    """

    #
    # CREATE NEW ITEM
    #

    async def create_new_item(self, item_name, cost, description, duration, stock, roles_id_required, roles_id_to_give,
                              roles_id_to_remove, max_bal, reply_message):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        json_items = json_content["items"]

        for i in range(len(json_items)):
            if json_items[i]["name"] == item_name:
                return "error", "Item with such name already exists."

        # calculate item duration
        today = datetime.today()
        print(today)
        expiration_date = today + timedelta(days=duration)

        print("expiration date : ", expiration_date)

        json_items.append({
            "name": item_name,
            "price": cost,
            "description": description,
            "duration": duration,
            "amount_in_stock": stock,
            "required_roles": roles_id_required,
            "given_roles": roles_id_to_give,
            "removed_roles": roles_id_to_remove,
            "maximum_balance": max_bal,
            "reply_message": reply_message,
            "expiration_date": str(expiration_date)
        })

        # overwrite, end
        json_content["items"] = json_items
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # REMOVE ITEM
    #

    async def remove_item(self, item_name):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        json_items = json_content["items"]
        item_found = item_index = 0
        for i in range(len(json_items)):
            if json_items[i]["name"] == item_name:
                item_found = 1
                item_index = i
        if not item_found:
            return "error", "Item not found."

        # delete from the "items" section
        json_items.pop(item_index)

        # delete for everyone who had it in their inventory
        user_content = json_content["userdata"]
        for i in range(len(user_content)):
            # tricky
            # i suppose the variable type will either be a string with "none"
            # or a list with lists : ["item_name", amount], so items = [ [], [] ] etc
            if user_content[i]["items"] == "none":
                pass
            else:
                try:
                    for ii in range(len(user_content[i]["items"])):
                        print(user_content[i]["items"][ii])
                        current_name = user_content[i]["items"][ii][0]
                        if current_name == item_name:
                            user_content[i]["items"].pop(ii)
                except Exception as e:
                    print(e)

        # overwrite, end
        json_content["items"] = json_items
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # BUY ITEM
    #

    async def buy_item(self, user, channel, username, user_pfp, item_name, amount, user_roles, server_object,
                       user_object):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        json_items = json_content["items"]
        item_found = item_index = 0
        for i in range(len(json_items)):
            if json_items[i]["name"] == item_name:
                item_found = 1
                item_index = i
        if not item_found:
            return "error", "Item not found."
        item = json_items[item_index]
        # get variables
        item_name = item_name
        item_price = item["price"]
        req_roles = item["required_roles"]
        give_roles = item["given_roles"]
        rem_roles = item["removed_roles"]
        max_bal = item["maximum_balance"]
        remaining_stock = item["amount_in_stock"]
        expiration_date = item["expiration_date"]
        reply_message = item["reply_message"]

        # calculate expiration
        today = datetime.today()
        expire = datetime.strptime(expiration_date, "%Y-%m-%d %H:%M:%S.%f")
        if today > expire:
            return "error", f"Item has already expired. Expiring date was {expiration_date}"
        # else we're good

        # 1. check req roles
        try:
            if req_roles == "none":
                pass
            else:
                for i in range(len(req_roles)):
                    if int(req_roles[i]) not in user_roles:
                        return "error", f"User does not seem to have all required roles."
        except Exception as e:
            print(e)
            return "error", f"Unexpected error."

        # 2. check give roles
        try:
            if rem_roles == "none":
                pass
            else:
                for i in range(len(rem_roles)):
                    role = discord.utils.get(server_object.roles, id=int(rem_roles[i]))
                    print(role)
                    await user_object.remove_roles(role)
        except Exception as e:
            print(e)
            return "error", f"Unexpected error."

        # 3. check rem roles
        try:
            if req_roles == "none":
                pass
            else:
                for i in range(len(give_roles)):
                    role = discord.utils.get(server_object.roles, id=int(give_roles[i]))
                    print(role)
                    await user_object.add_roles(role)
        except Exception as e:
            print(e)
            return "error", f"Unexpected error."

        # 4. check if enough money
        sum_price = item_price * amount
        sum_price = round(sum_price, 0)
        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)
        user_content = json_content["userdata"][user_index]
        user_cash = user_content["cash"]
        if user_cash < sum_price:
            return "error", f"Error! Not enough money in cash to purchase.\nto pay: {sum_price} ; in cash: {user_cash}"

        # 5. check if not too much money
        user_bank = user_content["bank"]
        if max_bal != "none":
            if (user_bank + user_cash) > max_bal:
                return "error", f"Error! You have too much money to purchase.\nnet worth: {'{:,}'.format(int(user_bank + user_cash))} ; max bal: {max_bal}"

        # 6. check if enough in stock or not
        if max_bal != "none":
            if remaining_stock <= 0:
                return "error", f"Error! Item not in stock."
            elif amount > remaining_stock:
                return "error", f"Error! Not enough remaining in stock ({remaining_stock} remaining)."

        # 8. rem money, substract stock, print message, add to inventory
        user_content["cash"] -= sum_price
        item["amount_in_stock"] -= amount

        if user_content["items"] == "none":
            user_content["items"] = [[item_name, amount]]
        else:
            user_content["items"].append([item_name, amount])

        color = self.discord_blue_rgb_code
        embed = discord.Embed(
            description=f"You have bought {amount} {item_name} and paid {str(self.currency_symbol)} **{'{:,}'.format(int(sum_price))}**",
            color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        embed.set_footer(text=reply_message)
        await channel.send(embed=embed)

        # overwrite, end
        json_content["userdata"][user_index] = user_content
        json_content["items"] = json_items
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # CHECK INVENTORY
    #

    async def check_inventory(self, user, channel, username, user_pfp):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        user_index, new_data = self.find_index_in_db(json_content["userdata"], user)
        user_content = json_content["userdata"][user_index]

        items = user_content["items"]
        if items == "none":
            inventory_checkup = "**Inventory empty. No items owned.**"
        else:
            inventory_checkup = ""
            for i in range(len(items)):
                inventory_checkup += f"Item: `{items[i][0]}`; amount: `{items[i][1]}`\n"

        color = self.discord_blue_rgb_code
        embed = discord.Embed(title="Owned Items", description=f"{inventory_checkup}", color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        embed.set_footer(text="nice")
        await channel.send(embed=embed)

        # overwrite, end
        # not needed

        return "success", "success"

    #
    # CATALOG
    #

    async def catalog(self, user, channel, username, user_pfp, item_check, server_object):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        items = json_content["items"]
        catalog_report = "__Items catalog:__\n```\n"
        if item_check == "default_list":
            for i in range(len(items)):
                catalog_report += f"Item {i}: {items[i]['name']}\n"
            catalog_report += "\n```\n*For details about an item: use* `catalog <item name>`"

        else:
            check = 0
            for i in range(len(items)):
                if items[i]["name"] == item_check:
                    check = 1
                    item_index = i
            if not check:
                return "error", "Error! Item not found."
            else:  # not needed, but for readability
                catalog_report = f"__Item {items[item_index]['name']} catalog:__\n\n"

                req_roles = ""
                for ii in range(len(items[item_index]["required_roles"])):
                    role = discord.utils.get(server_object.roles, id=int(items[item_index]["required_roles"][ii]))
                    req_roles += f"@{str(role)} "

                give_roles = ""
                for iii in range(len(items[item_index]["given_roles"])):
                    role = discord.utils.get(server_object.roles, id=int(items[item_index]["given_roles"][iii]))
                    give_roles += f"@{str(role)} "

                rem_roles = ""
                for iiii in range(len(items[item_index]["removed_roles"])):
                    role = discord.utils.get(server_object.roles, id=int(items[item_index]["removed_roles"][iiii]))
                    rem_roles += f"@{str(role)} "

                catalog_report += f"Item name: \"{items[item_index]['name']}\"\n" \
                                  f"Item price: {items[item_index]['price']}\n" \
                                  f"Item description: \"{items[item_index]['description']}\"\n" \
                                  f"Remaining time: item expires on the {str(items[item_index]['expiration_date'])[:10]}\n" \
                                  f"Amount remaining: {items[item_index]['amount_in_stock']} in stock\n" \
                                  f"Maximum balance to purchase: {self.currency_symbol} {items[item_index]['maximum_balance']}\n" \
                                  f"Required roles: {req_roles}\n" \
                                  f"Given roles: {give_roles}\n" \
                                  f"Removed roles: {rem_roles}\n"

                catalog_report += "---------------------------------"

        await channel.send(catalog_report)

        # overwrite, end
        # not needed

        return "success", "success"

    #
    # ROLE INCOMES - NEW ONE
    #

    async def new_income_role(self, user, channel, username, user_pfp, income_role_id, income):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        json_income_roles = json_content["income_roles"]

        for i in range(len(json_income_roles)):
            if json_income_roles[i]["role_id"] == income_role_id:
                return "error", "Role already exists as income role."

        json_income_roles.append({
            "role_id": income_role_id,
            "role_income": income
        })

        color = self.discord_blue_rgb_code
        embed = discord.Embed(
            description=f"New income role added.\nrole_id : {income_role_id}, income : {str(self.currency_symbol)} **{'{:,}'.format(int(income))}**",
            color=color)
        embed.set_author(name=username, icon_url=user_pfp)
        embed.set_footer(text="smooth")
        await channel.send(embed=embed)

        # overwrite, end
        json_content["income_roles"] = json_income_roles
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # ROLE INCOMES - REMOVE ONE
    #

    async def remove_income_role(self, user, channel, username, user_pfp, income_role_id):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        json_income_roles = json_content["income_roles"]
        role_found = role_index = 0
        for i in range(len(json_income_roles)):
            if json_income_roles[i]["role_id"] == income_role_id:
                role_found = 1
                role_index = i
        if not role_found:
            return "error", "Role not found."

        # delete from the "items" section
        json_income_roles.pop(role_index)

        # overwrite, end
        json_content["income_roles"] = json_income_roles
        self.overwrite_json(json_content)

        return "success", "success"

    #
    # ROLE INCOMES - LIST
    #

    async def list_income_roles(self, user, channel, username, user_pfp, server_object):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        json_income_roles = json_content["income_roles"]

        role_list_report = f"__Income Roles List:__\n\n"

        for i in range(len(json_income_roles)):
            role = discord.utils.get(server_object.roles, id=int(json_income_roles[i]["role_id"]))
            ping_role = f"@{str(role)}"

            role_list_report += f"Role name: \"{ping_role}\"\n" \
                                f"Role income: {self.currency_symbol} {'{:,}'.format(json_income_roles[i]['role_income'])}\n\n"

        role_list_report += "---------------------------------"

        await channel.send(role_list_report)

        # overwrite, end
        # not needed

        return "success", "success"

    #
    # ROLE INCOMES - UPDATE INCOMES
    #

    async def update_incomes(self, user, channel, username, user_pfp, server_object):
        # load json
        json_file = open(self.pathToJson, "r")
        json_content = json.load(json_file)

        json_income_roles = json_content["income_roles"]
        user_content = json_content["userdata"]

        # pretty straight forward i think.
        # first, we go into each role object
        # then we check in everyones roles if they have the role

        for role_index in range(len(json_income_roles)):
            role_id = json_income_roles[role_index]["role_id"]

            role = discord.utils.get(server_object.roles, id=int(role_id))
            for member in role.members:
                try:
                    # also to create user in case he isnt registered yet
                    user_index, new_data = self.find_index_in_db(json_content["userdata"], member.id)

                    json_user_content = json_content["userdata"][user_index]
                    json_user_content["bank"] += json_income_roles[role_index]["role_income"]
                    # overwrite
                    json_content["userdata"][user_index] = json_user_content

                except:
                    pass

        # overwrite, end
        json_content["income_roles"] = json_income_roles
        self.overwrite_json(json_content)

        return "success", "success"
