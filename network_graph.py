import pandas as pd
import numpy as np
import re
import json
from collections import defaultdict
import networkx as nx
from pyvis.network import Network

# we create our dataframe from our scraped json
df = pd.read_json('CGI_r.json')

# we give it the year we want to do
given_year = 1980

# some codes didn't exist back then and vice versa, not an issue, I removed Code rural et de la pêche maritime
codes = ["Code de l\'action sociale et des familles", "Code de l\'artisanat", "Code des assurances",
         "Code de l\'aviation civile", "Code du cinéma et de l\'image animée", "Code civil",
         "Code de la commande publique", "Code de commerce", "Code des communes",
         "Code des communes de la Nouvelle-Calédonie", "Code de la consommation",
         "Code de la construction et de l\'habitation", "Code de la défense", "Code de déontologie des architectes",
         "Code disciplinaire et pénal de la marine marchande", "Code du domaine de l\'Etat",
         "Code du domaine de l\'Etat et des collectivités publiques applicable à la collectivité territoriale de Mayotte",
         "Code du domaine public fluvial et de la navigation intérieure", "Code des douanes",
         "Code des douanes de Mayotte", "Code de l\'éducation", "Code électoral", "Code de l\'énergie", "Code de l\'entrée et du séjour des étrangers et du droit d\'asile",
         "Code de l\'environnement", "Code de l\'expropriation pour cause d\'utilité publique",
         "Code de la famille et de l\'aide sociale", "Code forestier", "Code général de la fonction publique",
         "Code général de la propriété des personnes publiques", "Code général des collectivités territoriales",
         "Code des impositions sur les biens et services", "Code des instruments monétaires et des médailles",
         "Code des juridictions financières", "Code de justice administrative",
         "Code de justice militaire", "Code de la justice pénale des mineurs",
         "Code de la Légion d\'honneur, de la Médaille militaire et de l\'ordre national du Mérite",
         "Code minier", "Code monétaire et financier", "Code de la mutualité", "Code de l'organisation judiciaire",
         "Code du patrimoine", "Code pénal", "Code des pensions civiles et militaires de retraite",
         "Code des pensions de retraite des marins français du commerce, de pêche ou de plaisance",
         "Code des pensions militaires d\'invalidité et des victimes de guerre",
         "Code des ports maritimes", "Code des postes et des communications électroniques",
         "Code de procédure civile", "Code de procédure pénale", "Code des procédures civiles d\'exécution",
         "Code de la propriété intellectuelle", "Code de la recherche",
         "Code des relations entre le public et l\'administration", "Code de la route", "Code rural", "Code de la santé publique", "Code de la sécurité intérieure",
         "Code de la sécurité sociale", "Code du service national", "Code du sport", "Code du tourisme",
         "Code des transports", "Code du travail", "Code du travail applicable à Mayotte", "Code du travail maritime",
         "Code de l'urbanisme", "Code de la voirie routière", "Code de l'industrie cinématographique", "Code des débits de boissons et des mesures contre l'alcoolisme"]

# we initialize matches which is going to contain all matches in a {source1: [target1, ..., targetn], ..., source2: [target1, ..., targetn]} fashion
matches = {}

# just a part of the boolean mask applied to df
mask = df.path.apply(lambda x: 'Code Général des Impôts' in x)

# we want to remove refs to TFUE
traite = ["article 107 du traité",
          "articles 107 et 108 du traité", "article 108 du traité"]


def rangeReplacement(match):
    """it's going to replace 'articles 1 à 3' by 'article 1 article 2 article 3'"""
    mystring = ""
    start = int(match.group(1))
    end = int(match.group(2))
    for i in range(start, end+1):
        mystring = mystring + " article " + str(i)
    return mystring


# we initialize a dict of list
codes_count = defaultdict(list)


def countRef(art):
    """we want to count refs to TFUE and codes"""
    for code in codes:
        if code.lower() in art.content.lower():
            codes_count[art["name"]].append(code)
    for item in traite:
        if item.lower() in art.content.lower():
            codes_count[art["name"]].append("Articles 107 et 108 du TFUE")


def removeBefore(code):
    """we want to remove refs to codes but also what is before in order
     not to match external articles
     """
    return '.' * 40 + code


def processArticle(article):
    """we process the article to use simple functions to match article"""
    # we remove 'dispositions -0'
    for w in [*["-0", "-1", "-2", "-3"], *traite]:
        article = article.replace(w, "")
    # we remove codes and 40 chars before
    for c in codes:
        article = re.sub(removeBefore(c), "", article)

    # we replace 'article 1 à 3' by 'article 1 article 2 article 3'
    article = re.sub(r"articles* (\d+) à (\d+)", rangeReplacement, article)

    # we replace 'article 2, 3' by 'article 2 article 3' recursively
    while True:
        output = re.sub(r"articles* (\d+) *(bis|ter|quater|quinquies|sexies|septies|octies|nonies|decies|undecies|duodecies|terdecies|quaterdecies|quindecies|sexdecies|septdecies|octodecies|novodecies|vicies)*, (\d+)", r"article \1 \2 article \3", article)
        if output == article:
            break
        article = output
    # we replace 'article 2 et 3' by 'article 2 article 3' recursively
    while True:
        output = re.sub(r"articles* (\d+) *(bis|ter|quater|quinquies|sexies|septies|octies|nonies|decies|undecies|duodecies|terdecies|quaterdecies|quindecies|sexdecies|septdecies|octodecies|novodecies|vicies)* et (\d+)", r"article \1 \2 article \3", article)
        if output == article:
            break
        article = output
    # we replace 'articles 1 à 3' by 'article 1 article 2 article 3' again to account for
    # situations like 'articles 2 et 5 à 17'
    article = re.sub(r"articles* (\d+) à (\d+)", rangeReplacement, article)
    return article


# we iterate over each article
for _, article in list(df[(df.year == given_year) & mask].iterrows()):
    # we initialize our keys in matches dict
    matches[article["name"]] = []
    # we count refs to TFUE and code and put them in code_counts dict
    countRef(article)
    # we process the article
    processed_article = processArticle(
        article["content"]).replace('articles', 'article').lower().replace(",", ".")
    # we check with the series in alphanumeric reverse to search for the larger match first
    # and then removes it, it will search first for 'article 36 ter.' and then
    # 'article 36 ter ' and after 'article 36.' and then 'article 36 '
    # matches are immediately appended to our matches dict and then removed
    for match in [*[x+'.' for x in df[(df.year == given_year) & mask].name.iloc[::-1]], *[x+' ' for x in df[(df.year == given_year) & mask].name.iloc[::-1]]]:
        if match.lower() in processed_article:
            matches[article["name"]].append(match[:-1])
            processed_article = processed_article.replace(match.lower(), "")

# we put everyting in a dict of list
dict_final = {key: matches.get(key, [])+dict(codes_count).get(key, [])
              for key in set(list(matches.keys())+list(dict(codes_count).keys()))}

# we initialize our network with arrows and full screen
net = Network(notebook=True, height='100%', width='100%', directed=True)
# we create our network from our list, idk if nx.DiGraph is doing anything
G = nx.from_dict_of_lists(dict_final, create_using=nx.DiGraph)

# gets a pagerank, each node is attributed a score
pr = nx.pagerank(G)

# we sort and reverse the order so that the most important is first
l = sorted(pr.keys(), key=lambda x: -pr[x])

# the nodes relative to external legislatives codes are bigger and in red their edges also
for code in set(G.nodes).intersection(set(codes)):
    G.nodes[code]['color'] = 'red'
    G.nodes[code]['size'] = 20

# we put the edges in red
for x in G.nodes:
    for y in G[x]:
        if y in codes:
            G[x][y].update({'color': 'red'})

# we use pyvis to create our graph from G
net.from_nx(G)

# these are options to allow for a better display of nodes and edges
options = """
var options = {
   "configure": {
        "enabled": true
   },
  "edges": {
    "color": {
      "inherit": true
    },
    "smooth": false
  },
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -60954,
      "centralGravity": 0,
      "springLength": 585
    },
    "maxVelocity": 61,
    "minVelocity": 0.75
  }
}
"""
# we set the options
net.set_options(options)
# net.toggle_physics(False)
# net.show("test_2022.html")

# we save the graph
net.save_graph('1980.html')
