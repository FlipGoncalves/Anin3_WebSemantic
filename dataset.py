import pandas as pd

def loadCSV2NT():

    animes = pd.read_csv("animes.csv")

    triples = []
    count = 0

    for _, rank, title, link, score, type, episodes, source, status, premiered, aired_date, studios, genres, themes, demographic, duration, age_rating, _, popularity, members, _, adaptation, sequel, prequel, characters, role, voice_actors, ops, ops_artist, ends, ends_artist in animes.values[:10000]:
        count += 1
        # print(count)

        anime_ID = title.strip().replace(" ", "_").replace("\"", "").replace("\\", "").replace("<", "").replace(">", "")
        title = title.replace("\"", "").replace("\\", "").replace("<", "").replace(">", "")

        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/rank> \"{rank}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/title> \"{title}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/website> \"{link}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/score> \"{score}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/type> \"{type}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/num_episodes> \"{episodes}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/source> \"{source}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/status> \"{status}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/premired> \"{premiered}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/aired_date> \"{aired_date}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/made_by> \"{studios}\".")

        if pd.notna(genres):
            for genre in genres.split(","):
                if genre != "":
                    triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/genre> \"{genre}\".")
        if pd.notna(themes):
            for theme in themes.split(","):
                if theme != "":
                    triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/theme> \"{theme}\".")

        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/demographic> \"{demographic}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/duration> \"{duration}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/age_rating> \"{age_rating}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/popularity> \"{popularity}\".")
        triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/num_members> \"{members}\".")

        if pd.notna(adaptation):
            adaptation = adaptation.replace(" ", "_").replace("\"", "").replace("\\", "").replace("<", "").replace(">", "")
            triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/adapted_from> \"{adaptation}\".")

        if not pd.isna(sequel):
            sequel_ID = sequel.strip().replace(" ", "_").replace("\"", "").replace("\\", "").replace("<", "").replace(">", "")
            triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/sequel> <http://anin3/ent/{sequel_ID}>.")
        if not pd.isna(prequel):
            prequel_ID = prequel.strip().replace(" ", "_").replace("\"", "").replace("\\", "").replace("<", "").replace(">", "")
            triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/prequel> <http://anin3/ent/{prequel_ID}>.")

        characters = [char for char in characters.strip('][').split('\'') if char != "" and char != ", "]
        voice_actors = [vc.replace("\"", "").replace("\\", "").replace("<", "").replace(">", "") for vc in voice_actors.strip('][').split('\'') if vc != "" and vc != ", "]
        role = role.strip('][').split(', ')

        for character in characters:
            char_ID = character.strip().replace(" ", "_").replace("\"", "").replace("\\", "").replace("<", "").replace(">", "")
            char_name = character.replace("\"", "").replace("\\", "").replace("<", "").replace(">", "")
            role_c = role[characters.index(character)%len(role)]
            triples.append(f"<http://anin3/ent/{char_ID}> <http://anin3/pred/role> \"{role_c}\".")
            triples.append(f"<http://anin3/ent/{char_ID}> <http://anin3/pred/name> \"{char_name}\".")
            if len(voice_actors) > 0:
                vc_name = voice_actors[characters.index(character)%len(voice_actors)]
                vc = vc_name.strip().replace(" ", "_").replace("\"", "").replace("\\", "").replace("<", "").replace(">", "")
                triples.append(f"<http://anin3/ent/{vc}> <http://anin3/pred/played> <http://anin3/ent/{char_ID}>.")
                triples.append(f"<http://anin3/ent/{vc}> <http://anin3/pred/name> \"{vc_name}\".")
                triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/voiced_at> <http://anin3/ent/{vc}>.")
            triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/starring> <http://anin3/ent/{char_ID}>.")
        
        if pd.notna(ops):
            if "[" in ops_artist:
                ops_artist = [opa.replace("\"", "").replace("\\", "").replace("<", "").replace(">", "") for opa in ops_artist.strip('][').split('\'') if opa != "" and opa != ", "]
            ops = [op.replace("\"", "").replace("\\", "").replace("<", "").replace(">", "") for op in ops.strip('][').split('\'') if op != "" and op != ", "]
            for op in ops:
                op_ID = op.strip().replace(" ", "_").replace("\"", "").replace("\\", "").replace("<", "").replace(">", "")
                triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/opening> <http://anin3/ent/{op_ID}>.")
                if "[" in ops_artist or len(ops_artist) > 0:
                    op_artist = ops_artist[ops.index(op)%len(ops_artist)]
                    op_artist_ID = op_artist.strip().replace(" ", "_").replace("\"", "").replace("\\", "").replace("<", "").replace(">", "")
                    triples.append(f"<http://anin3/ent/{op_ID}> <http://anin3/pred/played_by> <http://anin3/ent/{op_artist_ID}>.")
                    triples.append(f"<http://anin3/ent/{op_artist_ID}> <http://anin3/pred/name> \"{op_artist}\".")
        
        if pd.notna(ends):
            if "[" in ends_artist:
                ends_artist = [enda.replace("\"", "").replace("\\", "").replace("<", "").replace(">", "") for enda in ends_artist.strip('][').split('\'') if enda != "" and enda != ", "]
            ends = [end.replace("\"", "").replace("\\", "").replace("<", "").replace(">", "") for end in ends.strip('][').split('\'') if end != "" and end != ", "]
            for end in ends:
                end_ID = end.strip().replace(" ", "_").replace("\\", "").replace("<", "").replace(">", "")
                triples.append(f"<http://anin3/ent/{anime_ID}> <http://anin3/pred/ending> <http://anin3/ent/{end_ID}>.")
                if "[" in ends_artist or len(ends_artist) > 0:
                    end_artist = ends_artist[ends.index(end)%len(ends_artist)]
                    end_artist_ID = end_artist.strip().replace(" ", "_").replace("\"", "").replace("\\", "").replace("<", "").replace(">", "")
                    triples.append(f"<http://anin3/ent/{end_ID}> <http://anin3/pred/played_by> <http://anin3/ent/{end_artist_ID}>.")
                    triples.append(f"<http://anin3/ent/{end_artist_ID}> <http://anin3/pred/name> \"{end_artist}\".")

    with open("animes.nt", "w") as f:
        for triple in triples:
            f.write(triple + "\n")

# def saveToRDFFile(graph, filename, format):
#     # N-Triplets to N3 / XML
#     n3 = g.serialize(format=format)
#     with open(filename, "w") as f:
#         for triple in n3:
#             f.write(triple)

#     # N-Triplets to XML
#     n3 = g.serialize(format='xml')
#     with open("blade.xml", "w") as f:
#         for triple in n3:
#             f.write(triple)