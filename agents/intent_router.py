from graph.state import NovaState
from langchain_openai import ChatOpenAI
import json

# initialize LLM
llm = ChatOpenAI(model="gpt-4o",temperature=0)


# define the router node
def intent_router(state: NovaState)-> NovaState:
    user_query = state['user_query']

    # define prompt
    prompt = f"""
            you are an analyzer which identifies the intent of the users query and classifies it into 2 buckets : sql_agent and need_clarification
            and give the confidence score on your intent classification

            "user query":{user_query}

            output format: {{"intent":"identified_intent",
                            "confidence_score:"identified_intent_confidence"}}
        """
    response = llm.invoke(prompt)
    try:
        parsed=json.loads(response.content)
        intent = parsed["intent"]
        confidence_score = parsed["confidence_score"]

        return {
            **state,
            "is_user_query_ambigous":True if intent=="need_clarification" else False,
            "current_node":"intent_router",
            "node_trace":state["node_trace"]+['intent_router'],
            "intent_confidence_score":confidence_score,
            "intent_router_error":None
        }
    
    except Exception as e:
        return {
            **state,
            "is_user_query_ambigous":True,
            "current_node":"intent_router",
            "node_trace":state["node_trace"]+['intent_router'],
            "intent_confidence_score":0.0,
            "intent_router_error":str(e)
        }
        