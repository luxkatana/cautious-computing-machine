from discord.ui import View
from constants import HELPER_ROLE, EVENTS_CHANNEL
from . import build_default_embed
from standardlib.cancel_view import CancelView
from asyncio import sleep as async_sleep
from time import time
from random import choice
from roblox import Client
import discord


def generate_nonce(length: int) -> str:
    return ''.join([choice('0123456789') for _ in range(length)])

async def parse_displayname_by_user(user: discord.Member) -> tuple[bool, str, str]:
    try:
        splitted = user.display_name.split(" (@")
        if len(splitted) != 2:
            return (False, "", "")
        display, realuser = splitted[0], splitted[1][:-1:]
        return (True, display, realuser)
    except Exception:
        return (False, "", "")

class AnnouncementView(View):
    def __init__(self, 
                 bot: discord.Bot,
                 end_time: int):
        super().__init__(timeout=None)
        self.bot = bot
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
        EVENTS: discord.TextChannel = self.bot.get_channel(EVENTS_CHANNEL)
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

