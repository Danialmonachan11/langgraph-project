from graph.state import NovaState
from sqlalchemy import text
from db.connection import get_engine



# define sql execute agent
def execute_agent(state: NovaState) -> NovaState:
    """
    This function should execute the generated sql query
    """ 
    generated_sql = state['generated_sql']

    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(generated_sql))

        # code to close the connection once done
        # assuming the rows will have all the executed data
        rows = [dict(r.mapping) for r in result.fetchall()]
        return {
            **state,
            "executed_sql_output":rows,
            "current_node":"execute_agent",
            "node_trace": state['node_trace'] + ['execute_agent'],
            "sql_execution_error":None
        }

    except Exception as e:
        return {
            **state,
            "executed_sql_output":None,
            "current_node":"execute_agent",
            "node_trace": state['node_trace'] + ['execute_agent'],
            "sql_execution_error":str(e)
            }