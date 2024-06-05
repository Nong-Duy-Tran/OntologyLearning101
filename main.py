from coref_stage import Coref
from TermsExtractor import extractor
from NER import FlairNER, SpacyNER
from nltk import StanfordPOSTagger, word_tokenize
from CreateRDF import generator
from openie import StanfordOpenIE
import pandas as pd
import os
import spacy

# 1082 3790 3353 2509 1460

nlp = spacy.load('en_core_web_lg')

# Your java path
# Dont know where? just google it
os.environ["JAVAHOME"] = "C:/Program Files/Java/jre1.8.0_361/bin/java.exe"

JAR = 'C-Value-Term-Extraction-master/stanford-postagger-2017-06-09/stanford-postagger-2017-06-09/stanford-postagger.jar'
TAG_MODEL = 'C-Value-Term-Extraction-master/stanford-postagger-2017-06-09/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger'

TAGGER = StanfordPOSTagger(TAG_MODEL, JAR, encoding = "utf-8")

current_dir = os.getcwd().replace('\\', '/')
wiki_dir_path = current_dir + '/test_wiki'
wiki_dir_list = dir_list = os.listdir(wiki_dir_path)

file_name_list = []
for file_name in wiki_dir_list:
    file_name_list.append(file_name.split('.txt')[0])

# for name in file_name_list:

for file_name in file_name_list:
    temp_dir = f"Extraction/{file_name}/"
    if (os.path.exists(temp_dir) == False):
        os.mkdir(temp_dir)

for file_name in file_name_list:
    print('File Name: ' + file_name)

    temp_dir = f"Extraction/{file_name}/"

    new_txt = Coref(f'Wiki_dataset/{file_name}.txt')

    text_path = temp_dir + f"{file_name}.txt"
    # print('new text: ', new_txt)
    with open(text_path, 'w', encoding='utf8') as file:
        for line in new_txt:
            line = line.strip()
            if (line[-1] != '.'):
                line += '.'
            file.write(line + '\n')
        file.close()


    properties = {
        'openie.affinity_probability_cap': 1/5,
    }

    txt = open(text_path, 'r', encoding='utf8').read()
    txt = ' '.join(txt.splitlines())

    # print(txt)

    with StanfordOpenIE(properties=properties) as client:
        result = client.annotate(txt)
        # print(result)
        unfiltered_relation = pd.DataFrame.from_dict(result).sort_values(by=['object'])
        # graph_image = 'graph.png'
        # client.generate_graphviz_graph(txt, graph_image)
        # print('Graph generated: %s.' % graph_image)

        print('Finished relation extraction\n')

    # list các câu sau khi được coref
    sentences = []

    with open(text_path, 'r', encoding='utf8') as file:
        line = file.readline()
        while (line != ''):
            line = line.strip('\n')
            print('line in new text:', line)
            sentences.append(line)

            line = file.readline()
        
        sentencesTokenized = [word_tokenize(sentence) for sentence in sentences]
        # print(sentencesTokenized)

        file.close()

    tagged_sentences = TAGGER.tag_sents(sentencesTokenized)
    # print(tagged_sentences)

    tagged_text = ''
    for tagged_sentence in tagged_sentences:
        tagged_words = []
        for word, tag in tagged_sentence:
            tagged_words.append(f"{word}_{tag}")
        tagged_sentence_str = " ".join(tagged_words)
        tagged_text += tagged_sentence_str + ' '

    tagged_text = [tagged_text]

    term_list1 = extractor(tagged_text, 'Noun', 3, 2, 2)
    term_list2 = extractor(tagged_text, 'AdjNoun', 3, 2, 2)
    term_list3 = extractor(tagged_text, 'AdjPrepNoun', 3, 2, 2)

    final_term_list = pd.concat([term_list1, term_list2, term_list3], ignore_index=True).drop_duplicates(subset='Term')

    ner_df = SpacyNER(sentences)

    ner_df = ner_df.loc[(ner_df['Label'] == 'PERSON') |
                        (ner_df['Label'] == 'FAC') |
                        (ner_df['Label'] == 'NORP') |
                        (ner_df['Label'] == 'GPE') |
                        (ner_df['Label'] == 'LOC') |
                        (ner_df['Label'] == 'ORG')]


    terms = final_term_list['Term'].values.tolist() + ner_df['Entity'].values.tolist()
    # print(terms)

    filtered_rows = []
    for i in range(len(unfiltered_relation.index)):
        row = unfiltered_relation.iloc[i]
        for term in terms:
            if ((term == row['subject']) and (term == row['object']) or (term == row['object'])):
                # print(row)
                filtered_rows.append(row)
                break

    index = 0
    # while index < range(len(filtered_rows)):
    #     row = filtered_rows[index]
    #     temp_sentence = row['subject'] + ' ' + row['relation'] + ' ' + row['object']
    #     index +=

    filtered_rows_range = len(filtered_rows)
    i_index = 0
    while(i_index < filtered_rows_range):
        i_row = filtered_rows[i_index]
        i_sentence = i_row['subject'] + ' ' + i_row['relation'] + ' ' + i_row['object']
        # print('i sentence:', i_sentence)
        j_index = i_index + 1
        while j_index < filtered_rows_range:
            j_row = filtered_rows[j_index]
            j_sentence = j_row['subject'] + ' ' + j_row['relation'] + ' ' + j_row['object']
            # print('\tj sentence:', j_sentence)
            if (nlp(i_sentence).similarity(nlp(j_sentence)) > 0.8):
                del filtered_rows[j_index]
                filtered_rows_range -= 1
                continue

            j_index += 1
        print('Process detecting relation similarity: ', int((i_index/filtered_rows_range)*100), '%', sep='')
        i_index += 1
            
    print('Process detecting relation similarity: 100%')

    # for row in filtered_rows:
    #     temp_sentence = row['subject'] + ' ' + row['relation'] + ' ' + row['object']
    #     if index < 10:
    #         print(temp_sentence)
        
    #     else :
    #         break
    #     index += 1


    final_relation = pd.DataFrame(filtered_rows).sort_values(by=['object'])

    # for i in range(len(final_relation)):
        


    # for i in range(len(ner_df)):
    #     row = ner_df.iloc[i]
    #     temp = pd.DataFrame([{'subject': row['Label'], 'relation':'include', 'object':row['Entity']}])   
    #     final_relation = pd.concat([temp, final_relation])


    excel_path = temp_dir + file_name
    final_relation.drop_duplicates().reset_index(drop=True).to_excel(excel_path + '_SVO.xlsx')

    ner_df.drop_duplicates(['Entity']).reset_index(drop=True).to_excel(excel_path + '_NER.xlsx')

    final_term_list.reset_index(drop=True).to_excel(excel_path + '_terms.xlsx')

    generator(f'{file_name}_wiki', final_relation, ner_df, final_term_list)

    print(f'\n\nDone {file_name}')