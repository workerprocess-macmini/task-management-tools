#!/usr/bin/env python3
"""
Interactive Calculator Application (v2)

A command-line calculator supporting basic arithmetic operations
(+, -, *, /) with comprehensive error handling, user-friendly interface,
and clean code following PEP 8 standards.

Features:
- Basic arithmetic operations: addition, subtraction, multiplication, division
- Division by zero protection
- Invalid input validation
- Interactive loop with command history
- Clear output formatting with borders
- Type hints and docstrings

Author: Developer Agent
Date: 2026-04-14
Version: 2.0
Usage: python3 calculator_v2.py
"""

from typing import Callable, Dict


def add(a: float, b: float) -> float:
    """
    Add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b


def subtract(a: float, b: float) -> float:
    """
    Subtract two numbers.

    Args:
        a: First number (minuend)
        b: Second number (subtrahend)

    Returns:
        Difference of a minus b
    """
    return a - b


def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Product of a and b
    """
    return a * b


def divide(a: float, b: float) -> float:
    """
    Divide two numbers with error handling.

    Args:
        a: Dividend
        b: Divisor

    Returns:
        Result of a divided by b

    Raises:
        ValueError: If divisor is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def print_banner() -> None:
    """Print the calculator welcome banner."""
    print("\n" + "=" * 60)
    print(" " * 15 + "🔢 CALCULATOR v2.0 🔢")
    print("=" * 60)
    print("Supported Operations: + (add)  - (subtract)  * (multiply)  / (divide)")
    print("Commands: 'quit' to exit, 'help' for usage instructions")
    print("=" * 60 + "\n")


def print_help() -> None:
    """Print usage instructions."""
    print("\n" + "-" * 60)
    print("USAGE INSTRUCTIONS")
    print("-" * 60)
    print("Format: <number> <operator> <number>")
    print("Examples:")
    print("  10 + 5       →  15.0")
    print("  20 - 8       →  12.0")
    print("  6 * 7        →  42.0")
    print("  100 / 4      →  25.0")
    print("\nSpecial Commands:")
    print("  'quit'       →  Exit the calculator")
    print("  'help'       →  Show this help message")
    print("-" * 60 + "\n")


def format_result(num1: float, operator: str, num2: float,
                  result: float) -> str:
    """
    Format calculation result for display.

    Args:
        num1: First operand
        operator: Operation symbol
        num2: Second operand
        result: Calculation result

    Returns:
        Formatted result string
    """
    return f"✓ {num1} {operator} {num2} = {result}"


def get_operation_dict() -> Dict[str, Callable[[float, float], float]]:
    """
    Create and return the operations dictionary.

    Returns:
        Dictionary mapping operators to their functions
    """
    return {
        "+": add,
        "-": subtract,
        "*": multiply,
        "/": divide,
    }


def parse_input(user_input: str) -> tuple[str, str, str] | None:
    """
    Parse user input into operands and operator.

    Args:
        user_input: Raw user input string

    Returns:
        Tuple of (num1_str, operator, num2_str) or None if invalid

    Raises:
        ValueError: If input format is invalid
    """
    parts = user_input.strip().split()

    if len(parts) != 3:
        raise ValueError("Invalid format. Use: number operator number")

    return parts[0], parts[1], parts[2]


def main() -> None:
    """
    Run the interactive calculator main loop.

    Continuously prompts user for calculations and displays results
    with error handling for invalid inputs and operations.
    """
    print_banner()
    operations = get_operation_dict()
    calculation_count = 0

    while True:
        try:
            # Prompt for input
            user_input = input("Enter calculation (or 'help'/'quit'): ").strip()

            # Check for special commands
            if user_input.lower() == "quit":
                print(f"\n✓ Performed {calculation_count} calculation(s). Goodbye!\n")
                break

            if user_input.lower() == "help":
                print_help()
                continue

            if not user_input:
                print("⚠ Please enter a valid calculation.\n")
                continue

            # Parse input
            try:
                num1_str, operator, num2_str = parse_input(user_input)
            except ValueError as e:
                print(f"⚠ {e}\n")
                continue

            # Validate operator
            if operator not in operations:
                print(f"⚠ Invalid operator '{operator}'. "
                      f"Valid operators: {', '.join(operations.keys())}\n")
                continue

            # Convert to floats and validate
            try:
                num1 = float(num1_str)
                num2 = float(num2_str)
            except ValueError:
                print("⚠ Invalid input. Please enter valid numbers.\n")
                continue

            # Perform calculation
            try:
                result = operations[operator](num1, num2)
                formatted_result = format_result(num1, operator, num2, result)
                print(formatted_result + "\n")
                calculation_count += 1
            except ValueError as e:
                print(f"⚠ Error: {e}\n")

        except KeyboardInterrupt:
            print("\n\n⚠ Calculator interrupted by user. Goodbye!\n")
            break
        except Exception as e:
            print(f"⚠ Unexpected error: {e}\n")


if __name__ == "__main__":
    main()
