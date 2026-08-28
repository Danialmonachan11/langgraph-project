from graph.state import NovaState
from langchain_openai import ChatOpenAI
import json
from rag.schema_retriever import retrieve_schema
import redis


redis_client = redis.Redis()
redis_schema_client = redis_client.lrange("nova:schema",0,-1)


# initialize LLM
llm = ChatOpenAI(model="gpt-4o",temperature=0)


#define sql agent - which generates sql queries
def sql_agent(state: NovaState) -> NovaState:
    new_retry_count = state['retry_count']
    if state['validation_error'] or state['sql_execution_error']:
        new_retry_count = state['retry_count']-1
    user_query = state['user_query']
    formatted_text = '\n'.join(f'User:{i["role"]} \ncontent:{i["content"]}' for i in state["conversation_history"])

    '''
    - prompt level guardrail - on allowed statements
    - define schema context
    '''

    prompt = f"""
        you are an analyst, which generates sql query basis the users query.
        
        **you are only allowed to generate the queries with select statement, and 
        you are not allowed to generate any queries with delete, drop or truncate**
        
        while generating the queries, you should refer to the conversation history, you can only refer to these tables or
        provided schema context and not outside this

        schema context : {retrieve_schema(user_query,redis_schema_client)}
        conversation history : {formatted_text}     
        user query : {user_query}
        
        output format: {{"sql":generated sql}} and this should be in json format
        """
    response = llm.invoke(prompt)     

    try:
        parsed = json.loads(response.content)
        generated_sql = parsed['sql']
        return {
            **state,
            "generated_sql":generated_sql,
            "current_node":"sql_agent",
            "node_trace":state['node_trace'] + ['sql_agent'],
            "sql_agent_error":None,
            "retry_count":new_retry_count

        }
    
    except Exception as e:
        return {
            **state,
            "generated_sql":None,
            "current_node":"sql_agent",
            "node_trace":state['node_trace'] + ['sql_agent'],
            "sql_agent_error":str(e),
            "retry_count": new_retry_count
        }