# Nova

A LangGraph agent that turns a natural-language question into a SQL query, runs it, and answers in plain English.

## How it works

1. `input_validator` rejects empty, too-short, too-long, or non-string input, then runs `prompt_guard` (keyword blocklist plus an LLM check) against injection attempts.
2. `semantic_cache.get` checks Redis for a near-duplicate question (cosine similarity > 0.9) and returns the cached answer if found.
3. Otherwise the LangGraph graph in `builder.py` runs:
   - `intent_router` classifies the query as `sql_agent` or `need_clarification`. Below 0.9 confidence, or an ambiguous query, routes to `clarify_agent`.
   - `sql_agent` retrieves the top-3 matching tables from the Redis schema index (`rag/schema_retriever.py`) and asks the LLM for a SELECT-only query.
   - `validation_agent` rejects DROP/DELETE/TRUNCATE outright, then asks the LLM whether the query is semantically aligned with the question and actually uses the retrieved schema.
   - `execute_agent` runs the query against the configured database.
   - `result_validator_agent` asks the LLM whether the returned rows actually answer the question.
   - On failure, the graph retries `sql_agent` up to `retry_count` times before falling back to `escalate_agent`.
   - `response_agent` turns the row output into a conversational reply.
4. The reply is cached in Redis and appended to the session's conversation history.

State is a single `NovaState` TypedDict (`graph/state.py`) threaded through every node. Postgres (`PostgresSaver`) checkpoints graph state per `thread_id`.

## Layout

- `main.py` — entry point, Redis wiring, request handling (`handle_query`)
- `builder.py` — graph definition (nodes and edges)
- `graph/` — `state.py` (the TypedDict) and `edges.py` (routing logic)
- `agents/` — one file per node
- `rag/` — schema embedding and retrieval
- `security/` — prompt injection checks
- `api/input_validator.py` — request-level input checks
- `semantic_cache.py` — Redis-backed embedding cache (get/set)
- `scripts/seed_schema.py` — loads `schema.json` into the Redis schema index

## Setup

Requires Redis and Postgres running, plus an OpenAI API key.

```
CHECKPOINT_DB_URL=postgresql://...   # .env
```

`config.settings.get_settings()` and `db.connection.get_engine()` are imported by `builder.py`, `semantic_cache.py`, and `agents/execute.py` but don't exist in this repo yet — add them before running anything. `settings.py` at the repo root is a stub and isn't the module actually imported.

There's no `requirements.txt` yet. At minimum you'll need `langgraph`, `langchain-openai`, `langgraph-checkpoint-postgres`, `redis`, `sqlalchemy`, `numpy`, and `openai`.

To seed the schema index before first use:

```
python scripts/seed_schema.py
```

Fill in `schema.json` with your actual tables first, it ships as a single empty placeholder entry.

## Testing

```
pytest tests/
```

Only `agents/validation_agent.py`'s `allowed_statements` has a test right now.

## Known issues

- `main.py` generates a fresh `session_id` (and empty history) on every call to `handle_query`, so conversation history and Postgres checkpointing per thread never actually accumulate across turns.
- `rag/schema_retriever.py` filters candidates with `similarity_scores["score"]`, which doesn't exist (it's a dict of dicts keyed by table name), so this raises a `KeyError` whenever it runs.
- `semantic_cache.get` returns `None` implicitly instead of after checking every entry, so it can bail out on the first low-similarity result even when a later entry would match.
