from django.shortcuts import render
from rdflib import Graph
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import random

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
        SELECT *
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
        SELECT *
        WHERE {{
            {{
                ?anime pred:rank "{rank}" .
                ?anime ?pred ?object .
                FILTER (isliteral(?object))
            }}
            UNION
            {{
                ?anime pred:rank "{rank}" .
                ?anime ?pred ?object .
                ?object pred:name ?charname .
                ?object pred:role ?charrole .
                ?vc pred:played ?object .
                ?vc pred:name ?vcname .
            }}
            UNION
            {{
                ?anime pred:rank "{rank}" .
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
        SELECT DISTINT ?genres
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

    return render(request, "index.html", {'data': data})


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

    query = f"""

        PREFIX ent: <http://anin3/ent/>
        PREFIX pred: <http://anin3/pred/>
        INSERT DATA
        {{
            ent:Character1 pred:name "char1";
                        pred:role "role1" .	
            
            ent:Character2 pred:name "char2";
                        pred:role "role2" .	
            
            ent:VA1 pred:played ent:Character1;
                    pred:name "VA1" .	
            
            ent:VA2 pred:played ent:Character2;
                    pred:name "VA2" .	
            
            ent:OP pred:name "OP" ;
                pred:played_by ent:OPA .
            
            ent:END pred:name "END" ;
                    pred:played_by ent:ENDA .
            
            ent:OPA pred:name "OPA" .
                                    
            ent:ENDA pred:name "ENDA" .
            
            ent:Teste1 pred:title "Anime Do Filipe" ;
                pred:rank "AA" ;
                pred:website "ggg" ;
                pred:score "ggg" ;
                pred:type "ggg" ;
                pred:num_episodes "ggg" ;
                pred:source "ggg" ;
                pred:status "ggg" ;
                pred:aired_date "ggg" ;
                pred:age_rating "ggg" ;
                pred:popularity "ggg" ;
                pred:num_members "ggg" ;
                pred:made_by "ggg" ;
                pred:duration "ggg" ;
                pred:premiered "ggg" ;
                pred:demographic "ggg" ;
                                        
                pred:genre "ggg" ;
                pred:genre "hhh" ;
                                    
                pred:theme "ggg" ;
                pred:theme "hhh" ;
                            
                pred:adaptated_from "ggg" ;
                                            
                pred:sequel ent:ID ;
                                    
                pred:prequel ent:Bleach ;
                                    
                pred:voiced_at ent:VA1 ;
                pred:starring ent:Character1 ;
                pred:voiced_at ent:VA2 ;
                pred:starring ent:Character2 ;
                pred:opening ent:OP ;             
                pred:ending ent:END .
        }}

    """

    return render(request, "insert.html")

def formData(request):
    return render(request,"insert.html")


# def add_book(request):
#     if request.method == 'POST':
#         form = BookForm(request.POST)
#         if form.is_valid():
#             form.save()
#             # redirect to success page
#     else:
#         form = BookForm()
#     return render(request, 'add_book.html', {'form': form})