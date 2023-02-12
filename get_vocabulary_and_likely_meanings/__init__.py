import re

# third party library imports
from nltk.corpus import wordnet as wn
import pandas as pd
from nltk.stem import WordNetLemmatizer
import nltk
from gingerit.gingerit import GingerIt

from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()


# functions
def get_more_common_part_of_speech(part_of_speech):
    general_part_of_speech = None
    if part_of_speech in ["NNP","NNS","NN","CD","NNPS"]:
        general_part_of_speech = "n"
    elif part_of_speech in ["IN","DT","TO","CC"]:
        general_part_of_speech = "functional_word" # not meaningful/to common for note
    elif part_of_speech in ["PRP","WP","WRB","FW","WDT","PDT"]:
        general_part_of_speech = "s"
    elif part_of_speech in ["VBZ","VBP","VB","MD","VBN","VBG","VBD"]:
        general_part_of_speech = "v"
    elif part_of_speech in ["RB","RP","RBR"]:
        general_part_of_speech = "r"
    elif part_of_speech in ["JJ","JJS"]:
        general_part_of_speech = "r" #or a...?
    return general_part_of_speech

def find_likely_meanings(row):
    if row["lemma"] == None:
        return None
    else:
        # mapping to a more general part of speech for likely meanings
        general_part_of_speech = get_more_common_part_of_speech(row["part_of_speech"]) 
        # selecting the likely meanings
        part_of_speechsible_meanings = wn.synsets(row["corrected_word"])
        output = [x for x in part_of_speechsible_meanings if str(x).find(f'.{general_part_of_speech}.') > -1]
        if len(part_of_speechsible_meanings) == 0:
            output = None
        elif len(part_of_speechsible_meanings) == 1 and output == []:
            output = ["?" + str(part_of_speechsible_meanings[0])]
        elif general_part_of_speech == "r" and output == []:
            output = [x for x in part_of_speechsible_meanings if str(x).find(f'.a.') > -1]
        return output

# words_df["likely_meanings"] = words_df.apply(find_likely_meanings,axis=1)

def make_token_sentence_number_pairs(sentences):
    token_and_sentence_pairings = []
    for i, sentence in enumerate(sentences):
        token_and_sentence_pairings += [list(annotated_token) for annotated_token
            in list(zip(([i] * len(sentence)),sentence))]
    return [[pairing[0]] + list(pairing[1]) for pairing in token_and_sentence_pairings]

def decontracted(phrase):
    # specific
    phrase = re.sub(r"won\'t", "will not", phrase,flags=re.I)
    phrase = re.sub(r"can\'t", "can not", phrase,flags=re.I)
    phrase = re.sub(r"'cause","because",phrase,flags=re.I)
    # general
    phrase = re.sub(r"n\'t", " not", phrase)
    phrase = re.sub(r"\'re", " are", phrase)
    phrase = re.sub(r"\'s", " is", phrase)
    phrase = re.sub(r"\'d", " would", phrase)
    phrase = re.sub(r"\'ll", " will", phrase)
    phrase = re.sub(r"\'t", " not", phrase)
    phrase = re.sub(r"\'ve", " have", phrase)
    phrase = re.sub(r"\'m", " am", phrase)
    return phrase

  
# importing jaccard distance
# and ngrams from nltk.util
from nltk.metrics.distance import jaccard_distance
from nltk.util import ngrams

# Downloading and importing
# package 'words' from nltk corpus
# nltk.download('words')
from nltk.corpus import words
  
correct_words = words.words()
correct_words = set(correct_words)
for word in ["I","yeah","oh"]:
    correct_words.add(word)

# finding correct spelling
# based on jaccard distance
# and printing the correct word
def find_correct_spelling(word):
    try:
        temp = [(jaccard_distance(set(ngrams(word, 2)),
                                set(ngrams(w, 2))),w)
                for w in correct_words if w[0]==word[0]]
        return sorted(temp, key = lambda val:val[0])[0][1]
    except:
        return None

def test_for_correct_word_fix_if_not(word):
    if word.lower() in correct_words:
        return word
    else:
        return find_correct_spelling(word)

import pyautogui

def copy_information():
    pyautogui.keyDown("ctrl")
    pyautogui.press("c")
    pyautogui.keyUp("ctrl")

def confirm_selection():
    while True:
        if pyautogui.confirm("Select the words that you want to copy") == "OK":
            break
import tkinter as tk


if __name__ == "__main__":
    root = tk.Tk()
    confirm_selection()
    copy_information()
    information = root.clipboard_get()
    input_text = information
    # parser = GingerIt()
    # from nltk.tokenize import sent_tokenize
    # [parser.parse(x) for x in ["Cause you re a sky"]]
    from nltk.stem import WordNetLemmatizer
    


    lemmatizer = WordNetLemmatizer()


    

    # polish the song lines (remove contractions)
    song_lines = decontracted(input_text).replace("â€™","'").split("\n")

    # create a tabe of song lines
    song_lines_df = pd.DataFrame([list(line) for line in zip(range(len(song_lines)),song_lines)],columns=["line_number","line"])

    song_lines_df.to_pickle("song_lines.pkl")

    # create a tabe of words with corresponding song lines
    # fix bad spellings
    words_df = pd.DataFrame(song_lines_df.apply(lambda row: 
        [[token,test_for_correct_word_fix_if_not(token),row["line_number"]]
         for token in nltk.word_tokenize(row["line"])]
         ,axis=1))
    
    words_df.columns = ["groupings"]
    words_df = words_df["groupings"].apply(lambda x: list(zip(x,
        [grouping[1] for grouping in 
        nltk.pos_tag([y[1] if y[1] != None else "" for y in x])])))

    
    # words_df = pd.DataFrame(words_df.explode("groupings"))
    words_df = pd.DataFrame(words_df)
    words_df["groupings"] = words_df["groupings"].apply(lambda row: [grouping[0] + [grouping[1]] for grouping in row])
    words_df = words_df.explode("groupings")
    words_df = words_df["groupings"].apply(pd.Series)
    words_df.columns = ["original_word","corrected_word","line_number","part_of_speech"]
    words_df = words_df[~words_df["original_word"].isna()]
    words_df.loc[:,"part_of_speech"] = words_df["part_of_speech"].apply(lambda x: x if x.isalpha() else None)

    words_df["lemma"] = words_df["corrected_word"].apply(lambda word: lemmatizer.lemmatize(word) if word != None else word)

    #
    words_df["likely_meanings"] = words_df.apply(find_likely_meanings,axis=1)

    # saving the data (including collapsing synsets into a string of comma separated values)
    words_df.loc[:,"likely_meanings"] = words_df[
        "likely_meanings"].apply(
            lambda x: ",".join([str(meaning).replace(
            "Synset('","").replace("')","") for meaning in x]) if x != None else x)

    words_df.to_pickle("tokens_and_meanings.pkl")