from graph.state import NovaState


#define the intent routing 
def route_intent(state: NovaState) -> str:
    if state['is_user_query_ambigous'] == True or state['intent_confidence_score']<0.9:
           return "ask_clarificatory_questions"
    else:
          return "sql_agent"


def route_validation_agent(state: NovaState) -> str:
    if state['validation_error'] and "forbidden" in state['validation_error']:   
          return "escalate_node"
    if state['validation_error'] and ("semantic" in state['validation_error'] or "schema" in state['validation_error']):
        if state['retry_count']>0:
            return "sql_agent"
        else:
             return "escalate_agent"
    
    else:
        return "execute_agent"


def route_after_execution(state: NovaState) -> str:
    if (state['sql_execution_error'] or state["result_validator"]==False) and state['retry_count']!=0:
        return "sql_agent"

    if (state['sql_execution_error'] or state["result_validator"]==False) and state['retry_count']==0:
         return "escalate_agent"

    else:
         return "response_agent"
    


