# import re
import re
import pandas as pd
import bs4
import requests
import spacy
from spacy import displacy

nlp = spacy.load('en_core_web_sm')

from spacy.matcher import Matcher
from spacy.tokens import Span

import networkx as nx

import matplotlib.pyplot as plt
from tqdm import tqdm

pd.set_option('display.max_colwidth', 200)
# %matplotlib inline

# import wikipedia sentences
candidate_sentences = pd.read_csv("wiki_sentences_v2.csv")
candidate_sentences.shape
#
candidate_sentences['sentence'].sample(5)
#
# doc = nlp("the drawdown process is governed by astm standard d823")

# for tok in doc:
# print(tok.text, "...", tok.dep_)


#
def get_entities(sent):
    ## chunk 1
    ent1 = ""
    ent2 = ""

    prv_tok_dep = ""  # dependency tag of previous token in the sentence
    prv_tok_text = ""  # previous token in the sentence

    prefix = ""
    modifier = ""

    #############################################################

    for tok in nlp(sent):
        ## chunk 2
        # nếu token là một dấu chấm câu thì chuyển sang token tiếp theo
        if tok.dep_ != "punct":
            # check: token có phải là một từ ghép hay không
            if tok.dep_ == "compound":
                prefix = tok.text
                # nếu từ trước đó cũng là một 'từ ghép' thì hãy thêm từ hiện tại vào nó
                if prv_tok_dep == "compound":
                    prefix = prv_tok_text + " " + tok.text

            # check: token là một bổ ngữ hay không
            if tok.dep_.endswith("mod") == True:
                modifier = tok.text
                # nếu từ trước đó cũng là một 'từ ghép' thì hãy thêm từ hiện tại vào nó
                if prv_tok_dep == "compound":
                    modifier = prv_tok_text + " " + tok.text

            ## chunk 3
            if tok.dep_.find("subj") == True:
                ent1 = modifier + " " + prefix + " " + tok.text
                prefix = ""
                modifier = ""
                prv_tok_dep = ""
                prv_tok_text = ""

            ## chunk 4
            if tok.dep_.find("obj") == True:
                ent2 = modifier + " " + prefix + " " + tok.text

            ## chunk 5
            # update variables
            prv_tok_dep = tok.dep_
            prv_tok_text = tok.text
    #############################################################

    return [ent1.strip(), ent2.strip()]


#
get_entities("the film had 200 patents")
#
entity_pairs = []

for i in tqdm(candidate_sentences["sentence"]):
    entity_pairs.append(get_entities(i))

entity_pairs[10:20]


def get_relation(sent):

    doc = nlp(sent)

    # Matcher class object
    matcher = Matcher(nlp.vocab)

    #define the pattern
    pattern = [[{
        'DEP': 'ROOT'
    }, {
        'DEP': 'prep',
        'OP': "?"
    }, {
        'DEP': 'agent',
        'OP': "?"
    }, {
        'POS': 'ADJ',
        'OP': "?"
    }]]

    matcher.add("matching_1", patterns = pattern)

    matches = matcher(doc)
    k = len(matches) - 1  #if len(matches) >= 1 else 1
    # print("matches: ", matches)
    # print("type(matches): ", type(matches))
    # print("len(matches): ", len(matches))
    # print("k: ", k)
    
    tmpSpan = ""
    if len(matches) >= 1:
      span = doc[matches[k][1]:matches[k][2]]
      tmpSpan = span.text
      # print("span: ", span.text)
      # print("type(span): ", type(span.text))
      # print("---")
    # else:
    #   span = doc[].text = ""

    # return (span.text)
    return(tmpSpan)


# get_relation("John completed the task")

relations = [get_relation(i) for i in tqdm(candidate_sentences['sentence'])]

pd.Series(relations).value_counts()[:50]

# extract subject
source = [i[0] for i in entity_pairs]

# extract object
target = [i[1] for i in entity_pairs]

# print('source', len(source))
# print('target', len(target))
# print('edge', len(relations))

kg_df = pd.DataFrame({'source': source, 'target': target, 'edge': relations})

# create a directed-graph from a dataframe
# G = nx.from_pandas_edgelist(kg_df,
#                             "source",
#                             "target",
#                             edge_attr=True,
#                             create_using=nx.MultiDiGraph())

# plt.figure(figsize=(12,12))

# pos = nx.spring_layout(G)
# nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos = pos)
# plt.show()

G = nx.from_pandas_edgelist(kg_df[kg_df['edge'] == "composed by"],
                            "source",
                            "target",
                            edge_attr=True,
                            create_using=nx.MultiDiGraph())

plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G, k=0.5)  # k regulates the distance between nodes
nx.draw(G,
        with_labels=True,
        node_color='skyblue',
        node_size=1500,
        edge_cmap=plt.cm.Blues,
        pos=pos)
plt.show()