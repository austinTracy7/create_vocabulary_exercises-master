import pandas as pd
from nltk.corpus import wordnet as wn
import pyautogui
import nltk
import pickle

def sorting_function(x,pos_preferences):
    x = x.map(pos_preferences)
    return x

def find_defitions_and_ranking_them_by_preference(word,part_of_speech=None):
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


def get_related_words(unique_selected_words_df,i,row,meaning):
    related_everything = []
    def add_an_item(stuff_to_add,category,related_everything):
        try:
            related_everything.append([category,stuff_to_add()])
        except:
            print("exception")
            related_everything.append([])
        return related_everything
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
    if row["lemma"] in lemma_names:
        lemma_names.remove(row["lemma"])
    related_everything += [["synonyms",lemma_names]]
    related_everything = [x for x in related_everything if len(x[1]) > 0]
    unique_selected_words_df.loc[i,"related_words"].extend(related_everything)


def get_specific_input(text="Yes/No",options=["Yes","No"]):
    while True:
        output = input(text)
        if output in options:
            return output
        else:
            print("Please type one of the following options: " + " ".join(options) 
                + "\n")

unique_selected_words_df = pd.read_pickle("unique_selected_words.pkl")

unique_selected_words_df["original_word"].apply(lambda x: find_defitions_and_ranking_them_by_preference(x))



# unique_selected_words_df["accepted_meanings"] = unique_selected_words_df["likely_meanings"].apply(lambda x: [])
# unique_selected_words_df["related_words"] = unique_selected_words_df["likely_meanings"].apply(lambda x: [])

# # ensuring correct meanings are selected and getting more specific
# for i, row in unique_selected_words_df.iterrows():
#     response = ""
#     if row.likely_meanings == "" or row.likely_meanings == None:
#         response = "Manual Entry"        
#     while response not in ["Manual Entry","Done","ME","D"]:
#         print(row["original_word"])
#         possible_meanings = row.likely_meanings.split(",")
#         for y, meaning in enumerate(possible_meanings):
#             print(y, wn.synset(meaning.replace("?","")).definition())
#         response = get_specific_input(
#             text="""Input the number for the correct meaning or 
#             either Context (C) or Full Details (FD) for more information 
#             or Manual Entry (ME) to ignore the definitions provided
#             and give your own related words or Done (D).""",
#             options=[str(x) for x in list(
#             range(len(meaning)))] + ["Context", "Full Details","Done",
#             "Manual Entry","C","FD","D","ME"])
#         print(response)
#         if response.isnumeric():
#             unique_selected_words_df.loc[i,"accepted_meanings"].extend([
#                 wn.synset(possible_meanings[int(response)].replace(
#                     "?",""))]
#             ) 
#     if response in ["Manual Entry","ME"]:
#         original_word = row["original_word"]
#         related_words = input(f"Enter related words to {original_word} " +
#             "(with a space between them):\n")
#         from nltk.tokenize import word_tokenize
#         unique_selected_words_df.loc[i,"related_words"].extend(["user_entered",word_tokenize(related_words)])

#         unique_selected_words_df["accepted_meanings"]
    
#     print(unique_selected_words_df.loc[i,"accepted_meanings"])
#     print(unique_selected_words_df.loc[i,"related_words"])

#     export_unique_selected_words_df = unique_selected_words_df.copy()
#     export_unique_selected_words_df["accepted_meanings"] = export_unique_selected_words_df["accepted_meanings"].astype("str")

#     export_unique_selected_words_df.to_pickle("related_words.pkl")

# # getting meanings to work with if it only has manually entered information
# for i, row in export_unique_selected_words_df[export_unique_selected_words_df[
#         "accepted_meanings"].apply(lambda x: len(x) == 0)].iterrows():
#     # row["related_words"]
#     # export_unique_selected_words_df.at[i,"likely_meanings"] = 
#     # 
#     # row["likely_meanings"] = wn.synsets("alright")[1:]
    
#     def find_core_meaning_v1(word,related_words,likely_meanings):
#         if len(likely_meanings) > 0:
#             ####### if there are likely meanings
#             # find the related words' possible meanings
#             related_possible_definition_pairs = []
#             related_possible_definitions = []
#             all_related_possible_definitions = []
#             for r_word in related_words:
#                 meanings_of_r_word = wn.synsets(r_word)
#                 related_possible_definitions.append(meanings_of_r_word)
#                 all_related_possible_definitions += meanings_of_r_word

#             # try to find a main meaning by association
#             probable_meanings = []
#             for meaning in likely_meanings:
#                 if meaning in all_related_possible_definitions:
#                     probable_meanings.append(meaning)

#             # if one was found, that's it
#             if len(probable_meanings) > 0:
#                 return probable_meanings
#             else:
#                 dictionary = {}
#                 for item in [str(x) for x in all_related_possible_definitions]:
#                     if dictionary.get(item) == None:
#                         dictionary[item] = 1
#                     else:
#                         dictionary[item] += 1
#                 good_options = [i for i in dictionary.items() if i[1] > 1]
#                 if len(good_options) > 1:
#                     return good_options
#                 all_rel_df = pd.DataFrame([[x] + str(x).rsplit(".",2) for x in all_related_possible_definitions],columns=["meaning","word","pos","value"])
#                 all_rel_df["value"] = all_rel_df["value"].apply(lambda x: x.replace("')",""))
#                 all_rel_df["word"] = all_rel_df["word"].apply(lambda x: x.replace("Synset('",""))
                
#                 test_limited = all_rel_df[(all_rel_df["value"] == "01") & (all_rel_df["word"].isin(related_words))]
#                 if len(test_limited) > 0:
#                     return test_limited["meaning"].to_list()
#                     # nouns only???
                
#                 1/0
                
                
#                 1/0
                
#                     # related_possible_definitions_duplicate = related_possible_definitions.copy()
#                     # one_grouping = related_possible_definitions_duplicate.pop()
#                     # # ic = nltk.corpus.wordnet_ic.ic("ic-brown.dat")

#                     # # nltk.download('wordnet_ic')
#                     # grouping_evaluation = []
#                     # for meaning in one_grouping:
#                     #     for meaning_group in related_possible_definitions:
#                     #         for other_meaning in meaning_group:
#                     #             print(other_meaning)
#                     #             print(other_meaning.definition())
#                     #             if meaning.pos() == other_meaning.pos():
#                     #                 # grouping_evaluation.append([other_meaning,meaning.lch_similarity(other_meaning)])
#                     #                 print(meaning.wup_similarity(other_meaning))
#                     #                 print(meaning.path_similarity(other_meaning))
#                     #                 # help(meaning)
#                     #                 print(meaning.lowest_common_hypernyms(other_meaning))
#                     #                 # meaning.res_similarity(other_meaning,ic)
#                     #                 help(other_meaning)
                    

                            
                    

            
#     likely_meanings = [wn.synset(x.replace("?","")) for x in row["likely_meanings"].split(",")]
#     related_words = row["related_words"]
#     find_core_meaning_v1(row["lemma"],related_words,likely_meanings)
#     # export_unique_selected_words_df.at[i,"accepted_meanings"] = find_core_meaning_v1(row["lemma"],related_words,likely_meanings)
#     # if len(accepted_meanings) == 0:
#     #     export_unique_selected_words_df.at[i,"accepted_meanings"].append(find_core_meaning_v1(word,related_words,row["likely_meanings"]))

#     #     # print(related_possible_definition_pairs)
#         # df_related = pd.DataFrame(related_possible_definition_pairs)
#         # df_related["possible_meaning_count"] = df_related[1].apply(lambda x: len(x))

#     if len(accepted_meanings) == 0:
#         find_meanings([row["lemma"]] + related_words)


    
        
#     find_meaning("good",["okay","alright"])
#     break
#     if accepted_meanings < 0:
        
#     row["related_words"]
#     break
# # [meaning.definition() for meaning in wn.synsets("naive")]

# # getting related words part 1
# for i, row in unique_selected_words_df[
#     unique_selected_words_df["related_words"].apply(lambda x: len(x) < 3)
#     ].iterrows():
#     for meaning in row["accepted_meanings"]:
#         get_related_words(unique_selected_words_df,i,row,meaning)







# def find_unrelated_words(meanings):
#     # meanings = wn.synsets("heart")
#     for meaning in meanings:
#         for lemma in meaning.lemmas():
#             antonyms = lemma.antonyms()
#             if len(antonyms) > 0:
#                 return [lemma.name() for lemma in antonyms][0]
#     for meaning in meanings:
#         print(meaning)
#         meaning.part_holonyms()

# def add_an_item(stuff_to_add,category,related_everything):
#         try:
#             related_everything.append([category,stuff_to_add()])
#         except:
#             print("exception")
#             related_everything.append([])
#         return related_everything

# def get_related_words_v2(meaning):
#     related_words = []
#     word = meaning.lemmas()[0].name()
#     related_everything = []
#     for pair in [
#             [meaning.in_topic_domains,"in_topic_domains"],
#             [meaning.in_usage_domains,"in_usage_domains"],
#             [meaning.substance_holonyms,"substance_holonyms"],
#             [meaning.substance_meronyms,"substance_meronyms"],
#             [meaning.instance_hypernyms,"instance_hypernyms"],
#             [meaning.in_topic_domains,"in_topic_domains"],
#             [meaning.instance_hyponyms,"instance_hyponyms"],
#             [meaning.member_holonyms,"member_holonyms"],
#             [meaning.in_region_domains,"in_region_domains"],
#             [meaning.member_meronyms,"member_meronyms"],
#             [meaning.part_holonyms,"part_holonyms"],
#             [meaning.part_meronyms,"part_meronyms"],
#             [meaning.region_domains,"region_domains"],
#             [meaning.similar_tos,"similar_tos"],
#             [meaning.topic_domains,"topic_domains"],
#             [meaning.usage_domains,"usage_domains"]
#             ]:
#         related_everything = add_an_item(pair[0],pair[1],related_everything)

#     lemma_names = meaning.lemma_names()
#     current_word_name = meaning.lemmas()[0].name()
#     if current_word_name in lemma_names:
#         lemma_names.remove(current_word_name)
#     related_everything += [["synonyms",lemma_names]]
#     related_everything = [x for x in related_everything if len(x[1]) > 0]
#     related_df = pd.DataFrame(related_everything)
#     related_df.columns = ["type_of_relationship","meanings"]
#     related_df = related_df.explode("meanings")
    
#     related_df["lemma_naming"] = related_df["meanings"].apply(lambda x: [y.name() for y in x.lemmas()])
#     related_df["has_same_word"] = related_df["lemma_naming"].apply(lambda x: True in [word in y for y in x])
#     #doesn't have the same word
#     related_words.extend(related_df[related_df["has_same_word"] == False]["meanings"].to_list())
#     if len(related_words) >= 3:
#         return related_words
#     else:
#         related_df = related_df[related_df["has_same_word"]]
#         related_df["meanings"] = related_df["lemma_naming"].apply(lambda x: [wn.synsets(y.replace(word,"").replace("_"," ").strip()) for y in x if word in y])
#         for i, row in related_df[related_df["meanings"].apply(lambda x: True not in [True for y in x if len(y) > 0])].iterrows():
#             related_df.at[i,"meanings"].extend(get_related_words_from_definition(
#                 wn.synsets(row["lemma_naming"][0])[0]))
#         related_df["meanings"] = related_df["meanings"].apply(lambda x: list(filter(lambda y: y, x)))
#         related_df["meanings"] = related_df["meanings"].apply(lambda x: x[0] if str(type(x[0])) == "<class 'list'>" else x)
#         related_df["meanings"] = related_df["meanings"].apply(lambda x: x[0])
#         return sort_meanings_for_best_related_words(related_df["meanings"])

        

#         str(type([])) == "<class 'list'>"
#         related_df["lemma_naming"]
        
        
#         related_df
    
    
#         3.5 + 3 + 6 + 6 + 15 + 2.69 + 2.69 + 4 + 5
#         55 - 33.88
#         0/1
#         no_hypernyms

#     from nltk import pos_tag
    
#     get_related_words_from_definition(wn.synset('shirting.n.01'))

#     from nltk.corpus import stopwords
#     stop_words = set(stopwords.words('english'))

#     from nltk.tokenize import word_tokenize
    
#     related_df["meaning"] = related_df["lemma_naming"].apply(lambda x: get_meanings_without_the_same_word(word,x))
#     related_df = related_df.explode("meaning")
#     return related_everything

#     wn.synset('shirting.n.01').definition()

# get_related_words_v2(wn.synsets("shirt")[0])

# wn.synsets("silverware")[0]

# lemma = find_unrelated_words(wn.synsets("heart"))
# export_unique_selected_words_df["unrelated_words"
#     ] = export_unique_selected_words_df["related_words"].apply(lambda x: [])

# # export_unique_selected_words_df["related_words"] = export_unique_selected_words_df["related_words"].apply(lambda x: x[:2])

# for i, row in export_unique_selected_words_df.iterrows():
#     unrelated_word_suggestions = []
#     for word in row["related_words"]:
#         unrelated_word_suggestions.append(find_unrelated_words(
#             find_defitions_and_ranking_them_by_preference(word)))
#     export_unique_selected_words_df.at[
#         i,"unrelated_words"].extend(unrelated_word_suggestions)

#     .apply(lambda x: 
#     )



# meanings = find_defitions_and_ranking_them_by_preference("stupid")

#     for i, row in def_df.iterrows():
#         for lemma in row["meaning"].lemmas():
#             antonyms = lemma.antonyms()
#             if len(antonyms) > 0:
#                 break

#                 wn.synset('speechless.s.01').lemmas()[0].antonyms()
# find_best_definition("dumb")
# word = "dumb"

# 13


# from nltk.corpus import wordnet as wn

# for i in wn.all_synsets():
#     if i.pos() in ['a', 's']: # If synset is adj or satelite-adj.
#         for j in i.lemmas(): # Iterating through lemmas for each synset.
#             if j.antonyms(): # If adj has antonym.
#                 # Prints the adj-antonym pair.
#                 print(j.name(), j.antonyms()[0].name())

# def find_unrelated_words(cell):
#     for word in cell:
#         print(word)

# _ = export_unique_selected_words_df["related_words"].apply(find_unrelated_words)

# /specific meanings and antonyms


# # round two, expanding from round 1
# for i, row in unique_selected_words_df[
#     unique_selected_words_df["related_words"].apply(lambda x: len(x) < 5)
#     ].iterrows():
#     for meaning in row["related_words"]:
#         print(meaning)
        



#         wup_similarity
#         lin_similarity
#         lch_similarity
#         jcn_similarity
        




#         res_similarity



# # getting antonyms

