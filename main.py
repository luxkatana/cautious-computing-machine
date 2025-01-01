#!/home/luxkatana/pyenv/bin/python3
from datetime import datetime
import discord
from roblox import Client
import logging
from random import choice
from discord.ext import commands, tasks
from traceback import format_exc
from dotenv import load_dotenv
from asyncio import sleep as async_sleep
from os import environ
from time import time
from discord.ui import View
from string import digits 

print = logging.info
logging.basicConfig(filename="./log.log", filemode="a", level=logging.INFO)


def generate_nonce(length: int) -> str:
    return ''.join([choice(digits) for _ in range(length)])

async def parse_displayname_by_user(user: discord.Member) -> tuple[bool, str, str]:
    splitted = user.display_name.split(" (@")
    if len(splitted) != 2:
        return (False, "", "")
    display, realuser = splitted[0], splitted[1][:-1:]
    return (True, display, realuser)


load_dotenv()
TOKEN = environ['TOKEN']
bot = commands.Bot(intents=discord.Intents.all(), debug_guilds=[1321602258038820936])
EVENTS_CHANNEL = 1321622294388412480
HELPER_ROLE = 1321615619640135731
TRIDENT_TIME_TO_WAIT_IN_SECS: int = 600 # is 10 minutes
SEARCHING_FOR_HELPERS = True


@bot.event
async def on_ready() -> None:
    await bot.change_presence(activity=discord.Game(name="Making events..."))
    print(f"User logged at {bot.user}")
    channel = await bot.fetch_channel(EVENTS_CHANNEL)
    if channel is None:
        print("Couldn't clean")
    async for message in channel.history():
       if message.author.id == bot.user.id:
            await message.delete(reason="Startup")


    await channel.send(embed=discord.Embed(title="Bot cleanup", description="Beep boop started"))
    mainloop.start()

@bot.event
async def on_error(exception: Exception, *args, **kwargs) -> None:
    channel = bot.get_channel(1323285527486529627)
    await channel.send("Exception occured:\n"
                       f"```{format_exc()}```")
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


class CancelView(View):
    def __init__(self,
                 helper: discord.Member,
                 *args,
                 **kwargs):
        super().__init__(timeout=None, *args, **kwargs)
        self.helper = helper

    
    @discord.ui.button(label="Delete & finish this event (press this to delete and finish this event)", style=discord.ButtonStyle.red, custom_id="delete_btn")
    async def on_finish(self, _, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.helper.id:
            await interaction.response.send_message("This is not for you, this is for the helper!", ephemeral=True)
        else:
            embed = discord.Embed(title="This event has been marked as finished, this event will be deleted after 10 seconds", 
                                  description="Have fun with your trident! Make sure to invite people to this server!", color=discord.Colour.yellow())
            embed.add_field(name="Want to become a helper?", value="Contact an admin. Full desolete deep bestiary is required", inline=False)
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

@bot.event
async def on_message(message: discord.Message):
    thick_of_it = (
            '''
            from the screen to the ring to the bed to the king
            ''').lower().rstrip().strip()
    if message.author.id in [714149216787628075, 719072157229121579] and message.content.lower() == thick_of_it:
        await message.reply("OMG I HATE THIS NUMBER I AM JUST GONNA DELETE THIS CHANNEL IN 10 SECONDS!!!11!!")
        await async_sleep(10.0)
        await message.channel.delete(reason="Dumb ahh number")

    await bot.process_commands(message)


class AnnouncementView(View):
    def __init__(self, end_time: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_message: discord.Message = None
        self.lists_of_people_joined: list[discord.Member] = []
        self.end_time = end_time
        self.current_helper: discord.Member = None
    async def update_embed_counting(self) -> None:
        amount_of_people = len(self.lists_of_people_joined)
        helper = f"<@{self.current_helper.id}>" if self.current_helper is not None else "Currently no helper, if no helper, then the event will be cancelled."
        embed = discord.Embed(title="Hosting a trident-door-opening!")
        embed.description = "Trident-door will be opened in 10 minutes. React to the buttons"
        grammar = f"{amount_of_people} people are going to join this event"
        if amount_of_people == 0:
            grammar = "Zero people are going to join this event"
        elif amount_of_people == 1:
            grammar = "1 Person is going to join this event"
        embed.add_field(name="Amount of people",
                        value=f"**{grammar}.**",
                        inline=True)
        embed.add_field(name="Helper", value=helper, inline=True) 
        embed.add_field(name="Starting time", value=f"<t:{self.end_time}>", inline=True)
        embed.add_field(name="Requirements", value="* 150K (for Trident rod)\n* 5 enchant relics (optional)", inline=True)
        await self.original_message.edit(embed=embed)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green)
    async def reply_to_interactionviews(self, _, interaction: discord.Interaction) -> None:
        fomat_endtime = f"<t:{self.end_time}>"
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
                                  f"Be there at {fomat_endtime}, I will make a channel later after 10 minutes. You'll get pinged by me")
            embed.color = discord.Color.gold()
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            self.lists_of_people_joined.append(interaction.user)
            embed = discord.Embed(title="Joined",
                                  description=
                                  f"Be there at {fomat_endtime}, I will make a channel later after 10 minutes. You'll get pinged by me")
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

    @discord.ui.button(label="Become helper", style=discord.ButtonStyle.grey)
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
        await self.original_message.edit(view=None)
        if len(self.lists_of_people_joined) < 1:
            await self.original_message.edit("Cancelled, nobody joined the event..", delete_after=60.0)
            return 
        

        if self.current_helper is None:
            await self.original_message.edit(f"Cancelled, there is no helper assigned to this event, next event will be <t:{int(time() + 1200)}>",
                                              embed=None, delete_after=20 * 60)
            return

        permissions = {member: discord.PermissionOverwrite(read_messages=True, send_messages=True) for member in self.lists_of_people_joined + [self.current_helper]}
        permissions.update({guild.default_role: discord.PermissionOverwrite(read_messages=False)})


        channel = await EVENTS.guild.create_text_channel(f"JOIN The trident event ({generate_nonce(10)})",
                                                         reason="Auto create trident channel",
                                                         slowmode_delay=5,
                                                         overwrites=permissions)
        next_time = int(time() + (20 * 60))
        await self.original_message.edit(f"Go to <#{channel.id}> for instructions\nNext event will be <t:{next_time}>",
                                         embed=None,
                                         view=None, delete_after=60 * 20)
        result = "\n".join(map(lambda member: f"<@{member.id}>", self.lists_of_people_joined))
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
            await channel.send(f"{self.current_helper.mention} couldn't parse your account by username, please run ``/verify`` by bloxlink to set up your username.")


        message = await channel.send(result, view=cancel_view, embed=embed)
        await message.pin()

        
@tasks.loop(minutes=30)
async def mainloop() -> None:
    ending_time = int(time() + TRIDENT_TIME_TO_WAIT_IN_SECS)
    EVENTS: discord.TextChannel = bot.get_channel(EVENTS_CHANNEL)

    embed = discord.Embed(title="Hosting a trident-door-opening!")
    embed.description = "Trident-door will be opened in 10 minutes. React to the buttons"
    embed.add_field(name="Amount of people", value="**Zero people are going to join this event.**", inline=True) 
    embed.add_field(name="Helper", value="Currently no helper, if no helper, then the event will be cancelled.", inline=True) 
    embed.add_field(name="Starting time", value=f"<t:{ending_time}>", inline=True)
    embed.add_field(name="Requirements", value="* 150K (for Trident rod)\n* 5 enchant relics (optional)", inline=True)
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
    await interactionviews.go_continue()


class AppealModal(discord.ui.Modal):
    def __init__(self, solicitor: discord.Member) -> None:
        self.solicitor = solicitor
        super().__init__(title="Rejection modal", timeout=None, custom_id="rejection_modal")
        self.add_item(discord.ui.InputText(style=discord.InputTextStyle.short,
                                           custom_id="status",
                                           label="Reject or Accept",
                                           placeholder="Enter only reject or accept",
                                           max_length=6,
                                           min_length=5,
                                           required=True))


        self.add_item(discord.ui.InputText(style=discord.InputTextStyle.long, 
                                           custom_id="Reason for rejection (leave empty if accept)", 
                                           label="Why the rejection?", 
                                           placeholder="Because ...", 
                                           min_length=10,
                                           max_length=200,
                                           required=False, value="aaaaaaaaaaa"))
    async def callback(self, interaction: discord.Interaction):
        status, reason = self.children
        if status.value.lower() == "accept":
            helper_role = interaction.guild.get_role(HELPER_ROLE)
            try:
                await self.solicitor.add_roles(helper_role, reason=f"Accepted by {interaction.user}")
            except Exception:
                await interaction.response.send_message(f"Couldn't give role to {self.solicitor.mention}, please give it manually.")
            else:
                await interaction.response.send_message(f"Success, welcome {self.solicitor.mention} to the team!")
        else:
            await interaction.response.send_message(f"Sent rejection to {self.solicitor.mention}", ephemeral=True)
            try:
                if reason.value == "aaaaaaaaaaa":
                    await self.solicitor.send("You've been rejected for the helper application, sorry!")
                else:
                    await self.solicitor.send(f"You've been rejected or this helper application, sorry!\nReason: ```{reason.value}```")
            except Exception:
                GENERAL_CHAT = bot.get_channel(1321602258038820939)
                if reason.value == "aaaaaaaaaaa":
                    await GENERAL_CHAT.send("You've been rejected for the helper application, sorry!")
                else:
                    await GENERAL_CHAT.send(f"You've been rejected for the helper application, sorry!\nReason: ```{reason.value}```")



class ApplyHelperView(View):
    def __init__(self, solicitor: discord.Member, original_message: discord.Message):
        self.solicitor = solicitor    
        self.message = original_message
        super().__init__(timeout=None)
    @discord.ui.button(label="Review", style=discord.ButtonStyle.grey, custom_id="review_btn")
    async def review(self, _, interaction: discord.Interaction):
        if interaction.user.id not in [714149216787628075, 719072157229121579]:
            await interaction.response.send_message("Not for you, for the owners", ephemeral=True)
        else:
            modal = AppealModal(self.solicitor)
            await interaction.response.send_modal(modal)


@bot.slash_command(name="apply_as_helper", description="Apply as helper, file must be a picture of ")
async def apply_as_helper(ctx: discord.ApplicationContext, image: discord.Attachment) -> None:
    if ctx.author.guild.get_role(HELPER_ROLE) in ctx.author.roles:
        await ctx.respond("You are a helper.", ephemeral=True)
    elif SEARCHING_FOR_HELPERS is False:
        await ctx.respond("Helper applications are closed.", ephemeral=True)
    else:
        STAFF_CHAT = await ctx.guild.get_channel(1323056105835991050)

        embed = discord.Embed(title=f"{ctx.author.name} is applying for helper", description=f"{ctx.author.mention} is applying as a helper")
        embed.set_image(url=f"attachment://{image.filename}")
        applyview = ApplyHelperView(ctx.author)
        await STAFF_CHAT.send(embed=embed, file=image, view=applyview)
        await ctx.response.send_message(
                "Cool, thanks for applying as a helper, we're gonna make our decision later (you might get a DM or get mentioned by me)!",
                                        ephemeral=True)

bot.run(TOKEN)

