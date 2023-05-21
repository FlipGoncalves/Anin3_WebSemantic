import pandas as pd
from rdflib import Graph, Namespace
import re
import random

anime_ByID = {}

def removeTitle(var):
    return re.sub("[<>\"]", "", var).replace("\\", "")

def removeID(var):
    return re.sub("[^\da-zA-Z\'°.]", "00", var.replace(" ", ""))

def loadCSV2NT():

    animes = pd.read_csv("animes.csv")
    triples = []

    for _, rank, title, link, score, type, episodes, source, status, premiered, aired_date, studios, genres, themes, demographic, duration, age_rating, _, popularity, members, _, adaptation, sequel, prequel, characters, role, voice_actors, ops, ops_artist, ends, ends_artist in animes.values[:100]:

        title = removeTitle(title)
        anime_ID = removeID(title)

        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/rank> \"{int(rank)}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/title> \"{title}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/website> \"{link}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/score> \"{score}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/type> \"{type}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/num_episodes> \"{episodes}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/source> \"{source}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/status> \"{status}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/aired_date> \"{aired_date}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/age_rating> \"{age_rating}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/popularity> \"{popularity}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/num_members> \"{members}\".")

        if studios != "None found, add some":
            triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/made_by> \"{studios}\".")

        if pd.notna(duration):
            duration = re.sub("[.]", "", duration)
            triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/duration> \"{duration}\".")
        if pd.notna(premiered):
            triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/premired> \"{premiered}\".")
        if pd.notna(demographic):
            triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/demographic> \"{demographic}\".")
        if pd.notna(genres):
            for genre in genres.split(","):
                if genre != "":
                    triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/genre> \"{genre}\".")
        if pd.notna(themes):
            for theme in themes.split(","):
                if theme != "":
                    triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/theme> \"{theme}\".")
        if pd.notna(adaptation):
            adaptation = removeTitle(adaptation)
            triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/adapted_from> \"{adaptation}\".")
        if pd.notna(sequel):
            sequel_ID = removeID(removeTitle(sequel))
            triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/sequel> <http://anin3/ent/{sequel_ID}>.")
        if pd.notna(prequel):
            prequel_ID = removeID(removeTitle(prequel))
            triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/prequel> <http://anin3/ent/{prequel_ID}>.")

        characters = [char for char in characters.strip('][').split('\'') if char != "" and char != ", "]
        voice_actors = [removeTitle(vc) for vc in voice_actors.strip('][').split('\'') if vc != "" and vc != ", "]
        role = role.strip('][').split(', ')

        for character in characters:
            char_name = removeTitle(character)
            char_ID = removeID(char_name)
            role_c = role[characters.index(character)%len(role)].replace("\'", "")
            triples.append(f"<http://anin3/ent/{char_ID}> <http://anin3/pred/role> \"{role_c}\".")
            triples.append(f"<http://anin3/ent/{char_ID}> <http://anin3/pred/name> \"{char_name}\".")
            if len(voice_actors) > 0:
                vc_name = voice_actors[characters.index(character)%len(voice_actors)].replace(",", "")
                vc = removeID(vc_name)
                triples.append(f"<http://anin3/ent/{vc}> <http://anin3/pred/played> <http://anin3/ent/{char_ID}>.")
                triples.append(f"<http://anin3/ent/{vc}> <http://anin3/pred/name> \"{vc_name}\".")
                triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/voiced_at> <http://anin3/ent/{vc}>.")
            triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/starring> <http://anin3/ent/{char_ID}>.")
        
        if pd.notna(ops):
            if "[" in ops_artist:
                ops_artist = [removeTitle(opa) for opa in ops_artist.strip('][').split('\'') if opa != "" and opa != ", "]
            ops = [removeTitle(op) for op in ops.strip('][').split('\'') if op != "" and op != ", "]
            for op in ops:
                op_ID = removeID(op)
                triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/opening> <http://anin3/ent/{op_ID}>.")
                triples.append(f"<http://anin3/ent/{op_ID}> <http://anin3/pred/name> \"{op}\".")
                if "[" in ops_artist or len(ops_artist) > 0:
                    op_artist = ops_artist[ops.index(op)%len(ops_artist)].replace(",", "")
                    op_artist_ID = removeID(op_artist)
                    triples.append(f"<http://anin3/ent/{op_ID}> <http://anin3/pred/played_by> <http://anin3/ent/{op_artist_ID}>.")
                    triples.append(f"<http://anin3/ent/{op_artist_ID}> <http://anin3/pred/name> \"{op_artist}\".")
        
        if pd.notna(ends):
            if "[" in ends_artist:
                ends_artist = [removeTitle(enda) for enda in ends_artist.strip('][').split('\'') if enda != "" and enda != ", "]
            ends = [removeTitle(end) for end in ends.strip('][').split('\'') if end != "" and end != ", "]
            for end in ends:
                end_ID = removeID(end)
                triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/ending> <http://anin3/ent/{end_ID}>.")
                triples.append(f"<http://anin3/ent/{end_ID}> <http://anin3/pred/name> \"{end}\".")
                if "[" in ends_artist or len(ends_artist) > 0:
                    end_artist = ends_artist[ends.index(end)%len(ends_artist)].replace(",", "")
                    end_artist_ID = removeID(end_artist)
                    triples.append(f"<http://anin3/ent/{end_ID}> <http://anin3/pred/played_by> <http://anin3/ent/{end_artist_ID}>.")
                    triples.append(f"<http://anin3/ent/{end_artist_ID}> <http://anin3/pred/name> \"{end_artist}\".")

    with open("animes.nt", "w") as f:
        for triple in triples:
            f.write(triple + "\n")

loadCSV2NT()

g = Graph()
g.parse('animes.nt')

pred = Namespace("http://anin3/pred/")
ent = Namespace("http://anin3/ent/")

g.bind("pred", pred)
g.bind("ent", ent)

n3 = g.serialize(format='n3')

with open("animes.n3", "w") as f:
    f.write(n3)