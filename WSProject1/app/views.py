from django.shortcuts import render, redirect
from rdflib import Graph
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import random
import requests
import re

endpoint = "http://localhost:7200"
repo_name = "anin3"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)
pred = "http://anin3/pred/"


def refactorData(res):

    # data = {"theme": [], "genre": []}
    data = {"theme": [], "genre": [], "characters": [], "openings": [], "endings": []}

    for a in res['results']['bindings']:

        p = a["pred"]["value"].replace(pred, "")

        if p == "theme" or p == "genre":
            data[p].append(a["object"]["value"])

        elif p == "starring" and "charname" in a.keys():
            data["characters"].append({"name": a['charname']['value'], "role": a['charrole']['value'], "voiceactor": a['vcname']['value']})
            # if "characters" in data.keys():
            #     data["characters"].append({"name": a['charname']['value'], "role": a['charrole']['value'], "voiceactor": a['vcname']['value']})    
            # else:
            #     data["characters"] = [{"name": a['charname']['value'], "role": a['charrole']['value'], "voiceactor": a['vcname']['value']}]

        elif p == "opening" and "opname" in a.keys():
            data["openings"].append({"name": a['opname']['value'], "opartist": a['opa']['value']}) 
            # if "openings" in data.keys():
            #     data["openings"].append({"name": a['opname']['value'], "opartist": a['opa']['value']})    
            # else:
            #     data["openings"] = [{"name": a['opname']['value'], "opartist": a['opa']['value']}]

        elif p == "ending" and "opname" in a.keys():
            data["endings"].append({"name": a['opname']['value'], "endartist": a['opa']['value']}) 
            # if "endings" in data.keys():
            #     data["endings"].append({"name": a['opname']['value'], "endartist": a['opa']['value']})    
            # else:
            #     data["endings"] = [{"name": a['opname']['value'], "endartist": a['opa']['value']}]

        else:
            data[p] = a["object"]["value"]

    return data


def homePage(request):

    query = f"""
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX pred:<http://anin3/pred/>
        PREFIX ent:<http://anin3/ent/>
        SELECT ?title ?rk
        WHERE {{ 
            ?anime pred:rank ?rk .
            ?anime pred:title ?title .
            FILTER ( xsd:integer(?rk) < xsd:integer("11") )
        }} LIMIT 10
    """
    
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)

    res = json.loads(res)

    data = {"animes": []}

    for a in res['results']['bindings']:
        data["animes"].append({"Title": a['title']['value'], "Rank": a['rk']['value']})

    data = sorted(data["animes"], key=lambda a: int(a["Rank"]))

    return render(request, "index.html", {'data': data})


def voiceActor(request, nome):

    query = f"""
        PREFIX ent: <http://anin3/ent/>
        PREFIX pred: <http://anin3/pred/>
        SELECT ?character_name ?role ?animename
        WHERE {{
            ?voice_actor pred:name "{nome}".
            ?voice_actor pred:played ?character .
            ?character pred:name ?character_name .
            ?character pred:role ?role .
            ?anime pred:starring ?character .
            ?anime pred:title ?animename .
        }}
    """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)

    data = {"Name": nome}

    for a in res['results']['bindings']:
        if "Characters" in data.keys():
            data["Characters"].append({"Name": a['character_name']['value'], "Role": a['role']['value'], "Anime": a['animename']['value']})    
        else:
            data["Characters"] = [{"Name": a['character_name']['value'], "Role": a['role']['value'], "Anime": a['animename']['value']}]

    return render(request, "voice.html", {'data': data})


def animeTitle(request, title):

    query = f"""
        PREFIX ent: <http://anin3/ent/>
        PREFIX pred: <http://anin3/pred/>
        SELECT *
        WHERE {{
            {{
                ?anime pred:title "{title}" .
                ?anime ?pred ?object .
                FILTER (isliteral(?object))
            }}
            UNION
            {{
                ?anime pred:title "{title}" .
                ?anime ?pred ?object .
                ?object pred:name ?charname .
                ?object pred:role ?charrole .
                ?vc pred:played ?object .
                ?vc pred:name ?vcname .
            }}
            UNION
            {{
                ?anime pred:title "{title}" .
                ?anime ?pred ?object .
                ?object pred:name ?opname .
                ?object pred:played_by ?op .
                ?op pred:name ?opa .
            }}
        }}
    """
    
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)

    res = json.loads(res)

    data = refactorData(res)

    return render(request, "anime.html", {'data': data})


def randomAnime(request):

    rank = random.randint(1,10000-1)

    query = f"""
        PREFIX ent: <http://anin3/ent/>
        PREFIX pred: <http://anin3/pred/>
        SELECT ?title
        WHERE {{
            ?anime pred:rank "{rank}" .
            ?anime pred:title ?title .
        }}
    """
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)

    res = json.loads(res)

    return redirect(f'/anime/{res["results"]["bindings"][0]["title"]["value"]}/')


def searchByName(request):

    text = request.GET.get('query')
    query = f"""
        PREFIX ent: <http://anin3/ent/>
        PREFIX pred: <http://anin3/pred/>
        SELECT ?charname ?title ?vcname
        WHERE {{
            {{
                ?s pred:title ?title .
                FILTER (contains(?title, "{text}"))
            }}
            UNION
            {{
                ?s pred:starring ?character .
                ?character pred:name ?charname .
                ?s pred:title ?title .
                FILTER (contains(?charname, "{text}"))        
            }}
            UNION
            {{
                ?s pred:voiced_at ?vc .
                ?vc pred:name ?vcname .
                ?s pred:title ?title .
                FILTER (contains(?vcname, "{text}"))
            }}
        }}
    """
    
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)

    res = json.loads(res)

    data = {"animes": [], "characters": [], "voiceactors": []}

    for a in res['results']['bindings']:
        if "charname" in a.keys():
            data["characters"].append({"Title": a["title"]["value"], "Character": a["charname"]["value"]})
        elif "vcname" in a.keys():
            data["voiceactors"].append({"Title": a["title"]["value"], "VoiceActor": a["vcname"]["value"]})
        else:
            data["animes"].append({"Title": a["title"]["value"]})

    return render(request, "search.html", {'data': data, 'text': text})


def getGenres(request):

    query = f"""
        PREFIX ent: <http://anin3/ent/>
        PREFIX pred: <http://anin3/pred/>
        SELECT DISTINCT ?genres
        WHERE {{ 
            {{
                ?s pred:theme ?genres .
            }}
            UNION
            {{
                ?s pred:genre ?genres .
            }}
        }}
    """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)

    res = json.loads(res)

    data = {"genres": []}

    for a in res['results']['bindings']:
        data["genres"].append(a["genres"]["value"])

    return render(request, "allgenre.html", {'data': data})


def animeByGenre(request, genre):

    query = f"""
        PREFIX ent: <http://anin3/ent/>
        PREFIX pred: <http://anin3/pred/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT DISTINCT ?title ?rank
        WHERE {{ 
            {{
                ?anime pred:theme "{genre}" .
            }}
            UNION
            {{
                ?anime pred:genre "{genre}" .
            }}
            {{
                ?anime pred:rank ?rank .
                ?anime pred:title ?title.

            }}
        }} ORDER BY ASC(xsd:integer(?rank)) LIMIT 20
    """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)

    res = json.loads(res)

    data = {"animes": []}

    for a in res['results']['bindings']:
        data["animes"].append({"Title": a['title']['value'], "Rank": a['rank']['value']})
    
    data = sorted(data["animes"], key=lambda a: int(a["Rank"]))
    return render(request, "genre.html", {'data': data, 'genre': genre})


def insertData(request):
    if request.method == 'POST':
        # Get the form data
        title = request.POST.get('title')

        if title == "":
            return render(request, 'insert.html', {'error': "Could not create a new Anime"})

        genre = request.POST.get('genre')
        score = request.POST.get('score')
        eps = request.POST.get('numeps')
        rank = request.POST.get('rank')
        status = request.POST.get('status')
        duration = request.POST.get('duration')
        studio = request.POST.get('studio')
        demographic = request.POST.get('demo')

        identification = re.sub("[^\d\w\'°.]", "", title)

        query = f"""
            PREFIX ent: <http://anin3/ent/>
            PREFIX pred: <http://anin3/pred/>
            INSERT DATA
            {{
                ent:{identification} pred:title "{title}" ;
                    pred:rank "{rank}" ;
                    pred:website "" ;
                    pred:score "{score}" ;
                    pred:type "" ;
                    pred:num_episodes "{eps}" ;
                    pred:source "" ;
                    pred:status "{status}" ;
                    pred:aired_date "" ;
                    pred:age_rating "" ;
                    pred:popularity "" ;
                    pred:num_members "" ;
                    pred:made_by "{studio}" ;
                    pred:duration "{duration}" ;
                    pred:premiered "" ;
                    pred:demographic "{demographic}" ;
                    pred:genre "{genre}" ;
                    pred:adaptated_from "" .
            }}
        """

        payload_query = {"update": query, "baseURI": "http://anin3/"}

        res = requests.post(endpoint+f"/repositories/{repo_name}/statements", params=payload_query, headers={"Content-Type": "application/rdf+xml", 'Accept': 'application/json'})

        if res.status_code != 204:
            return render(request, 'insert.html', {'error': "Could not create a new Anime"})
        
        return render(request, 'insert.html', {'success': "Anime created successfully"})
    else:
        return render(request, 'insert.html')
