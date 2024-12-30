#!/home/luxkatana/pyenv/bin/python3

from datetime import datetime, timedelta
import discord
from roblox import Client
from random import choice
from discord.ext import commands, tasks
from traceback import format_exc
from dotenv import load_dotenv
from asyncio import sleep as async_sleep
from os import environ
from time import time
from discord.ui import View
from string import digits 


async def parse_displayname_by_user(user: discord.Member) -> tuple[bool, str, str]:
    realuser = user.display_name
    splitted = realuser.split(" (@")
    if len(splitted) != 2:
       return (False, "", "")
    (display, realuser) = (splitted[0], splitted[1][:-1:1])

    return (True, display, realuser)

def generate_nonce(length: int) -> str:
    return ''.join([choice(digits) for _ in range(length)])

load_dotenv()
TOKEN = environ['TOKEN']
bot = commands.Bot(intents=discord.Intents.all())
EVENTS_CHANNEL = 1321622294388412480
HELPER_ROLE = 1321615619640135731
TRIDENT_TIME_TO_WAIT_IN_SECS: int = 600 # is 10 minutes

@bot.event
async def on_ready() -> None:
    await bot.change_presence(activity=discord.Game(name="Making events..."))
    print(f"User logged at {bot.user}")
    mainloop.start()

@bot.event
async def on_error(exception: Exception, *args, **kwargs) -> None:
    print(args, kwargs)
    channel = bot.get_channel(1323285527486529627)
    await channel.send(f"raw exception: {exception}")
    await channel.send("Exception occured:\n"
                       f"```{format_exc()}```")
    raise exception


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


class AnnouncementView(View):
    def __init__(self, end_time: int, *args, **kwargs):
        now = datetime.now()
        later = datetime.fromtimestamp(end_time)
        later = datetime.strptime(str(later), "%Y-%m-%d %H:%M:%S")
        later = datetime(later.year, later.month, later.day, later.hour, later.minute, 0)
        time_to_wait = int((later - now).total_seconds())
        print("expected stopping:", later)
        print("RN: ", now)
        super().__init__(timeout=time_to_wait, *args, **kwargs)
        self.original_message: discord.Message = None
        self.lists_of_people_joined: list[discord.Member] = []
        self.end_time = end_time
        self.current_helper: discord.Member = None
    async def update_embed_counting(self) -> None:
        amount_of_people = len(self.lists_of_people_joined)
        helper = f"<@{self.current_helper.id}>" if self.current_helper is not None else "Currently no helper, if no helper, then the event will be cancelled."
        embed = discord.Embed(title="Hosting a trident-door-opening!")
        embed.description = "Trident-door will be opened in 10 minutes. React to the buttons"
        embed.add_field(name="Amount of people",
                        value=f"**{'zero' if amount_of_people == 0 else amount_of_people} people are going to join this event.**",
                        inline=True)
        embed.add_field(name="Helper", value=helper, inline=True) 
        embed.add_field(name="Starting time", value=f"<t:{self.end_time}>", inline=True)
        await self.original_message.edit(embed=embed)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green)
    async def reply_to_interactionviews(self, _, interaction: discord.Interaction) -> None:
        if self.current_helper is not None and self.current_helper.id == interaction.user.id:
            await interaction.response.send_message("You're the helper, you don't have to join!", ephemeral=True)
            return
        if interaction.user in self.lists_of_people_joined:
            await interaction.response.send_message(f"You're already in the party.. but be there at <t:{self.end_time}:t>", ephemeral=True)
        else:
            self.lists_of_people_joined.append(interaction.user)
            await interaction.response.send_message(f"Joined, be there at  <t:{self.end_time}:t>", ephemeral=True)
            await self.update_embed_counting()

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
    async def on_timeout(self) -> None:
        print("Timeout reached.")
        EVENTS: discord.TextChannel = bot.get_channel(EVENTS_CHANNEL)
        guild = self.original_message.guild
        await self.original_message.edit(view=None)
        if len(self.lists_of_people_joined) < 1:
            await self.original_message.edit("Cancelled, nobody joined the event..", delete_after=60.0)
            return 
        

        if self.current_helper is None:
            await self.original_message.edit("Cancelled, there is no helper assigned to this event, next event will be after 20 minutes.",
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
                                         view=None)
        result = "\n".join(map(lambda member: f"<@{member.id}>", self.lists_of_people_joined))
        result = f'||{result}||'
        embed = discord.Embed(title="Welcome adventurers",
                              description=f"Welcome, this is the trident-door-opening event. Please do what {self.current_helper.mention} asks you to do", colour=discord.Color.gold())
        cancel_view = CancelView(self.current_helper)
        (status, display, username) = await parse_displayname_by_user(self.current_helper)
        if status is True:
            print(display, username)
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
    embed.add_field(name="Amount of people", value="**zero people are going to join this event.**", inline=True) 
    embed.add_field(name="Helper", value="Currently no helper, if no helper, then the event will be cancelled.", inline=True) 
    embed.add_field(name="Starting time", value=f"<t:{ending_time}>", inline=True)
    interactionviews = AnnouncementView(ending_time)
    message = await EVENTS.send(embed=embed, view=interactionviews)
    interactionviews.original_message = message


bot.run(TOKEN)

