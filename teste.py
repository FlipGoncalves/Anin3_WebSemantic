from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://localhost:7200/repositories/Anin3_Ontology")
sparql.setReturnFormat(JSON)

sparql.setQuery("""
    PREFIX dc: <http://mydata.com/dc>
    prefix celc: <http://mydata.com/celc/>
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    select ?s ?p ?o
    where {
        ?s rdf:type celc:Celebrity ;
            ?p ?o .

    }
"""
)

try:
    ret = sparql.queryAndConvert()

    for r in ret["results"]["bindings"]:
        print(r)
except Exception as e:
    print(e)