from flair.data import Sentence
from flair.nn import Classifier
import spacy
import pandas as pd



tagger = Classifier.load('ner')
nlp = spacy.load("en_core_web_sm")

def FlairNER(sentences):
    entities = []
    ent_start_char = []
    ent_end_char = []
    labels = []
    confidence = []
    for setence in sentences:
        sentence = Sentence(setence)

        # run NER over sentence
        tagger.predict(sentence)

        # print the sentence with all annotations
        # print(sentence.to_dict()['entities'])
        for element in sentence.to_dict()['entities']:
            print('1', list(element.values()))
            text, start_pos, end_pos, ner_labels = list(element.values())
            ner_labels = ner_labels[0]
            entities.append(text)
            ent_start_char.append(start_pos)
            ent_end_char.append(end_pos)
            labels.append(ner_labels['value'])
            confidence.append(ner_labels['confidence'])

            print(labels)
    
    df = pd.DataFrame(list(zip(entities, ent_start_char, ent_end_char, labels, confidence)), columns= ['Entity', 'Start Index', 'End Index', 'Label', 'Confidence']).drop_duplicates(subset=['Entity', 'Label'])
    df.reset_index(inplace=True)
    df.drop(columns='index', inplace=True)
    return df
    # df.to_excel('Ner_xlsx/Oshumed_NER.xlsx')

def SpacyNER(lines:list):
    entities = []
    ent_start_char = []
    ent_end_char = []
    labels = []

    for line in lines:
        doc = nlp(line)
        for ent in doc.ents:
            entities.append(ent.text)
            ent_start_char.append(ent.start_char)
            ent_end_char.append(ent.end_char)
            labels.append(ent.label_)
    
    df = pd.DataFrame(list(zip(entities, ent_start_char, ent_end_char, labels)), columns= ['Entity', 'Start Index', 'End Index', 'Label']).drop_duplicates(subset=['Entity', 'Label'])
    df.reset_index(inplace=True)
    df.drop(columns='index', inplace=True)
    return df
    # df.to_excel('Ner_xlsx/Oshumed_NER.xlsx')