from commons.speech_ai_agent.model import _get_model
from commons.speech_ai_agent.state import AgentState
from typing import TypedDict
from langchain_core.messages import RemoveMessage

gather_prompt = """You are tasked with helping draft a marketing content of the speech. \

Your first job is to gather all the speaker;s requirements about sales his speech. \
You should have a clear sense of how to make target audience interested in the speech. \

You are conversing with a user. Ask as many follow up questions as necessary - but only ask ONE question at a time. \
Only gather information about the speech. \
If you have a good idea of how they are trying to build, call the `Build` tool to draft the marketing content.

Do not ask unnecessary questions! Do not ask them to confirm your understanding or the structure! The user will be able to \
correct you even after you call the Build tool, so just do enough to draft the marketing content. always response in zh-tw"""


class Build(TypedDict):
    requirements: str


def gather_requirements(state: AgentState, config):
    messages = [
       {"role": "system", "content": gather_prompt}
   ] + state['messages']
    model = _get_model(config, "openai", "gather_model").bind_tools([Build])
    response = model.invoke(messages)
    if len(response.tool_calls) == 0:
        return {"messages": [response]}
    else:
        requirements = response.tool_calls[0]['args']['requirements']
        delete_messages = [RemoveMessage(id=m.id) for m in state['messages']]
        return {"requirements": requirements, "messages": delete_messages}
