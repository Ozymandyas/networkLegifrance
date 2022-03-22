# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 10:48:29 2022

@author: Malo
"""

import json
import pandas as pd
import numpy as np
import math
import os
import matplotlib.pyplot as plt
import re

df = pd.read_json("CGI_v.json", encoding='utf-8')

df['len'] = df.content.str.len()

#length of longest article in database
print(len(max(df.values, key = lambda x:len(x[-4]))[-4]))


#shortest article in database
print(min(df.values, key = lambda x:len(x[-4])))


plt.hist(list(map(len,df['content'])), bins = 50, log = True)
plt.title('Répartition des longueurs d\'articles')
plt.show()


plt.title('nombre d\'articles par année')
plt.grid()
plt.show()

plt.plot(df.groupby('year')['len'].mean())
plt.grid()
plt.title('longueur des articles par annee (caractères)')
plt.show()

plt.hist(df.name.value_counts(),bins = 75)
plt.title('répartition des nombres de versions d\'un même article')
plt.show()

VC = re.compile('[aeiou]+[^aeiou]+', re.I)
def count_syllables(word):
    return len(VC.findall(word))

def kf(art):
    words = art.split(' ')
    num_sents = len(art.split('.'))
    num_words = len(words)
    num_syllables = sum(count_syllables(w) for w in words)
    score = 206.835 - 1.015 * (num_words / num_sents) - 84.6 * (num_syllables / num_words)
    return(score)
    
df['score']=df['content'].apply(kf)

plt.plot(df.groupby('year')['score'].mean())
plt.grid()
plt.title('score Kincaid-Flesch moyen des articles par annee')
plt.show()

