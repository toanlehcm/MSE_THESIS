import os
import requests
import json
from data_normalizer import normalize

NER_MODEL_BERT = "phobert_large"
NER_MODEL_BILSTM = "BiLSTM"
NER_MODEL_BILSTM_CRF = "BiLSTM+CRF"
INTENT_MODEL_ONE_VS_REST = "onevsrest"


def handle_get_entities(text):
    """
  It takes a text, extracts entities from it, and returns a list of entities

  :param text: The text to be processed
  :return: A list of entities
  """
    entities_raw = extract_ner(text)
    _, entities = ner_postprocess(entities_raw)
    return entities


def extract_ner(text, model=NER_MODEL_BERT):
    """
    Input Arguments:
        - text : the sentence which will be extracted NER
    """
    ner_service_url = os.getenv("NER_SERVICE_URL",
                                default="http://localhost:8001/api/v1/ner")

    data = {'model': model, 'text': text}

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    r = requests.post(ner_service_url, data=json.dumps(data), headers=headers)

    return r.json()


def ner_postprocess(entities_raw):
    """Postprocess for NER: 
    1. normalize values
    2. only accept the related information with previous question

    Args:
        entities_raw (Dict): result of NER service

    Returns:
        Dict, Dict: raw and normalized entities
    """
    entities_normed = dict()
    entities_raw_out = dict()

    for entity in entities_raw:
        key = entity['label']
        if key == 'O': continue

        value_raw = entity['content']
        if key not in entities_raw_out.keys():
            entities_raw_out[key] = [value_raw]
        else:
            entities_raw_out[key].append(value_raw)

        value_normed = normalize(value_raw, key)
        if key not in entities_normed.keys():
            entities_normed[key] = [value_normed]
        else:
            entities_normed[key].append(value_normed)

    return entities_raw_out, entities_normed