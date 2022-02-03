# **UnbelievaBoat-like Discord Bot in python**
### For questions about the bot and how to set it up: ask me on Discord at *<Kendrik 2.0#7373>*

### Forker Note: my discord is hoemotion#2854, don't even try running this if you never used python. Also don't dm me with stupid questions, only if you're getting errors or have some suggestions etc. lmao
> there's no fucking way i got terminated lmao (5th time yet)

Code isn't finished yet.

### - Info
The Bot uses most of UnbelievaBoat's commands for minigames and economy (not moderation tho). 
#### For a full list, see `src/command_list.txt`.
It emerged from the problem of UB having a balance ceiling and no automated role-income increasing to user's balances.

### - Goal
The goal was to make a easily customizable Template of a discord bot, also fixing the issues stated above.
You can use and adjust the code as you want so it fits your needs.

### - Install & Use
1. Create a Discord Application for your bot (see https://youtu.be/b61kcgfOm_4, https://discord.com/developers/applications)
2. In the Discord Dev Portal, in the "Bot" tab of your application, **enable presence intent, server members intent and message intent**.
3. Download the code, structured as in this repo.
4. Open the `main.py` file, line 15 and change the **token** to the one of your created bot or if you're on replit, create a secret with your token and call the secret token.
5. If you want log info : In `main.py`, go to line 88 and put a channel ID of the server you want to use the bot in. (Activate Developer Mode Discord to copy channel IDs). This channel will be used to send information about the bot status. Also uncomment line 88, 93, 94, 100 and 109
6. In the `database/database.json` file: scroll down to the symbols part and put a *custom emoji id* in the "symbol_emoji" variable. It It can be any emoji from one of the servers your bot is in.
7. Invite the bot to your server as shown in https://youtu.be/b61kcgfOm_4
8. Install python3 if you dont have it
9. Install the Discord Api Wrapper for python3 using pip (`pip install discord.py`)
10. In the owners.json file, add your user id and the user id of other bot developers for having access to exclusive commands (such as add-money etc.).
11. Launch main.py with **python3**.
You should be good to go!

### - Not implemented:
`russian-roulette`
### - Implemented but not available with original UnbelievaBoat
`daily` - Simple daily command for getting an amount of money

`upgrade` - You can upgrade the multiplicator of daily, work, crime and slut (costs 10k each x0.1 more)

`stats` - this is not the unbelieva stats command! This shows the stats of a user like his chicken winning rate, his last work, etc. and his multiplicators

`unix timestamps` tells us the exact time of something

*If the bot appears as online in the sidebar, try gghelpeconomy for a commands list*
