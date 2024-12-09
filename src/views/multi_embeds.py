import discord
from datetime import datetime

class MultiEmbeds:

    @staticmethod
    def ayuda_embed():
        return discord.Embed(title=f"Ejemplos de como ejecutar las pruebas",
                               description="- Ejecutar automaticas: \n"
                                           "```"
                                           "/auto"
                                           "``` \n"
                                           "- Ver historial de tests \n"
                                           "```"
                                           f"/history"
                                           "```\n"
                                           "- Verificar los workflows corriendo \n"
                                           "```"
                                           "/running"
                                           "``` \n"
                                           "- Obtener minutos consumidos de las actions\n"
                                           "```"
                                           "/actions-time"
                                           "``` \n"
                                           "                           _v1.27.1_"
                               ,
                               colour= discord.Colour.blue())

    @staticmethod
    def pong_embed():
        return discord.Embed(title=f"PONG! Bot ready!",
                              description=f" Envia '/ayuda' para ver ejemplos de comandos.",
                              colour=discord.Colour.brand_red(),
                              type='article')

    @staticmethod
    def loading():
        return discord.Embed(title=f"Cargando...",
                             colour=discord.Colour.orange(),
                             type='article')

    @staticmethod
    def embed_confirm_auto(interaction, env, perfil, mark, jira, in_execution):
        # Crea un embed
        embed = discord.Embed(
            title=f"Hola {interaction.user.name}! 🎉",
            description=f"He recibido tu solicitud con los siguientes detalles: ",
            colour=discord.Colour.blurple()
        )

        if in_execution:
            embed.description += f"\n**{in_execution}** ya fueron ejecutados anteriormente, espera que terminen por favor"

        # Agregamos campos para cada detalle
        embed.add_field(name="🌐 Ambiente", value=f"**{env}**", inline=True)
        embed.add_field(name="👤 Perfil", value=f"**{perfil}**", inline=True)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="🏷️ Mark", value=f"**{mark}**", inline=True)
        embed.add_field(name="📝 Jira", value=f"**{jira}**", inline=True)

        # Agregamos una nota o mensaje final si es necesario
        embed.set_footer(text="Gracias por tu solicitud. ¡Estamos trabajando en ello!")

        return embed

    @staticmethod
    def billing_answer(load_result, data):
        url = 'https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions'
        answer = discord.Embed(title=f"  ACTIONS :  _Estado de consumo_  ⏱ ",

                               description=f"consumido: \n" + load_result,
                               colour=discord.Colour.orange())
        answer.add_field(name="", value="", inline=False)
        answer.add_field(name="> Min. usados:", value=f">   {int(data['total_usado'])}", inline=True)
        answer.add_field(name="> Min. devops:", value=f">   {int(data['devops'])}", inline=True)
        answer.add_field(name="> Min. QA:", value=f">   {int(data['QA'])}", inline=True)
        answer.add_field(name="", value="", inline=False)
        answer.add_field(name="> Min. totales:", value=f">   {int(data['minutos_totales'])}", inline=True)
        answer.add_field(name="> Prox renov:", value=f">   {int(data['dias_restantes'])} días", inline=True)
        answer.add_field(name="> Min. disponibles:", value=f">   {int(data['minutos_disponibles'])}", inline=True)
        return answer

    @staticmethod
    def no_workflows_running():
        answer = discord.Embed(title=f"No hay workflows corriendo :white_check_mark: ",
                               description="",
                               colour=discord.Colour.blue())
        return answer

    @staticmethod
    def workflows_running(workflows):
        answer = discord.Embed(title=f"Estos son los workflows que estan funcionando ahora mismo ",
                               description=workflows,
                               colour=discord.Colour.blue())
        return answer

    @staticmethod
    def successful_emoji_reaction_answer(repo_environ):
        answer = discord.Embed(title=f"Hola!, recibí tu reacción.",
                               description=f"Procesando la detención de la automática solicitada de {repo_environ}",
                               colour=discord.Colour.red())

        return answer

    @staticmethod
    def successful_canceled_run_petition_answer( repo_environ, html_url):
        answer = discord.Embed(title=f"{repo_environ} ❌ Automática cancelada",
                               description=f"[workflow]({html_url})",
                               colour=discord.Colour.green())

        return answer

    @staticmethod
    def failed_canceled_run_petition_answer(repo_environ, html_url):
        answer = discord.Embed(title=f"{repo_environ} No se ha cancelado, por favor verificar manualmente",
                               description=f"[workflow]({html_url})",
                               colour=discord.Colour.red())

        return answer

    @staticmethod
    def error_run_repo_and_env_is_running(env, repo, url):
        answer = discord.Embed(title=f"Parece que ya existe un job en {env} corriendo en {repo} :stopwatch: ",
                               description=f"Vas a tener que esperar, o terminar con el workflow corriendo \n"
                                           f"Url : [Enlace del workflow]({url}) \n",

                               colour=discord.Colour.red())
        return answer

    @staticmethod
    def workflows_previously_executed(workflows):
        answer = discord.Embed(title=f"Estos perfiles ya estan en ejecucion, aguarde su finalizacion por favor.",
                               description=workflows,
                               colour=discord.Colour.blue())
        return answer