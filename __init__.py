import tkinter as tk
import get_vocabulary_and_likely_meanings as gvam
from nltk.stem import WordNetLemmatizer
import pandas as pd
import nltk
from unidecode import unidecode
import get_token_frequency as gtf
from os import startfile
import pyautogui
import get_related_words as grw

from get_related_words import *
import os


if __name__ == "__main__":
    ###
    #@feature add way to just run program from anywhere

    ### get vocabulary and likely meanings
    lemmatizer = WordNetLemmatizer()

    # copy text to get vocabulary from
    root = tk.Tk()
    gvam.confirm_selection()
    gvam.copy_information()
    information = root.clipboard_get()
    input_text = information
    
    # polish the song lines (remove contractions)
    song_lines = gvam.decontracted(input_text).replace("â€™","'").split("\n")

    # create a table of song lines
    song_lines_df = pd.DataFrame([list(line) for line in zip(range(len(song_lines)),song_lines)],columns=["line_number","line"])

    song_lines_df.to_pickle("intermediate_outputs/song_lines.pkl")

    # fix spellings
    #@bug (diggin came back as digitaria rather than dig...)
    words_df = pd.DataFrame(song_lines_df.apply(lambda row: 
        [[token,gvam.test_for_correct_word_fix_if_not(unidecode(token)),row["line_number"]]
         for token in nltk.tokenize.word_tokenize(row["line"])]
         ,axis=1))
    
    # other prep
    words_df.columns = ["groupings"]
    words_df = words_df["groupings"].apply(lambda x: list(zip(x,
        [grouping[1] for grouping in 
        nltk.pos_tag([y[1] if y[1] != None else "" for y in x])])))

    # put tokens on their own lines for a table of words
    words_df = pd.DataFrame(words_df)
    words_df["groupings"] = words_df["groupings"].apply(lambda row: [grouping[0] + [grouping[1]] for grouping in row])
    words_df = words_df.explode("groupings")
    words_df = words_df["groupings"].apply(pd.Series)
    words_df.columns = ["original_word","corrected_word","line_number","part_of_speech"]

    # clean up the table
    words_df = words_df[~words_df["original_word"].isna()]
    words_df.loc[:,"part_of_speech"] = words_df["part_of_speech"].apply(lambda x: x if x.isalpha() else None)
    
    # lemmatize the words
    words_df["lemma"] = words_df["corrected_word"].apply(lambda word: lemmatizer.lemmatize(word) if word != None else word)

    words_df.to_pickle("intermediate_outputs/tokens_and_meanings.pkl")

    # get the frequency rank of the lemmas
    words_df["frequency_rank_of_lemma"] = words_df["lemma"].apply(gtf.find_frequency_ranking)

    # find unique words, sort them by frequency, 
    # and present them to a user for getting vocabulary
    unique_words = words_df[~words_df.duplicated("corrected_word")]

    unique_words = unique_words.reset_index()

    unique_words = unique_words.drop("index",axis=1)

    unique_words.sort_values(["frequency_rank_of_lemma"],ascending=False).join(
        song_lines_df.set_index("line_number"),on="line_number")[[
            "original_word","line","frequency_rank_of_lemma"]].to_csv("ordered_suggested_words.csv")
    unique_words["lemma"].to_list()

    startfile( r"C:\Users\lis\3D Objects\Downloads\create_vocabulary_exercises-master\create_vocabulary_exercises-master\ordered_suggested_words.csv" )
    if pyautogui.confirm("Wait for the file to open. Delete all but the rows of the words that you would like to work with. After that press OK.") == "OK":
        unique_selected_words = pd.read_csv("ordered_suggested_words.csv")
        unique_selected_words = unique_selected_words.join(unique_words,on="Unnamed: 0",rsuffix="_uw")
        unique_selected_words.drop("original_word_uw",inplace=True,axis=1)
        unique_selected_words.drop("frequency_rank_of_lemma_uw",inplace=True,axis=1)
        unique_selected_words.to_pickle("intermediate_outputs/unique_selected_words.pkl")

        selected_df = words_df[
            words_df["original_word"].isin(
                unique_selected_words["original_word"])]
                
        selected_df.to_pickle("intermediate_outputs/selected_words.pkl")

        selected_df = selected_df.groupby(['original_word', 'corrected_word', 'part_of_speech','lemma', 'frequency_rank_of_lemma']).agg({"line_number": lambda x: x.tolist()})
        selected_df = selected_df.reset_index()            

        lowest_selected_frequency = min(selected_df["frequency_rank_of_lemma"])

        # get meanings and related words
        unique_selected_words_df = selected_df.copy()
        unique_selected_words_df["pos"] = unique_selected_words_df["part_of_speech"].apply(get_more_common_part_of_speech)
        unique_selected_words_df["suggested_possible_meanings"] = unique_selected_words_df.apply(
                lambda x: find_definitions_and_ranking_them_by_preference(x["original_word"],part_of_speech=x["pos"]),axis=1)

        unique_selected_words_df["meaning(s) used"] = unique_selected_words_df["suggested_possible_meanings"].apply(lambda x: x[0] if len(x) > 0 else None)
        unique_selected_words_df["related_words"] = unique_selected_words_df["meaning(s) used"].apply(lambda x: [])
        for i, row in unique_selected_words_df.iterrows():
            meaning = row["meaning(s) used"]
            
            if str(meaning) != "None":
                for related_word in get_related_words(meaning,
                    word=row["original_word"],lowest_frequency=lowest_selected_frequency):
                    unique_selected_words_df.loc[i,"related_words"].append(related_word)

        # get select related words
        related_words_df = unique_selected_words_df[["original_word","related_words"]] #.explode("related_words")
        related_words_df = related_words_df.set_index("original_word")
        related_words_df = related_words_df.join(related_words_df["related_words"].apply(pd.Series))
        related_words_df.drop("related_words",inplace=True,axis=1
        related_words_df.to_csv(r"C:\Users\lis\3D Objects\Downloads\create_vocabulary_exercises-master\create_vocabulary_exercises-master\related_word_selection.csv")

        startfile(r"C:\Users\lis\3D Objects\Downloads\create_vocabulary_exercises-master\create_vocabulary_exercises-master\related_word_selection.csv" )
        if pyautogui.confirm("Wait for the file to open. Delete all the words in each row except the ones you want to present as related to the original word. You may also type more on the same row.") == "OK":
            accepted_related_words = pd.read_csv(r"C:\Users\lis\3D Objects\Downloads\create_vocabulary_exercises-master\create_vocabulary_exercises-master\related_word_selection.csv" )
            # clean up the table
            accepted_related_words = accepted_related_words.dropna(axis=1, how='all')    

            accepted_related_words = accepted_related_words.set_index("original_word")

            accepted_related_words_dictionary = accepted_related_words.T.to_dict("records")

            pairs_related_and_original = []
            for series in accepted_related_words_dictionary:
                pairs_related_and_original+=[[x[0],x[1]] for x in series.items()]

            # get unrelated or less related words to the 
            vocabulary_exercise_df = pd.DataFrame(pairs_related_and_original)
            vocabulary_exercise_df.columns = ["original","related_word"]
            

            # for i, row in vocabulary_exercise_df.iterrows():
            #     meaning = row["meaning(s) used"]
                
            #     if str(meaning) != "None":
            #         for related_word in get_related_words(meaning,
            #             word=row["original_word"],lowest_frequency=lowest_selected_frequency):
            #             unique_selected_words_df.loc[i,"related_words"].append(related_word)

            # vocabulary_exercise_df["suggested_possible_meanings"] = vocabulary_exercise_df.apply(
            #     lambda x: find_definitions_and_ranking_them_by_preference(x["original_word"],
            #         part_of_speech=x["pos"]),axis=1)

            # vocabulary_exercise_df
            
            vocabulary_exercise_df["part_of_speech"] = vocabulary_exercise_df["related_word"].apply(
                lambda x: nltk.pos_tag([x])[0][1])

            vocabulary_exercise_df["pos"] = vocabulary_exercise_df["part_of_speech"].apply(get_more_common_part_of_speech)

            vocabulary_exercise_df["suggested_possible_meanings"] = vocabulary_exercise_df.apply(
                lambda x: find_definitions_and_ranking_them_by_preference(x["related_word"],part_of_speech=x["pos"]),axis=1)

            vocabulary_exercise_df["meaning(s) used"] = vocabulary_exercise_df["suggested_possible_meanings"].apply(lambda x: x[0] if len(x) > 0 else None)
            vocabulary_exercise_df["related_words"] = vocabulary_exercise_df["meaning(s) used"].apply(lambda x: [])
            for i, row in vocabulary_exercise_df.iterrows():
                meaning = row["meaning(s) used"]
                if str(meaning) != "None":
                    for related_word in get_related_words(meaning,
                        word=row["related_word"],lowest_frequency=lowest_selected_frequency):
                        vocabulary_ex

                
            vocabulary_exercise_df.apply(get_unrelated_words,axis=1)
            ercise_df.loc[i,"related_words"].append(related_word)

            def get_unrelated_words(row):
                row = vocabulary_exercise_df.loc[0]
                meaning = row["meaning(s) used"]
                lemmas = meaning.lemmas()
                unrelated_words = []
                # get antonyms
                for lemma in lemmas:
                    antonyms = lemma.antonyms()
                    if len(antonyms) > 0:
                        unrelated_words += antonyms
                
                # find less related items
                #@feature add variation to differential
                # find hypernyms
                differential = 2
                next_hypernyms = flatten_list_items(
                    get_related_hypernyms(meaning)["meanings"].to_list())
                hypernyms_path = next_hypernyms[:]
                for i in range(differential - 1):
                    current_hypernym_finds = []
                    for hypernym in next_hypernyms:
                        current_hypernym_finds += flatten_list_items(
                        get_related_hypernyms(hypernym)["meanings"].to_list())
                    next_hypernyms = current_hypernym_finds[:]
                    hypernyms_path += current_hypernym_finds
                # come back down for hyponyms, with less related items
                next_hyponym_batch = next_hypernyms
                hyponyms = []
                for i in range(differential):
                    next_hyponyms = []
                    for hyponym in next_hyponym_batch:
                        print(hyponym)
                        next_hyponyms += flatten_list_items(get_hyponyms(hypernym)["meanings"].to_list())
                    next_hyponyms = [x for x in next_hyponyms if x not in hypernyms_path]
                    hyponyms += next_hyponyms
                    next_hyponym_batch = next_hyponyms

                hyponyms.reverse()

                    
                
                    
                        
                        for hypernym in next_hypernyms:
                        next_hypernyms = []
                for hypernym in first_hypernyms:
                    second_hypernyms += flatten_list_items(
                    get_related_hypernyms(hypernym)["meanings"].to_list())
                
                for hypernym in second_hypernyms:
                    print(hypernym)
                    hypernym.hyponyms()

            
def if_error(function,default=None):
    try:
        return function()
    except:
        return default

def get_related_hypernyms(meaning,word=None):
    related_words = []
    # word = "Superman"
    if word == None:
        word = meaning.lemmas()[0].name()
    related_everything = []
    for pair in [
            # [meaning.instance_hyponyms,"instance_hyponyms"],
            [meaning.hypernyms,"hypernyms"],
            [meaning.member_holonyms,"member_holonyms"],
            # [meaning.member_meronyms,"member_meronyms"],
            [meaning.part_holonyms,"part_holonyms"],
            # [meaning.part_meronyms,"part_meronyms"],
            ]:
        related_everything.append([if_error(pair[0],default=[]),pair[1]])
    related_everything = [x for x in related_everything if len(x[0]) > 0]
    related_df = pd.DataFrame(related_everything)

    # if len(related_df.columns) == 3:
    #     related_df.columns = ["mystery","type_of_relationship","meanings"]    
    #     related_df = related_df[related_df["mystery"].apply(lambda x: str(type(x)) == "<class 'str'>")]
    #     related_df = related_df.drop("meanings",axis=1)
    related_df.columns = ["meanings","type_of_relationship"]

    return related_df

def get_hyponyms(meaning,word=None):
    related_words = []
    # word = "Superman"
    if word == None:
        word = meaning.lemmas()[0].name()
    related_everything = []
    for pair in [
            [meaning.instance_hyponyms,"instance_hyponyms"],
            [meaning.member_meronyms,"member_meronyms"],
            [meaning.part_meronyms,"part_meronyms"],
            [meaning.hyponyms,"hyponyms"],
            ]:
        related_everything.append([if_error(pair[0],default=[]),pair[1]])
    related_everything = [x for x in related_everything if len(x[0]) > 0]
    related_df = pd.DataFrame(related_everything)

    # if len(related_df.columns) == 3:
    #     related_df.columns = ["mystery","type_of_relationship","meanings"]    
    #     related_df = related_df[related_df["mystery"].apply(lambda x: str(type(x)) == "<class 'str'>")]
    #     related_df = related_df.drop("meanings",axis=1)
    related_df.columns = ["meanings","type_of_relationship"]

    return related_df
    