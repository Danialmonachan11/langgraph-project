from graph.state import NovaState
import logging

logger = logging.getLogger(__name__)

# define clarify agent
def clarify_agent(state:NovaState)->NovaState:
        return {
            **state,
            "final_response":"Can you clarify this question ?",
            "current_node":"clarify_agent",
            "node_trace":state['node_trace']+["clarify_agent"]
        }

# define escalate agent
def escalate_agent(state: NovaState)->NovaState:
    logger.error("Escalation triggered", extra={
    "user_query": state['user_query'],
    "error": state['validation_error'] or state['sql_execution_error'],
    "node_trace": state['node_trace']
        })
    return {
        **state,
        "final_response": "We have observed an error and we have notified our team",
        "current_node": "escalate_node",
        "node_trace": state['node_trace'] + ['escalate_node']
    }