from graph.state import NovaState
from langchain_openai import ChatOpenAI
import json


# initialize LLM
llm = ChatOpenAI(model="gpt-4o",temperature=0)


# define response agent
def result_validator_agent(state: NovaState) -> NovaState:
    user_query = state['user_query']
    executed_sql_output = state['executed_sql_output']

    prompt = f"""
        you are responsible to validate the validator response if Validator agent approves
        basis the users query and the executed sql output.

        user_query = {user_query}
        executed_sql_output = {executed_sql_output}

        output format : {{"is_valid":true/false,"reason":explanation}}
        
    """
    try:
        response = llm.invoke(prompt)
        parsed = json.loads(response.content)

        return {
            **state,
            "result_validator":parsed["is_valid"],
            "current_node":"result_validator_agent",
            "node_trace":state["node_trace"]+['result_validator_agent'],
            "result_validator_error":None
        }
    except Exception as e:
        return {
            **state,
            "final_response":None,
            "current_node":"response_agent",
            "node_trace":state["node_trace"]+['response_agent'],
            "result_validator_error":str(e)
        }    