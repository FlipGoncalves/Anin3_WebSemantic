import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
import re
import random

g = Graph()
pred = Namespace("http://anin3/pred/")
ent = Namespace("http://anin3/ent/")
g.bind("pred", pred)
g.bind("ent", ent)

animes = pd.read_csv("animes.csv")

def removeTitle(var):
    return re.sub("[<>\"]", "", var).replace("\\", "")

def removeID(var):
    id_ = re.sub("[^\da-zA-Z]", "", var.replace(" ", ""))
    if id_ == "":
        id_ = "id0"
    return id_

openings = []
endings = []

for _, rank, title, link, score, type, episodes, source, status, premiered, aired_date, studios, genres, themes, demographic, duration, age_rating, _, popularity, members, _, adaptation, sequel, prequel, characters, role, voice_actors, ops, ops_artist, ends, ends_artist in animes.values[:1000]:

    print(int(rank))

    title = removeTitle(title)
    anime_ID = removeID(title)

    same = True
    while same:
        same = False
        for s,p,o in g.triples((URIRef("http://anin3/ent/"+anime_ID), None, None)):
            if p == pred.title:
                same = False
                break
            same = True
            anime_ID += "0"
            break

    anime_ID = URIRef("http://anin3/ent/"+anime_ID)

    g.add((anime_ID, pred.title, Literal(title)))
    g.add((anime_ID, pred.rank, Literal(int(rank))))
    g.add((anime_ID, pred.website, Literal(link)))
    g.add((anime_ID, pred.score, Literal(score)))
    g.add((anime_ID, pred.type, Literal(type)))
    g.add((anime_ID, pred.num_episodes, Literal(episodes)))
    g.add((anime_ID, pred.source, Literal(source)))
    g.add((anime_ID, pred.status, Literal(status)))
    g.add((anime_ID, pred.aired_date, Literal(aired_date)))
    g.add((anime_ID, pred.age_rating, Literal(age_rating)))
    g.add((anime_ID, pred.popularity, Literal(popularity)))
    g.add((anime_ID, pred.num_members, Literal(members)))


    if studios != "None found, add some":
        g.add((anime_ID, pred.made_by, Literal(studios)))

    if pd.notna(duration):
        duration = re.sub("[.]", "", duration)
        g.add((anime_ID, pred.duration, Literal(duration)))
    if pd.notna(premiered):
        g.add((anime_ID, pred.premired, Literal(premiered)))
    if pd.notna(demographic):
        g.add((anime_ID, pred.demographic, Literal(demographic)))
    if pd.notna(genres):
        for genre in genres.split(","):
            if genre != "":
                g.add((anime_ID, pred.genre, Literal(genre)))
    if pd.notna(themes):
        for theme in themes.split(","):
            if theme != "":
                g.add((anime_ID, pred.theme, Literal(theme)))
    if pd.notna(adaptation):
        adaptation = removeTitle(adaptation)
        g.add((anime_ID, pred.adapted_from, Literal(adaptation)))


    if pd.notna(sequel):
        sequel_ID = removeID(removeTitle(sequel))

        found = False
        for s,p,o in g.triples((None, pred.title, sequel)):
            sequel_ID = str(s)
            found = True

        if not found:
            same = True
            while same:
                same = False
                count = 0
                for s,p,o in g.triples((URIRef("http://anin3/ent/"+sequel_ID), None, None)):
                    count += 1
                    if p == pred.played or p == pred.played_by or p == pred.title or p == pred.role:
                        same = True
                        sequel_ID += "0"
                        break
                if count == 1:
                    same = True
                    sequel_ID += "0"
        
        g.add((anime_ID, pred.sequel, URIRef("http://anin3/ent/"+sequel_ID)))
        g.add((URIRef("http://anin3/ent/"+sequel_ID), pred.title, Literal(sequel)))
    if pd.notna(prequel):
        prequel_ID = removeID(removeTitle(prequel))

        found = False
        for s,p,o in g.triples((None, pred.title, prequel)):
            prequel_ID = str(s)
            found = True

        if not found:
            same = True
            while same:
                same = False
                count = 0
                for s,p,o in g.triples((URIRef("http://anin3/ent/"+prequel_ID), None, None)):
                    count += 1
                    if p == pred.played or p == pred.played_by or p == pred.title or p == pred.role:
                        same = True
                        prequel_ID += "0"
                        break
                if count == 1:
                    same = True
                    prequel_ID += "0"
                    
        g.add((anime_ID, pred.prequel, URIRef("http://anin3/ent/"+prequel_ID)))
        g.add((URIRef("http://anin3/ent/"+prequel_ID), pred.title, Literal(prequel)))


    characters = [char for char in characters.strip('][').split('\'') if char != "" and char != ", "]
    voice_actors = [removeTitle(vc) for vc in voice_actors.strip('][').split('\'') if vc != "" and vc != ", "]
    role = role.strip('][').split(', ')

    for character in characters:
        char_name = removeTitle(character)
        char_ID = removeID(char_name)
        role_c = role[characters.index(character)%len(role)].replace("\'", "")

        same = True
        while same:
            same = False
            count = 0
            for s,p,o in g.triples((URIRef("http://anin3/ent/"+char_ID), None, None)):
                count += 1
                if p == pred.played or p == pred.played_by or p == pred.title:
                    same = True
                    char_ID += "0"
                    break
            if count == 1:
                same = True
                char_ID += "0"

        g.add((URIRef("http://anin3/ent/"+char_ID), pred.role, Literal(role_c)))
        g.add((URIRef("http://anin3/ent/"+char_ID), pred.char_name, Literal(char_name)))

        if len(voice_actors) > 0:
            vc_name = voice_actors[characters.index(character)%len(voice_actors)].replace(",", "")
            vc = removeID(vc_name)

            same = True
            while same:
                same = False
                count = 0
                for s,p,o in g.triples((URIRef("http://anin3/ent/"+vc), None, None)):
                    count += 1
                    if p == pred.role or p == pred.played_by or p == pred.title:
                        same = True
                        vc += "0"
                        break
                if count == 1:
                    same = True
                    vc += "0"

            g.add((URIRef("http://anin3/ent/"+vc), pred.played, URIRef("http://anin3/ent/"+char_ID)))
            g.add((URIRef("http://anin3/ent/"+vc), pred.va_name, Literal(vc_name)))
            g.add((anime_ID, pred.voiced_at, URIRef("http://anin3/ent/"+vc)))
        g.add((anime_ID, pred.starring, URIRef("http://anin3/ent/"+char_ID)))
    
    if pd.notna(ops):
        if "[" in ops_artist:
            ops_artist = [removeTitle(opa) for opa in ops_artist.strip('][').split('\'') if opa != "" and opa != ", "]
        ops = [removeTitle(op) for op in ops.strip('][').split('\'') if op != "" and op != ", "]

        for op in ops:
            op_ID = removeID(op)

            same = True
            while same:
                same = False
                for s,p,o in g.triples((URIRef("http://anin3/ent/"+op_ID), None, None)):
                    same = True
                    op_ID += "0"
                    break
                if URIRef("http://anin3/ent/"+op_ID) in endings:
                    same = True
                    op_ID += "0"

            g.add((anime_ID, pred.opening, URIRef("http://anin3/ent/"+op_ID)))
            g.add((URIRef("http://anin3/ent/"+op_ID), pred.op_name, Literal(op)))
            openings.append(URIRef("http://anin3/ent/"+op_ID))

            if "[" in ops_artist or len(ops_artist) > 0:
                op_artist = ops_artist[ops.index(op)%len(ops_artist)].replace(",", "")
                op_artist_ID = removeID(op_artist)

                same = True
                while same:
                    same = False
                    for s,p,o in g.triples((URIRef("http://anin3/ent/"+op_artist_ID), None, None)):
                        if p == pred.role or p == pred.played or p == pred.played_by or p == pred.title:
                            same = True
                            op_artist_ID += "0"
                            break
                    if not same and (URIRef("http://anin3/ent/"+op_artist_ID) in openings or URIRef("http://anin3/ent/"+op_artist_ID) in endings):
                        same = True
                        op_artist_ID += "0"
                        continue
                    for s,p,o in g.triples((URIRef("http://anin3/ent/"+op_artist_ID), pred.sing_name, None)):
                        if o != Literal(op_artist):
                            same = True
                            op_artist_ID += "0"
                            break
                    for s,p,o in g.triples((URIRef("http://anin3/ent/"+op_artist_ID), pred.op_name, None)):
                        if o != Literal(op_artist):
                            same = True
                            op_artist_ID += "0"
                            break

                g.add((URIRef("http://anin3/ent/"+op_ID), pred.played_by, URIRef("http://anin3/ent/"+op_artist_ID)))
                g.add((URIRef("http://anin3/ent/"+op_artist_ID), pred.sing_name, Literal(op_artist)))

    if pd.notna(ends):
        if "[" in ends_artist:
            ends_artist = [removeTitle(enda) for enda in ends_artist.strip('][').split('\'') if enda != "" and enda != ", "]
        ends = [removeTitle(end) for end in ends.strip('][').split('\'') if end != "" and end != ", "]

        for end in ends:
            end_ID = removeID(end)

            same = True
            while same:
                same = False
                for s,p,o in g.triples((URIRef("http://anin3/ent/"+end_ID), None, None)):
                    same = True
                    end_ID += "0"
                    break
                if URIRef("http://anin3/ent/"+end_ID) in openings:
                    same = True
                    end_ID += "0"

            g.add((anime_ID, pred.ending, URIRef("http://anin3/ent/"+end_ID)))
            g.add((URIRef("http://anin3/ent/"+end_ID), pred.end_name, Literal(end)))
            endings.append(URIRef("http://anin3/ent/"+end_ID))

            if "[" in ends_artist or len(ends_artist) > 0:
                end_artist = ends_artist[ends.index(end)%len(ends_artist)].replace(",", "")
                end_artist_ID = removeID(end_artist)

                same = True
                while same:
                    same = False
                    for s,p,o in g.triples((URIRef("http://anin3/ent/"+end_artist_ID), None, None)):
                        if p == pred.role or p == pred.played or p == pred.played_by or p == pred.title:
                            same = True
                            end_artist_ID += "0"
                            break
                    if not same and (URIRef("http://anin3/ent/"+end_artist_ID) in openings or URIRef("http://anin3/ent/"+end_artist_ID) in endings):
                        same = True
                        end_artist_ID += "0"
                        continue
                    for s,p,o in g.triples((URIRef("http://anin3/ent/"+end_artist_ID), pred.sing_name, None)):
                        if o != Literal(op_artist):
                            same = True
                            end_artist_ID += "0"
                            break
                    for s,p,o in g.triples((URIRef("http://anin3/ent/"+end_artist_ID), pred.end_name, None)):
                        if o != Literal(op_artist):
                            same = True
                            end_artist_ID += "0"
                            break

                g.add((URIRef("http://anin3/ent/"+end_ID), pred.played_by, URIRef("http://anin3/ent/"+end_artist_ID)))
                g.add((URIRef("http://anin3/ent/"+end_artist_ID), pred.sing_name, Literal(end_artist)))

n3 = g.serialize(format='n3')

with open("animes.n3", "w") as f:
    f.write(n3)