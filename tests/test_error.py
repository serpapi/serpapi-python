"""
Test suite for SerpApi Error handling.
"""

import pytest
from serpapi import SerpApiError


class TestSerpApiError:
    """Test cases for SerpApiError exception."""
    
    def test_serpapi_error_inheritance(self):
        """Test that SerpApiError inherits from Exception."""
        error = SerpApiError("Test error message")
        assert isinstance(error, Exception)
        assert str(error) == "Test error message"
    
    def test_serpapi_error_with_message(self):
        """Test SerpApiError with custom message."""
        message = "API request failed"
        error = SerpApiError(message)
        assert str(error) == message
    
    def test_serpapi_error_raise(self):
        """Test raising SerpApiError."""
        with pytest.raises(SerpApiError, match="Test error"):
            raise SerpApiError("Test error")
    
    def test_serpapi_error_catch(self):
        """Test catching SerpApiError."""
        try:
            raise SerpApiError("Caught error")
        except SerpApiError as e:
            assert str(e) == "Caught error"
        except Exception:
            pytest.fail("SerpApiError should be caught")
