"""Comprehensive test suite for OllamaClient module."""

import pytest
import json
from unittest.mock import patch, MagicMock, Mock
import requests
from src.ollamapy.ollama_client import OllamaClient


class TestOllamaClientInitialization:
    """Test OllamaClient initialization."""

    def test_default_initialization(self):
        """Test client initialization with default values."""
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.timeout == 30

    def test_custom_initialization(self):
        """Test client initialization with custom values."""
        client = OllamaClient(base_url="http://custom:8080", timeout=60)
        assert client.base_url == "http://custom:8080"
        assert client.timeout == 60

    def test_base_url_normalization(self):
        """Test that base URL is properly normalized."""
        # Test URL without trailing slash
        client = OllamaClient(base_url="http://localhost:11434/")
        assert client.base_url == "http://localhost:11434"

        # Test URL with path
        client = OllamaClient(base_url="http://localhost:11434/api")
        assert client.base_url == "http://localhost:11434/api"


class TestChatMethod:
    """Test chat functionality."""

    @patch("requests.post")
    def test_chat_successful_response(self, mock_post):
        """Test successful chat response."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = json.dumps(
            {"message": {"content": "Test response"}, "done": True}
        )
        mock_post.return_value = mock_response

        client = OllamaClient()
        response = client.chat("test-model", "Hello")

        assert response == "Test response"
        mock_post.assert_called_once()

        # Verify the request parameters
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:11434/api/chat"

        request_data = json.loads(call_args[1]["data"])
        assert request_data["model"] == "test-model"
        assert request_data["messages"] == [{"role": "user", "content": "Hello"}]
        assert request_data["stream"] is False

    @patch("requests.post")
    def test_chat_with_system_message(self, mock_post):
        """Test chat with system message."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = json.dumps(
            {"message": {"content": "System response"}, "done": True}
        )
        mock_post.return_value = mock_response

        client = OllamaClient()
        response = client.chat("test-model", "Hello", system="You are helpful")

        assert response == "System response"

        # Verify system message is included
        call_args = mock_post.call_args
        request_data = json.loads(call_args[1]["data"])
        expected_messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
        ]
        assert request_data["messages"] == expected_messages

    @patch("requests.post")
    def test_chat_with_conversation_history(self, mock_post):
        """Test chat with conversation history."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = json.dumps(
            {"message": {"content": "History response"}, "done": True}
        )
        mock_post.return_value = mock_response

        history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"},
        ]

        client = OllamaClient()
        response = client.chat("test-model", "Follow up", messages=history)

        assert response == "History response"

        # Verify history is preserved
        call_args = mock_post.call_args
        request_data = json.loads(call_args[1]["data"])
        expected_messages = history + [{"role": "user", "content": "Follow up"}]
        assert request_data["messages"] == expected_messages

    @patch("requests.post")
    def test_chat_connection_error(self, mock_post):
        """Test handling of connection errors."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        client = OllamaClient()

        with pytest.raises(Exception, match="Failed to connect to Ollama"):
            client.chat("test-model", "Hello")

    @patch("requests.post")
    def test_chat_timeout_error(self, mock_post):
        """Test handling of timeout errors."""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        client = OllamaClient()

        with pytest.raises(Exception, match="Request to Ollama timed out"):
            client.chat("test-model", "Hello")

    @patch("requests.post")
    def test_chat_http_error(self, mock_post):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Not Found"
        )
        mock_post.return_value = mock_response

        client = OllamaClient()

        with pytest.raises(Exception, match="HTTP error occurred"):
            client.chat("test-model", "Hello")

    @patch("requests.post")
    def test_chat_json_decode_error(self, mock_post):
        """Test handling of JSON decode errors."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = "Invalid JSON"
        mock_post.return_value = mock_response

        client = OllamaClient()

        with pytest.raises(Exception, match="Failed to parse response from Ollama"):
            client.chat("test-model", "Hello")

    @patch("requests.post")
    def test_chat_missing_message_content(self, mock_post):
        """Test handling of missing message content in response."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = json.dumps({"done": True})  # Missing message
        mock_post.return_value = mock_response

        client = OllamaClient()

        with pytest.raises(Exception, match="Invalid response format from Ollama"):
            client.chat("test-model", "Hello")


class TestListModelsMethod:
    """Test list_models functionality."""

    @patch("requests.get")
    def test_list_models_success(self, mock_get):
        """Test successful model listing."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "models": [
                {"name": "model1:latest", "size": 1000},
                {"name": "model2:7b", "size": 2000},
            ]
        }
        mock_get.return_value = mock_response

        client = OllamaClient()
        models = client.list_models()

        assert len(models) == 2
        assert "model1:latest" in models
        assert "model2:7b" in models

        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=30)

    @patch("requests.get")
    def test_list_models_empty_response(self, mock_get):
        """Test handling of empty model list."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response

        client = OllamaClient()
        models = client.list_models()

        assert models == []

    @patch("requests.get")
    def test_list_models_connection_error(self, mock_get):
        """Test handling of connection error in list_models."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        client = OllamaClient()

        with pytest.raises(Exception, match="Failed to connect to Ollama"):
            client.list_models()

    @patch("requests.get")
    def test_list_models_invalid_response(self, mock_get):
        """Test handling of invalid response format."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"invalid": "format"}
        mock_get.return_value = mock_response

        client = OllamaClient()
        models = client.list_models()

        assert models == []


class TestIsModelAvailableMethod:
    """Test is_model_available functionality."""

    @patch.object(OllamaClient, "list_models")
    def test_is_model_available_exists(self, mock_list_models):
        """Test checking for existing model."""
        mock_list_models.return_value = ["model1:latest", "model2:7b"]

        client = OllamaClient()

        assert client.is_model_available("model1:latest") is True
        assert client.is_model_available("model2:7b") is True
        assert client.is_model_available("nonexistent:model") is False

    @patch.object(OllamaClient, "list_models")
    def test_is_model_available_error(self, mock_list_models):
        """Test handling of error in model availability check."""
        mock_list_models.side_effect = Exception("Connection error")

        client = OllamaClient()

        assert client.is_model_available("any-model") is False


class TestGenerateMethod:
    """Test generate functionality."""

    @patch("requests.post")
    def test_generate_success(self, mock_post):
        """Test successful generate request."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = json.dumps({"response": "Generated text", "done": True})
        mock_post.return_value = mock_response

        client = OllamaClient()
        response = client.generate("test-model", "Generate something")

        assert response == "Generated text"

        # Verify request parameters
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:11434/api/generate"

        request_data = json.loads(call_args[1]["data"])
        assert request_data["model"] == "test-model"
        assert request_data["prompt"] == "Generate something"
        assert request_data["stream"] is False

    @patch("requests.post")
    def test_generate_with_system(self, mock_post):
        """Test generate with system prompt."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.text = json.dumps(
            {"response": "System generated text", "done": True}
        )
        mock_post.return_value = mock_response

        client = OllamaClient()
        response = client.generate("test-model", "Generate", system="You are creative")

        assert response == "System generated text"

        # Verify system is included
        call_args = mock_post.call_args
        request_data = json.loads(call_args[1]["data"])
        assert request_data["system"] == "You are creative"

    @patch("requests.post")
    def test_generate_error_handling(self, mock_post):
        """Test error handling in generate method."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        client = OllamaClient()

        with pytest.raises(Exception, match="Failed to connect to Ollama"):
            client.generate("test-model", "Generate something")


class TestHealthCheckMethod:
    """Test health check functionality."""

    @patch("requests.get")
    def test_health_check_healthy(self, mock_get):
        """Test health check when service is healthy."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = OllamaClient()
        assert client.health_check() is True

        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)

    @patch("requests.get")
    def test_health_check_unhealthy(self, mock_get):
        """Test health check when service is unhealthy."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        client = OllamaClient()
        assert client.health_check() is False

    @patch("requests.get")
    def test_health_check_timeout(self, mock_get):
        """Test health check timeout."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        client = OllamaClient()
        assert client.health_check() is False


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_prompt(self):
        """Test handling of empty prompt."""
        client = OllamaClient()

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.text = json.dumps(
                {"message": {"content": "Empty response"}, "done": True}
            )
            mock_post.return_value = mock_response

            response = client.chat("test-model", "")
            assert response == "Empty response"

    def test_very_long_prompt(self):
        """Test handling of very long prompts."""
        client = OllamaClient()
        long_prompt = "x" * 10000  # 10k characters

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.text = json.dumps(
                {"message": {"content": "Long response"}, "done": True}
            )
            mock_post.return_value = mock_response

            response = client.chat("test-model", long_prompt)
            assert response == "Long response"

    def test_special_characters_in_prompt(self):
        """Test handling of special characters."""
        client = OllamaClient()
        special_prompt = 'Test "quotes" and \\backslashes\\ and 中文'

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.text = json.dumps(
                {"message": {"content": "Special response"}, "done": True}
            )
            mock_post.return_value = mock_response

            response = client.chat("test-model", special_prompt)
            assert response == "Special response"

            # Verify special characters are properly encoded in JSON
            call_args = mock_post.call_args
            request_data = json.loads(call_args[1]["data"])
            assert request_data["messages"][0]["content"] == special_prompt
