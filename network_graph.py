import pandas as pd
import numpy as np
import re
import json
from collections import defaultdict
import networkx as nx
from pyvis.network import Network
import streamlit as st
import streamlit.components.v1 as components

df = pd.read_json('CGI_r.json')

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

matches = {}

mask = df.path.apply(lambda x: 'Code Général des Impôts' in x)

traite = ["article 107 du traité",
          "articles 107 et 108 du traité", "article 108 du traité"]


def rangeReplacement(match):
    mystring = ""
    start = int(match.group(1))
    end = int(match.group(2))
    for i in range(start, end+1):
        mystring = mystring + " article " + str(i)
    return mystring


codes_count = defaultdict(list)


def countRef(art):
    for code in codes:
        if code.lower() in art.content.lower():
            codes_count[code].append(art["name"])
    for item in traite:
        if item.lower() in art.content.lower():
            codes_count["Articles 107 et 108 du TFUE"].append(art["name"])


def removeBefore(code):
    return '.' * 20 + code


def processArticle(article):
    for w in [*["-0", "-1", "-2", "-3"], *traite]:
        article = article.replace(w, "")
    for c in codes:
        article = re.sub(removeBefore(c), "", article)

    article = re.sub(r"articles* (\d+) à (\d+)", rangeReplacement, article)

    while True:
        output = re.sub(r"articles* (\d+) *(bis|ter|quater|quinquies|sexies|septies|octies|nonies|decies|undecies|duodecies|terdecies|quaterdecies|quindecies|sexdecies|septdecies|octodecies|novodecies|vicies)*, (\d+)", r"article \1 \2 article \3", article)
        if output == article:
            break
        article = output
    while True:
        output = re.sub(r"articles* (\d+) *(bis|ter|quater|quinquies|sexies|septies|octies|nonies|decies|undecies|duodecies|terdecies|quaterdecies|quindecies|sexdecies|septdecies|octodecies|novodecies|vicies)* et (\d+)", r"article \1 \2 article \3", article)
        if output == article:
            break
        article = output
    article = re.sub(r"articles* (\d+) à (\d+)", rangeReplacement, article)
    return article


given_year = 2018
for _, article in list(df[(df.year == given_year) & mask].iterrows()):
    matches[article["name"]] = []
    countRef(article)
    processed_article = processArticle(
        article["content"]).replace('articles', 'article').lower()
    # we check with the series in reverse to search for the most large match first and then removes it
    for match in [*[x+'.' for x in df[(df.year == given_year) & mask].name.iloc[::-1]], *[x+' ' for x in df[(df.year == given_year) & mask].name.iloc[::-1]]]:
        if match.lower() in processed_article:
            matches[article["name"]].append(match[:-1])
            processed_article = processed_article.replace(match.lower(), "")

dict_final = {**matches, **dict(codes_count)}
# in 1980 you have 2094 articles but only 2085 nodes for articles are created because you have 9 articles with the same name...

# we initialize our network with arrows and full screen
net = Network(notebook=True, height='100%', width='100%', directed=True)
# we create our network from our list
G = nx.from_dict_of_lists(dict_final)

# the nodes relative to external legislatives codes are bigger and in red their edges also
for code in set(G.nodes).intersection(set(codes)):
    G.nodes[code]['color'] = 'red'
    G.nodes[code]['size'] = 20
    for node in G[code]:
        G[code][node]['color'] = 'red'

net.from_nx(G)
# it's going to add all missing nodes (orphan nodes) because nodes are not replicated
net.add_nodes(list(df[(df.year == given_year) & mask].name))
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

net.set_options(options)
# net.toggle_physics(False)
# net.show("test_2022.html")

st.title("My network for CGI")

try:
    net.save_graph('tmp/pyvis_graph.html')
    HtmlFile = open('tmp/pyvis_graph.html', 'r', encoding='utf-8')

    # Save and read graph as HTML file (locally)
except:
    net.save_graph('html_files/pyvis_graph.html')
    HtmlFile = open('html_files/pyvis_graph.html', 'r', encoding='utf-8')

    # Load HTML file in HTML compon
    # ent for display on Streamlit page
components.html(HtmlFile.read(), height=435)
