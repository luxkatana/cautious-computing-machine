import discord

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



