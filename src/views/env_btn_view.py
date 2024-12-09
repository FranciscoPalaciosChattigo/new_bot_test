import discord
from src.views.perfil_btn_view import PerfilSelectView

class EnvSelectView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.ambiente = ''

    @discord.ui.button(label="Pantera", style=discord.ButtonStyle.primary, custom_id="pantera")
    async def pantera(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.ambiente = 'pantera'
        button.disabled = True

        # Crear la nueva vista para la configuración
        nueva_vista = PerfilSelectView(self.ambiente)
        await interaction.message.delete()
        await interaction.response.send_message(f"Has elegido **{self.ambiente}**. Ahora selecciona un perfil:",
                                       view=nueva_vista)

    @discord.ui.button(label="Bugs", style=discord.ButtonStyle.primary, custom_id="bugs")
    async def bugs(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.ambiente = 'bugs'
        button.disabled = True

        # Crear la nueva vista para la configuración
        nueva_vista = PerfilSelectView(self.ambiente)
        await interaction.message.delete()
        await interaction.response.send_message(f"Has elegido **{self.ambiente}**. Ahora selecciona un perfil:",
                                                view=nueva_vista)

    @discord.ui.button(label="Leones", style=discord.ButtonStyle.primary, custom_id="leones")
    async def leones(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.ambiente = 'leones'
        button.disabled = True

        # Crear la nueva vista para la configuración
        nueva_vista = PerfilSelectView(self.ambiente)
        await interaction.message.delete()
        await interaction.response.send_message(f"Has elegido **{self.ambiente}**. Ahora selecciona un perfil:",
                                                view=nueva_vista)

    @discord.ui.button(label="Suppport Bugs", style=discord.ButtonStyle.primary, custom_id="support-bugs")
    async def suppport_bugs(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.ambiente = 'support-bugs'
        button.disabled = True

        # Crear la nueva vista para la configuración
        nueva_vista = PerfilSelectView(self.ambiente)
        await interaction.message.delete()
        await interaction.response.send_message(f"Has elegido **{self.ambiente}**. Ahora selecciona un perfil:",
                                                view=nueva_vista)