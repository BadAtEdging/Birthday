# Birthday

This is a bot to keep track of birthdays on a discord server.

# Installation:

Create a bot in discord developer portal and copy it's token to the file
`bot_token.py`
with contents:
```
BOT_TOKEN = {insert your token}
```

Then, run

```
pip install -r requirements.tx
```

to install required python libraries


Then create the database using

```
python data.py
```

Then run the bot using

```
python bot.py
```
# Setup

First, run `>set_birthday_channel {channel name in text}` to set the channel you wish to receive birthday notifications in.

# The commands

`>delete_member [member]`

Delete all information of a member from database. Deletes your own information if username not specified. Requires admin if member is not yourself.

`>invite_link `

Print bot invite link.

`>[list_birthdays|list_bd] `

List the birthdays of all users, starting from the closest birthday.

`>manual_timezone_update`

Manually update verified and location roles, done automatically every hour. This command should be unnecessary, unless something goes wrong.

`>[set_all_birthday_messages|set_msg] <message>`

Set the birthday message of everyone to a string, must contain <@> which is syntax for user mention.

`>[set_birthday|set_bd] [member] <birthday_in_local_time>`

Set the birthday of a user to specified datetime given in their local time. Requires admin if member is not yourself. Example: ">set_bd @username april 1 13:37"

`>set_birthday_channel <channel_name>`

Set birthday channel name (as mentioned in setup).

`>[set_timezone|set_tz] <timezone> [member]`

Set the timezone of a member to specified value. If member is not given, changes your own timezone. Requires admin if member is not yourself.

# Example setup and usage.

Let's assume a user named User#0000 wishes to set his birthday as 5 minutes from the current time 18:38 and receive notification of the format 'Happy birthday <@>, long live <@>!' in channel called `bot-shit`.

First, they would set birthday channel:
`>set_birthday_channel bot-shit`
Birthday channel name set to: bot-shit

Next, set message to specified format:
`>set_msg Happy birthday <@>, long live <@>!`
Birthday message set to: Happy birthday <@>, long live <@>!

Next, set correct timezone:
`>set_tz America/Chicago`
Timezone of User#0000 set as America/Chicago, local time: 2020-09-07 18:38

Finally, they would set their birthday:
`>set_bd @User 18:43`
Setting birthday of @User as 2020-09-07 18:43:00

After that, User#0000 should be notified in channel `bot-shit`
With the following message:
Happy birthday @User, long live @User!
