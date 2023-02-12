import pandas as pd
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

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

def get_specific_input(text="Yes/No",options=["Yes","No"]):
    while True:
        output = input(text)
        if output in options:
            return output
        else:
            print("Please type one of the following options: " + " ".join(options) 
                + "\n")

# pull in the brown corpus

import pickle
if __name__ == "__main__":
    annotated_tokens_df = pd.read_pickle("tokens_and_meanings.pkl")

    # get ranked lemmas
    with (open("lemmas_ranked.pkl", "rb")) as openfile:
        while True:
            try:
                lemmas_ranked = pickle.load(openfile)
            except EOFError:
                break


    # ranking the words according to their frequency in that corpus
    
    annotated_tokens_df["brown_frequency"] = annotated_tokens_df["corrected_word"].apply(
        lambda x: find_frequency_ranking(x))

    unique_words = annotated_tokens_df[~annotated_tokens_df.duplicated("corrected_word")]

    # presenting the words to a user for approving 10
    approved_ten = []
    
    unique_words.columns

    song_lines_df = pd.read_pickle("song_lines.pkl")

    unique_words = unique_words.reset_index()

    unique_words = unique_words.drop("index",axis=1)

    unique_words.sort_values(["brown_frequency"],ascending=False).join(
        song_lines_df.set_index("line_number"),on="line_number")[[
            "original_word","line"]].to_csv("ordered_suggested_words.csv")

    from os import startfile
    import pyautogui
    startfile( r"C:\Users\lis\3D Objects\Downloads\create_vocabulary_exercises-master\create_vocabulary_exercises-master\ordered_suggested_words.csv" )
    if pyautogui.confirm("Wait for the file to open. Delete all but the rows of the words that you would like to work with. After that press OK.") == "OK":
        unique_selected_words = pd.read_csv("ordered_suggested_words.csv")
        unique_selected_words = unique_selected_words.join(unique_words,on="Unnamed: 0",rsuffix="_uw")
        unique_selected_words.drop("original_word_uw",inplace=True,axis=1)
        unique_selected_words.to_pickle("unique_selected_words.pkl")

        annotated_tokens_df[
            annotated_tokens_df["original_word"].isin(
                unique_selected_words["original_word"])].to_pickle("selected_words.pkl")



    


    # for _, row in unique_words.sort_values(["brown_frequency"],ascending=False).iterrows():
    #     # presenting the word
    #     _, token, line_number, part_of_speech, likely_meanings, _ = row
    #     if token != None and token.isalpha():
    #         if likely_meanings != None and likely_meanings != '' and "?" not in likely_meanings:
    #             likely_meanings = likely_meanings.split(",")
    #             approval = get_specific_input(f"The next suggested word is {token} ({part_of_speech})."
    #                 + "\nShould it be included in the exercise? (Yes/No/Context/Full details) ",
    #                 ["Yes","No","Context","Full details"])
    #             if approval == "Context":
    #                 approval = get_specific_input(f"The word {token} comes from this sentence:\n"
    #                     + " ".join(annotated_tokens_df[annotated_tokens_df["line_number"]
    #                         == line_number]["original_word"].tolist())
    #                     + f"\nDo you want to include it? (Yes/No/Full details) ")
    #             if approval == "Full details":
    #                 approval = get_specific_input(f"The word {token} comes from this sentence:\n"
    #                     + " ".join(annotated_tokens_df[annotated_tokens_df["line_number"]
    #                         == line_number]["original_word"].tolist())
    #                     + "\nThese are the part_of_speechsible meanings suggested for it:\n"
    #                     + "\n".join([f"{i} {wn.synset(meaning).definition()}" for i, meaning in enumerate(likely_meanings)])
    #                     + f"\nDo you want to include it? (Yes/No/Full details) ")
    #             if approval == "Yes":
    #                 approved_ten.append(token)
    #     if len(approved_ten) == 10:
    #         break
    # print("You did not select enough words.")
    # # add part_of_speechsible loop?

    # unique_words[unique_words.corrected_word.isin(approved_ten)].to_pickle("unique_selected_words.pkl")

    # annotated_tokens_df[annotated_tokens_df.corrected_word.isin(approved_ten)].to_pickle("selected_words.pkl")

    