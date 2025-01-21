from discord.ui import View
from discord import Interaction
import discord
import asyncio


class ConfirmationView(View):
    def __init__(self, user: discord.Member,
                 confirmations: list[bool]):
        self.user = user
        self.sticked_message: discord.Message = None
        self.confirmations = confirmations
        super().__init__(disable_on_timeout=True, timeout=3 * 60)


    def stop(self) -> None:
        self.disable_all_items()
        super().stop()
    async def interaction_check(self, 
                                interaction: Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("Not for you", 
                                                    ephemeral=True)
            return False
        return True

    @discord.ui.button(label="I got the trident", 
                       style=discord.ButtonStyle.green)
    async def on_got(self, _, interaction: Interaction):
        already_has_role: discord.Role = (interaction
                                          .guild
                                    .get_role(1325150669568610335))
        await interaction.user.add_roles(already_has_role)
        await interaction.response.send_message(
                "Catched that, great job!", 
                                                ephemeral=True)
        self.stop()
        self.confirmations.append(True)
        await interaction.delete_original_message()

    @discord.ui.button(label="Nah I got no trident",
                       style=discord.ButtonStyle.red)
    async def nah_i_got_no(self, _, interaction: discord.Interaction):
        await interaction.response.send_message("That sucks.. Pay attention next time!", ephemeral=True)
        self.stop()
        await interaction.delete_original_message()
        await self.confirmations.append(False)

    async def on_timeout(self) -> None:
        await self.disable_all_items()   
        self.confirmations.append(False)





class WaitingList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._length_futures: dict[int, asyncio.Future] = {}
    
    def append(self, item) -> None:
        super().append(item)
        # Check if we have any futures waiting for this length
        new_length = len(self)
        futures_to_resolve = [
            (length, future) 
            for length, future in self._length_futures.items() 
            if length <= new_length
        ]
        
        # Resolve all futures that are waiting for this length or less
        for length, future in futures_to_resolve:
            if not future.done():
                future.set_result(None)
            del self._length_futures[length]
    
    async def wait_for(self, length: int, timeout: float = None) -> None:
        """
        Wait until the list reaches the specified length.
        
        Args:
            length: The length to wait for
            timeout: Optional timeout in seconds. If None, wait indefinitely
            
        Raises:
            asyncio.TimeoutError: If the timeout is reached before the list reaches
                                the specified length
        """
        if len(self) >= length:
            return
            
        # Create a future if we don't already have one for this length
        if length not in self._length_futures:
            self._length_futures[length] = asyncio.Future()
            
        try:
            await asyncio.wait_for(self._length_futures[length], timeout=timeout)
        except asyncio.TimeoutError:
            # Clean up the future if we timeout
            if length in self._length_futures:
                del self._length_futures[length]
            raise

