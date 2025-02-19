#!/home/luxkatana/pyenv/bin/python3
from datetime import datetime
from io import BytesIO
from re import search as regex_search
from threading import Thread
from httpx._exceptions import ConnectTimeout
from discord.ext import commands
from standardlib import build_default_embed
from standardlib.cancel_view import CancelView
from json import dumps
from websockets.asyncio.server import ServerConnection, serve
from standardlib.announcement_view import AnnouncementView
from standardlib.confirm_view import ConfirmationView, WaitingList
from discord.ext import tasks
from traceback import format_exc
from time import time
from notify_update import notify_user
from constants import HAS_TRIDENT_ROLE, SPECIAL_SQUAD, EVENTS_CHANNEL, HELPER_ROLE, TRIDENT_TIME_TO_WAIT_IN_SECS, WS_PORT
from os import environ
from dotenv import load_dotenv
from uuid import getnode
import asyncio
import subprocess
import logging
import base64
import discord
import aiosqlite
load_dotenv()


TOKEN = environ['TOKEN']
bot = commands.Bot(intents=discord.Intents.all(), debug_guilds=[1321602258038820936]) 
ws_clients: set[ServerConnection] = set()
async def ws_handler(ws: ServerConnection):
    GUILD = bot.get_guild(1321602258038820936)
    try:
        payload = {
                "guild": GUILD.member_count,
                "trident_role": len(GUILD.get_role(HAS_TRIDENT_ROLE).members),
                "not_trident_role": len(GUILD.get_role(1341168113928114276).members)
        }
        await ws.send(dumps(payload)) 
        ws_clients.add(ws)
        async for _ in ws:
            pass # to keep it on the server
    except Exception as e:
        ws_clients.remove(ws)
        raise e

async def ws_main() -> None:
    async with serve(ws_handler, "0.0.0.0", WS_PORT) as server:
        await server.serve_forever()

DEBUGGING_MODE: bool = getnode() != 345045631689

desolate_group = bot.create_group(name="helpers_application", description="Utilities for applying as a helper")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("log.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logging.getLogger("discord").setLevel(logging.ERROR)

def __print__(msg: str, *args, **kwargs):
    logger.info(msg, *args, **kwargs)
    logging.info(msg, *args, **kwargs)

def __eprint__(msg: str, *args, **kwargs):
    logger.error(msg, *args, **kwargs)
    logging.error(msg, *args, **kwargs)
print = __print__
eprint = __eprint__

def hard_restart():
    subprocess.run(["./apply_to_production.sh"])

@bot.event
async def on_error(exception: Exception, *args, **kwargs) -> None:
    if isinstance(exception, ConnectTimeout): # Discord is down
        eprint("Executing 'apply-to-production.sh' since timeout error")
        Thread(target=hard_restart, daemon=True).start()
        return

    channel = bot.get_channel(1323285527486529627)
    await channel.send("Exception occured:\n"
                       f"```{format_exc()}```")
    eprint(str(exception))
    eprint(exception)
    raise exception

@bot.event
async def on_application_command_error(
    ctx: discord.ApplicationContext, 
    exception: Exception):
    await ctx.respond("Error occured while applying", ephemeral=True)
    channel = bot.get_channel(1323285527486529627)
    await channel.send(f"raw: {exception}")
    await channel.send("Exception occured:\n"
                       f"```{format_exc()}```")
    eprint(exception)
    raise exception



@bot.event
async def on_message(message: discord.Message):
    if message.guild is None or isinstance(message.author, discord.User):
        await bot.process_commands(message)
        return

    thick_of_it = (
            '''
            abracadabra remove channel
            ''').lower().rstrip().strip()
    if message.content.lower() == "somethingpoopy":
        await resolve_broken_cancel_views()
        return
    if message.content.lower() == thick_of_it and message.guild.get_role(HELPER_ROLE) in message.author.roles and \
            message.channel.name.startswith("join-the-trident"):
        embed = discord.Embed(title="This event has been marked as finished, this event will be deleted after 10 seconds", 
                              description="Have fun with your trident! Make sure to invite people to this server!", 
                              color=discord.Colour.random())
        embed.set_footer(text="Please make sure to thank the helper for his help!")

        await message.channel.send(embed=embed)
        await asyncio.sleep(10)
        await message.channel.delete(reason=f"Event finished, <@{message.author.id}> deleted by using delete command")

    await bot.process_commands(message)



        
@tasks.loop(minutes=45)
async def mainloop() -> None:
    ending_time = int(time() + TRIDENT_TIME_TO_WAIT_IN_SECS)
    EVENTS: discord.TextChannel = bot.get_channel(EVENTS_CHANNEL)
    embed = build_default_embed(ending_time, 0)

    interactionviews = AnnouncementView(bot, ending_time)
    message = await EVENTS.send(embed=embed, view=interactionviews, content="||<@&1341168113928114276>||")
    interactionviews.original_message = message

    later = datetime.strptime(str(datetime.fromtimestamp(ending_time)), "%Y-%m-%d %H:%M:%S") 

    later = datetime(later.year, later.month, later.day, later.hour, later.minute, 0)
    now = datetime.now()
    time_to_wait = int((later - now).total_seconds())
    print(f"expected stopping: {later}")
    print(f"RN: {now}")
    print(f"waiting time: {time_to_wait}")
    await asyncio.sleep(time_to_wait)
    if bot.get_message(message.id) is None:
        return
    print("STARTING WITH EVENT, WAIT FINISH")
    await interactionviews.go_continue()

@bot.message_command(name="Delete event (free robux)")
async def del_event(ctx: discord.ApplicationContext, msg: discord.Message):
    if ctx.author.id not in SPECIAL_SQUAD:
        await ctx.respond("only special people can do this", ephemeral=True)
    elif msg.author.id != bot.user.id:
        await ctx.respond("Wha.. No", ephemeral=True)
    elif ctx.channel_id != 1321622294388412480:
        await ctx.respond("Wrong channel bro", ephemeral=True)
    else:
        await ctx.respond("Finito", ephemeral=True)
        await msg.delete(reason="Event cancelled by luxkatana")
        


async def resolve_broken_cancel_views() -> None:
    guild = bot.get_guild(1321602258038820936)
    channels: tuple[discord.TextChannel, ...] = tuple(filter(lambda j: j.name.startswith("join-the-trident"), guild.channels))
    for channel in channels:
        pinned_msg = await channel.pins()
        if len(pinned_msg) != 1:
            view = CancelView(bot.get_user(1008651612820095056))
            await channel.send("This must be a debugging channel", view=view)
            continue
        pinned_msg: discord.Message = pinned_msg[0]
        older_embed_description = pinned_msg.embeds[0].description
        result = regex_search(r"<@(\d+)>", older_embed_description)
        if result:
            view = CancelView(bot.get_user(int(result.group(1))))
            await pinned_msg.edit(view=view)
            await pinned_msg.reply("Beep boop (this message means that the bot has been updated in robot language)", delete_after=10.0) 

@bot.event
async def on_ready() -> None:
    if hasattr(bot, "on_ready_ran") is False:
        bot.on_ready_ran = True
    else:
        return

    bot.connection = await aiosqlite.connect("./main.db")


    if DEBUGGING_MODE is False:
        await bot.change_presence(activity=discord.Game(name="Making events..."))
    else:

        await bot.change_presence(activity=discord.Game(name="[DEBUGGING] making nukes to nuke France..."))
        print("ON DEBUGGING MODE, THEREFORE SKIPPING SANITY CHECKS")
        return

    bot.add_view(AnnouncementView(bot, 0))
    bot.add_view(CancelView(None))
    await resolve_broken_cancel_views()
    print(f"User logged at {bot.user}")
    channel = await bot.fetch_channel(EVENTS_CHANNEL)
    if channel is None:
        print("Couldn't clean")
    async for message in channel.history(oldest_first=True):
       if message.author.id == bot.user.id or message.webhook_id is not None:

           await message.delete(reason="Startup")


    await channel.send(embed=discord.Embed(title="Heya", 
                                           description="May, luxkatana, the best programmer of the universe update the bot.")
                       .set_footer(text="I am wishing y'all a good time"))
    if DEBUGGING_MODE is False:
        await notify_user(channel)
        await channel.send(embed=discord.Embed(title="Bot cleanup", description="Beep boop started"), delete_after=10.0)
        mainloop.start()
    else:
        raise "This isn't an error, but debugging mode is currently on, just so you know :)"



@bot.user_command(name="Get desolate deep bestiary", 
                  description="This will pull the desolate deep bestiary from the user, if applied")
async def retrieve_desolate(ctx: discord.ApplicationContext, user: discord.Member):
    if ctx.guild.get_role(HELPER_ROLE) not in ctx.author.roles:
        await ctx.respond("You're not allowed to do this.", ephemeral=True)
        return
    cursor: aiosqlite.Cursor = await bot.connection.cursor()
    await cursor.execute("SELECT image FROM desolatebs WHERE USERID=?", (user.id,))
    fetch = await cursor.fetchone()
    if fetch is None:
        await ctx.respond("User did not submit yet a desolate deep bestiary.", ephemeral=True)
    else:
        fetch = tuple(fetch)
        decoded_content = base64.b64decode(fetch[0].encode())
        io = BytesIO(decoded_content)
        await ctx.respond(f"Image supplied by {user.mention}", file=discord.File(fp=io, filename="holyfimcmlois.jpg"))


@desolate_group.command(name="submit_desolate_bestiary", 
                        description="This will submit your desolate deep bestiary for the helpers application")
@discord.option(name="image", input_type=discord.Attachment, required=True)
async def submit_desolate(ctx: discord.ApplicationContext,
                          image: discord.Attachment):
    if ctx.guild.get_role(HELPER_ROLE) in ctx.author.roles:
        await ctx.respond("This is not for helpers, this is for people that are applying", ephemeral=True)
        return

    if not image.content_type.startswith("image/"):
        await ctx.respond("Attachment is not a valid image.", ephemeral=True)
        return

    encoded_data: str = base64.b64encode(await image.read()).decode()
    cursor: aiosqlite.Cursor = await bot.connection.cursor()
    await cursor.execute("SELECT COUNT(*) FROM desolatebs WHERE USERID=?;", (ctx.author.id,))
    result = await cursor.fetchone()

    if tuple(result)[0] == 0: # doesnt exist, create new
        await cursor.execute("INSERT INTO desolatebs(USERID, image) VALUES (?, ?)", (ctx.author.id, encoded_data))
    else:
        await cursor.execute("UPDATE desolatebs SET image=? WHERE USERID=?", (encoded_data, ctx.author.id))

    await bot.connection.commit()
    await cursor.close()
    await ctx.respond("Succesfully submitted desolate deep bestiary.", file=await image.to_file(), ephemeral=True)

@bot.slash_command(name="seelogs", description="Read logger handler")
async def read_logs(ctx: discord.ApplicationContext):
    if ctx.author.id not in SPECIAL_SQUAD:
        await ctx.respond("Not for you", ephemeral=True)
        return
    await ctx.defer()
    try:
        with open("./log.log", 'r') as file:
            data = file.read()
        await ctx.respond(data)


    except Exception:
        await ctx.respond("log.log file doesn't exist, therefore it's not possible to read it", ephemeral=True)


@bot.slash_command(name="trial", description="Preview a view")
@discord.option(name="viewtype", input_type=str, choices=["cancel_view", "confirm_view"])
async def trial(ctx: discord.ApplicationContext, viewtype: str):
    if ctx.author.id not in SPECIAL_SQUAD:
        await ctx.respond("not for you", ephemeral=True)
        return
    if viewtype == "cancel_view":
        view = CancelView(ctx.author)
        await ctx.respond("Follow the blah blah (just know that it could actually do stuff)", view=view)
    else:
        waitinglist = WaitingList()
        view = ConfirmationView(ctx.author, waitinglist)
        await ctx.respond("Got the trident role lil bro (this is cringe)?", view=view)
        try:
            await waitinglist.wait_for(1, 3 * 60)
        except Exception:
            await ctx.channel.send("Not sent on time (timeout reached)")
        else:
            await ctx.channel.send("Success")

async def main():
    bot_task = asyncio.create_task(bot.start(TOKEN))
    ws_task = asyncio.create_task(ws_main())
    await asyncio.gather(bot_task, ws_task)
    
@bot.event
async def on_member_join(member: discord.Member):
    bot.on_member_update(member, None)

@bot.event
async def on_member_remove(member: discord.Member):
    bot.on_member_update(member, None)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    payload = dumps({
            "guild": before.guild.member_count,
            "trident_role": len(before.guild.get_role(HAS_TRIDENT_ROLE).members),
            "not_trident_role": len(before.guild.get_role(1341168113928114276).members)
    })
    print("oke")
    for client in ws_clients:
        await client.send(payload)


asyncio.run(main())


