#!/usr/bin/env python3
"""
Calculator V3 - Advanced Interactive Calculator

A comprehensive calculator application supporting:
- Basic operations: +, -, *, /, ** (power), % (modulo)
- Error handling for division by zero and invalid input
- Interactive mode with command history
- Clear output formatting
- Help documentation
- Quit command

Author: Developer Agent
Date: 2026-04-14
Version: 3.0
"""

from typing import Union, List, Tuple
from dataclasses import dataclass
from enum import Enum
import sys


class OperationType(Enum):
    """Enumeration of supported operations."""

    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    POWER = "**"
    MODULO = "%"


@dataclass
class CalculationResult:
    """Data class to store calculation results."""

    operation: str
    operand1: float
    operand2: float
    result: float
    error: bool = False
    error_message: str = ""

    def __str__(self) -> str:
        """Format result as a readable string."""
        if self.error:
            return f"Error: {self.error_message}"
        return f"{self.operand1} {self.operation} {self.operand2} = {self.result}"


class Calculator:
    """
    Advanced calculator with history and error handling.

    Attributes:
        history: List of all calculation results
    """

    def __init__(self) -> None:
        """Initialize the calculator with empty history."""
        self.history: List[CalculationResult] = []

    def add(self, a: float, b: float) -> CalculationResult:
        """
        Add two numbers.

        Args:
            a: First operand
            b: Second operand

        Returns:
            CalculationResult with operation details
        """
        result = a + b
        calc_result = CalculationResult("+", a, b, result)
        self.history.append(calc_result)
        return calc_result

    def subtract(self, a: float, b: float) -> CalculationResult:
        """
        Subtract two numbers.

        Args:
            a: First operand (minuend)
            b: Second operand (subtrahend)

        Returns:
            CalculationResult with operation details
        """
        result = a - b
        calc_result = CalculationResult("-", a, b, result)
        self.history.append(calc_result)
        return calc_result

    def multiply(self, a: float, b: float) -> CalculationResult:
        """
        Multiply two numbers.

        Args:
            a: First operand
            b: Second operand

        Returns:
            CalculationResult with operation details
        """
        result = a * b
        calc_result = CalculationResult("*", a, b, result)
        self.history.append(calc_result)
        return calc_result

    def divide(self, a: float, b: float) -> CalculationResult:
        """
        Divide two numbers with error handling for zero division.

        Args:
            a: Dividend
            b: Divisor

        Returns:
            CalculationResult with operation details or error

        Raises:
            Handled internally - returns error in result
        """
        if b == 0:
            error_result = CalculationResult(
                "/", a, b, 0.0, error=True, error_message="Division by zero"
            )
            self.history.append(error_result)
            return error_result

        result = a / b
        calc_result = CalculationResult("/", a, b, result)
        self.history.append(calc_result)
        return calc_result

    def power(self, a: float, b: float) -> CalculationResult:
        """
        Raise a number to a power.

        Args:
            a: Base
            b: Exponent

        Returns:
            CalculationResult with operation details
        """
        result = a ** b
        calc_result = CalculationResult("**", a, b, result)
        self.history.append(calc_result)
        return calc_result

    def modulo(self, a: float, b: float) -> CalculationResult:
        """
        Calculate modulo (remainder) of division.

        Args:
            a: Dividend
            b: Divisor

        Returns:
            CalculationResult with operation details or error
        """
        if b == 0:
            error_result = CalculationResult(
                "%", a, b, 0.0, error=True, error_message="Modulo by zero"
            )
            self.history.append(error_result)
            return error_result

        result = a % b
        calc_result = CalculationResult("%", a, b, result)
        self.history.append(calc_result)
        return calc_result

    def parse_expression(self, expression: str) -> CalculationResult:
        """
        Parse and evaluate a mathematical expression.

        Args:
            expression: String containing "operand1 operator operand2"

        Returns:
            CalculationResult with the evaluated result or error

        Example:
            >>> calc = Calculator()
            >>> result = calc.parse_expression("10 + 5")
            >>> print(result)
            10.0 + 5.0 = 15.0
        """
        try:
            parts = expression.strip().split()

            if len(parts) != 3:
                error_result = CalculationResult(
                    "?",
                    0.0,
                    0.0,
                    0.0,
                    error=True,
                    error_message="Invalid format. Use: operand1 operator operand2",
                )
                self.history.append(error_result)
                return error_result

            operand1_str, operator, operand2_str = parts

            try:
                operand1 = float(operand1_str)
                operand2 = float(operand2_str)
            except ValueError:
                error_result = CalculationResult(
                    "?",
                    0.0,
                    0.0,
                    0.0,
                    error=True,
                    error_message="Invalid operand(s). Must be numbers.",
                )
                self.history.append(error_result)
                return error_result

            if operator == "+":
                return self.add(operand1, operand2)
            elif operator == "-":
                return self.subtract(operand1, operand2)
            elif operator == "*":
                return self.multiply(operand1, operand2)
            elif operator == "/":
                return self.divide(operand1, operand2)
            elif operator == "**":
                return self.power(operand1, operand2)
            elif operator == "%":
                return self.modulo(operand1, operand2)
            else:
                error_result = CalculationResult(
                    operator,
                    0.0,
                    0.0,
                    0.0,
                    error=True,
                    error_message=f"Unknown operator: {operator}",
                )
                self.history.append(error_result)
                return error_result

        except Exception as e:
            error_result = CalculationResult(
                "?",
                0.0,
                0.0,
                0.0,
                error=True,
                error_message=f"Unexpected error: {str(e)}",
            )
            self.history.append(error_result)
            return error_result

    def get_history(self) -> List[CalculationResult]:
        """
        Retrieve all calculation history.

        Returns:
            List of CalculationResult objects
        """
        return self.history

    def display_history(self) -> None:
        """Display formatted calculation history."""
        if not self.history:
            print("No calculation history.")
            return

        print("\n" + "=" * 60)
        print("CALCULATION HISTORY".center(60))
        print("=" * 60)
        for idx, result in enumerate(self.history, 1):
            status = "[ERROR]" if result.error else "[OK]"
            print(f"{idx:2d}. {status} {str(result)}")
        print("=" * 60 + "\n")

    def clear_history(self) -> None:
        """Clear all calculation history."""
        self.history.clear()
        print("History cleared.")


def display_help() -> None:
    """Display help information."""
    help_text = """
╔════════════════════════════════════════════════════════════╗
║          CALCULATOR V3 - HELP & USAGE GUIDE               ║
╚════════════════════════════════════════════════════════════╝

SUPPORTED OPERATIONS:
  +       Addition:           5 + 3 = 8
  -       Subtraction:        10 - 4 = 6
  *       Multiplication:     6 * 7 = 42
  /       Division:           20 / 4 = 5
  **      Power/Exponent:     2 ** 3 = 8
  %       Modulo/Remainder:   17 % 5 = 2

SPECIAL COMMANDS:
  history     Show all previous calculations
  clear       Clear calculation history
  help        Display this help message
  quit        Exit the calculator

INPUT FORMAT:
  Enter expressions as: operand1 operator operand2
  Example: 15 + 8
  Example: 100 / 5
  Example: 2 ** 10

ERROR HANDLING:
  • Division by zero will show an error
  • Invalid operands will be caught
  • Malformed expressions will prompt you

╚════════════════════════════════════════════════════════════╝
"""
    print(help_text)


def display_banner() -> None:
    """Display welcome banner."""
    banner = """
╔════════════════════════════════════════════════════════════╗
║                    CALCULATOR V3                          ║
║           Advanced Interactive Calculator                 ║
║                                                            ║
║  Type 'help' for commands or enter: operand op operand   ║
║  Type 'quit' to exit                                      ║
╚════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main() -> None:
    """
    Main entry point for the calculator application.

    Runs an interactive loop accepting user input for calculations.
    """
    calculator = Calculator()
    display_banner()

    while True:
        try:
            user_input = input("\n➤ ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("\n✓ Thank you for using Calculator V3. Goodbye!")
                break

            if user_input.lower() == "help":
                display_help()
                continue

            if user_input.lower() == "history":
                calculator.display_history()
                continue

            if user_input.lower() == "clear":
                calculator.clear_history()
                continue

            result = calculator.parse_expression(user_input)

            if result.error:
                print(f"\n✗ {result.error_message}")
            else:
                print(f"\n✓ {str(result)}")

        except KeyboardInterrupt:
            print("\n\n✓ Calculator closed. Goodbye!")
            break
        except EOFError:
            print("\n✓ Calculator closed. Goodbye!")
            break


if __name__ == "__main__":
    main()
