from django.shortcuts import render
from rdflib import Graph
import random

# Create your views here.
def index(request):
    return render(request, "index.html")

def voiceActor(request, nome):

    graph = SimpleGraph()

    g = Graph()
    g.parse("animes.nt")

    for sub, pred, obj in g:
        graph.add(str(sub), str(pred), str(obj))

    # graph.printAllTriples()

    lista = graph.query( [('?voice_actor', 'http://anin3/pred/name', nome),
                          ('?voice_actor', 'http://anin3/pred/played', '?character'),
                          ('?character', 'http://anin3/pred/name', '?character_name'),
                          ('?character', 'http://anin3/pred/role', '?role'),
                          ('?anime', 'http://anin3/pred/starring', '?character'),
                          ('?anime','http://anin3/pred/title', '?animename'),
                        ] )

    data = {}
    data["Name"] = nome

    for a in lista:
        if "Characters" in data.keys():
            data["Characters"].append({"Name": a['character_name'], "Role": a['role'], "Anime": a['animename']})    
        else:
            data["Characters"] = [{"Name": a['character_name'], "Role": a['role'], "Anime": a['animename']}]

    return render(request, "voice.html", {'data': data})

def animeTitle(request, title):

    graph = SimpleGraph()

    g = Graph()
    g.parse("animes.nt")

    for sub, pred, obj in g:
        graph.add(str(sub), str(pred), str(obj))

    # graph.printAllTriples()

    lista = graph.query( [('?anime','http://anin3/pred/title', title),
                        ('?anime', 'http://anin3/pred/starring', '?character'),
                        ('?character', 'http://anin3/pred/name', '?character_name'),
                        ('?character', 'http://anin3/pred/role', '?role'),
                        ('?voice_actor', 'http://anin3/pred/played', '?character'),
                        ('?voice_actor', 'http://anin3/pred/name', '?voice_actor_name'),
                        ] )

    data = {}
    data["Name"] = title

    for a in lista:
        if "Characters" in data.keys():
            data["Characters"].append({"Name": a['character_name'], "Role": a['role'], "VoiceActor": a['voice_actor_name']})    
        else:
            data["Characters"] = [{"Name": a['character_name'], "Role": a['role'], "VoiceActor": a['voice_actor_name']}]

    return render(request, "anime.html", {'data': data})

def randomAnime(request):

    graph = SimpleGraph()

    g = Graph()
    g.parse("animes.nt")

    for sub, pred, obj in g:
        graph.add(str(sub), str(pred), str(obj))

    # graph.printAllTriples()

    lista = graph.query( [('?anime','http://anin3/pred/title', "?title"),
                        ] )

    anime = random.choice(lista)['title']

    lista = graph.query( [('?anime','http://anin3/pred/title', anime),
                        ('?anime', 'http://anin3/pred/starring', '?character'),
                        ('?character', 'http://anin3/pred/name', '?character_name'),
                        ('?character', 'http://anin3/pred/role', '?role'),
                        ('?voice_actor', 'http://anin3/pred/played', '?character'),
                        ('?voice_actor', 'http://anin3/pred/name', '?voice_actor_name'),
                        ] )

    data = {}
    data["Name"] = anime

    for a in lista:
        if "Characters" in data.keys():
            data["Characters"].append({"Name": a['character_name'], "Role": a['role'], "VoiceActor": a['voice_actor_name']})    
        else:
            data["Characters"] = [{"Name": a['character_name'], "Role": a['role'], "VoiceActor": a['voice_actor_name']}]

    return render(request, "anime.html", {'data': data})

class SimpleGraph:
    """
    Implementa um grafo simples subject-predicate-object
    Guarda todas as permutações possíveis do triplo,
    para que a pesquisa por chave seja possível para todos os items do triplo
    """

    # inicialização
    def __init__(self):
        self._spo = {}  # cria índice subject-predicate-object
        self._pos = {}  # cria índice predicate-object-subject
        self._osp = {}  # cria índice object-subject-predicate

    # adiciona um triplo aos 3 índices
    def add(self, sub, pred, obj):
        self._addToIndex(self._spo, sub, pred, obj)
        self._addToIndex(self._pos, pred, obj, sub)
        self._addToIndex(self._osp, obj, sub, pred)


    # adiciona os termos ao índice
    def _addToIndex(self, index, a, b, c):
        if a not in index:           # se ainda não existe a chave 'a' no dicionario
            index[a] = {b:set([c])}       # cria chave 'a', atribui-lhe um dicionario com chave 'b' e valor igual a set com elemento c
        else:                        # se ja existe chave 'a'
            if b not in index[a]:    # mas não existe chave 'b' no dicionario valor
                index[a][b]=set([c])      # cria chave 'b', atribui-lhe set com elemento c
            else:                    # se ja existe chave 'a' e 'b'
                index[a][b].add(c)# adiciona elemento c ao set valor

    # pesquisa por um triplo padrão e devolve todos os triplos que obedeçam ao mesmo
    # padrões possíveis: (sub, pred, obj), (sub, pred, None), (sub, None, None), (None, None, None)
    # para (sub, pred, obj) só deve devolver um triplo, para (None, None, None) deve devolver todos
    def triples(self, sub, pred, obj):
        try:
            if sub != None:
                if pred != None:
                    # sub pred obj
                    if obj != None:
                        if obj in self._spo[sub][pred]:
                            yield (sub, pred, obj)
                    # sub pred None
                    else:
                        for retObj in self._spo[sub][pred]:
                            yield (sub, pred, retObj)
                else:
                    # sub None obj
                    if obj != None:
                        for retPred in self._osp[obj][sub]:
                            yield (sub, retPred, obj)
                    # sub None None
                    else:
                        for retPred, objSet in self._spo[sub].items():
                            for retObj in objSet:
                                yield (sub, retPred, retObj)
            else:
                if pred != None:
                    # None pred obj
                    if obj != None:
                        for retSub in self._pos[pred][obj]:
                            yield (retSub, pred, obj)
                    # None pred None
                    else:
                        for retObj, subSet in self._pos[pred].items():
                            for retSub in subSet:
                                yield (retSub, pred, retObj)
                else:
                    # None None obj
                    if obj != None:
                        for retSub, predSet in self._osp[obj].items():
                            for retPred in predSet:
                                yield (retSub, retPred, obj)
                    # None None None
                    else:
                        for retSub, predSet in self._spo.items():
                            for retPred, objSet in predSet.items():
                                for retObj in objSet:
                                    yield (retSub, retPred, retObj)
        # KeyErrors occur if a query term wasn't in the index,
        # so we yield nothing:
        except KeyError:
            pass

    # faz um query ao grafo,
    # passando-lhe uma lista de tuplos (triplos restrição)
    # devolve uma lista de dicionarios (var:valor)
    def query(self, clauses):
        bindings = None                      # resultado a devolver
        for clause in clauses:               # para cada triplo
            bpos = {}                        # dicionário que associa a variável à sua posição no triplo de pesquisa
            qc = []                          # lista de elementos a passar ao método triples
            for pos, x in enumerate(clause): # enumera o triplo, para poder ir buscar cada elemento e sua posição
                if x.startswith('?'):        # para as variáveis
                    qc.append(None)          # adiciona o valor None à lista de elementos a pssar ao método triples
#                    bpos[x] = pos            # guarda a posição da variável no triplo (0,1 ou 2)
                    bpos[x[1:]]=pos          # linha de cima re-escrita porque é necessário guardar o nome da variável, mas sem o ponto de interrogação (?)
                else:
                    qc.append(x)             # adiciona o valor dado à lista de elementos a pssar ao método triples

            rows = list(self.triples(qc[0], qc[1], qc[2])) # faz a pesquisa com o triplo acabado de construir

            # primeiro triplo pesquisa, todos os resultados servem
            # para cada triplo resultado, cria um dicionario de variaveis (1 a 3 variaveis)
            # em cada dicionario, as variaveis tomam o valor devolvido pelo elemento na mesma posicao da variavel
            if bindings == None:
                bindings = []                # cria a lista a devolver
                for row in rows:             # para cada triplo resultado
                    binding = {}             # cria um dicionario
                    for var, pos in bpos.items(): # para cada variável e sua posição
                        binding[var] = row[pos] # associa à variável o valor do elemento do triplo na sua posição
                    bindings.append(binding) # adiciona o dicionario à lista

            else:                            # triplos pesquisa seguintes, eliminar resultados que não servem
                # In subsequent passes, eliminate bindings that don't work
                # Retira da lista dicionários, aqueles que
                newb = []                    # cria nova lista a devolver
                for binding in bindings:     # para cada dicionario da lista de dicionarios
                    for row in rows:         # para cada triplo resultado
                        validmatch = True    # começa por assumir que o dicionario serve
                        tempbinding = binding.copy() # faz copia temporaria do dicionario
                        for var, pos in bpos.items(): # para cada variavel em sua posição
                            if var in tempbinding: # caso a variavel esteja presente no dicionario
                                if tempbinding[var] != row[pos]: # se o valor da variavel diferente do valor na sua posicao no triplo
                                    validmatch = False # o dicionário não serve
                            else:
                                tempbinding[var] = row[pos] # associa à variável o valor do elemento do triplo na sua posição
                        if validmatch:
                            newb.append(tempbinding) # se dicionario serve, inclui-o na nova lista
                bindings = newb              # sbstituiu lista por nova
        return bindings


    # imprime todos os triplos
    def printAllTriples(self):
        t = self.triples(None, None, None)
        SimpleGraph.printTriples(t)


    # método estático para imprimir conjuntos de triplos num iterador
    @staticmethod
    def printTriples(t):
        for el in t:
            print(("%15s --> %15s --> %15s" % el).encode())