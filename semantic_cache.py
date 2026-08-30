import json
import numpy as np
from openai import OpenAI
from config.settings import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    # using this function since sklearn cosine similarity requires 2D vector array

    va, vb = np.array(a) , np.array(b)
    return float(np.dot(va,vb)/(np.linalg.norm(a) * np.linalg.norm(b)))


def embed(text: str) -> list[float]:
    """call OpenAI embeddings API
    return the embedding vector
    """
    response = client.embeddings.create(
        input=text, model="text-embedding-3-small"
    )
    return (response.data[0].embedding)

def get(query: str, redis_client) -> str | None:
    # 1. embed the query
    # 2. get all stored entries from Redis
    # 3. for each entry, calculate cosine similarity
    # 4. if similarity above threshold, return stored response
    # 5. otherwise return None
    ...
    embedded_query = embed(query)

    # load all stored entries from Redis
    redis_data = redis_client.lrange("nova:cache",0,-1)     # this function retrives data using (key,start,stop) where -1 means last element
    for i in redis_data:
        entry = json.loads(i)
        similarity = cosine_similarity(entry["embeddings"],embedded_query)
        if similarity>0.9:
            return entry["response"]
    return None


def set(query: str, response: str, redis_client) -> None:
    # 1. embed the query
    # 2. store embedding + response in Redis as JSON
    embedded_query = embed(query)
    entry = json.dumps({
        "embeddings":embedded_query,
        "response":response
    })
    redis_client.rpush("nova:cache",entry)


