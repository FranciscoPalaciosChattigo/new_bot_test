import discord
from src.Github_api_manager.github_api import GithubApi
from src.views.multi_embeds import MultiEmbeds


class InputModal(discord.ui.Modal, title="Mark"):
    def __init__(self, env, perfil, jira):
        super().__init__()
        self.env = env
        self.perfil = perfil
        self.jira = jira
        self.input_field = discord.ui.TextInput(
            label=self.perfil,
            placeholder="Solo escribir en caso de querer ejecutar Marks",
            style=discord.TextStyle.short,  # Campo de texto corto
            required=False,
            min_length=0,
            default=''
        )
        self.add_item(self.input_field)  # Añadir el campo al modal

    async def on_submit(self, interaction: discord.Interaction):
        #await interaction.message.delete()
        # Crear el campo de entrada dentro del constructor


        # print(':::>>> ', self.env, self.perfil, self.input_field.value, self.jira)
        #
        # mark = 'All' if len(self.input_field.value) == 0 else self.input_field.value
        # jira = 'Si' if self.jira else 'No'
        #
        # # EJECUCION
        # # github_api_to_all_repo = GithubApi(env=self.env, markers=mark, jira=jira, repo=self.perfil)
        # # github_api_to_all_repo.run_tests()
        #
        # embed = MultiEmbeds.embed_confirm_auto(interaction,
        #                                        self.env,
        #                                        self.perfil,
        #                                        mark,
        #                                        jira)

        # await interaction.message.edit(embed=embed, view=None, content=None)
        return str(self.input_field.value)