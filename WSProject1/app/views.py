from django.shortcuts import render, redirect
from rdflib import Graph
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import random
import requests
import re
from SPARQLWrapper import SPARQLWrapper, JSON

sparql_repo = SPARQLWrapper("http://localhost:7200/repositories/anin3")
sparql_repo.setReturnFormat(JSON)
sparql_wikidata = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql_wikidata.setReturnFormat(JSON)
sparql_dbpedia = SPARQLWrapper("https://dbpedia.org/sparql")
sparql_dbpedia.setReturnFormat(JSON)
pred = "http://anin3/pred/"

NEW_ANIME_COUNT = 0

def refactorData(res):

    # data = {"theme": [], "genre": []}
    data = {"theme": [], "genre": [], "characters": [], "openings": [], "endings": []}

    for a in res['results']['bindings']:

        if "pred" in a.keys():
            p = a["pred"]["value"].replace(pred, "")

            if p == "theme" or p == "genre":
                data[p].append(a["object"]["value"])
            else:
                data[p] = a["object"]["value"]

        else:
            if "charname" in a.keys():
                data["characters"].append({"name": a['charname']['value'], "role": a['charrole']['value'], "voiceactor": a['vcname']['value']})
                # if "characters" in data.keys():
                #     data["characters"].append({"name": a['charname']['value'], "role": a['charrole']['value'], "voiceactor": a['vcname']['value']})    
                # else:
                #     data["characters"] = [{"name": a['charname']['value'], "role": a['charrole']['value'], "voiceactor": a['vcname']['value']}]

            elif "opname" in a.keys():
                data["openings"].append({"name": a['opname']['value'], "opartist": a['opa']['value']}) 
                # if "openings" in data.keys():
                #     data["openings"].append({"name": a['opname']['value'], "opartist": a['opa']['value']})    
                # else:
                #     data["openings"] = [{"name": a['opname']['value'], "opartist": a['opa']['value']}]

            elif "endname" in a.keys():
                data["endings"].append({"name": a['endname']['value'], "endartist": a['enda']['value']}) 
                # if "endings" in data.keys():
                #     data["endings"].append({"name": a['opname']['value'], "endartist": a['opa']['value']})    
                # else:
                #     data["endings"] = [{"name": a['opname']['value'], "endartist": a['opa']['value']}]

    return data


def homePage(request):

    query = f"""
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX pred:<http://anin3/pred/>
        PREFIX ent:<http://anin3/ent/>
        SELECT DISTINCT ?title ?rk
        WHERE {{ 
            ?anime a ent:Anime .
            ?anime pred:rank ?rk .
            ?anime pred:title ?title .
            FILTER ( xsd:integer(?rk) < xsd:integer("11") )
        }}
    """

    sparql_repo.setQuery(query)
    
    data = {"animes": []}

    print("teste")

    try:
        res = sparql_repo.queryAndConvert()

        for a in res['results']['bindings']:
            data["animes"].append({"Title": a['title']['value'], "Rank": a['rk']['value']})

        data = sorted(data["animes"], key=lambda a: int(a["Rank"]))
    except Exception as e:
        print(e)

    return render(request, "index.html", {'data': data})


def voiceActor(request, nome):

    query = f"""
        PREFIX ent: <http://anin3/ent/>
        PREFIX pred: <http://anin3/pred/>
        SELECT DISTINCT ?character_name ?role ?animename
        WHERE {{
            ?voice_actor pred:va_name "{nome}".
            ?voice_actor a ent:VoiceActor .
            ?voice_actor pred:played ?character .
            ?character a ent:Character .
            ?character pred:char_name ?character_name .
            ?character pred:role ?role .
            ?character pred:starred_at ?anime.
            ?anime a ent:Anime .
            ?anime pred:title ?animename .
        }} LIMIT 100
    """

    sparql_repo.setQuery(query)
    
    data = {"Name": nome}

    try:
        res = sparql_repo.queryAndConvert()

        for a in res['results']['bindings']:
            if "Characters" in data.keys():
                data["Characters"].append({"Name": a['character_name']['value'], "Role": a['role']['value'], "Anime": a['animename']['value']})    
            else:
                data["Characters"] = [{"Name": a['character_name']['value'], "Role": a['role']['value'], "Anime": a['animename']['value']}]
    except Exception as e:
        print(e)

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
                ?object a ent:Character .
                ?object pred:starred_at ?anime .
                ?anime a ent:Anime .
                ?anime pred:title "{title}" .
                ?object pred:char_name ?charname .
                ?object pred:role ?charrole .
                ?vc pred:played ?object .
                ?vc pred:va_name ?vcname .
                ?vc a ent:VoiceActor .
            }}
            UNION
            {{
                ?object a ent:Opening .
                ?object pred:op_played_in ?anime .
       			?anime a ent:Anime .
                ?anime pred:title "{title}" .
                ?object pred:op_name ?opname .
                ?object pred:played_by ?op .
                ?op a ent:Singer .
                ?op pred:sing_name ?opa .
            }}
            UNION
            {{
                ?object a ent:Ending .
                ?object pred:end_played_in ?anime .
       			?anime a ent:Anime .
                ?anime pred:title "{title}" .
                ?object pred:end_name ?endname .
                ?object pred:played_by ?end .
                ?end a ent:Singer .
                ?end pred:sing_name ?enda .
            }}
        }}
    """
    
    sparql_repo.setQuery(query)

    try:

        res = sparql_repo.queryAndConvert()

    except Exception as e:
        print(e)

    data = refactorData(res)

    query_wikidata = f"""
    SELECT ?id ?pred_label ?sub_label WHERE {{
    ?id rdfs:label|skos:altLabel "{title}"@en.
    ?id p:P31 ?statement0.
    ?statement0 ps:P31 wd:Q63952888.
    ?id ?pred ?sub .
    ?pred2 wikibase:directClaim ?pred;
    rdfs:label ?pred_label.
    ?sub rdfs:label ?sub_label.
    FILTER(?pred = wdt:P57 || ?pred = wdt:P364 || ?pred = wdt:P750 || ?pred = wdt:P8670 || ?pred = wdt:P272)
    FILTER(((LANG(?sub_label)) = "en") && ((LANG(?pred_label)) = "en"))
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """

    sparql_wikidata.setQuery(query_wikidata)

    data["Wikidata"] = []
    try:
        res = sparql_wikidata.queryAndConvert()
        data["Wikidata"].append({"pred_label": "Wikidata Identifier", "sub_label" : res['results']['bindings'][0]['id']['value']})
        for a in res['results']['bindings']:
            data["Wikidata"].append({"pred_label": a['pred_label']['value'], "sub_label" : a['sub_label']['value']})
    except Exception as e:
        print(e)

    data['dbpedia'] = []

    title_dbpedia = "/" + title.replace(' ', '_')

    query = f"""
    SELECT * WHERE {{
        ?res a dbo:Anime
        FILTER regex(?res, "{title}", "i")
    }}
    """

    sparql_dbpedia.setQuery(query)

    dbpedia_uri = ""

    try:
        ret = sparql_dbpedia.queryAndConvert()

        print(title_dbpedia)

        for r in ret["results"]["bindings"]:
            temp2 = "http://dbpedia.org/resource" + title_dbpedia
            temp3 = "http://dbpedia.org/resource" + title_dbpedia + "__tv_series__1"
            if r['res']['value'] == temp2 or r['res']['value'] == temp3:
                print("nice")
                dbpedia_uri = r['res']['value']
                print(dbpedia_uri)
                data['dbpedia'].append({"pred_label": "DBPedia Resource URI", "sub_label" : dbpedia_uri})
    except Exception as e:
        print(e)

    query = f"""
    SELECT distinct ?sub_label ?pred_label
    WHERE {{
    <{dbpedia_uri}> ?property ?value .
    ?property rdfs:label ?pred_label .
    ?value rdfs:label ?sub_label .
    FILTER(lang(?pred_label) = "en" && lang(?sub_label) = "en")
    }}
    """

    sparql_dbpedia.setQuery(query)

    try:
        ret = sparql_dbpedia.queryAndConvert()
        print(ret)
        for r in ret["results"]["bindings"]:
            print("fuck")
            print(r)
            data["dbpedia"].append({"pred_label": r['pred_label']['value'], "sub_label" : r['sub_label']['value']})
    except Exception as e:
        print(e)

    print(data["dbpedia"])

    return render(request, "anime.html", {'data': data})


def randomAnime(request):

    rank = random.randint(1,10000-1)

    query = f"""
        PREFIX ent: <http://anin3/ent/>
        PREFIX pred: <http://anin3/pred/>
        SELECT ?title
        WHERE {{
            ?anime a ent:Anime .
            ?anime pred:rank {rank} .
            ?anime pred:title ?title .
        }}
    """
    sparql_repo.setQuery(query)

    try:

        res = sparql_repo.queryAndConvert()

    except Exception as e:
        print(e)

    return redirect(f'/anime/{res["results"]["bindings"][0]["title"]["value"]}/')


def searchByName(request):

    text = request.GET.get('query')
    query = f"""
        PREFIX ent: <http://anin3/ent/>
        PREFIX pred: <http://anin3/pred/>
        SELECT ?charname ?title ?vcname
        WHERE {{
            {{
                    ?anime a ent:Anime .
                    ?anime pred:title ?title .
                    FILTER (contains(?title, "{text}"))
                }}
            UNION
            {{
                    ?character a ent:Character .
                    ?character pred:char_name ?charname .
                    ?character pred:starred_at ?anime .
                    ?anime pred:title ?title .
                    FILTER (contains(?charname, "{text}"))        
                }}
            UNION
            {{
                    ?voiceactor a ent:VoiceActor .
                    ?voiceactor pred:va_name ?vcname .
                    ?voiceactor pred:voiced_in ?anime .
                    ?anime pred:title ?title .
                    FILTER (contains(?vcname, "{text}"))
                }}
        }}
    """

    data = {"animes": [], "characters": [], "voiceactors": []}

    sparql_repo.setQuery(query)

    try:

        res = sparql_repo.queryAndConvert()

        for a in res['results']['bindings']:
            if "charname" in a.keys():
                data["characters"].append({"Title": a["title"]["value"], "Character": a["charname"]["value"]})
            elif "vcname" in a.keys():
                data["voiceactors"].append({"Title": a["title"]["value"], "VoiceActor": a["vcname"]["value"]})
            else:
                data["animes"].append({"Title": a["title"]["value"]})

    except Exception as e:
        print(e)

    return render(request, "search.html", {'data': data, 'text': text})


def getGenres(request):

    query = f"""
        PREFIX ent: <http://anin3/ent/>
        PREFIX pred: <http://anin3/pred/>
        SELECT DISTINCT ?genres
        WHERE {{ 
            {{
                ?s a ent:Anime .
                ?s pred:theme ?genres .
            }}
            UNION
            {{
                ?s a ent:Anime .
                ?s pred:genre ?genres .
            }}
        }}
    """

    data = {"genres": []}

    sparql_repo.setQuery(query)

    try:

        res = sparql_repo.queryAndConvert()

        for a in res['results']['bindings']:
            data["genres"].append(a["genres"]["value"])

    except Exception as e:
        print(e)

    return render(request, "allgenre.html", {'data': data})


def animeByGenre(request, genre):

    query = f"""
        PREFIX ent: <http://anin3/ent/>
        PREFIX pred: <http://anin3/pred/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT DISTINCT ?title ?rank
        WHERE {{ 
            {{
                ?anime a ent:Anime .
                ?anime pred:theme "{genre}" .
            }}
            UNION
            {{
                ?anime a ent:Anime .
                ?anime pred:genre "{genre}" .
            }}
            {{
                ?anime pred:rank ?rank .
                ?anime pred:title ?title.

            }}
        }} ORDER BY ASC(xsd:integer(?rank)) LIMIT 20
    """

    data = {"animes": []}

    sparql_repo.setQuery(query)

    try:

        res = sparql_repo.queryAndConvert()

        for a in res['results']['bindings']:
            data["animes"].append({"Title": a['title']['value'], "Rank": a['rank']['value']})

    except Exception as e:
        print(e)
    
    data = sorted(data["animes"], key=lambda a: int(a["Rank"]))
    return render(request, "genre.html", {'data': data, 'genre': genre})


def insertData(request):
    global NEW_ANIME_COUNT

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

        title = re.sub("[<>\"]", "", title).replace("\\", "")

        identification = "AnimeInserted" + NEW_ANIME_COUNT
        NEW_ANIME_COUNT += 1

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

        res = requests.post("http://localhost:7200/repositories/anin3/statements", params=payload_query, headers={"Content-Type": "application/rdf+xml", 'Accept': 'application/json'})

        if res.status_code != 204:
            return render(request, 'insert.html', {'error': "Could not create a new Anime"})
        
        return render(request, 'insert.html', {'success': "Anime created successfully"})
    else:
        return render(request, 'insert.html')
