from langgraph.graph import MessagesState
from typing import TypedDict, Literal
class AgentState(MessagesState):
    requirements: str
    content: str
    accepted: bool


class OutputState(TypedDict):
    content: str


class GraphConfig(TypedDict):
    gather_model: Literal['openai', 'anthropic']
    draft_model: Literal['openai', 'anthropic']
    critique_model: Literal['openai', 'anthropic']
