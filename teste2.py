import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import random

endpoint = "http://localhost:7200"
repo_name = "teste"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)

# lista = graph.query( [('?voice_actor', 'http://anin3/pred/name', nome),
    #                       ('?voice_actor', 'http://anin3/pred/played', '?character'),
    #                       ('?character', 'http://anin3/pred/name', '?character_name'),
    #                       ('?character', 'http://anin3/pred/role', '?role'),
    #                       ('?anime', 'http://anin3/pred/starring', '?character'),
    #                       ('?anime','http://anin3/pred/title', '?animename'),
    #                     ] )

rank = float(random.randint(1,10))

query = """
PREFIX ent: <http://anin3/ent/>
PREFIX pred: <http://anin3/pred/>
select *
where{
    ?anime pred:rank \"""" + str(rank) + """\".
    ?anime pred:title ?title .
    ?anime pred:starring ?character .
    ?character pred:name ?character_name .
    ?character pred:role ?role .
    ?voice_actor pred:played ?character .
    ?voice_actor pred:name ?voice_actor_name .
}
"""
print (query)
payload_query = {"query": query}
res = accessor.sparql_select(body=payload_query,
repo_name=repo_name)
res = json.loads(res)
print(res)
print("CAGUEI")
print(res['results']['bindings'][0]['title']['value'])

data = {}
data["Name"] = res['results']['bindings']['title']['value']

for a in res['results']['bindings']:
    if "Characters" in data.keys():
        data["Characters"].append({"Name": a['character_name']['value'], "Role": a['role']['value'], "Anime": a['animename']['value']})    
    else:
        data["Characters"] = [{"Name": a['character_name']['value'], "Role": a['role']['value'], "Anime": a['animename']['value']}]
