import requests
import json

endpoint = "http://localhost:7200"
repo_name = "anin3"
get_repositories = "/rest/repositories"

res = requests.get(endpoint + get_repositories)
res = json.loads(res.text)
print(res.text)