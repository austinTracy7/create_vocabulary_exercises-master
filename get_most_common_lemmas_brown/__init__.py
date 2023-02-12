from nltk.corpus import brown
from nltk import FreqDist
from nltk.stem import WordNetLemmatizer
import pickle

lemmatizer = WordNetLemmatizer

def get_frequency_of_brown_words_case_insensitive():
    return FreqDist([lemmatizer.lemmatize(word.lower()) for word 
        in brown.words() if word.isalpha()])

lemma_frequencies = get_frequency_of_brown_words_case_insensitive()

lemmas_ranked = list(lemma_frequencies.keys())

with open("lemmas_ranked.pkl","wb") as f:
    pickle.dump(lemmas_ranked,f)
