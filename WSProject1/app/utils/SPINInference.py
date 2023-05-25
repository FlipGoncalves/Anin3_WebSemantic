import requests

endpoint = "http://localhost:7200"
repo_name = "anin3"

insert_music_cast = f"""
PREFIX pred: <http://anin3/pred/>

INSERT {{
    ?anime pred:music_cast ?singer .
}} WHERE {{
    {{
        ?anime pred:opening ?music .
        ?music pred:played_by ?singer .
    }}
    UNION
    {{
        ?anime pred:ending ?music .
        ?music pred:played_by ?singer .
    }}
}}
"""

insert_worked_with = f"""
PREFIX pred: <http://anin3/pred/>

INSERT {{
    ?va1 pred:worked_with ?va2 .
}} WHERE {{
    {{
        ?va1 pred:played ?character1 .
        ?anime pred:starring ?character1 .
        ?anime pred:starring ?character2 .
        ?va2 pred:played ?character2 .
        FILTER(?va1 != ?va2) .
    }}
}}

"""

def update_graph(query):
    payload_query = {"update": query, "baseURI": "http://anin3/"}

    res = requests.post(endpoint+f"/repositories/{repo_name}/statements", params=payload_query, headers={"Content-Type": "application/rdf+xml", 'Accept': 'application/json'})

    if res.status_code != 204:
        print(res.status_code)
        print(res.json())
        raise Exception()
    
def main():
    update_graph(insert_music_cast)
    update_graph(insert_worked_with)
    
if __name__ == "__main__":
    main()