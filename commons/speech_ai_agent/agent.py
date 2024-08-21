from typing import Literal

from langgraph.graph import StateGraph, END, MessagesState
from langchain_core.messages import AIMessage, HumanMessage
from langchain.schema import runnable


from commons.speech_ai_agent.draft import draft_answer
from commons.speech_ai_agent.gather_requirements import gather_requirements
from commons.speech_ai_agent.state import AgentState, OutputState, GraphConfig

def inp(query: str) -> AgentState:
    """
    Initialize the state of the agent with a query.
    """
    return AgentState(
        messages=[HumanMessage(content=query)],
        accepted=False,
        requirements=None
    )

def out(state: OutputState) -> str:
    """
    Return the output of the agent.
    """
    return state['messages'][-1].content

def route_start(state: AgentState) -> Literal["draft_answer", "gather_requirements"]:
    if state.get('requirements'):
        return "draft_answer"
    else:
        return "gather_requirements"


def route_gather(state: AgentState) -> Literal["draft_answer", END]:
    if state.get('requirements'):
        return "draft_answer"
    else:
        return END


# Define a new graph
def create_workflow():
    workflow = StateGraph(AgentState, input=MessagesState, output=OutputState, config_schema=GraphConfig)
    workflow.add_node(draft_answer)
    workflow.add_node(gather_requirements)
    workflow.set_conditional_entry_point(route_start)
    workflow.add_conditional_edges("gather_requirements", route_gather)
    workflow.add_edge("draft_answer", END)
    graph = workflow.compile()
    final_chain = runnable.RunnableLambda(inp) | graph
    return final_chain
