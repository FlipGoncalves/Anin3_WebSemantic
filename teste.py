import json
import requests

endpoint = "http://localhost:7200"
repo_name = "teste"

url = endpoint
query = """
    PREFIX ent: <http://anin3/ent/>
    PREFIX pred: <http://anin3/pred/>
    select ?anime_title ?rank
    where{
        ?s pred:title ?anime_title .
        ?s pred:rank ?rank
    }
    """
data = {'query':query}

res = requests.get(endpoint + '/repositories/' + repo_name, params=data)
print(res.text)
res = json.loads(res.json)
for e in res['results']['bindings']:
    print(e['anime_title']['value'])