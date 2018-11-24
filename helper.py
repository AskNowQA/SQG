import json
import pickle
import requests


# Load Files


def load_json(path):
    with open(path) as data_file:
        return json.load(data_file)


def load_txt(name):
    with open(name) as data_file:
        data = data_file.readlines()
    data = [d.replace("\n", "") for d in data]
    return data


def load_pickle(path):
    with open(path) as data_file:
        return pickle.load(data_file)


# Save Files


def save_json(data, name):
    with open(name, "w") as data_file:
        json.dump(data, data_file, sort_keys=True, indent=4, separators=(',', ': '))


# runs a sparql query on a target endpoint
def query(q, bonn=False):
    payload = (
        ('query', q),
        ('format', 'application/json'))
    try:
        if not bonn:
            r = requests.get("http://dbpedia.org/sparql", params=payload, timeout=60)
        else:
            r = requests.get("http://131.220.9.219/sparql", params=payload, timeout=60, auth=('sda01dbpedia', 'softrock'))
    except:
        return 0, None

    return r.status_code, r.json() if r.status_code == 200 else None