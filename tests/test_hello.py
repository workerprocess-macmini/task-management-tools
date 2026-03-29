#!/usr/bin/env python3
"""
Unit tests for hello script with datetime support
"""

import sys
import os
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from hello import hello, hello_with_datetime, hello_with_style

def test_hello_default():
    """Test hello with default name"""
    result = hello("World", include_datetime=False)
    assert result == "Hello, World! 👋"
    print("✅ test_hello_default passed")

def test_hello_custom():
    """Test hello with custom name"""
    result = hello("Ekachai", include_datetime=False)
    assert result == "Hello, Ekachai! 👋"
    print("✅ test_hello_custom passed")

def test_hello_with_datetime():
    """Test hello_with_datetime function"""
    result = hello_with_datetime("Test", "simple")
    assert "Hello, Test!" in result or result == "Hello, Test!"
    print("✅ test_hello_with_datetime passed")

def test_hello_with_datetime_formal():
    """Test hello_with_datetime with formal style"""
    result = hello_with_datetime("Test", "formal")
    assert "Greetings, Test." in result or result == "Greetings, Test."
    print("✅ test_hello_with_datetime_formal passed")

def test_hello_with_datetime_friendly():
    """Test hello_with_datetime with friendly style"""
    result = hello_with_datetime("Test", "friendly")
    assert "Hey Test! 😊" in result or result == "Hey Test! 😊"
    print("✅ test_hello_with_datetime_friendly passed")

def test_hello_with_datetime_emoji():
    """Test hello_with_datetime with emoji style"""
    result = hello_with_datetime("Test", "emoji")
    assert "Hello Test! 🎉" in result or result == "Hello Test! 🎉"
    print("✅ test_hello_with_datetime_emoji passed")

def test_hello_with_style_simple():
    """Test hello_with_style with simple style"""
    result = hello_with_style("Test", "simple")
    assert result == "Hello, Test!"
    print("✅ test_hello_with_style_simple passed")

def test_hello_with_style_formal():
    """Test hello_with_style with formal style"""
    result = hello_with_style("Test", "formal")
    assert result == "Greetings, Test."
    print("✅ test_hello_with_style_formal passed")

def test_hello_with_style_friendly():
    """Test hello_with_style with friendly style"""
    result = hello_with_style("Test", "friendly")
    assert result == "Hey Test! 😊"
    print("✅ test_hello_with_style_friendly passed")

def test_hello_with_style_emoji():
    """Test hello_with_style with emoji style"""
    result = hello_with_style("Test", "emoji")
    assert result == "Hello Test! 🎉"
    print("✅ test_hello_with_style_emoji passed")

def test_hello_with_style_default():
    """Test hello_with_style with unknown style defaults to simple"""
    result = hello_with_style("Test", "unknown")
    assert result == "Hello, Test!"
    print("✅ test_hello_with_style_default passed")

if __name__ == "__main__":
    print("Running tests...")
    print("=" * 50)
    
    test_hello_default()
    test_hello_custom()
    test_hello_with_datetime()
    test_hello_with_datetime_formal()
    test_hello_with_datetime_friendly()
    test_hello_with_datetime_emoji()
    test_hello_with_style_simple()
    test_hello_with_style_formal()
    test_hello_with_style_friendly()
    test_hello_with_style_emoji()
    test_hello_with_style_default()
    
    print("=" * 50)
    print("✅ All 11 tests passed!")
