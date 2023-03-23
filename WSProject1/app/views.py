from django.shortcuts import render
from rdflib import Graph
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import random

endpoint = "http://localhost:7200"
repo_name = "teste"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)

# Create your views here.
def index(request):
    return render(request, "index.html")

def voiceActor(request, nome):
    query = """
    PREFIX ent: <http://anin3/ent/>
    PREFIX pred: <http://anin3/pred/>
    select *
    where{
        ?voice_actor pred:name \"""" + nome + """\".
        ?voice_actor pred:played ?character .
        ?character pred:name ?character_name .
        ?character pred:role ?role .
        ?anime pred:starring ?character .
        ?anime pred:title ?animename .
    }
    """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
    repo_name=repo_name)
    res = json.loads(res)

    data = {}
    data["Name"] = nome

    for a in res['results']['bindings']:
        if "Characters" in data.keys():
            data["Characters"].append({"Name": a['character_name']['value'], "Role": a['role']['value'], "Anime": a['animename']['value']})    
        else:
            data["Characters"] = [{"Name": a['character_name']['value'], "Role": a['role']['value'], "Anime": a['animename']['value']}]

    return render(request, "voice.html", {'data': data})

def animeTitle(request, title):

    query = """
    PREFIX ent: <http://anin3/ent/>
    PREFIX pred: <http://anin3/pred/>
    select *
    where{
        ?anime pred:title \"""" + title + """\".
        ?anime pred:starring ?character .
        ?character pred:name ?character_name .
        ?character pred:role ?role .
        ?voice_actor pred:played ?character .
        ?voice_actor pred:name ?voice_actor_name .
    }
    """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
    repo_name=repo_name)
    res = json.loads(res)

    data = {}
    data["Name"] = title

    for a in res['results']['bindings']:
        if "Characters" in data.keys():
            data["Characters"].append({"Name": a['character_name']['value'], "Role": a['role']['value'], "VoiceActor": a['voice_actor_name']['value']})    
        else:
            data["Characters"] = [{"Name": a['character_name']['value'], "Role": a['role']['value'], "VoiceActor": a['voice_actor_name']['value']}]

    return render(request, "anime.html", {'data': data})

def randomAnime(request):

    rank = random.randint(1,10)

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
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query,
    repo_name=repo_name)
    res = json.loads(res)

    data = {}
    data["Name"] = res['results']['bindings'][0]['title']['value']

    for a in res['results']['bindings']:
        if "Characters" in data.keys():
            data["Characters"].append({"Name": a['character_name']['value'], "Role": a['role']['value'], "VoiceActor": a['voice_actor_name']['value']})    
        else:
            data["Characters"] = [{"Name": a['character_name']['value'], "Role": a['role']['value'], "VoiceActor": a['voice_actor_name']['value']}]


    return render(request, "anime.html", {'data': data})