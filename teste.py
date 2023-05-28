from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

dbpedia = SPARQLWrapper("https://dbpedia.org/sparql")
dbpedia.setReturnFormat(JSON)

title = "/Naruto"

query = f"""
SELECT * WHERE {{
     ?res a dbo:Anime
     FILTER regex(?res, "{title}", "i")
}}
"""

dbpedia.setQuery(query)

dbpedia_uri = ""

try:
    ret = dbpedia.queryAndConvert()

    for r in ret["results"]["bindings"]:
        temp2 = "http://dbpedia.org/resource" + title
        temp3 = "http://dbpedia.org/resource" + title + "__tv_series__1"
        if r['res']['value'] == temp2 or r['res']['value'] == temp3:
            dbpedia_uri = r['res']['value']
except Exception as e:
    print(e)

print(dbpedia_uri)

query = f"""
SELECT distinct ?sub_label ?pred_label
WHERE {{
 <{dbpedia_uri}> ?property ?value .
 ?property rdfs:label ?pred_label .
 ?value rdfs:label ?sub_label .
 FILTER(lang(?pred_label) = "en" && lang(?sub_label) = "en")
}}
"""

dbpedia.setQuery(query)

try:
    ret = dbpedia.queryAndConvert()
    print(ret)
    for r in ret["results"]["bindings"]:
        print(r)
except Exception as e:
    print(e)

## Query para ter todos os animes que existem na wikidata
# sparql.setQuery("""
#     SELECT DISTINCT ?item ?item_label WHERE {
#   ?item p:P31 ?statement0.
#   ?statement0 ps:P31 wd:Q63952888.
#   ?item rdfs:label ?item_label.
#   FILTER(((LANG(?item_label)) = "en"))
#   SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
# }
#  """
# )

##todas as informaçoes sobre um anime na wikidata
# sparql.setQuery("""
# SELECT ?pred ?pred2 ?pred_label ?sub ?sub_label
# WHERE
# {
# wd:Q26971382 ?pred ?sub.
# ?pred2 wikibase:directClaim ?pred .
# ?pred2 rdfs:label ?pred_label .
# ?sub rdfs:label ?sub_label.
# Filter (lang(?sub_label) = 'en' && lang(?pred_label) = 'en')
# SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
# }
# """
# )

##Get id from name
# sparql.setQuery("""
#     SELECT distinct ?id
# where
# {
#   ?id p:P31 ?statement0.
#   ?statement0 ps:P31 wd:Q63952888.
#   ?id rdfs:label "Naruto"@en.
#   SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
# }
# """
# )

## Get id from regex name
# sparql.setQuery("""
# SELECT distinct ?id
# where
# {
#   ?id p:P31 ?statement0.
#   ?statement0 ps:P31 wd:Q63952888.
#   ?id rdfs:label ?item_label.
#   FILTER regex(?item_label, "Naruto")
#   filter (LANG(?item_label) = "en")
#   SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
# }
# }
# """
# )


## Every query combined
# sparql.setQuery("""
# SELECT ?id ?pred ?pred2 ?pred_label ?sub ?sub_label WHERE {
#   ?id rdfs:label "Naruto"@en.
#   ?id p:P31 ?statement0.
#   ?statement0 ps:P31 wd:Q63952888.
#   ?id ?pred ?sub .
#   ?pred2 wikibase:directClaim ?pred;
#   rdfs:label ?pred_label.
#   ?sub rdfs:label ?sub_label.
#   FILTER(((LANG(?sub_label)) = "en") && ((LANG(?pred_label)) = "en"))
#   SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
# }
# """)


# query_wikidata = f"""
#     SELECT ?id ?pred_label ?sub_label WHERE {{
#     ?id rdfs:label "Naruto: Shippuuden"@en.
#     ?id p:P31 ?statement0.
#     ?statement0 ps:P31 wd:Q63952888.
#     ?id ?pred ?sub .
#     ?pred2 wikibase:directClaim ?pred;
#     rdfs:label ?pred_label.
#     ?sub rdfs:label ?sub_label.
#     FILTER(((LANG(?sub_label)) = "en") && ((LANG(?pred_label)) = "en"))
#     SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
#     }}
# """

# sparql.setQuery(query_wikidata)

# try:
#     ret = sparql.queryAndConvert()

#     for r in ret["results"]["bindings"]:
#         print(r)
# except Exception as e:
#     print(e)