
import time
import discord
from discord.ext import commands
import json
from src.google_gcs.google_gcs_managment import GoogleCloudConnector
from src.views.env_btn_view import EnvSelectView
from src.views.calendar_view import InputDate
from src.views.multi_embeds import MultiEmbeds
from src.Github_api_manager.github_api import GithubApi
from discord.ui import View, Button
from datetime import datetime, timedelta
import os


TOKEN = os.environ['TOKEN_TEST_BOT']
TOKEN_2 = os.environ['TOKEN_DISCORD_AUTO']


# Inicializa el cliente del bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")


# Comando /ping
@bot.tree.command(name="ping", description="Bot, estas?")
async def ping_command(interaction: discord.Interaction):
    try:
        print('PING!')
        await interaction.response.send_message(embed=MultiEmbeds.pong_embed())
    except Exception as e:
        print(f"Error: {e}")

# Comando /ayuda
@bot.tree.command(name="ayuda", description="Comandos basicos")
async def ayuda_command(interaction: discord.Interaction):
    try:
        await interaction.response.send_message(embed=MultiEmbeds.ayuda_embed())
    except Exception as e:
        print(f"Error: {e}")

# Comando /auto
@bot.tree.command(name="auto", description="Selecciona un ambiente")
async def auto_command(interaction: discord.Interaction):
    try:
        ambientes_select_view = EnvSelectView()
        await interaction.response.send_message("Selecciona una opción:", view=ambientes_select_view)

    except Exception as e:
        print(f"Error: {e}")


# Comando /history
@bot.tree.command(name="history", description="Historial de automatias por fecha")
async def history_command(interaction: discord.Interaction):
    try:
        imput_date = InputDate()
        # await interaction.response.send_message("Selecciona una fecha:")
        await interaction.response.send_modal(imput_date)
    except Exception as e:
        print(f"Error: {e}")

@bot.tree.command(name="running", description="En ejecucion actualmente:")
async def running_command(interaction: discord.Interaction):
    try:
        def capturar_ambiente_en_el_step(lista_de_steps):
            for step in lista_de_steps:
                if any(env in step['name'] for env in ['leones', 'bugs', 'pantera','support-bugs']):
                    return step['name']

        await interaction.response.send_message(embed=MultiEmbeds.loading())
        workflows_running = ''
        repo_runs = GithubApi().get_run_all_repo_jobs()
        for repo_run in repo_runs:
            for workflow_run in repo_run['workflow_runs']:
                # pprint.pprint(workflow_run['status'])

                repo_name = workflow_run['head_repository']['url'].split('/')[-1]
                job_info = GithubApi().get_job_info(workflow_run['id'], repo_name)
                workflows_running = workflows_running + f"- _{repo_name}_ en _{capturar_ambiente_en_el_step(job_info['jobs'][0]['steps']).split(' ')[-1]}_ \n"

        if len(workflows_running) > 0:
            await interaction.edit_original_response(embed=MultiEmbeds.workflows_running(workflows_running))
        else:
            await interaction.edit_original_response(embed=MultiEmbeds.no_workflows_running())

    except Exception as e:
        print(f"Error: {e}")


# Comando /action-time
@bot.tree.command(name="action-time", description="action-time")
async def acition_time_command(interaction: discord.Interaction):
    try:
        # Responde a la interacción primero
        await interaction.response.send_message(embed=MultiEmbeds.loading())
        # - consumo de Actions en modificaciones de kubernetes por parte de Dev-Ops
        devops_usage_kubernetes =  GithubApi().get_timing_by_workflow("kubernetes-loft-gitops",
                                                                                "notify_discord_on_commit.yml")
        # - consumo de Actions en el repo de config por parte de Dev-Ops
        devops_usage_config =  GithubApi().get_timing_by_workflow("config_preprod_ms_loft",
                                                                            "repository_dispatch.yml")

        # - consumo de Actions en borrado de canales de YML
        devops_usage_channel_delete =  GithubApi().get_timing_by_workflow("config_preprod_ms_loft",
                                                                                    "channel_delete_dispatch.yml")

        devops_usage = devops_usage_kubernetes + devops_usage_config + devops_usage_channel_delete

        load_result, data = GithubApi().get_timing_by_org(paid=35, devops_usage=devops_usage)

        # Editar la respuesta original con los datos calculados
        await interaction.edit_original_response(content='', embed=MultiEmbeds.billing_answer(load_result, data))
    except Exception as e:
        print(f"Error: {e}")

# Comando /test
@bot.tree.command(name="test", description="Test title")
async def test_command(interaction: discord.Interaction):
    try:
        # view = View()
        # button1 = Button(label="Cancelar ejecucion", style=discord.ButtonStyle.danger, custom_id="Cancelar")
        # view.add_item(button1)
        #
        # async def on_button1_click(interaction: discord.Interaction):
        #     await interaction.response.send_message("¡Presionaste el Botón 1!", ephemeral=True)
        #
        # button1.callback = on_button1_click

        #await interaction.response.send_message(embed=MultiEmbeds.embed_test(), view=view)

        await interaction.response.send_message(embed=MultiEmbeds.pong_embed())
    except Exception as e:
        print(f"Error: {e}")

@bot.event
async def on_raw_reaction_add(payload):
    # payload contiene datos del evento
    interaction: discord.Interaction
    channel = bot.get_channel(payload.channel_id)
    user = bot.get_user(payload.user_id)
    emoji = payload.emoji
    emoji = str(emoji)
    comparison = '🤚'
    if emoji.encode('utf-8') == comparison.encode('utf-8'):
        message = await channel.fetch_message(payload.message_id)
        print(message.embeds[0].title.split(':'))

        if 'Success' in message.embeds[0].title:
            repo_name = message.embeds[0].fields[4].value.split("(")[1].split(")")[0].split("/")[-4]
            # print('repo name: ', repo_name)
            run_id = message.embeds[0].fields[4].value.split("(")[1].split(")")[0].split("/")[-1]
            # print('run_id: ', run_id)
            html_url = message.embeds[0].fields[4].value.split("(")[1].split(")")[0]
            # print('html_url: ', html_url)

            embed_ok = MultiEmbeds.successful_emoji_reaction_answer(repo_name)
            embed_confirm = MultiEmbeds.successful_canceled_run_petition_answer(repo_name, html_url)
            failed_embed = MultiEmbeds.failed_canceled_run_petition_answer(repo_name, html_url)

            # try:
            #     GithubApi().delete_run_process(repo_name=repo_name, run_id=run_id)
            #     await message.channel.send(embed=embed_ok)
            #     res = GithubApi().get_run_status_by_id(run_id=run_id, repo_name=repo_name)
            #     if res['conclusion'] == 'cancelled':
            #         conclusion = res['conclusion']
            #         await message.channel.send(embed=embed_confirm)
            # except Exception as e:
            #     await message.channel.send(embed=failed_embed)

            GithubApi().delete_run_process(repo_name=repo_name, run_id=run_id)
            await message.channel.send(embed=embed_ok)
            conclusion = None
            for _ in range(6):
                res = GithubApi().get_run_status_by_id(run_id, repo_name=repo_name)
                if res['conclusion'] == 'cancelled':
                    conclusion = res['conclusion']
                    await message.channel.send(embed=embed_confirm)
                    return
                else:
                    time.sleep(10)
            return await message.channel.send(embed=failed_embed)



# @bot.event
# async def on_message(message):
#     # Evita que el bot entre en un bucle editando sus propios mensajes
#     print(message.author, bot.user)
#     if message.author == bot.user:
#         return
#
#     print("content => ", message.content)
#     print("embeds => ", message.embeds)
#     print("channel => ", message.channel)


bot.run(TOKEN)


def obtener_fechas_desde_ahora(self, dias: int):
    fechas = []
    fecha_actual = datetime.now()

    for i in range(dias):
        fecha = fecha_actual - timedelta(days=i)
        fechas.append(fecha.strftime("%Y-%m-%dT"))

    return fechas


