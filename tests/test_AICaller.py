import pytest
import responses
from llm_handler.AICaller import AICaller

@pytest.fixture
def ai_caller():
    return AICaller("llama2", "http://localhost:11434")

@responses.activate
def test_non_streaming_call(ai_caller):
    responses.add(
        responses.POST,
        "http://localhost:11434/api/generate",
        json={"response": "Test response"},
        status=200
    )
    
    response, p_tokens, c_tokens = ai_caller.call_model(
        prompt={"system": "Test", "user": "Hello"},
        stream=False
    )
    
    assert response == "Test response"
    assert isinstance(p_tokens, int)
    assert isinstance(c_tokens, int)

@pytest.mark.asyncio
async def test_streaming_call(ai_caller):
    responses.add(
        responses.POST,
        "http://localhost:11434/api/generate",
        body="Test\nstream\nresponse",
        status=200
    )
    
    response, p_tokens, c_tokens = ai_caller.call_model(
        prompt={"system": "Test", "user": "Hello"},
        stream=True
    )
    
    assert response != ""
    assert isinstance(p_tokens, int)
    assert isinstance(c_tokens, int)