import discord
from discord.ext import commands, tasks
from discord.utils import get

import pytz
from dateutil import parser

import config
from data import Data
from datetime import *

from time_util import time_until
import sys

bot = commands.Bot(command_prefix='>')

@bot.event
async def on_ready():
    print('------------------------------')
    timezone_update_loop.start()
    birthday_update_loop.start()

@bot.event
async def on_member_update(before, after):
    if get(after.roles,name='verified'):
        Data.set_elem(after.guild.id,after.id,'is_verified',1)
    else:
        Data.set_elem(after.guild.id,after.id,'is_verified',0)
    found = False
    for region in config.REGION_TZ.keys():
        if get(after.roles,name=region):
            found = True
            # print(after.guild.id,after.id)
            Data.set_elem(after.guild.id,after.id,'region',region)
    if not found:
        # print('not found')
        Data.delete_region(after.guild.id,after.id)
    update_timestamp(after.guild.id,after.id)

@bot.event
async def on_member_remove(member):
    await timezone_update(member.guild)

@bot.command(help='Print bot invite link.')
async def invite_link(ctx):
    await ctx.send('<https://discord.com/api/oauth2/authorize?client_id=748726425917456406&permissions=523328&scope=bot>')

@bot.command(aliases=['set_bd'],help='Set the birthday of a user to specified datetime given in their local time. Requires admin if member is not yourself. Example: ">set_bd @username april 1 13:37"')
async def set_birthday(ctx, member: discord.Member=None, *, birthday_in_local_time):
    if member is None:
        member = ctx.author
    is_admin = ctx.author.guild_permissions.administrator
    if ctx.author != member and not is_admin:
        ctx.send("You need to be admin to change data of other people!")
        return
    any_birthday_local = parser.parse(birthday_in_local_time)
    await ctx.send(f'Setting birthday of <@{member.id}> as {any_birthday_local}')
    Data.set_elem(ctx.guild.id,member.id,'any_birthday_local',any_birthday_local)
    update_timestamp(ctx.guild.id,member.id)


@bot.command(aliases=['list_bd'],help='List the birthdays of all users, starting from the closest birthday.')
async def list_birthdays(ctx):
    message = []
    message.append('** BIRTHDAYS: **')
    people = Data.all_birthdays(ctx.guild.id)
    for (member_id, birthday) in people:
        member = get(bot.get_all_members(),id=member_id)
        message.append(f'{member} on {birthday.date()} (in {time_until(birthday)})')
    await ctx.send('\n'.join(message))

@bot.command(help='Delete all information of a member from database. Deletes your own information if username not specified. Requires admin if member is not yourself.')
async def delete_member(ctx, member: discord.Member=None):
    if member is None:
        member = ctx.author
    is_admin = ctx.author.guild_permissions.administrator
    if ctx.author != member and not is_admin:
        ctx.send("You need to be admin to change data of other people!")
        return
    Data.delete_member(ctx.guild.id,member.id)
    await ctx.send(f"Deleted {member}'s info (guild = {ctx.guild})")

def update_timestamp(guild_id,member_id):
    timezone = Data.get_timezone(guild_id,member_id)
    any_birthday_local = Data.get_any_birthday_local(guild_id,member_id)
    last_announced_utc = Data.get_last_announced_utc(guild_id,member_id)
    if timezone is None or any_birthday_local is None:
        return
    any_birthday_local = timezone.localize(any_birthday_local)
    birthday_utc = any_birthday_local.astimezone(pytz.utc)
    utc_dt = datetime.now(pytz.utc)

    birthday_utc = birthday_utc.replace(tzinfo=None)
    utc_dt = utc_dt.replace(tzinfo=None)
    while birthday_utc-utc_dt > timedelta(days=365):
        birthday_utc = birthday_utc.replace(year=birthday_utc.year-1)
    while utc_dt-birthday_utc > timedelta(days=366):
        birthday_utc = birthday_utc.replace(year=birthday_utc.year+1)
    if last_announced_utc is not None:
        while birthday_utc-last_announced_utc < timedelta(minutes=1):
            birthday_utc = birthday_utc.replace(year=birthday_utc.year+1)
    Data.set_elem(guild_id,member_id,'next_birthday_utc',birthday_utc)

async def timezone_update(guild):
    Data.unset_roles(guild.id)
    birthday_channel = get(guild.channels,name=config.BIRTHDAY_CHANNEL)
    verified_role = get(guild.roles,name='verified')
    if verified_role is not None:
        for member in verified_role.members:
            Data.set_elem(guild.id,member.id,'is_verified',1)
    for region in config.REGION_TZ.keys():
        region_role = get(guild.roles,name=region)
        if region_role is not None:
            members = region_role.members
            # await birthday_channel.send(f'{region_role} members in {guild}: {members}')
            for member in members:
                Data.set_elem(guild.id,member.id,'region',region_role.name)
    for member in guild.members:
        update_timestamp(guild.id,member.id)

@bot.command(help='Manually update verified and location roles, done automatically every hour. This command should be unnecessary, unless something goes wrong.')
async def manual_timezone_update(ctx):
    await timezone_update(ctx.guild)

@tasks.loop(hours=1)
async def timezone_update_loop():
    for guild in bot.guilds:
        await timezone_update(guild)

@tasks.loop(seconds=1)
async def birthday_update_loop():
    guild_id, member_id, next_birthday_utc = Data.next_birthday()
    if next_birthday_utc < datetime.utcnow():
        Data.set_elem(guild_id,member_id,'last_announced_utc',datetime.utcnow())
        guild = get(bot.guilds,id=guild_id)
        birthday_channel = get(guild.channels,name=config.BIRTHDAY_CHANNEL)
        await birthday_channel.send(f"Happy birthday, <@{member_id}>!")
        update_timestamp(guild_id, member_id)





@bot.command(aliases=['set_tz'],help='Set the timezone of a member to specified value. If member is not given, changes your own timezone. Requires admin if member is not yourself.')
async def set_timezone(ctx, timezone, member: discord.Member=None):
    if member is None:
        member = ctx.author
    is_admin = ctx.author.guild_permissions.administrator
    if ctx.author != member and not is_admin:
        ctx.send("You need to be admin to change data of other people!")
        return
    if timezone not in pytz.all_timezones:
        timezone = None
    if timezone is None:
        Data.delete_timezone(ctx.guild.id,member.id)
        await ctx.send(f'Invalid timezone: {timezone}, deleted old timezone instead.')
    else:
        Data.set_elem(ctx.guild.id,member.id, 'timezone',timezone)
        await ctx.send(f"Timezone of {member} set as {timezone}, local time: {local_time(timezone)}")
    update_timestamp(ctx.guild.id,member.id)

def local_time(target_tz):
    target_tz = pytz.timezone(target_tz)
    utc_dt = datetime.now(timezone.utc)
    local_dt = utc_dt.astimezone(target_tz)
    return local_dt

# @bot.command()
# async def region_time(ctx, *, region):
    # if region not in config.REGION_TZ:
        # await ctx.send(f'Region not selected, using utc...')
        # target_tz = timezone.utc
    # else:
        # target_tz = pytz.timezone(config.REGION_TZ[region])
    # utc_dt = datetime.now(timezone.utc)
    # local_dt = utc_dt.astimezone(target_tz)
    # await ctx.send(f'Current time in {target_tz.zone} : {local_dt}')



bot.run(config.BOT_TOKEN)
