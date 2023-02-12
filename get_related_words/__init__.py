import pandas as pd
from nltk.corpus import wordnet as wn
import pyautogui
import nltk
import pickle

def sorting_function(x,pos_preferences):
    x = x.map(pos_preferences)
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
    words = [w for w in word_tokenize(definition) if w not in stop_words]
    word_df = pd.DataFrame(pos_tag(words))
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


def get_related_words(meaning):
    related_words = []
    word = meaning.lemmas()[0].name()
    related_everything = []
    for pair in [
            [meaning.in_topic_domains,"in_topic_domains"],
            [meaning.in_usage_domains,"in_usage_domains"],
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
        related_everything = add_an_item(pair[0],pair[1],related_everything)

    lemma_names = meaning.lemma_names()
    current_word_name = meaning.lemmas()[0].name()
    if current_word_name in lemma_names:
        lemma_names.remove(current_word_name)
    related_everything += [["synonyms",lemma_names]]
    related_everything = [x for x in related_everything if len(x[1]) > 0]
    related_df = pd.DataFrame(related_everything)
    related_df.columns = ["type_of_relationship","meanings"]
    related_df = related_df.explode("meanings")
    
    related_df["lemma_naming"] = related_df["meanings"].apply(lambda x: [y.name() for y in x.lemmas()])
    related_df["has_same_word"] = related_df["lemma_naming"].apply(lambda x: True in [word in y for y in x])
    #doesn't have the same word
    related_words.extend(related_df[related_df["has_same_word"] == False]["meanings"].to_list())
    if len(related_words) >= 3:
        return related_words
    else:
        related_df = related_df[related_df["has_same_word"]]
        related_df["meanings"] = related_df["lemma_naming"].apply(lambda x: [wn.synsets(y.replace(word,"").replace("_"," ").strip()) for y in x if word in y])
        for i, row in related_df[related_df["meanings"].apply(lambda x: True not in [True for y in x if len(y) > 0])].iterrows():
            related_df.at[i,"meanings"].extend(get_related_words_from_definition(
                wn.synsets(row["lemma_naming"][0])[0]))
        related_df["meanings"] = related_df["meanings"].apply(lambda x: list(filter(lambda y: y, x)))
        related_df["meanings"] = related_df["meanings"].apply(lambda x: x[0] if str(type(x[0])) == "<class 'list'>" else x)
        related_df["meanings"] = related_df["meanings"].apply(lambda x: x[0])
        return sort_meanings_for_best_related_words(related_df["meanings"])

        



if __name__ == "__main__":
    unique_selected_words_df = pd.read_pickle("unique_selected_words.pkl")
    unique_selected_words_df["pos"] = unique_selected_words_df["part_of_speech"].apply(get_more_common_part_of_speech)
    unique_selected_words_df["suggested_possible"] = unique_selected_words_df.apply(
            lambda x: find_definitions_and_ranking_them_by_preference(x["original_word"],part_of_speech=x["pos"]),axis=1)

    unique_selected_words_df["one_meaning_used"] = unique_selected_words_df["suggested_possible"].apply(lambda x: x[0] if len(x) > 0 else None)
    
    unique_selected_words_df["one_meaning_used"].apply(lambda x: get_related_words_from_definition(x) if x != None else None)
    


