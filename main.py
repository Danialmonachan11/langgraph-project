import uuid
import json
from graph.builder import graph, checkpointer
from graph.state import NovaState
from semantic_cache import get, set
import redis
from api.input_validator import validate_input

redis_client = redis.Redis()


# ── startup ───────────────────────────────────────────

# load the redis schema at startup
schema_entries = redis_client.lrange("nova:schema",0,-1)    # this function retrives data using (key,start,stop) where -1 means last element
schema_cache = [json.loads(e) for e in schema_entries]

# compile graph once at module level
app = graph.compile(checkpointer=checkpointer)


# load the redis dependency functions
def get_history(session_id:str)->list:
    data = redis_client.get(f"history:{session_id}")
    return json.loads(data) if data else []

def save_history(session_id:str, history:list)-> None:
    redis_client.set(f"history:{session_id}",json.dumps(history))


# ── per request ───────────────────────────────────────
def handle_query(user_query: str) -> str:

    session_id= str(uuid.uuid4())

    # redis function to load the prev conversation history
    history = get_history(session_id)

    # create initial state
    initial_state: NovaState = {
        "session_id":session_id,
        "user_query":user_query ,
        "node_trace":[] ,
        "current_node": "start",
        "cached_found":False ,
        "retry_count": 3,
        "conversation_history": history,

        # all Optional fields start as None
        "intent_router_error": None,
        "intent_confidence_score": None,
        "is_user_query_ambigous": None,
        "generated_sql": None,
        "sql_agent_error": None,
        "is_sql_valid": None,
        "validation_error": None,
        "executed_sql_output": None,
        "sql_execution_error": None,
        "final_response_error": None,
        "final_response": None  
    }

    # define the config id to manage state per user
    config = {"configurable":{"thread_id":session_id}}

    # before searching the user query in database, lets first perform checks on user_query
    is_safe, result = validate_input(user_query)

    if not is_safe:
        return result

    else:
        user_query = result
        # check if we have users query response in redis cache
        response=get(user_query,redis_client)
        if response is not None:
            exchange = {
                        "role":"user",
                        "content":user_query
                    }
            response = {
                "role":"assistant",
                "content": response
            }
            save_history(session_id, history+[exchange,response])
            return response["content"]

        else:
            # invoke the graph
            final_state = app.invoke(initial_state,config=config)

            # save the final response in the conversation history
            exchange = {
                "role":"user",
                "content":user_query
            }
            response = {
                "role":"assistant",
                "content": final_state["final_response"]
            }
            save_history(session_id, history+[exchange,response])

            # saving the results in redis cache 
            set(user_query,final_state["final_response"],redis_client)

            # return the final response
            return final_state["final_response"]