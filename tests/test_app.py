# test_app.py
import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
import os
import sys

# Add the directory containing app.py to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions from your app
# Note: You may need to adjust the import based on how you've structured your files
from app import initialize_components, get_agent, execute_query

# test_app.py
import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
import os
import sys

# Add the directory containing app.py to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions from your app
# Note: You may need to adjust the import based on how you've structured your files
from app import initialize_components, get_agent, execute_query

# Test 1: Test component initialization
# Test 2: Test agent creation
@patch('llama_index.core.agent.ReActAgent.from_tools')
def test_get_agent(mock_react_agent):
    """Test that the agent is created correctly using cached components"""
    # Setup mock
    mock_agent = MagicMock()
    mock_react_agent.return_value = mock_agent
    
    # Mock the initialize_components function to return controlled test data
    with patch('app.initialize_components') as mock_init:
        mock_init.return_value = {
            "llm": MagicMock(),
            "sql_query_engine": MagicMock(),
            "llama_cloud_query_engine": MagicMock()
        }
        
        # Clear the Streamlit cache to ensure fresh initialization
        if hasattr(get_agent, 'clear'):
            get_agent.clear()
        else:
            # Fallback to clearing all caches
            st.cache_data.clear()
            st.cache_resource.clear()
        
        # Call the function
        agent = get_agent()
        
        # Assert the expected agent is returned
        assert agent == mock_agent
        
        # Assert the ReActAgent.from_tools was called
        mock_react_agent.assert_called_once()

# Test 3: Test query execution with caching
@patch('app.get_agent')
def test_execute_query(mock_get_agent):
    """Test that execute_query correctly processes a query and utilizes caching"""
    # Setup mock
    mock_agent = MagicMock()
    mock_response = MagicMock()
    mock_response.response = "Test response about California"
    mock_agent.query.return_value = mock_response
    mock_get_agent.return_value = mock_agent
    
    # Clear the Streamlit cache to ensure fresh execution
    if hasattr(execute_query, 'clear'):
        execute_query.clear()
    else:
        # Fallback to clearing all caches
        st.cache_data.clear()
        st.cache_resource.clear()
    
    # Execute the query twice with the same text
    result1 = execute_query("Tell me about California")
    result2 = execute_query("Tell me about California")
    
    # Should return the same cached result
    assert result1 == "Test response about California"
    assert result2 == "Test response about California"
    
    # The agent's query method should only be called once due to caching
    mock_agent.query.assert_called_once_with("Tell me about California")
    
    # Try a different query
    mock_agent.query.reset_mock()
    mock_response.response = "Test response about New York"
    mock_agent.query.return_value = mock_response
    
    result3 = execute_query("Tell me about New York")
    
    # Should return the new response
    assert result3 == "Test response about New York"
    mock_agent.query.assert_called_once_with("Tell me about New York")