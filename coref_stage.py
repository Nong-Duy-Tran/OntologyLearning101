import nltk
import spacy
from fastcoref import FCoref

PRONOUNS = ['he', 'him', 'his', 'she', 'her', 'hers', 'they', 'them', 'their', 'theirs', 'i', 'my', 'mine', 'me', 'you', 'your', 'yours', 'it', 'its']

def list_to_dict_count(list1):
    """Returns a dictionary with unique elements of the given list as keys and their count of occurrence as values.

    Args:
        list1: A Python list.

    Returns:
        A Python dictionary.
    """

    dict1 = {}
    for element in list1:
        if element in dict1:
            dict1[element] += 1
        else:
            dict1[element] = 1
    dict1 = sorted(dict1, reverse= False)
    return dict1


def Coref(path, name = ''):
    with open(path, 'r', encoding='utf8') as file:
        txt = file.read()
        # print(txt)
        # print()
        file.close()

    normal_sentence = nltk.sent_tokenize(txt)
    text = ' '.join(normal_sentence)
    print('text:\n', text)

    FCorefmodel = FCoref(device='cuda:0')

    pred1 = FCorefmodel.predict(texts=text)

    FCoref_terms_stringtype = pred1.get_clusters(as_strings=True)
    FCoref_terms_indextype = pred1.get_clusters(as_strings=False)

    # print(FCoref_terms_stringtype)
    
    terms = []
    start_inds = []
    cluster_inds = []
    end_inds = []

    for i, cluster in enumerate(FCoref_terms_stringtype):
        for j, term in enumerate(cluster):
            terms.append(term)
            cluster_inds.append(i)
            start_inds.append(FCoref_terms_indextype[i][j][0])
            end_inds.append(FCoref_terms_indextype[i][j][1])

    coref_output = list(zip(start_inds, end_inds, terms, cluster_inds))
    sorted_coref_output = sorted(coref_output, key = lambda x: x[0])
    # print(sorted_coref_output[0])


    # find indeces of sentences
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    doc_sentences = []
    start_chars = []
    end_chars = []
    for sent in doc.sents:
        doc_sentences.append(sent.text)
        start_chars.append(sent.start_char)
        end_chars.append(sent.end_char)
        # print(sent.text, sent.start_char, sent.end_char)

    # print('Doc sentence:', doc_sentences)
    sent_inds = list(zip(start_chars, end_chars, doc_sentences))
    # print('sent_index: ', sent_inds[1])


    # find representative
    # preprocessing: normalize letters, remove common pronouns and those containing common pronouns
    # rank elements by their frequencies
    # choose those of highest frequency AND shortest in length (some are too long)
    cluster_representatives = []
    for i, cluster in enumerate(FCoref_terms_stringtype):
        # print(cluster)
        cluster_terms = [term.lower() for term in cluster]
        removeables = []
        # a good way of checking containment of pronouns is using .split, because history also has his
        for j, term in enumerate(cluster_terms):
            for pronoun in PRONOUNS:
                if pronoun == term:
                    removeables.append(j)
                    break
        cluster = [cluster[i] for i in range(len(cluster)) if i not in removeables]
        cluster_term_count = list_to_dict_count(cluster)
        print(cluster_term_count)
        if len(cluster_term_count) > 0:
            cluster_representatives.append(cluster_term_count[0])

        else:
            cluster_representatives.append('entity')
        # print(cluster)
        # print(cluster_representatives[i])


    # replace per sentence
    # sai lam lon, viet lai sau

    # re-arrange the sorted_coref_output
    # if one term contains the other, ignore the child term
    ignoreable_coref = []
    for i in range(len(sorted_coref_output)):
        for j in range(i + 1, len(sorted_coref_output)):
            if sorted_coref_output[i][0] <= sorted_coref_output[j][0] and sorted_coref_output[i][1] >= sorted_coref_output[j][1]:
                ignoreable_coref.append(j)
            # very rough if-else case, look back on "As a leader of the progressive movement" sentence
            elif sorted_coref_output[j][0] <= sorted_coref_output[i][0] and sorted_coref_output[j][1] >= sorted_coref_output[i][1]:
                ignoreable_coref.append(i)

    new_sorted_coref_output = [sorted_coref_output[i] for i in range(len(sorted_coref_output)) if i not in ignoreable_coref]
    # print('ignoreable coref:', ignoreable_coref, '\n')
    # print('sorted coref output:', sorted_coref_output, '\n')
    # print('new sorted coref:', new_sorted_coref_output, '\n')


    start_term_index = 0
    output_sents = []
    for sent in sent_inds:
        print('SENTENCE:', sent, '\n')
        if start_term_index >= len(new_sorted_coref_output):
            output_sents.append(sent[2])
            continue

        terms_in_sent = []
        for i in range(start_term_index, len(new_sorted_coref_output)):
            if new_sorted_coref_output[i][0] >= sent[0] and new_sorted_coref_output[i][0] <= sent[1]:
                terms_in_sent.append(new_sorted_coref_output[i])
                start_term_index += 1
            else:
                break

        output_sent = ""

        if len(terms_in_sent) > 0:
            # we can imagine the merging process as sent_chunk[i] + terms_in_sent[i] + sent_chunk[i + 1]
            # because chunks are always 1 more than terms, we can repeat + terms_in_sent[i] + sent_chunk[i + 1]
            
            for i, term in enumerate(terms_in_sent):
                if i == 0:
                    output_sent += (text[(sent[0]): (term[0])])
                    
                    # print(output_sent)
                else:
                    # where the "initials, TR" error occurs, happens because the term contains another term
                    output_sent += (text[terms_in_sent[i - 1][1] + 1: term[0]])
                    # print((text[terms_in_sent[i - 1][1] + 1: term[0]]))
                    output_sent += ''
                output_sent += (cluster_representatives[term[3]]) + ' '
                # print((cluster_representatives[term[3]]) + ' ')
                output_sent += ''
            output_sent += (text[terms_in_sent[-1][1] + 1: sent[1]])
        else:
            output_sent += (sent[2])
        output_sents.append(output_sent)

    return output_sents

    

