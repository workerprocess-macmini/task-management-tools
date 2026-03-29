#!/usr/bin/env python3
"""
Hello Script - Simple greeting program with datetime support
"""

import sys
from datetime import datetime

def hello(name="World", include_datetime=True):
    """Print hello message with optional datetime"""
    message = f"Hello, {name}! 👋"
    
    if include_datetime:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    else:
        print(message)
    
    return message

def hello_with_datetime(name="World", style="simple"):
    """Print hello with datetime and different styles"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    styles = {
        "simple": f"Hello, {name}!",
        "formal": f"Greetings, {name}.",
        "friendly": f"Hey {name}! 😊",
        "emoji": f"Hello {name}! 🎉"
    }
    
    message = styles.get(style, styles["simple"])
    print(f"[{timestamp}] {message}")
    return message

def hello_with_style(name="World", style="simple"):
    """Print hello with different styles (no datetime)"""
    styles = {
        "simple": f"Hello, {name}!",
        "formal": f"Greetings, {name}.",
        "friendly": f"Hey {name}! 😊",
        "emoji": f"Hello {name}! 🎉"
    }
    
    message = styles.get(style, styles["simple"])
    print(message)
    return message

if __name__ == "__main__":
    # Default greeting with datetime
    print("=== Greeting with DateTime ===")
    hello("Ekachai")
    
    # Greeting with different styles and datetime
    print("\n=== Different Styles with DateTime ===")
    hello_with_datetime("Ekachai", "simple")
    hello_with_datetime("Ekachai", "formal")
    hello_with_datetime("Ekachai", "friendly")
    hello_with_datetime("Ekachai", "emoji")
    
    # Greeting without datetime
    print("\n=== Different Styles without DateTime ===")
    hello_with_style("Ekachai", "simple")
    hello_with_style("Ekachai", "formal")
    hello_with_style("Ekachai", "friendly")
    hello_with_style("Ekachai", "emoji")
    
    # Custom greeting from command line
    if len(sys.argv) > 1:
        name = sys.argv[1]
        hello(name)
