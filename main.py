import discord;
from discord.ext import commands;
from discord import utils;
import os;
import config;
bot = commands.Bot(command_prefix='!', intents = discord.Intents.all());
@bot.event
async def on_ready():
    print('We have logged');
@bot.event
async def on_member_join(member):
    role = utils.get(member.guild.roles, id=config.ROLE);
    await bot.get_channel(758724426455580685).send(f"У нас новый гражданский!{member.mention}");
    await member.add_roles(role);
bot.run(config.TOKEN);
