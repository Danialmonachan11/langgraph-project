from graph.state import NovaState
from langchain_openai import ChatOpenAI
import json
import logging
import re


logger = logging.getLogger(__name__)



# initialize LLM
llm = ChatOpenAI(model="gpt-4o",temperature=0)

# define validation agent for semantic and validating schema context
def validation_agent(state: NovaState) -> NovaState:
    generated_sql = state['generated_sql']
    user_query = state['user_query']
    schema_context = state['schema_context']

    if not allowed_statements(generated_sql):

        """
        - semantically aligned queries
        - queries taking schema context
        """

        prompt = f"""
            you are a validation agent and you check the following
            - generated sql query are semantically aligned with user query 
            - generated sql query are taking schema context
            
            user_query = {user_query}
            schema_context = {schema_context}

            output format should be in json : {{"semantically_aligned":"True" or "False",
                            "taking_schema_context":"True" or "False"}}

            """

        respose = llm.invoke(prompt)

        try:
            parsed = json.loads(respose.content)
            if parsed['semantically_aligned'].lower()=="false" :
                 return {
                    **state,
                    "is_sql_valid" : False,
                    "current_node" : "validation_agent",
                    "node_trace" : state['node_trace']+['validation_agent'],
                    "validation_error":"Failed because the query is not semantically aligned"
                                 }

            if parsed['taking_schema_context'].lower()=="false":
                return {
                    **state,
                    "is_sql_valid" : False,
                    "current_node" : "validation_agent",
                    "node_trace" : state['node_trace']+['validation_agent'],
                    "validation_error":"Failed because the query is not taking right schema"
                                    }
            return {
                **state,
                "is_sql_valid" : True,
                "current_node" : "validation_agent",
                "node_trace" : state['node_trace']+['validation_agent'],
                "validation_error":None
            }
                 
        except Exception as e:
                return {
                    **state,
                    "is_sql_valid" : False,
                    "current_node" : "validation_agent",
                    "node_trace" : state['node_trace']+['validation_agent'],
                    "validation_error":str(e)
                }

    else:
        logger.error("Hard failure", extra={
              "generated_sql": state["generated_sql"],
              "current_node":"validation_agent",
              "node_trace":state['node_trace']+['validation_agent']
         })
        return {
            **state,
            "is_sql_valid" : False,
            "current_node" : "validation_agent",
            "node_trace" : state['node_trace']+['validation_agent'],
            "validation_error": "Forbidden SQL statement"
        }
             


def allowed_statements(sql:str) -> bool:

    # Pattern looks for 'drop', 'delete', or 'truncate' as standalone words
    forbidden_pattern = r"\b(drop|delete|truncate)\b"
    
    # re.IGNORECASE makes the check case-insensitive (matches DROP, drop, Drop, etc.)
    if re.search(forbidden_pattern, sql, re.IGNORECASE):
        return False
    else:
         return True 
    


