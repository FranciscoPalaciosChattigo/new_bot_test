import json
import os
import re

import requests
import pprint
import time
from decimal import Decimal
from dotenv import load_dotenv
from src.utils.load_bar import LoadBar
from src.views.multi_embeds import MultiEmbeds

load_dotenv()


class GithubApi:

    def __init__(self, env='', markers='', jira=False, repo=''):
        self.env = env
        self.markers = markers
        self.jira = jira
        self.repo = repo
        self.valid_envs = ['leones', 'bugs', 'pantera','support-bugs']
        self.valid_repos = ['agente', 'bot', 'supervisor']
        self.base_url = os.environ.get("GITHUB_BASE_URL")
        self.token = os.environ.get("GITHUB_TOKEN_USER")
        self.org_token = os.environ.get("GITHUB_TOKEN_USER_ORG")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.headers_org = {"Authorization": f"Bearer {self.org_token}",
                            'X-GitHub-Api-Version': '2022-11-28',
                            "Accept": "application/vnd.github+json"}
        self.available_repos = self.__get_available_repositories()

    def run_tests(self):
        print(self.available_repos, "self.available_repos")
        for repo in self.available_repos:
            repoenv_sent = self.env + "-" + self.repo

            print(repoenv_sent, "repoenv_sent")
            if repoenv_sent in self.available_repos:
                url = f"{self.base_url}/{repoenv_sent}/dispatches"
                print(url, "url")
                data = self.__make_payload()
                return requests.post(url=url, headers=self.headers, data=data)

    def run_all_tests(self, available_profiles):
        url_lists = []
        for repo in available_profiles:
            url_lists.append(f"{self.base_url}/{repo}/dispatches")

        data = self.__make_payload()
        returns = []
        for url in url_lists:
            print("url_lists", url)
            returns.append(requests.post(url=url, headers=self.headers, data=data))
        return returns

    def run_test_api(self, message):
        url = f"{self.base_url}/automation-api/dispatches"
        data = self.__make_payload_api_test(message)
        return requests.post(url=url, headers=self.headers, data=data)

    def run_test_log_pods(self, message):
        url = f"{self.base_url}/commons-qa-pods/dispatches"
        data = self.__make_payload_api_log_pods(message)
        return requests.post(url=url, headers=self.headers, data=data)

    def run_clean(self, message):
        data = str(message).split(' ')
        print(data, 'data')
        url = f"{self.base_url}/staging_manager/dispatches"
        print(url)
        data = self.__make_payload_clean(data[1])
        return requests.post(url=url, headers=self.headers, data=data)

    def get_history(self, env, date):
        print(env, date)
        url = f"{self.base_url}/automation-supervisor/dispatches"
        print(url)
        data = self.__make_payload_history(env, date)
        return requests.post(url=url, headers=self.headers, data=data)

    def get_run_jobs(self):
        # data = str(message).split(' ')
        url = f"https://api.github.com/repos/chattigodev/{self.env}-{self.repo}/actions/runs?status=in_progress"
        headers = self.headers
        headers['Accept'] = 'application/vnd.github.v3+json'

        return requests.get(url=url, headers=headers).json()

    def get_run_status_by_id(self, run_id, repo_name):
        url = f"https://api.github.com/repos/chattigodev/{repo_name}/actions/runs/{run_id}"
        headers = self.headers
        headers['Accept'] = 'application/vnd.github.v3+json'
        return requests.get(url=url, headers=headers).json()

    def get_run_all_repo_jobs(self):
        url_lists = []
        for repo in self.available_repos:
            url_lists.append(f"https://api.github.com/repos/chattigodev/{repo}/actions/runs?status=in_progress")
        headers = self.headers
        headers['Accept'] = 'application/vnd.github.v3+json'

        returns = []
        for url in url_lists:
            returns.append(requests.get(url=url, headers=headers).json())
        return returns

    def get_run_and_timing_by_date_and_repo(self, date, repository):
        url = f"https://api.github.com/repos/chattigodev/{repository}/actions/runs?created={str(date)}"
        # (url)
        headers = self.headers_org
        headers['Accept'] = 'application/vnd.github.v3+json'

        data_return = requests.get(url=url, headers=headers).json()
        # print("data run",data_return)
        data_final = {'workflow_runs': []}
        total_minutes = 0
        for index, workflow_run in enumerate(data_return['workflow_runs']):
            data_timing = self.get_timing_by_run_id(repository, workflow_run['id'])
            workflow_info = []

            workflow_run_minutes = data_timing['run_duration_ms'] / 1000 / 60 if 'run_duration_ms' in data_timing else 0
            workflow_info.append({"run_time": round(workflow_run_minutes)})
            workflow_info.append({"id": data_return['workflow_runs'][index]["id"]})
            workflow_info.append({'run_number': data_return['workflow_runs'][index]['run_number']})
            data_final['workflow_runs'].append(workflow_info)
            total_minutes += workflow_run_minutes
            # pprint.pprint(data_return['workflow_runs'][index])

        # pprint.pprint(data_final)

        return data_final, total_minutes, len(data_return['workflow_runs'])

    def get_timing_by_run_id(self, repository, run_id):
        url = f"https://api.github.com/repos/chattigodev/{repository}/actions/runs/{run_id}/timing"
        headers = self.headers
        headers['Accept'] = 'application/vnd.github.v3+json'
        return requests.get(url=url, headers=headers).json()

    def get_timing_by_org(self, paid, devops_usage):
        """

        :param paid: le pega a el endpoint del consumo de actions, para saber los totales del mes
        :return: devuelve la barra de consumo de la actions y la información de consumo por organización
        """

        endpoint_billing = 'https://api.github.com/orgs/chattigodev/settings/billing/actions'
        endpoint_days_left = 'https://api.github.com/orgs/chattigodev/settings/billing/shared-storage'
        data = {}
        self.headers_org['Accept'] = 'application/vnd.github.v3+json'
        self.headers_org['X-GitHub-Api-Version'] = '2022-11-28'

        billing_res = requests.get(url=endpoint_billing, headers=self.headers_org).json()
        billing_days_left = requests.get(url=endpoint_days_left, headers=self.headers_org).json()
        price_per_minute = 0.008  # cambiarlo si sube, o baja o cambian de producto
        # print(billing_res)
        minutes_used = billing_res['total_minutes_used']
        # minutes_paid = billing_res['total_paid_minutes_used']
        minutos_incluidos = billing_res['included_minutes']
        minutos_extra_totales = (paid / price_per_minute)
        data['total_usado'] = minutes_used
        data['minutos_totales'] = (paid / price_per_minute) + minutos_incluidos
        data['minutos_disponibles'] = data['minutos_totales'] - minutes_used
        data['dias_restantes'] = billing_days_left['days_left_in_billing_cycle']
        data['devops'] = devops_usage
        data['QA'] = minutes_used - devops_usage

        porcentaje = (minutes_used / (minutos_extra_totales + minutos_incluidos)) * 100
        # print("total", minutos_extra_totales)
        # print("porcentaje", porcentaje)
        load_bar = LoadBar(porcentaje=porcentaje)
        result_bar_load = load_bar.barra_de_carga()
        # pprint.pprint(billing_days_left)
        # pprint.pprint(billing_res)
        # pprint.pprint(result_bar_load)
        return result_bar_load, data

    def get_timing_by_workflow(self, repo, workflow):
        """

        :param paid:
        :param user: el usuario del consumo
        :return:
        """
        billing_workflow = f'https://api.github.com/repos/chattigodev/{repo}/actions/workflows/{workflow}/timing'
        billing_res = requests.get(url=billing_workflow, headers=self.headers_org).json()
        total_workflow_usage = 0
        if 'UBUNTU' in billing_res['billable']:
            total_workflow_usage = int(billing_res['billable']['UBUNTU']['total_ms']) / 1000 / 60
        print(f" repo {repo}  ", str(total_workflow_usage) + " minutos")
        return total_workflow_usage

    def get_time_by_days(self):
        url_lists = [
            "https://api.github.com/repos/chattigodev/automation-agente/actions/runs",
            "https://api.github.com/repos/chattigodev/automation-bot-chattigo/actions/runs",
            "https://api.github.com/repos/chattigodev/automation-supervisor/actions/runs",
        ]

    def get_job_info(self, id, repo):
        # data = str(message).split(' ')
        url = f'https://api.github.com/repos/chattigodev/{repo}/actions/runs/{id}/jobs'
        headers = self.headers
        headers['Accept'] = 'application/vnd.github.v3+json'
        return requests.get(url=url, headers=headers).json()

    def delete_run_process(self, repo_name, run_id):
        # data = str(message).split(' ')
        url = f'https://api.github.com/repos/chattigodev/{repo_name}/actions/runs/{run_id}/cancel'
        headers = self.headers
        headers['Accept'] = 'application/vnd.github.v3+json'
        return requests.post(url=url, headers=headers).json()

    def check_run_by_job_id(self, repo_name, run_id):
        # data = str(message).split(' ')
        url = f'https://api.github.com/repos/chattigodev/{repo_name}/actions/jobs/{run_id}/logs'
        headers = self.headers
        headers['Accept'] = 'application/vnd.github.v3+json'
        return requests.post(url=url, headers=headers).json()

    def check_log_by_job(self, repo_name, run_id):
        # data = str(message).split(' ')
        url = f'https://api.github.com/repos/chattigodev/{repo_name}/actions/jobs/{run_id}/logs'
        headers = self.headers_org
        headers['Accept'] = 'application/vnd.github.v3+json'
        print(url, "url")
        return requests.get(url=url, headers=headers).text

    def get_org_repos(self):
        repos = []
        repos_to_run = []
        url = f"https://api.github.com/orgs/chattigodev/repos"
        headers = self.headers
        headers['Accept'] = 'application/vnd.github.v3+json'
        response = requests.get(url=url, headers=headers)
        for urls in response.json():
            repos.append(urls['name'])
        if response.status_code != 200:
            print(f"Error: {response.status_code}")

        for ambiente in repos:
            if '-' in ambiente:
                amb_org = ambiente.split('-')[-2]
                repo_org = ambiente.split('-')[-1]
                if amb_org in self.valid_envs and repo_org in self.valid_repos:
                    repos_to_run.append(ambiente)

        return repos_to_run

    # -- validación de repositorios corriendo --

    async def validate_jobs_in_run_all(self):

        available_profiles = [f'{self.env}-agente', f'{self.env}-bot', f'{self.env}-supervisor']
        not_available_run = []

        # -- validacion de repositorios --

        repo_runs = GithubApi().get_run_all_repo_jobs()
        for repo_run in repo_runs:
            for workflow_run in repo_run['workflow_runs']:
                repo_name = workflow_run['head_repository']['url'].split('/')[-1]

                job_info = GithubApi().get_job_info(workflow_run['id'], repo_name)

                if self.env in self.capturar_ambiente_en_el_step(job_info['jobs'][0]['steps']):
                    not_available_run.append(repo_name)
                    available_profiles.remove(repo_name)

        print('yes: ', available_profiles)
        print('no: ', not_available_run)

        return {
            'available_profiles': available_profiles,
            'not_available_run': not_available_run
        }

    async def validate_commands_and_jobs_in_run(self):
        repo_run = self.get_run_jobs()
        pprint.pprint(repo_run)
        if 'workflow_runs' in repo_run:
            for workflow_run in repo_run['workflow_runs']:
                repo_name = workflow_run['head_repository']['url'].split('/')[-1]
                job_info = self.get_job_info(workflow_run['id'], repo_name)

                url_workflow = f'https://github.com/chattigodev/{repo_name}/actions/runs/{workflow_run["id"]}/job/{job_info["jobs"][0]["id"]}'
                if self.env in self.capturar_ambiente_en_el_step(job_info['jobs'][0]['steps']) and self.repo in repo_name:
                    return url_workflow
                    #raise Exception("ERROR: run en proceso.")
        else:
            return False

    def capturar_ambiente_en_el_step(self, lista_de_steps):
        for step in lista_de_steps:
            if any(env in step['name'] for env in self.valid_envs):
                return step['name']

    # -- Métodos Auxiliares --

    def __make_payload(self):

        zyphyr = 'false'
        is_test = 'false'

        if self.jira:
            zyphyr = 'true'

        channel_name = 'bot-qa'

        if channel_name in ['bot-qa', 'general']:
            is_test = 'true'
        elif channel_name == 'qa-automaticas':
            is_test = 'false'

        body = {
            "event_type": "automaticas",
            "client_payload":
                {"markers": self.markers,
                 "environment": self.env,
                 "zephyr": zyphyr,
                 "is_test": is_test
                 }
        }
        payload = json.dumps(body, default=lambda o: self.__default_converter(o), sort_keys=True, indent=4)
        return payload

    def __make_payload_to_test(self):

        zyphyr = 'false'
        is_test = 'false'

        if self.bot_discord.jira:
            zyphyr = 'true'

        channel_name = self.bot_discord.message.channel.name

        if channel_name in ['bot-qa', 'general']:
            is_test = 'true'
        elif channel_name == 'qa-automaticas':
            is_test = 'false'

        print(channel_name)

        body = {
            "event_type": "test",
            "client_payload":
                {"markers": self.markers,
                 "environment": self.env,
                 "zephyr": zyphyr,
                 "is_test": is_test
                 }
        }

        payload = json.dumps(body, default=lambda o: self.__default_converter(o), sort_keys=True, indent=4)
        return payload

    def __make_payload_api_test(self, data):

        body = {
            "event_type": "Ejecución de Discord",
            "client_payload": {
                "path": data["path"],
                "method": data["method"],
                "expected_response": data["expected_response"],
                "headers": data["headers"],
                "payload": data["payload"],
                "is_test": data["is_test"]
            }
        }

        payload = json.dumps(body, default=lambda o: self.__default_converter(o), sort_keys=True, indent=4)
        return payload

    def __make_payload_history(self, env, date):

        body = {
            "event_type": "history",
            "client_payload":
                {
                    "environment": env,
                    "date": date
                }
        }
        payload = json.dumps(body, default=lambda o: self.__default_converter(o), sort_keys=True, indent=4)
        return payload

    def __make_payload_api_log_pods(self, data):

        body = {
            "event_type": "Ejecución de Discord",
            "client_payload": {
                "type_cfg": data["type_cfg"],
                "label_app": data["label_app"],
                "show_logs": data["show_logs"],
                "data": data["data"]}
        }

        payload = json.dumps(body, default=lambda o: self.__default_converter(o), sort_keys=True, indent=4)
        return payload

    def __make_payload_clean(self, data):

        body = {
            "event_type": "wake-up-manager",
            "client_payload": {
                "MDP_LIST": data
            }
        }

        payload = json.dumps(body, default=lambda o: self.__default_converter(o), sort_keys=True, indent=4)
        return payload

    def __default_converter(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return obj.__dict__

    def __get_available_repositories(self):
        """

        :param bot_discord:
        :return: devuelve el nombre de los repositorios a correr
        """
        repos_to_run = []
        res_ambientes = self.get_org_repos()
        for ambiente in res_ambientes:
            if '-' in ambiente:
                amb_org = ambiente.split('-')[-2]
                repo_org = ambiente.split('-')[-1]
                if amb_org in self.valid_envs and repo_org in self.valid_repos:
                    repos_to_run.append(ambiente)
        return repos_to_run
