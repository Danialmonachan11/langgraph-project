from langgraph.graph import StateGraph, END
from graph.state import NovaState
from langgraph.checkpoint.postgres import PostgresSaver
from config.settings import get_settings

from agents.intent_router import intent_router
from agents.sql_agent import sql_agent
from agents.validation_agent import validation_agent
from agents.execute import execute_agent
from agents.response import response_agent
from agents.terminal_node import clarify_agent, escalate_agent
from agents.result_validator import result_validator_agent 
from graph.edges import route_intent, route_validation_agent, route_after_execution



settings = get_settings()
# _checkpointer_cm must stay referenced: it's a context manager, and letting it
# get garbage-collected runs its __exit__ and closes the connection
_checkpointer_cm = PostgresSaver.from_conn_string(settings.checkpoint_db_url)
checkpointer = _checkpointer_cm.__enter__()
checkpointer.setup()

graph = StateGraph(NovaState)

# add nodes
graph.add_node("intent_router",intent_router)
graph.add_node("ask_clarificatory_questions",clarify_agent)
graph.add_node("sql_agent",sql_agent)
graph.add_node("validation_agent",validation_agent)
graph.add_node("execute_agent",execute_agent)
graph.add_node("response_agent",response_agent)
graph.add_node("escalate_agent",escalate_agent)
graph.add_node("result_validator_agent",result_validator_agent)

# set entry point
graph.set_entry_point("intent_router")

# add edges
graph.add_conditional_edges("intent_router",
                           route_intent,
                           {
                               "ask_clarificatory_questions":"ask_clarificatory_questions",
                               "sql_agent":"sql_agent"
                           })

graph.add_edge("sql_agent","validation_agent")

graph.add_conditional_edges(
    "validation_agent",
    route_validation_agent,
    {
        "escalate_agent":"escalate_agent",
        "sql_agent":"sql_agent",
        "execute_agent":"execute_agent"
    }
)
graph.add_edge("execute_agent","result_validator_agent")

graph.add_conditional_edges(
    "result_validator_agent",
    route_after_execution,
    {
        "sql_agent":"sql_agent",
        "escalate_agent":"escalate_agent",
        "response_agent":"response_agent"
    }
)

graph.add_edge("response_agent", END)




