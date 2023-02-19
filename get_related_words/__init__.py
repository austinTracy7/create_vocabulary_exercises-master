import pandas as pd
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import pyautogui
import nltk
import pickle

from nltk.stem import WordNetLemmatizer

stop_words = list (stopwords.words('english')) 

lemmatizer = WordNetLemmatizer()

def get_and_sort_words_for_best_related_words(meanings,word,lowest_frequency):
    # meanings = related_df["meanings"].to_list()
    related_words = pd.DataFrame([[x] + x.name().rsplit(".",2) for x in meanings],columns=["meaning","word","pos","value"])
    related_words["lemma_naming"] = related_words["meaning"].apply(lambda x: [y.name() for y in x.lemmas()])
    related_words["has_same_word"] = related_words["lemma_naming"].apply(lambda x: True in [word in y for y in x])
    related_words = related_words.explode("lemma_naming")
    related_words["frequency_ranking"] = related_words["lemma_naming"].apply(find_frequency_ranking)
    related_words = related_words[related_words["frequency_ranking"] > 0]
    related_words = related_words[related_words["word"] != word]
    pos_preferences = {"n": 0, "s": 5, "v": 3, "a": 2, "r": 4}
    related_words = related_words.sort_values(by=["value","frequency_ranking","pos"],key=lambda x: sorting_function_v2(x,pos_preferences))
    related_words_to_return = []
    for word in related_words["lemma_naming"]:
        if word not in related_words_to_return:
            related_words_to_return.append(word)
    return related_words_to_return

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


testing = pd.DataFrame(["04","02",1])
def sorting_function(x,pos_preferences):
    x = x.map(pos_preferences)
    return x

def sorting_function_v2(x,pos_preferences):
    x = x.apply(lambda x: x if str(type(x)) != "<class 'str'>" else int(x) if x.isnumeric() else pos_preferences[x])
    return x

def find_definitions_and_ranking_them_by_preference(word,part_of_speech=None):
    def_df = pd.DataFrame([[x] + str(x).rsplit(".",2) for x in wn.synsets(word)],columns=["meaning","word","pos","value"])
    def_df["value"] = def_df["value"].apply(lambda x: x.replace("')",""))
    def_df["word"] = def_df["word"].apply(lambda x: x.replace("Synset('",""))
    pos_preferences = {"01": 1,"02": 2, "03": 3, "04": 4,"n": 0, "s": 5, "v": 3, "a": 2, "r": 4}
    if part_of_speech == "v":
        pos_preferences["v"] = -1 
    elif part_of_speech == "a":
        pos_preferences["a"] = -2 
        pos_preferences["r"] = -1 
    elif part_of_speech == "r":
        pos_preferences["r"] = -2 
        pos_preferences["a"] = -1 
    def_df = def_df.sort_values(by=["value","pos"],key=lambda x: sorting_function(x,pos_preferences))
    
    return def_df["meaning"].to_list()

def get_meanings_without_the_same_word(word,cell):
        meanings = [wn.synsets(w.replace(word,"").replace("_"," ").strip()) for w in cell if word in w][0]
        if len(meanings) == 0:
            print([[y.definition() for y in wn.synsets(x)] for x in cell])
        return meanings

def sort_meanings_for_best_related_words(meanings):
    related_words = pd.DataFrame([[x] + x.name().rsplit(".",2) for x in meanings],columns=["meaning","word","pos","value"])
    related_words = related_words[related_words["word"] != word]
    pos_preferences = {"01": 1,"02": 2, "03": 3, "04": 4,"n": 0, "s": 5, "v": 3, "a": 2, "r": 4}
    related_words = related_words.sort_values(by=["value","pos"],key=lambda x: sorting_function(x,pos_preferences))
    return related_words["meaning"].to_list()



def get_related_words_from_definition(meaning):
    definition = meaning.definition()
    words = [w for w in nltk.tokenize.word_tokenize(definition) if w not in stop_words]
    word_df = pd.DataFrame(nltk.tag.pos_tag(words))
    if not word_df.empty:
        word_df["pos"] = word_df[1].apply(lambda x: get_more_common_part_of_speech(x))
        word_df["meanings"] = word_df[0].apply(lambda x: wn.synsets(x))
        word_df["has_hypernym"] = word_df["meanings"].apply(lambda x: True in [True for y in x if len(y.hypernyms()) > 0])
        no_hypernyms = word_df[~word_df["has_hypernym"]]
        word_df = word_df[word_df["has_hypernym"]]
        word_df = word_df.explode("meanings")
        return sort_meanings_for_best_related_words(word_df["meanings"].to_list())

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
        general_part_of_speech = "a" #or a...?
    return general_part_of_speech



# get ranked lemmas
with (open("lemmas_ranked.pkl", "rb")) as openfile:
    while True:
        try:
            lemmas_ranked = pickle.load(openfile)
        except EOFError:
            break
def get_specific_input(text="Yes/No",options=["Yes","No"]):
    while True:
        output = input(text)
        if output in options:
            return output
        else:
            print("Please type one of the following options: " + " ".join(options) 
                + "\n")


def get_related_words(meaning,word=None,lowest_frequency=500):
    related_words = []
    # word = "Superman"
    if word == None:
        word = meaning.lemmas()[0].name()
    related_everything = []
    for pair in [
            [meaning.in_topic_domains,"in_topic_domains"],
            # [meaning.in_usage_domains,"in_usage_domains"],
            [meaning.substance_holonyms,"substance_holonyms"],
            [meaning.substance_meronyms,"substance_meronyms"],
            [meaning.instance_hypernyms,"instance_hypernyms"],
            [meaning.in_topic_domains,"in_topic_domains"],
            [meaning.instance_hyponyms,"instance_hyponyms"],
            [meaning.member_holonyms,"member_holonyms"],
            [meaning.in_region_domains,"in_region_domains"],
            [meaning.member_meronyms,"member_meronyms"],
            [meaning.part_holonyms,"part_holonyms"],
            [meaning.part_meronyms,"part_meronyms"],
            [meaning.region_domains,"region_domains"],
            [meaning.similar_tos,"similar_tos"],
            [meaning.topic_domains,"topic_domains"],
            [meaning.usage_domains,"usage_domains"]
            ]:
        related_everything.append([pair[0],pair[1]])

    lemma_names = meaning.lemma_names()
    if word in lemma_names:
        lemma_names.remove(word)

    related_everything += [["synonym",wn.synsets(lemma_name)] for lemma_name in lemma_names]

    related_everything += [["mentioned_in_definition",[meaning]] for meaning in get_related_words_from_definition(meaning)]

    related_everything = [x for x in related_everything if len(x[1]) > 0]
    # related_everything[0]
    related_df = pd.DataFrame(related_everything)
    if len(related_df.columns) == 3:
        related_df.columns = ["mystery","type_of_relationship","meanings"]    
        related_df = related_df[related_df["mystery"].apply(lambda x: str(type(x)) == "<class 'str'>")]
        related_df = related_df.drop("meanings",axis=1)
    related_df.columns = ["type_of_relationship","meanings"]
    
    related_df = related_df.explode("meanings")
    
    return get_and_sort_words_for_best_related_words(related_df["meanings"].to_list(),word,1000)  



if __name__ == "__main__":
    pass
    # unique_selected_words_df = pd.read_pickle("unique_selected_words.pkl")
    # unique_selected_words_df["pos"] = unique_selected_words_df["part_of_speech"].apply(get_more_common_part_of_speech)
    # unique_selected_words_df["suggested_possible"] = unique_selected_words_df.apply(
    #         lambda x: find_definitions_and_ranking_them_by_preference(x["original_word"],part_of_speech=x["pos"]),axis=1)

    # unique_selected_words_df["one_meaning_used"] = unique_selected_words_df["suggested_possible"].apply(lambda x: x[0] if len(x) > 0 else None)
    
    # for i, row in unique_selected_words_df.iterrows():
    #     meaning = row["one_meaning_used"]
    #     if str(meaning) != "None":
    #         print(meaning)
            
    #         print(get_related_words(meaning,word=row["original_word"]))
    #     print(i, )
    #     [0:1].apply(lambda x: get_related_words(x) if str(x) != "None" else None)
    
    


