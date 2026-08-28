import redis
import json
from rag.schema_indexer import index_schema

redis_client = redis.Redis()

# load schema once at module level - this will be in structure [{'table':"","text":"","embeddings":""}]
with open("schema.json", "r") as f:
    schema_context = json.load(f)
    index_schema(schema_context,redis_client)


