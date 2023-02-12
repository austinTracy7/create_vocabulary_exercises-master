import pandas as pd
from nltk.corpus import wordnet as wn
import pyautogui
import nltk

unique_selected_words_df = pd.read_pickle("unique_selected_words.pkl")

unique_selected_words_df["meaning_used"] = unique_selected_words_df["likely_meanings"].apply(lambda x: [])
unique_selected_words_df["related_words"] = unique_selected_words_df["likely_meanings"].apply(lambda x: [])



# ensuring correct meanings are selected and getting more specific
for i, row in unique_selected_words_df.iterrows():
    response = ""
    if row.likely_meanings == "" or row.likely_meanings == None:
        response = "Manual Entry"        
    while response not in ["Manual Entry","Done","ME","D"]:
        print(row["original_word"])
        possible_meanings = row.likely_meanings.split(",")
        for y, meaning in enumerate(possible_meanings):
            print(y, wn.synset(meaning.replace("?","")).definition())
        response = get_specific_input(
            text="""Input the number for the correct meaning or 
            either Context (C) or Full Details (FD) for more information 
            or Manual Entry (ME) to ignore the definitions provided
            and give your own related words or Done (D).""",
            options=[str(x) for x in list(
            range(len(meaning)))] + ["Context", "Full Details","Done",
            "Manual Entry","C","FD","D","ME"])
        print(response)
        if response.isnumeric():
            unique_selected_words_df.loc[i,"accepted_meanings"].extend([
                wn.synset(possible_meanings[int(response)].replace(
                    "?",""))]
            ) 
    if response in ["Manual Entry","ME"]:
        original_word = row["original_word"]
        related_words = input(f"Enter related words to {original_word} " +
            "(with a space between them):\n")
        from nltk.tokenize import word_tokenize
        unique_selected_words_df.loc[i,"related_words"].extend(["user_entered",word_tokenize(related_words)])

        unique_selected_words_df["accepted_meanings"]
    
    print(unique_selected_words_df.loc[i,"accepted_meanings"])
    print(unique_selected_words_df.loc[i,"related_words"])

    export_unique_selected_words_df = unique_selected_words_df.copy()
    export_unique_selected_words_df["accepted_meanings"] = export_unique_selected_words_df["accepted_meanings"].astype("str")

    export_unique_selected_words_df.to_pickle("related_words.pkl")


# getting meanings to work with if it only has manually entered information
for i, row in export_unique_selected_words_df[export_unique_selected_words_df[
        "accepted_meanings"].apply(lambda x: len(x) == 0)].iterrows():
    # row["related_words"]
    # export_unique_selected_words_df.at[i,"likely_meanings"] = 
    # 
    # row["likely_meanings"] = wn.synsets("alright")[1:]
    
    def find_core_meaning_v1(word,related_words,likely_meanings):
        if len(likely_meanings) > 0:
            ####### if there are likely meanings
            # find the related words' possible meanings
            related_possible_definition_pairs = []
            related_possible_definitions = []
            all_related_possible_definitions = []
            for r_word in related_words:
                meanings_of_r_word = wn.synsets(r_word)
                related_possible_definitions.append(meanings_of_r_word)
                all_related_possible_definitions += meanings_of_r_word

            # try to find a main meaning by association
            probable_meanings = []
            for meaning in likely_meanings:
                if meaning in all_related_possible_definitions:
                    probable_meanings.append(meaning)

            # if one was found, that's it
            if len(probable_meanings) > 0:
                return probable_meanings
            else:
                dictionary = {}
                for item in [str(x) for x in all_related_possible_definitions]:
                    if dictionary.get(item) == None:
                        dictionary[item] = 1
                    else:
                        dictionary[item] += 1
                good_options = [i for i in dictionary.items() if i[1] > 1]
                if len(good_options) > 1:
                    return good_options
                all_rel_df = pd.DataFrame([[x] + str(x).rsplit(".",2) for x in all_related_possible_definitions],columns=["meaning","word","pos","value"])
                all_rel_df["value"] = all_rel_df["value"].apply(lambda x: x.replace("')",""))
                all_rel_df["word"] = all_rel_df["word"].apply(lambda x: x.replace("Synset('",""))
                
                test_limited = all_rel_df[(all_rel_df["value"] == "01") & (all_rel_df["word"].isin(related_words))]
                if len(test_limited) > 0:
                    return test_limited["meaning"].to_list()
                    # nouns only???
                
                1/0
                
                
                1/0
                
                    # related_possible_definitions_duplicate = related_possible_definitions.copy()
                    # one_grouping = related_possible_definitions_duplicate.pop()
                    # # ic = nltk.corpus.wordnet_ic.ic("ic-brown.dat")

                    # # nltk.download('wordnet_ic')
                    # grouping_evaluation = []
                    # for meaning in one_grouping:
                    #     for meaning_group in related_possible_definitions:
                    #         for other_meaning in meaning_group:
                    #             print(other_meaning)
                    #             print(other_meaning.definition())
                    #             if meaning.pos() == other_meaning.pos():
                    #                 # grouping_evaluation.append([other_meaning,meaning.lch_similarity(other_meaning)])
                    #                 print(meaning.wup_similarity(other_meaning))
                    #                 print(meaning.path_similarity(other_meaning))
                    #                 # help(meaning)
                    #                 print(meaning.lowest_common_hypernyms(other_meaning))
                    #                 # meaning.res_similarity(other_meaning,ic)
                    #                 help(other_meaning)
                    

                            
                    

            
    likely_meanings = [wn.synset(x.replace("?","")) for x in row["likely_meanings"].split(",")]
    related_words = row["related_words"]
    find_core_meaning_v1(row["lemma"],related_words,likely_meanings)
    # export_unique_selected_words_df.at[i,"accepted_meanings"] = find_core_meaning_v1(row["lemma"],related_words,likely_meanings)
    # if len(accepted_meanings) == 0:
    #     export_unique_selected_words_df.at[i,"accepted_meanings"].append(find_core_meaning_v1(word,related_words,row["likely_meanings"]))

    #     # print(related_possible_definition_pairs)
        # df_related = pd.DataFrame(related_possible_definition_pairs)
        # df_related["possible_meaning_count"] = df_related[1].apply(lambda x: len(x))

    if len(accepted_meanings) == 0:
        find_meanings([row["lemma"]] + related_words)


    
        
    find_meaning("good",["okay","alright"])
    break
    if accepted_meanings < 0:
        
    row["related_words"]
    break
# [meaning.definition() for meaning in wn.synsets("naive")]

# getting related words part 1
for i, row in unique_selected_words_df[
    unique_selected_words_df["related_words"].apply(lambda x: len(x) < 3)
    ].iterrows():
    for meaning in row["accepted_meanings"]:
        get_related_words(unique_selected_words_df,i,row,meaning)



/specific meanings and antonyms


# round two, expanding from round 1
for i, row in unique_selected_words_df[
    unique_selected_words_df["related_words"].apply(lambda x: len(x) < 5)
    ].iterrows():
    for meaning in row["related_words"]:
        print(meaning)
        



        wup_similarity
        lin_similarity
        lch_similarity
        jcn_similarity
        




        res_similarity



# getting antonyms

