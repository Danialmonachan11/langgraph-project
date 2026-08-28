import json
from openai import OpenAI
from semantic_cache import embed
from main import redis_client

# define function which will index the table description - one table - one embedding
def index_schema(tables, redis_client)->None:
    # since the tables are in list of dict format, we need to make it in text representation
    for t in tables:
        table_text_representation = [f"table:{t['table']},description:{t['description']},columns:{t['columns']}"]

        # now embed the text representation
        embedded_tables=embed(table_text_representation)

        # store both the original table definitions list along with embeddings because we will be needing the original one to put in the prompt
        entry = json.dumps({
            "table":t["table"],
            "text_representation":table_text_representation,
            "embeddings": embedded_tables
        })

        # push the embeddings to the redis
        redis_client.rpush("nova:schema",entry)
