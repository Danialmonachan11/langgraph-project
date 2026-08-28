import json
from semantic_cache import get, embed, cosine_similarity
from main import schema_cache


# define the function to retrieve the relevant tables using cosine similarity
def retrieve_schema(query, redis_client, top_k=3):
    embedded_query = embed(query)

    # define a dict which will store the table:sim. scores 
    similarity_scores={}

    # load all stored entries from Redis
    redis_data = schema_cache     
    for i in redis_data:
        entry = json.loads(i)
        similarity = cosine_similarity(entry["embeddings"],embedded_query)
        similarity_scores[entry["table"]]={"score":similarity,
                                           "text":entry["text_representation"]}

    sorted_tables = sorted(similarity_scores,key=lambda x: similarity_scores[x]["score"],reverse=True)
    return "\n\n".join([similarity_scores[t]["text"] for t in sorted_tables[:top_k] if similarity_scores["score"]>0.6])    

