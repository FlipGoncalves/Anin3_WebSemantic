from django.apps import AppConfig
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import requests
import os
from .utils import SPINInference

endpoint = "http://localhost:7200"
repo_name = "anin3"
get_repositories = "/rest/repositories"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)   


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
            
            dir_partition = file_dir.partition("WebSemanticaProjeto")

            main_dir = dir_partition[0] + dir_partition[1]

            repo_config_dir = os.path.join(main_dir + os.sep, "anin3-config.ttl")

            data_dir = os.path.join(main_dir + os.sep, "animes.n3")
            
            with open(repo_config_dir, 'r', encoding='utf-8') as file:
                data = file.readlines()

            data[41] = "            graphdb:imports \"" + data_dir + "\" ;\n"
            
            with open(repo_config_dir, 'w', encoding='utf-8') as file:
                file.writelines(data)

            #Repo does not exist
            with open(repo_config_dir, 'rb') as f: 
                res = requests.post(endpoint + "/rest/repositories", files={'config':f})
                print("Repository created and data inserted.")

            SPINInference.main()
            print("Inference applied to data.")