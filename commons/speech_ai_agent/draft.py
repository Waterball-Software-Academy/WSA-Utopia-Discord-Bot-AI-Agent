from commons.speech_ai_agent.model import _get_model
from commons.speech_ai_agent.state import AgentState



def draft_answer(state: AgentState, config):
    # github_url = "https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/tests/test_pregel.py"
    # file_contents = load_github_file(github_url)
    messages = [
        {"role": "system", "content": "根據你收到的資訊，建立一個精彩的課程介紹文案，字數不超過300字. always generate in zh-tw"},
                   {"role": "user", "content": state.get('requirements')}
    ] + state['messages']
    model = _get_model(config, "openai", "draft_model")
    response = model.invoke(messages)
    return {"messages": [response]}
