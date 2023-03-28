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
        if(not repo_exists):
            file_dir = os.path.abspath(__file__)
            
            dir_partition = file_dir.partition("WebSemanticaTrabalho1")

            main_dir = dir_partition[0] + dir_partition[1]

            repo_config_dir = main_dir + "\\anin3-config.ttl"

            print(repo_config_dir)

            #Repo does not exist
            with open(repo_config_dir, 'rb') as f: 
                res = requests.post(endpoint + "/rest/repositories", files={'config':f})
                print(res.status_code)
                print(res.text)

            #Check if dir to import data exists, if not create
            user = os.getenv('USERPROFILE')

            isExist = os.path.exists(user + "\graphdb-import")

            if not isExist:
                os.makedirs(user + "\graphdb-import")

            #Import .nt file to dir to be imported to repository
            data_dir = main_dir + "\\animes.nt"
            print(data_dir)

            shutil.copy(data_dir, user + "\graphdb-import")

            data = '{"fileNames": ["animes.nt"]}'
            headers = {'Content-type': 'application/json'}

            res2 = requests.post(endpoint + "/rest/repositories/anin3/import/server",headers=headers , data=data)
            print(res2.status_code)
            print(res2.text)


