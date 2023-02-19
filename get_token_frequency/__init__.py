import pandas as pd
import pickle
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

# get ranked lemmas
with (open("lemmas_ranked.pkl", "rb")) as openfile:
    while True:
        try:
            lemmas_ranked = pickle.load(openfile)
        except EOFError:
            break

# pull in the brown corpus
def find_frequency_ranking(word):
    """This is meant to find the most unusual words with
    high numbers, but to ignore anything with punctuation
    that is much more common."""
    output = 100000 # bigger than any in the brown corpus 
    if word != None and word.isalpha():
        word = lemmatizer.lemmatize(word.lower())
        try:
            output = lemmas_ranked.index(word)
        except:
            pass
    else:
        output = 0 # insignificant
    return output
