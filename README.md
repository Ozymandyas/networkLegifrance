# This repository contains everything

- CGI_r.zip is the whole dataset, individual datasets exist for each book but not added to repo
- scraping.js is the script used to scrape Legifrance when it was possible
- merge.js is just a utility file i used to merge all books and other things
- 1980.html and 2022.html are newtork visualisations for the Code Général des Impôts (only this book), each arrow means 'mentions'
- network_graph2.py is the script used to create the aforementioned visualisations and pagerank
- retrieveAPI.py is an alernative method to get the dataset using the API, keys are to be added
- common_words.csv is a dictionnary of 5000 words i used to analyse the aggregated 6 books (CGI + annexe 1 à 4 + LPF) for 1980 and 2022
- 5000words.csv is the resulting data of this analysis where one can see increases in occurences of the words
- dictionnary_analysis.ipynb is a jupyter notebook used to make research with this dictionnary and take screens
- ml.py was an attempt to use machine learning to study wording over the years but it failed because of packages-related issues
- script4.py is a script of scripts to plot some data about the CGI.
