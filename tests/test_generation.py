"""Tests for the generation module."""

import pytest
from unittest.mock import patch, AsyncMock

from librarybench.utils import extract_code
from librarybench.generation.models import OpenAiClient, ClaudeClient


def test_extract_code_openai_dash_pattern():
    """Test extracting code from OpenAI solution with dash pattern."""
    solution = """Here's the solution:

-----
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
-----

This function calculates the fibonacci sequence recursively."""

    code = extract_code(solution, "openai")
    assert "def fibonacci(n):" in code
    assert "return fibonacci(n-1) + fibonacci(n-2)" in code


def test_extract_code_claude_markdown():
    """Test extracting code from Claude solution with markdown."""
    solution = """To solve this problem, I'll use a dynamic programming approach:

```python
def fibonacci(n):
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n+1):
        a, b = b, a + b
    return b
```

This implementation is more efficient than the recursive approach."""

    code = extract_code(solution, "claude")
    assert "def fibonacci(n):" in code
    assert "a, b = b, a + b" in code


def test_extract_code_fallback():
    """Test extracting code when no markers are present."""
    solution = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
    
# This function calculates fibonacci numbers recursively"""

    code = extract_code(solution)
    assert "def fibonacci(n):" in code
    assert "return fibonacci(n-1) + fibonacci(n-2)" in code


@pytest.mark.asyncio
@patch("openai.AsyncOpenAI")
async def test_openai_client(mock_openai):
    """Test OpenAI client with mocked API."""
    # Mock the API response
    mock_client = AsyncMock()
    mock_completion = AsyncMock()
    mock_completion.choices = [AsyncMock()]
    mock_completion.choices[0].message.content = "Test response"
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_client

    # Test the client
    with patch.dict("os.environ", {"OPENAI_API_KEY": "fake_key"}):
        client = OpenAiClient(model="o3-mini")
        response = await client.generate_completion("Test prompt", "Test system prompt")

    assert response == "Test response"
    mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
@patch("anthropic.AsyncAnthropic")
async def test_claude_client(mock_anthropic):
    """Test Claude client with mocked API."""
    # Mock the API response
    mock_client = AsyncMock()
    mock_message = AsyncMock()
    mock_content = AsyncMock()
    mock_content.text = "Test response"
    mock_message.content = [mock_content]
    mock_client.messages.create.return_value = mock_message
    mock_anthropic.return_value = mock_client

    # Test the client
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "fake_key"}):
        client = ClaudeClient(model="claude-3-haiku-20240307")
        response = await client.generate_completion("Test prompt", "Test system prompt")

    assert response == "Test response"
    mock_client.messages.create.assert_called_once()
