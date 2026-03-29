#!/usr/bin/env python3
"""
Hello Script - Simple greeting program
"""

import sys
from datetime import datetime

def hello(name="World"):
    """Print hello message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Hello, {name}! 👋"
    print(f"[{timestamp}] {message}")
    return message

def hello_with_style(name="World", style="simple"):
    """Print hello with different styles"""
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
    # Default greeting
    hello("Ekachai")
    
    # Greeting with different styles
    print("\n--- Different Styles ---")
    hello_with_style("Ekachai", "simple")
    hello_with_style("Ekachai", "formal")
    hello_with_style("Ekachai", "friendly")
    hello_with_style("Ekachai", "emoji")
    
    # Custom greeting from command line
    if len(sys.argv) > 1:
        name = sys.argv[1]
        hello(name)
