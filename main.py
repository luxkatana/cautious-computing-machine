#!/home/luxkatana/pyenv/bin/python3
from datetime import datetime
import discord
from re import search as regex_search
from roblox import Client
import logging
from uuid import getnode
from random import choice
from discord.ext import commands, tasks
from traceback import format_exc
from dotenv import load_dotenv
from asyncio import sleep as async_sleep
from os import environ
from time import time
from discord.ui import View
from string import digits 
from notify_update import notify_user


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("log.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logging.getLogger("discord").setLevel(logging.ERROR)

print = logger.info
eprint = logger.error

def generate_nonce(length: int) -> str:
    return ''.join([choice(digits) for _ in range(length)])

async def parse_displayname_by_user(user: discord.Member) -> tuple[bool, str, str]:
    try:
        splitted = user.display_name.split(" (@")
        if len(splitted) != 2:
            return (False, "", "")
        display, realuser = splitted[0], splitted[1][:-1:]
        return (True, display, realuser)
    except Exception:
        return (False, "", "")


load_dotenv()
TOKEN = environ['TOKEN']
bot = commands.Bot(intents=discord.Intents.all(), debug_guilds=[1321602258038820936]) 
EVENTS_CHANNEL = 1321622294388412480
HAS_TRIDENT_ROLE: int = 1325150669568610335
HELPER_ROLE = 1321615619640135731
DEBUGGING_MODE: bool = getnode() != 240374920240546

TRIDENT_TIME_TO_WAIT_IN_SECS: int = 15 * 60 
def build_default_embed(ending_time: int,
                        amount_of_people: int=0,
                        helper: discord.Member=None) -> discord.Embed:

    grammar = f"{amount_of_people} people are going to join this event"
    if amount_of_people == 0:
        grammar = "Zero people are going to join this event"
    elif amount_of_people == 1:
        grammar = "1 Person is going to join this event"
    DEFAULT_EMBED = discord.Embed(title="Hosting a trident door opening event, read <#1323633658766032896>")
    DEFAULT_EMBED.description = f"Become a participant for the trident door event in {TRIDENT_TIME_TO_WAIT_IN_SECS / 60:.0f} minutes. React to the buttons below"
    DEFAULT_EMBED.add_field(name="Amount of people", value=f"**{grammar}**", inline=True) 
    DEFAULT_EMBED.add_field(name="Helper", value="Currently no helper, if no helper, then the event will be cancelled."\
            if helper is None else f"<@{helper.id}> ({helper.name})", inline=True) 
    DEFAULT_EMBED.add_field(name="Starting time", value=f"<t:{ending_time}:t>", inline=True)
    DEFAULT_EMBED.add_field(name="Requirements", value="* **150K (for Trident rod)**\n* **5 enchant relics**", inline=True)
    return DEFAULT_EMBED



@bot.event
async def on_error(exception: Exception, *args, **kwargs) -> None:
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


class CancelView(View):
    def __init__(self,
                 helper: discord.Member,
                 *args,
                 **kwargs):
        super().__init__(timeout=None, *args, **kwargs)
        self.helper = helper
        self.clicked: bool = False

    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != 714149216787628075 and interaction.user.id != self.helper.id:
            await interaction.response.send_message("Not for you..", ephemeral=True)
            return False

        return True
    @discord.ui.button(label="Assign trident role for users (required)", custom_id="assign_to_btn")
    async def assign(self, _, interaction: discord.Interaction):
        self.clicked = True

        def is_a_normal_member(user: discord.Member) -> bool:
            helper_role = interaction.guild.get_role(HELPER_ROLE)
            return (helper_role not in user.roles) and (user.id not in [714149216787628075, 719072157229121579]) and user.bot is False
        
        def create_btn_callback(user: discord.Member):
            async def assign(interaction: discord.Interaction):
                HAS_TRIDENT_OBJ = interaction.guild.get_role(HAS_TRIDENT_ROLE)
                if HAS_TRIDENT_OBJ in user.roles:
                    await interaction.response.send_message(f"{user.mention} somehow sneaked in with the role..? Anyways didn't assign",
                                                            ephemeral=True)
                    return
                await user.add_roles(HAS_TRIDENT_OBJ, reason="assign role complete")
                embed = discord.Embed(title="Success", description="Successfully assigned the <@&1325150669568610335> role",
                                      colour=discord.Color.green())
                embed.add_field(name="To who", value=user.mention, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return assign


        users = tuple(filter(is_a_normal_member, interaction.channel.members))
        if len(users) == 0:
            await interaction.response.send_message("Something aint right, 0 members!1!!?", ephemeral=True)
            return
        normalview = discord.ui.View(timeout=500)
        if len(users) > 25:
            users = users[:24:]

        for user in users:
            btn = discord.ui.Button(label=f"{user.display_name}", style=discord.ButtonStyle.grey)
            btn.callback = create_btn_callback(user)
            normalview.add_item(btn)
        if len(users) > 25:
            await interaction.response.send_message("Assign the users that you have to assign\n"
                                                    "**NOTE: please note that you have to click one more time the assign button**", 
                                                    view=normalview, 
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("Alright, click to assign the trident role", view=normalview, ephemeral=True)



    @discord.ui.button(label="Delete & finish this event (press this to delete and finish this event)", style=discord.ButtonStyle.red, custom_id="delete_btn")
    async def on_finish(self, _, interaction: discord.Interaction) -> None:
        if self.clicked is False:
            await interaction.response.send_message("You still have to assign people with the 'Already has trident' role\n"
                                                    "***If you don't know how to do that, on the pinned message in the current channel "
                                                    "you can find a button that may allow you to assign people with the role***\n"
                                                    "If there is nobody to assign this role to, then just click it and close the channel.",
                                                    ephemeral=True)
        else:
            embed = discord.Embed(title="This event has been marked as finished, this event will be deleted after 10 seconds", 
                                  description="Have fun with your trident! Make sure to invite people to this server!", color=discord.Colour.yellow())
            embed.set_footer(text=f"Please make sure to thank {self.helper.display_name} for his help!")
            await interaction.response.send_message("Deleting after 10 seconds. Thank you for your service!", ephemeral=True)
            await interaction.channel.send(embed=embed)
            
            await async_sleep(10)
            await interaction.channel.delete(reason=f"Event finished, <@{interaction.user.id}> clicked this button")
    @discord.ui.button(label="Instructions for helpers 101", custom_id="instructions_101", style=discord.ButtonStyle.grey)
    async def instructions(self, _, interaction: discord.Interaction):
        if interaction.user.id != self.helper.id:
            await interaction.response.send_message("Not meant for you", ephemeral=True)
        else:
            embed = discord.Embed(title="Instructions for helpers 101", color=discord.Colour.green())
            embed.add_field(name="Channel dead in the begin?", value="If this is the case, then ping everyone", inline=False)
            embed.add_field(name="Channel is still dead, what now?", value="At this point, ping @everyone and give a warning that you'll definitely start after 5 minutes", inline=False)
            embed.add_field(name="Nobody replied, and nobody joined what now?", value="You have the right to press the red 'close' button", 
                            inline=False)
            embed.add_field(name="Someone is not working out together, what now?", 
                            value="Ask the participant to reply to your statement/question", 
                            inline=False)
            embed.add_field(name="Got questions?", value="Sure, go ahead and ping one of the owners.", inline=False)
            embed.set_footer(text="I rage quited while helping people, some don't know the language")
            await interaction.response.send_message(embed=embed, ephemeral=True)


'''@bot.slash_command(name="delete channel", description="Use this command if the bot is not replying")
async def remove_channel(ctx: discord.ApplicationContext):
    role: discord.Role = ctx.guild.get_role(HELPER_ROLE)
    if role in ctx.author.roles:
        if ctx.channel.name.startswith("join-the-trident"):
            embed = discord.Embed(title="This event has been marked as finished, this event will be deleted after 10 seconds", 
                                  description="Have fun with your trident! Make sure to invite people to this server!", 
                                  color=discord.Colour.yellow())
            embed.add_field(name="Want to become a helper?", value="Contact an admin. Full desolate deep bestiary is required", inline=False)
            embed.set_footer(text="Please make sure to thank the helper for his help!")

            await ctx.respond("Deleting after 10 seconds. Thank you for your service!", ephemeral=True)
            await ctx.channel.send(embed=embed)
            await async_sleep(10)
            await ctx.channel.delete(reason=f"Event finished, <@{ctx.author.id}> deleted by using delete command")

        else:
            await ctx.respond("This is not a trident-channel!!!!", ephemeral=True)
    else:
        await ctx.respond("You don't have the permissions to do this", ephemeral=True)'''
    



@bot.event
async def on_message(message: discord.Message):
    if message.guild is None or isinstance(message.author, discord.User):
        await bot.process_commands(message)
        return

    thick_of_it = (
            '''
            abracadabra remove channel
            ''').lower().rstrip().strip()
    if message.content.lower() == thick_of_it and message.guild.get_role(HELPER_ROLE) in message.author.roles and \
            message.channel.name.startswith("join-the-trident"):
        embed = discord.Embed(title="This event has been marked as finished, this event will be deleted after 10 seconds", 
                              description="Have fun with your trident! Make sure to invite people to this server!", 
                              color=discord.Colour.random())
        embed.set_footer(text="Please make sure to thank the helper for his help!")

        await message.channel.send(embed=embed)
        await async_sleep(10)
        await message.channel.delete(reason=f"Event finished, <@{message.author.id}> deleted by using delete command")

    await bot.process_commands(message)


class AnnouncementView(View):
    def __init__(self, end_time: int):
        super().__init__(timeout=None)
        self.original_message: discord.Message = None
        self.lists_of_people_joined: list[discord.Member] = []
        self.end_time = end_time
        self.current_helper: discord.Member = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.end_time == 0:
            await interaction.response.send_message("Currently applying an update, please wait!", ephemeral=True)
            return False
        return True

            
    async def update_embed_counting(self) -> None:
        await async_sleep(1.0)
        embed = build_default_embed(self.end_time, len(self.lists_of_people_joined), self.current_helper)
        await self.original_message.edit(embed=embed)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, custom_id="join_btn")
    async def reply_to_interactionviews(self, _, interaction: discord.Interaction) -> None:
        fomat_endtime = f"<t:{self.end_time}:t>"
        if interaction.guild.get_role(1325150669568610335) in interaction.user.roles:
            await interaction.response.send_message("You already have the trident, why bother joining?", ephemeral=True)
            return

        if self.current_helper is not None and self.current_helper.id == interaction.user.id:
            await interaction.response.send_message(f"You're the helper, you don't have to join! Be prepared at {fomat_endtime}", 
                                                    ephemeral=True)
            return
        HELPER_G_ROLE = interaction.guild.get_role(HELPER_ROLE)
        if HELPER_G_ROLE in interaction.user.roles:
            await interaction.response.send_message(embed=discord.Embed(
                title="Failed",
                description="As a helper, you can't join an event, but you can claim one"), ephemeral=True)
            return


        if interaction.user in self.lists_of_people_joined:
            embed = discord.Embed(title="You are already in the party",
                                  description=
                                  f"Be there at {fomat_endtime}, I will make a channel later after 15 minutes. You'll get pinged by me")
            embed.color = discord.Color.gold()
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            self.lists_of_people_joined.append(interaction.user)
            embed = discord.Embed(title="Joined",
                                  description=
                                  f"Be there at {fomat_endtime}, I will make a channel later after 15 minutes. You'll get pinged by me")
            embed.color = discord.Color.blue()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.update_embed_counting()

    @discord.ui.button(label="See who is going to join", style=discord.ButtonStyle.secondary, custom_id="list_users")
    async def list_users(self, _, interaction: discord.Interaction) -> None:
        if len(self.lists_of_people_joined) == 0:
            await interaction.response.send_message("This event is empty...", ephemeral=True)
        else:
            result = "\n* ".join([user.mention for user in self.lists_of_people_joined])
            result = f"* {result}"
            await interaction.response.send_message(result, ephemeral=True)

    async def on_timeout(self) -> None:
        print("I AM ON TIMEOUT")
    async def on_error(error, item, interaction):
        await interaction.response.send_message("EH??")
        print(error)
        print(item)

    @discord.ui.button(label="Become helper", style=discord.ButtonStyle.grey, custom_id="become_helper_btn")
    async def become_helper(self, _, interaction: discord.Interaction) -> None:
        role = interaction.guild.get_role(HELPER_ROLE)
        if role not in interaction.user.roles:
            await interaction.response.send_message(f"Looks like you don't have the {role.name} role", ephemeral=True)
            return

        if self.current_helper is None:
            self.current_helper = interaction.user
            if self.current_helper in  self.lists_of_people_joined:
                self.lists_of_people_joined.remove(interaction.user)
            await interaction.response.send_message("Successfully assigned you as helper =)", ephemeral=True)
            await self.update_embed_counting()
        else:
            await interaction.response.send_message("There is already a helper assigned to this event.. Better luck next time!", ephemeral=True)
    async def go_continue(self) -> None:
        EVENTS: discord.TextChannel = bot.get_channel(EVENTS_CHANNEL)
        guild = self.original_message.guild
        await self.original_message.edit(view=None, embed=None)
        if len(self.lists_of_people_joined) < 1:
            await self.original_message.edit(f"Cancelled, nobody joined the event.. Next event will be <t:{int(time() + 30 * 60)}:t>", 
                                             delete_after=30 * 60)
            return 
        

        if self.current_helper is None:
            await self.original_message.edit(f"Cancelled, there is no helper assigned to this event, next event will be <t:{int(time() + 30 * 60)}:t>", delete_after=30 * 60)
            return

        permissions = {member: discord.PermissionOverwrite(read_messages=True, send_messages=True) for member in self.lists_of_people_joined + [self.current_helper]}
        permissions.update({guild.default_role: discord.PermissionOverwrite(read_messages=False)})


        channel = await EVENTS.guild.create_text_channel(f"JOIN The trident event ({generate_nonce(10)})",
                                                         reason="Auto create trident channel",
                                                         slowmode_delay=5,
                                                         overwrites=permissions)
        next_time = int(time() + (30 * 60))
        msg = (f"# For people who attended to this event\n> Please go to {channel.mention} for instructions\n"
              "# For people who didn't attend to this event and is waiting for the next trident-door event\n" 
               f"> Next event will be <t:{next_time}:t> (after 30 minutes)")

        await self.original_message.edit(content=msg, delete_after=30 * 60)
        result = "\n".join(map(lambda member: f"<@{member.id}>", self.lists_of_people_joined + [self.current_helper]))
        result = f'||{result}||'
        embed = discord.Embed(title="Welcome adventurers",
                              description=f"Welcome, this is the trident-door-opening event. Please do what {self.current_helper.mention} asks you to do", colour=discord.Color.gold())
        cancel_view = CancelView(self.current_helper)
        (status, display, username) = await parse_displayname_by_user(self.current_helper)
        if status is True:
            userid = await Client().get_user_by_username(username)
            userid = userid.id
            cancel_view.add_item(discord.ui.Button(label=f"Visit {display} on roblox",
                                                       url=f"https://roblox.com/users/{userid}/profile")) 
        else:
            print("COULDN'T PARSE")
            await channel.send(f"{self.current_helper.mention} couldn't parse your account by username, please run ``/verify`` by bloxlink to set up your username.")


        print("PINNING MESSAGE")
        message = await channel.send(result, view=cancel_view, embed=embed)
        print("MESSAGE PINGED")
        await message.pin()

        
@tasks.loop(minutes=45)
async def mainloop() -> None:
    ending_time = int(time() + TRIDENT_TIME_TO_WAIT_IN_SECS)
    EVENTS: discord.TextChannel = bot.get_channel(EVENTS_CHANNEL)
    embed = build_default_embed(ending_time, 0)

    interactionviews = AnnouncementView(ending_time)
    message = await EVENTS.send(embed=embed, view=interactionviews, content="||<@&1321786602778787870>||")
    interactionviews.original_message = message

    later = datetime.strptime(str(datetime.fromtimestamp(ending_time)), "%Y-%m-%d %H:%M:%S") 

    later = datetime(later.year, later.month, later.day, later.hour, later.minute, 0)
    now = datetime.now()
    time_to_wait = int((later - now).total_seconds())
    print(f"expected stopping: {later}")
    print(f"RN: {now}")
    print(f"waiting time: {time_to_wait}")
    await async_sleep(time_to_wait)
    if bot.get_message(message.id) is None:
        return
    print("STARTING WITH EVENT, WAIT FINISH")
    await interactionviews.go_continue()

@bot.message_command(name="Delete event (free robux)")
async def del_event(ctx: discord.ApplicationContext, msg: discord.Message):
    if ctx.author.id != 714149216787628075:
        await ctx.respond("only luxkatana can do this", ephemeral=True)
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
    bot.add_view(AnnouncementView(0))
    bot.add_view(CancelView(None))

    if DEBUGGING_MODE is False:
        await bot.change_presence(activity=discord.Game(name="Making events..."))
    else:
        await bot.change_presence(activity=discord.Game(name="[DEBUGGING] making nukes to nuke France..."))
        print("ON DEBUGGING MODE, THEREFORE SKIPPING SANITY CHECKS")
        return

    await resolve_broken_cancel_views()
    print(f"User logged at {bot.user}")
    channel = await bot.fetch_channel(EVENTS_CHANNEL)
    if channel is None:
        print("Couldn't clean")
    async for message in channel.history(oldest_first=True):
       if message.author.id == bot.user.id or message.webhook_id is not None:

           await message.delete(reason="Startup")


    if DEBUGGING_MODE is False:
        await notify_user()
        await channel.send(embed=discord.Embed(title="Bot cleanup", description="Beep boop started"), delete_after=10.0)
        mainloop.start()
    else:
        raise BaseException("This isn't an error, but debugging mode is currently on, just so you know :)")



@bot.slash_command(name="seelogs", description="Read logger handler")
async def read_logs(ctx: discord.ApplicationContext):
    if ctx.author.id not in [714149216787628075, 719072157229121579]:
        await ctx.respond("Not for you", ephemeral=True)
        return
    await ctx.defer()
    try:
        with open("./log.log", 'r') as file:
            data = file.read()
        await ctx.respond(data)


    except Exception:
        await ctx.respond("log.log file doesn't exist, therefore it's not possible to read it", ephemeral=True)


bot.run(TOKEN)

