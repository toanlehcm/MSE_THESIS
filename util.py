import json


def get_concepts(text):
    """
  It takes a string of text and returns a dictionary of concepts and their aliases

  :param text: The text to be analyzed
  :return: A dictionary of concepts and their aliases.
  """
    with open('data/intent_alias_data.json', encoding="utf8") as f:
        intent_alias_data = json.load(f)

    out = {}
    for concept in intent_alias_data:
        for alias in sorted(intent_alias_data[concept], key=len, reverse=1):
            if alias in text:
                out[concept] = alias
                break
    return out


def get_match_relation(concept_key_list):
    """
  It takes a list of concept keys and returns a list of match relations between those concepts

  :param concept_key_list: a list of concept keys
  :return: A list of match relations between the concepts in the concept_key_list
  """
    with open('data/match_relation_dict.json', encoding="utf8") as f:
        match_relation_dict = json.load(f)

    match_relation_out = []
    for start_node in match_relation_dict:
        if start_node in concept_key_list:
            for end_node in match_relation_dict[start_node]:
                if end_node in concept_key_list:
                    match_relation_out.append(
                        match_relation_dict[start_node][end_node])

    return match_relation_out
