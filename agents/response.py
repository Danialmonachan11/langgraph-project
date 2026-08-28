from graph.state import NovaState
from langchain_openai import ChatOpenAI


# initialize LLM
llm = ChatOpenAI(model="gpt-4o",temperature=0)


# define response agent
def response_agent(state: NovaState) -> NovaState:
    user_query = state['user_query']
    executed_sql_output = state['executed_sql_output']

    prompt = f"""
        you are responsible to give the final output to the user basis the users 
        query and the executed sql output. the output should be clean and in
        readable format.

        user_query = {user_query}
        executed_sql_output = {executed_sql_output}

        output format : {{this should be very communicative and conversational}}
        
    """
    try:
        response = llm.invoke(prompt)
        final_response = response.content.strip()

        return {
            **state,
            "final_response":final_response,
            "current_node":"response_agent",
            "node_trace":state["node_trace"]+['response_agent'],
            "final_response_error":None
        }
    except Exception as e:
        return {
            **state,
            "final_response":None,
            "current_node":"response_agent",
            "node_trace":state["node_trace"]+['response_agent'],
            "final_response_error":str(e)
        }    