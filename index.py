#!/usr/bin/env python

import discord
from discord.ext import commands

from utils import Mapper, PlayerFinder, Prettifier
from time import sleep

import config

bot = commands.Bot(command_prefix='!')

# Get the stats from the utils module helpers.
# Creates a response based on the data received.
def fetch_stats(request):
    if request == "about":
        return discord.Embed(title="About this bot", description="A bot made by NSNull#6107, built on the opensource reddit bot HowStat by @pranavrc. Source code is available at [jamiebishop/discord-cricket-stat-bot](https://github.com/jamiebishop/discord-cricket-stat-bot)", color=discord.Color.green())

    # Create a mapper instance
    init = Mapper()

    # Create an URL mapping using the input request.
    try:
        mapped = init.map_string(request)
    except:
        return build_error_embed("Unable to parse your command.")

    # Find the player using the player name in the request.
    try:
        player_url = PlayerFinder(init.player_name)
    except:
        return build_error_embed("Sorry, the service seems to be unavailable right now.")

    # Scrape and parse the statistics for the corresponding player.
    try:
        zeroed_in = player_url.zero_in()
        if not player_url.test_player:
            base_url = zeroed_in.replace("class=11;", "")
        else:
            base_url = zeroed_in.replace("class=1;", "")
    except:
        return build_error_embed("I couldn't find that, sorry.")
        
    # Create a Prettifier instance if it's a valid stats url.
    try:
        if base_url[-1] == ";":
            base_url += mapped
            if init.has_type_override:
                base_url = base_url.replace("type=allround;", "")
            prettifier = Prettifier(base_url, player_url.test_player)
        else:
            return build_error_embed("I couldn't find that, sorry.")
    except:
        return build_error_embed("I couldn't find that, sorry.")

    try:
        stat_dict = prettifier.parse_into_dict(init.class_allround)
    except Exception as e:
        print(e)
        return build_error_embed("An unknown error occured. Contact <@507975140567416843> with the command which caused this error.")

    return build_embed_fields_from_stats(stat_dict, base_url, init)

def stat_dict_add_fields_to_embed(embed, stat_dict):
    # TODO: - Make category names nicer
    for category, value in stat_dict.items():
        embed.add_field(name=category, value=value, inline=True)

def build_embed_fields_from_stats(stats, url, request_map):
    embed = discord.Embed(title="Statistics for {}".format(request_map.player_name.title()), url=url, color=discord.Color.green())
    embed.set_footer(text="Bot made by NSNull#6107, built on the opensource reddit bot HowStat by @pranavrc. Contact NSNull for support with any issues/feature requests.")
    if "filtered" in stats:
        stat_dict_add_fields_to_embed(embed, stats["filtered"])
    elif "overall" in stats:
        stat_dict_add_fields_to_embed(embed, stats["overall"])
    else:
        embed.add_field(name="Error", value="No stats for that player could be found.")
    return embed

def build_error_embed(error):
    return discord.Embed(title="An error occured", description=error, color=discord.Colour.red())

@bot.command()
async def cricstat(ctx, *, request):
    await ctx.send("{}".format(ctx.message.author.mention), embed=fetch_stats(request))

bot.remove_command("help")

bot.run(config.bot_token)