from rdflib import Graph, Namespace, URIRef, Literal

g = Graph()
gOntologia = Graph()

# descomentar gOntologia e comentar o g para fazer apenas um ficheiro, ao contrario pr dois ficheiros
# g.parse('animes.n3')
gOntologia.parse('animes.n3')

obj = Namespace("http://anin3/classobject/")
pred = Namespace("http://anin3/pred/")
ent = Namespace("http://anin3/ent/")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

gOntologia.bind("obj", obj)
gOntologia.bind("pred", pred)
gOntologia.bind("ent", ent)

gOntologia.add((obj.Source, rdf.type, rdfs.Class))
gOntologia.add((obj.Type, rdf.type, rdfs.Class))

gOntologia.add((obj.Person, rdf.type, rdfs.Class))
gOntologia.add((obj.Voice_Actor, rdf.type, rdfs.Class))
gOntologia.add((obj.Singer, rdf.type, rdfs.Class))
gOntologia.add((obj.Voice_Actor, rdf.subClassOf, rdfs.Person))
gOntologia.add((obj.Singer, rdf.subClassOf, rdfs.Person))

sources = []
for s, p, o in g.triples((None, pred.source, None)):
    sources.append(str(o))

for source in list(set(sources)):
    name = source.replace(" ", "")
    gOntologia.add((URIRef("http://anin3/classobject/"+name), rdf.type, rdfs.Class))
    gOntologia.add((URIRef("http://anin3/classobject/"+name), rdfs.subClassOf, obj.Source))
    gOntologia.add((URIRef("http://anin3/classobject/"+name), pred.value, Literal(source)))

types = []
for s, p, o in g.triples((None, pred.type, None)):
    types.append(str(o))

for typ in list(set(types)):
    name = typ.replace(" ", "")
    gOntologia.add((URIRef("http://anin3/classobject/"+name), rdf.type, rdfs.Class))
    gOntologia.add((URIRef("http://anin3/classobject/"+name), rdfs.subClassOf, obj.Type))
    gOntologia.add((URIRef("http://anin3/classobject/"+name), pred.value, Literal(typ)))

for s, p, o in g.triples((None, pred.title, None)):
    gOntologia.add((s, rdf.type, obj.Anime))
    for _, p2, o2 in g.triples((s, None, None)):
        o2 = o2.replace(" ", "")
        if p2 == pred.type:
            gOntologia.add((s, rdf.member, URIRef("http://anin3/classobject/"+str(o2))))

        if p2 == pred.source:
            gOntologia.add((s, rdf.member, URIRef("http://anin3/classobject/"+str(o2))))

        if p2 == pred.voiced_at:
            gOntologia.add((URIRef(o2), rdf.member, obj.Voice_Actor))

        if p2 == pred.opening or p2 == pred.ending:
            for mus, p3, sing in g.triples((URIRef(o2), pred.played_by, None)):
                gOntologia.add((URIRef(sing), rdf.member, obj.Singer))

    g.remove((s, pred.type, None))
    g.remove((s, pred.source, None))

n3 = gOntologia.serialize(format='n3')

with open("animesOntologyALL.n3", "w") as f:
    f.write(n3)