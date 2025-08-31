"""Comprehensive test suite for main module functionality."""

import pytest
import sys
from unittest.mock import patch, MagicMock
from src.ollamapy.main import (
    hello, greet, main, chat, run_vibe_tests, run_skill_gen, run_skill_editor
)


class TestBasicFunctions:
    """Test basic utility functions."""
    
    def test_hello(self):
        """Test hello function returns correct message."""
        assert hello() == "Hello, World!"
        
    def test_greet(self):
        """Test greet function with various inputs."""
        assert greet("Alice") == "Hello, Alice!"
        assert greet("Bob") == "Hello, Bob!"
        assert greet("") == "Hello, !"
        assert greet("123") == "Hello, 123!"
        assert greet("Test User") == "Hello, Test User!"


class TestArgumentParsing:
    """Test command line argument parsing."""
    
    def test_hello_argument(self):
        """Test --hello argument processing."""
        test_args = ["ollamapy", "--hello"]
        with patch.object(sys, 'argv', test_args):
            with patch('builtins.print') as mock_print:
                with patch.object(sys, 'exit'):
                    try:
                        main()
                    except SystemExit:
                        pass
                mock_print.assert_any_call("Hello, World!")
                mock_print.assert_any_call("Hello, Python!")
    
    @patch('src.ollamapy.main.run_vibe_tests')
    def test_vibetest_argument(self, mock_run_vibe):
        """Test --vibetest argument processing."""
        mock_run_vibe.return_value = True
        test_args = ["ollamapy", "--vibetest"]
        
        with patch.object(sys, 'argv', test_args):
            with patch.object(sys, 'exit') as mock_exit:
                main()
                mock_run_vibe.assert_called_once_with(
                    model='gemma3:4b',
                    iterations=1, 
                    analysis_model=None
                )
                mock_exit.assert_called_once_with(0)
    
    @patch('src.ollamapy.main.run_skill_gen')
    def test_skillgen_argument(self, mock_run_skill):
        """Test --skillgen argument processing."""
        mock_run_skill.return_value = True
        test_args = ["ollamapy", "--skillgen", "--count", "3"]
        
        with patch.object(sys, 'argv', test_args):
            with patch.object(sys, 'exit') as mock_exit:
                main()
                mock_run_skill.assert_called_once_with(
                    model='gemma3:4b',
                    analysis_model='gemma3:4b',
                    count=3,
                    ideas=None
                )
                mock_exit.assert_called_once_with(0)
    
    @patch('src.ollamapy.main.run_skill_editor')
    def test_skill_editor_argument(self, mock_run_editor):
        """Test --skill-editor argument processing."""
        mock_run_editor.return_value = True
        test_args = ["ollamapy", "--skill-editor", "--port", "8080"]
        
        with patch.object(sys, 'argv', test_args):
            with patch.object(sys, 'exit') as mock_exit:
                main()
                mock_run_editor.assert_called_once_with(
                    port=8080,
                    skills_directory=None
                )
                mock_exit.assert_called_once_with(0)


class TestChatFunction:
    """Test chat functionality."""
    
    @patch('src.ollamapy.main.TerminalInterface')
    @patch('src.ollamapy.main.AIQuery')
    @patch('src.ollamapy.main.ChatSession')
    @patch('src.ollamapy.main.AnalysisEngine')
    @patch('src.ollamapy.main.ModelManager')
    @patch('src.ollamapy.main.OllamaClient')
    def test_chat_with_defaults(self, mock_client, mock_model_manager, 
                               mock_analysis_engine, mock_chat_session, 
                               mock_ai_query, mock_terminal):
        """Test chat function with default parameters."""
        mock_terminal_instance = MagicMock()
        mock_terminal.return_value = mock_terminal_instance
        
        chat()
        
        mock_client.assert_called_once()
        mock_model_manager.assert_called_once()
        mock_analysis_engine.assert_called_once_with('gemma3:4b', mock_client.return_value)
        mock_chat_session.assert_called_once_with('gemma3:4b', mock_client.return_value, 'You are a helpful assistant.')
        mock_ai_query.assert_called_once_with(mock_client.return_value, model='gemma3:4b')
        mock_terminal_instance.run.assert_called_once()
    
    @patch('src.ollamapy.main.TerminalInterface')
    @patch('src.ollamapy.main.AIQuery')
    @patch('src.ollamapy.main.ChatSession')
    @patch('src.ollamapy.main.AnalysisEngine')
    @patch('src.ollamapy.main.ModelManager')
    @patch('src.ollamapy.main.OllamaClient')
    def test_chat_with_custom_params(self, mock_client, mock_model_manager, 
                                   mock_analysis_engine, mock_chat_session, 
                                   mock_ai_query, mock_terminal):
        """Test chat function with custom parameters."""
        mock_terminal_instance = MagicMock()
        mock_terminal.return_value = mock_terminal_instance
        
        chat(model="llama3.2:3b", system="Custom system", analysis_model="gemma2:2b")
        
        mock_analysis_engine.assert_called_once_with('gemma2:2b', mock_client.return_value)
        mock_chat_session.assert_called_once_with('llama3.2:3b', mock_client.return_value, 'Custom system')
        mock_ai_query.assert_called_once_with(mock_client.return_value, model='gemma2:2b')


class TestVibeTestFunction:
    """Test vibe test functionality."""
    
    @patch('src.ollamapy.vibe_tests.run_vibe_tests')
    def test_run_vibe_tests_success(self, mock_vibe_tests):
        """Test successful vibe test execution."""
        mock_vibe_tests.return_value = True
        
        result = run_vibe_tests(model="test-model", iterations=5)
        
        assert result is True
        mock_vibe_tests.assert_called_once_with(
            model="test-model",
            iterations=5,
            analysis_model="gemma3:4b"
        )
    
    @patch('src.ollamapy.vibe_tests.run_vibe_tests')
    def test_run_vibe_tests_with_analysis_model(self, mock_vibe_tests):
        """Test vibe tests with custom analysis model."""
        mock_vibe_tests.return_value = False
        
        result = run_vibe_tests(
            model="chat-model",
            iterations=3,
            analysis_model="analysis-model"
        )
        
        assert result is False
        mock_vibe_tests.assert_called_once_with(
            model="chat-model",
            iterations=3,
            analysis_model="analysis-model"
        )


class TestSkillGenFunction:
    """Test skill generation functionality."""
    
    @patch('src.ollamapy.skill_generator.run_skill_generation')
    def test_run_skill_gen_defaults(self, mock_skill_gen):
        """Test skill generation with default parameters."""
        mock_skill_gen.return_value = True
        
        result = run_skill_gen()
        
        assert result is True
        mock_skill_gen.assert_called_once_with(
            model="gemma3:4b",
            analysis_model=None,
            count=1,
            ideas=None
        )
    
    @patch('src.ollamapy.skill_generator.run_skill_generation')
    def test_run_skill_gen_custom_params(self, mock_skill_gen):
        """Test skill generation with custom parameters."""
        mock_skill_gen.return_value = False
        ideas = ["idea1", "idea2"]
        
        result = run_skill_gen(
            model="custom-model",
            analysis_model="analysis-model",
            count=3,
            ideas=ideas
        )
        
        assert result is False
        mock_skill_gen.assert_called_once_with(
            model="custom-model",
            analysis_model="analysis-model",
            count=3,
            ideas=ideas
        )


class TestSkillEditorFunction:
    """Test skill editor functionality."""
    
    def test_run_skill_editor_dependency_check(self):
        """Test skill editor dependency checking."""
        # Test that the function handles missing dependencies gracefully
        with patch('builtins.print') as mock_print:
            result = run_skill_editor(port=8080, skills_directory="/tmp/test_skills")
            
            # Should return False if dependencies are missing
            if result is False:
                mock_print.assert_any_call("❌ Error: Missing dependencies for skill editor.")
            else:
                # If dependencies are available, should return True
                assert result is True
    
    def test_run_skill_editor_import_error(self):
        """Test skill editor with missing dependencies."""
        with patch('builtins.__import__', side_effect=ImportError("Missing flask")):
            with patch('builtins.print') as mock_print:
                result = run_skill_editor()
                
                assert result is False
                mock_print.assert_any_call("❌ Error: Missing dependencies for skill editor.")


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @patch('src.ollamapy.main.run_vibe_tests', side_effect=Exception("Test error"))
    def test_vibetest_error_handling(self, mock_run_vibe):
        """Test error handling in vibe test execution."""
        test_args = ["ollamapy", "--vibetest"]
        
        with patch.object(sys, 'argv', test_args):
            with patch.object(sys, 'exit') as mock_exit:
                with pytest.raises(Exception, match="Test error"):
                    main()
    
    @patch('src.ollamapy.main.chat', side_effect=KeyboardInterrupt())
    def test_keyboard_interrupt_handling(self, mock_chat):
        """Test graceful handling of keyboard interrupt."""
        test_args = ["ollamapy"]
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(KeyboardInterrupt):
                main()


class TestInputValidation:
    """Test input validation for various functions."""
    
    def test_greet_with_none(self):
        """Test greet function with None input."""
        # The greet function handles None by converting to string
        result = greet(None)
        assert result == "Hello, None!"
    
    def test_greet_with_numeric_input(self):
        """Test greet function with numeric input."""
        assert greet(42) == "Hello, 42!"
        assert greet(3.14) == "Hello, 3.14!"
    
    @patch('src.ollamapy.main.run_vibe_tests')
    def test_negative_iterations(self, mock_run_vibe):
        """Test handling of negative iteration counts."""
        mock_run_vibe.return_value = True
        test_args = ["ollamapy", "--vibetest", "-n", "-1"]
        
        with patch.object(sys, 'argv', test_args):
            with patch.object(sys, 'exit'):
                main()
                mock_run_vibe.assert_called_once_with(
                    model='gemma3:4b',
                    iterations=-1,
                    analysis_model=None
                )