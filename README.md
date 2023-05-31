# Anin3
Projeto Prático da cadeira de Web Semântica.

## Contexto
A World Wide Web revolucionou a maneira como as pessoas comunicam e partilham informação entre elas. No entanto, a enorme quantidade disponivel na Web deu origem a vários desafios, não só na sua gestão, mas também endender esta informação.

Para tentar resolver estes desafios, o campo da Web Semântica (WS) emergiu como uma forma de fazer a Web mais organizada e com mais significado. A WS envolve o uso de standards e tecnologias que dão estrutura e significado aos recursos da web, tornando mais eficiente a pesquisa, partilha e analise da informatica.

Neste trabalho prático, onde nos foi pedido para desenvolvermos um sistema de informação baseado na web, escolhemos utilizar informação sobre anime. 

Anime, palavra japonesa derivada da palavra inglesa animation, é um tipo de animação feita à mão ou gerada por computadores com origem japonesa. Este estilo de animação tem vindo a ganhar cada vez mais popularidade ao longo do tempo, sendo que nos últimos anos, as grandes plataformas de streaming como Netflix e Disney+ aumentaram em larga escala a sua oferta de anime.

## Introdução
No desenvolvimento deste trabalho, foi utilizado:
- Python/Django: Programação da aplicação
- RDF/NT/N3: Formatação dos dados
- Triplestore GraphDB: Repositório de dados
- SPARQL: Pesquisa e alteração de dados na triplestore
- RDFS/OWL: Criação da Ontologia
- SPIN: Conjunto de Inferências
- SPARQLWrapper: Acesso ao endpoint da DBpedia e Wikidata
- RDFa: Publicação da semântica dos dados

Durante o desenvolvimento deste sistema, tivemos como objetivos desenvolver um sistema:
- Com o maior nivel possivel de exploração e inter-relação entre as tecnologias mencionadas previamente
- Com uma interface fácil e intuitiva para o utilizador
- Com um dataset rico e com dados bastante relacionados entre si, assim como a exploração destas relações
- Desenvolvido modularmente, separando os dados, a lógica e a apresentação 
- Com uma ontologia completa, descrevendo exaustivamente o domínio de conhecimento dos dados
- Com regras de inferencia que permitam, não só o estabelecimento de novas relações entre as entidades, mas também que motores de inferência automática consigam gerar novas relações
- Com a publicação da semântica dos dados

## Organização
A pasta "Entregáveis" contém os relatórios e as apresentações deste trabalho.

A pasta "Dataset" contém o dataset original, o ficheiro python usado para transformar os dados em N-Triples, e o ficheiro N-Triples dos dados utilizados.

A pasta "WSProject1" contém o project DJango.

Os ficheiros "animes.n3" e "anin3-config.ttl" sáo ficheiros usados pelo projeto DJango e corresnpodem aos dados utilizados em formato N3 e ao ficheiro de configuração do RDF4J para um repositório de GraphDB, respetivamente.

## Como Correr

Iniciar o GraphDB no seu computador em http://localhost:7200/ e certificar-se que não tem um repositório chamado "anin3" inicialmente. 

Para iniciar a aplicação django, basta executar os seguintes comandos:

        cd path/to/project/folder/
        cd WSProject1/
        pip install -r requirements.txt
        python3 manage.py runserver
        
## Participantes
- Filipe Gonçalves, 98083, Mestrado em Robótica e Sistemas Inteligentes
- Gonçalo Machado, 98359, Mestrado em Engenharia Informática
- João Borges, 98155, Mestrado em Engenharia Informática
- Afonso Campos, 100055, Mestrado em Engenharia Informática
