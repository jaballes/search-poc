import json
import datetime
import numpy as np
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

SERVER_URL = "http://localhost:9200"
#INDEX_NAME = "products_market"
INDEX_NAME = "home_kitchen"

# METADATA_PATH = "metadata_us_Grocery_and_Gourmet_Food.json"
METADATA_PATH = "metadata_us_Home_and_Kitchen.json"

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def normalize_data(data):
    return data / np.linalg.norm(data, ord=2)


def load_file(file_path):
    try:
        json_objects = []
        with open(file_path, "r") as json_file:
            for line in json_file:
                data = json.loads(line)
                if type(data) is list:
                    for element in data:
                        if "imgUrl" in element and type(element["imgUrl"]) is not list:
                            imgUrl = list(json.loads(element["imgUrl"]).keys())[0]
                            element["imgUrl"] = imgUrl
                            json_objects.append(element)
                elif "imgUrl" in data and type(data["imgUrl"]) is not list:
                    imgUrl = list(json.loads(data["imgUrl"]).keys())[0]
                    data["imgUrl"] = imgUrl
                    json_objects.append(data)
        print("Done")
    finally:
        json_file.close()
    return json_objects


def get_client(server_url: str) -> Elasticsearch:
    es_client_instance = Elasticsearch(request_timeout=600, hosts=server_url)
    print("ES connected")
    print(datetime.datetime.now())
    return es_client_instance


def create_index(index_name: str, es_client: Elasticsearch, metadata: np):
    if es_client.indices.exists(index=index_name):
        delete_index(index_name, es_client)
    mapping = {
        "mappings": {
            "properties": {
                "asin": {
                    "type": "keyword"
                },
                "description_vector": {
                    "type": "dense_vector",
                    "dims": get_vector_dimension(metadata),
                    "index": True,
                    "similarity": "cosine"
                },
                "item_image": {
                    "type": "keyword",
                },
                "text_field": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword_field": {
                            "type": "keyword"
                        }
                    }
                }
            }
        },
        "settings": {
            "index": {
                "number_of_shards": "1",
                "number_of_replicas": "0"
            }
        }

    }
    es_client.indices.create(index=index_name, mappings=mapping["mappings"], settings=mapping["settings"])


def delete_index(index_name: str, es_client: Elasticsearch):
    es_client.indices.delete(index=index_name)


def get_vector_dimension(metadata: list):
    title = metadata[0]["title"]
    embeddings = model.encode(title)
    return len(embeddings)


def store_index(index_name: str, data: np.array, metadata: list, es_client: Elasticsearch):
    actions = []
    for index_num, vector in enumerate(data):
        metadata_line = metadata[index_num]
        text_field = metadata_line["title"]
        embedding = model.encode(text_field)
        norm_text_vector_np = normalize_data(embedding)
        action = {"index": {"_index": index_name, "_id": index_num}}
        document = {
            "asin": metadata_line["asin"],
            "description_vector": norm_text_vector_np.tolist(),
            "item_image": metadata_line["imgUrl"],
            "text_field": text_field
        }
        actions.append(action)
        actions.append(document)
        if index_num % 1000 == 0 or index_num == len(data):
            es_client.bulk(index=index_name, operations=actions)
            actions = []
            print(f"bulk {index_num} indexed successfully")
            es_client.indices.refresh(index=index_name)

    es_client.indices.refresh(index=index_name)


def main():
    es_client = get_client(SERVER_URL)
    metadata = load_file(METADATA_PATH)
    create_index(INDEX_NAME, es_client, metadata)
    store_index(INDEX_NAME, metadata, metadata, es_client)


if __name__ == "__main__":
    main()
