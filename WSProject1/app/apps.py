from django.apps import AppConfig
import json
import requests
import os
import shutil

endpoint = "http://localhost:7200"
repo_name = "anin3"
get_repositories = "/rest/repositories"

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    def ready(self):
        repo_exists = False
        #Check if repository exists
        res = requests.get(endpoint + get_repositories)
        res = json.loads(res.text)
        for repo in res:
            if(repo["id"] == "anin3"):
                repo_exists = True
                print("Repository already exists, using existing one.")
        if(not repo_exists):
            file_dir = os.path.abspath(__file__)
            
            dir_partition = file_dir.partition("WebSemanticaTrabalho1")

            main_dir = dir_partition[0] + dir_partition[1]

            repo_config_dir = main_dir + "\\anin3-config.ttl"

            data_dir = main_dir + "\\animes.nt"
            
            with open(repo_config_dir, 'r', encoding='utf-8') as file:
                data = file.readlines()

            data[41] = "            graphdb:imports \"" + data_dir + "\" ;\n"
            
            with open(repo_config_dir, 'w', encoding='utf-8') as file:
                file.writelines(data)

            #Repo does not exist
            with open(repo_config_dir, 'rb') as f: 
                res = requests.post(endpoint + "/rest/repositories", files={'config':f})
                print("Repository created and data inserted.")