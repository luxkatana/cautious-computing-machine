
from discord.ui import View
import discord
from standardlib.confirm_view import WaitingList, ConfirmationView
from constants import SPECIAL_SQUAD, HELPER_ROLE

class CancelView(View):
    def __init__(self,
                 helper: discord.Member,
                 *args,
                 **kwargs):
        super().__init__(timeout=None, *args, **kwargs)
        self.helper = helper

    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id not in SPECIAL_SQUAD and interaction.user.id != self.helper.id:
            await interaction.response.send_message("Not for you..", ephemeral=True)
            return False

        return True



    @discord.ui.button(label="Delete & finish this event (press this to delete and finish this event)", style=discord.ButtonStyle.red, custom_id="delete_btn")
    async def on_finish(self, _, interaction: discord.Interaction) -> None:
        embed = discord.Embed(title="This event has been marked as finished, this event will be deleted after when everyone replied (or in 3 minutes automatic)", 
                              description="Have fun with your trident! Make sure to invite people to this server!", color=discord.Colour.yellow())
        embed.set_footer(text=f"Please make sure to thank {self.helper.display_name} for his help!")
        await interaction.response.send_message("Sending messages, thx!", ephemeral=True)
        await interaction.channel.send(embed=embed)
        confirmations = WaitingList()
        count = 0
        for user in interaction.channel.members:
            print(user)
            if user.bot is False and interaction.guild.get_role(HELPER_ROLE) not in user.roles:
                count += 1
                conf_view = ConfirmationView(user, confirmations)
                conf_view.sticked_message = await interaction.channel.send(f"{user.mention}, did you get the trident?", view=conf_view)

        try:
            await confirmations.wait_for(count, 3 * 60)
        except Exception: ...

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


