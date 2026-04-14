#!/usr/bin/env python3
"""
Calculator V3 - Advanced Calculator with Power and Modulo Operations

A fully-featured calculator with support for basic arithmetic, power, and modulo
operations. Includes error handling, command history, and interactive mode.

Author: Development Team
Version: 3.0
"""

from typing import Union, Optional
from dataclasses import dataclass


@dataclass
class CalculationResult:
    """
    Represents the result of a calculation operation.
    
    Attributes:
        value: The calculated result (float)
        error: Boolean flag indicating if an error occurred
        message: Error message if applicable
    """
    value: Optional[float] = None
    error: bool = False
    message: str = ""


class Calculator:
    """
    Advanced calculator supporting +, -, *, /, ** (power), and % (modulo).
    
    Features:
        - Basic arithmetic operations
        - Power and modulo operations
        - Comprehensive error handling
        - Command history tracking
        - Interactive mode with help
    """
    
    def __init__(self) -> None:
        """Initialize the calculator with empty history."""
        self.history: list[str] = []
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
        
        Returns:
            Sum of a and b
        """
        result = float(a + b)
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Subtract two numbers.
        
        Args:
            a: First number (minuend)
            b: Second number (subtrahend)
        
        Returns:
            Difference of a and b
        """
        result = float(a - b)
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
        
        Returns:
            Product of a and b
        """
        result = float(a * b)
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> CalculationResult:
        """
        Divide two numbers with error handling.
        
        Args:
            a: Dividend
            b: Divisor
        
        Returns:
            CalculationResult with value or error flag set
        """
        if b == 0:
            return CalculationResult(
                error=True,
                message="Error: Division by zero"
            )
        result = float(a / b)
        self.history.append(f"{a} / {b} = {result}")
        return CalculationResult(value=result, error=False)
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> float:
        """
        Calculate base raised to the power of exponent.
        
        Args:
            base: The base number
            exponent: The exponent
        
        Returns:
            Result of base ** exponent
        """
        result = float(base ** exponent)
        self.history.append(f"{base} ** {exponent} = {result}")
        return result
    
    def modulo(self, a: Union[int, float], b: Union[int, float]) -> CalculationResult:
        """
        Calculate remainder of a divided by b (modulo operation).
        
        Args:
            a: Dividend
            b: Divisor
        
        Returns:
            CalculationResult with remainder or error flag set
        """
        if b == 0:
            return CalculationResult(
                error=True,
                message="Error: Modulo by zero"
            )
        result = float(a % b)
        self.history.append(f"{a} % {b} = {result}")
        return CalculationResult(value=result, error=False)
    
    def get_history(self) -> list[str]:
        """
        Get the list of all calculations performed.
        
        Returns:
            List of calculation history entries
        """
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear all calculation history."""
        self.history.clear()
    
    def display_history(self) -> str:
        """
        Format history for display.
        
        Returns:
            Formatted history string
        """
        if not self.history:
            return "No calculations yet."
        return "\n".join(f"{i+1}. {entry}" for i, entry in enumerate(self.history))
    
    def help(self) -> str:
        """
        Display help information for available commands.
        
        Returns:
            Help text with all available commands
        """
        return """
Calculator V3 - Help

Available Operations:
  add <a> <b>        - Addition: a + b
  sub <a> <b>        - Subtraction: a - b
  mul <a> <b>        - Multiplication: a * b
  div <a> <b>        - Division: a / b
  pow <base> <exp>   - Power: base ** exponent
  mod <a> <b>        - Modulo: a % b

Special Commands:
  history            - Display calculation history
  clear              - Clear calculation history
  help               - Show this help message
  quit               - Exit the calculator

Examples:
  add 10 5           → 15.0
  pow 2 3            → 8.0
  mod 10 3           → 1.0
  div 10 0           → Error (division by zero)
"""


def main() -> None:
    """
    Run the interactive calculator mode.
    
    Supports command-line input with various operations and special commands.
    """
    calc = Calculator()
    print("Calculator V3 - Interactive Mode")
    print("Type 'help' for commands or 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("calc> ").strip()
            
            if not user_input:
                continue
            
            parts = user_input.split()
            command = parts[0].lower()
            
            if command == "quit":
                print("Goodbye!")
                break
            
            elif command == "help":
                print(calc.help())
            
            elif command == "history":
                print(calc.display_history())
            
            elif command == "clear":
                calc.clear_history()
                print("History cleared.")
            
            elif command == "add":
                if len(parts) < 3:
                    print("Error: add requires two numbers")
                    continue
                result = calc.add(float(parts[1]), float(parts[2]))
                print(f"Result: {result}")
            
            elif command == "sub":
                if len(parts) < 3:
                    print("Error: sub requires two numbers")
                    continue
                result = calc.subtract(float(parts[1]), float(parts[2]))
                print(f"Result: {result}")
            
            elif command == "mul":
                if len(parts) < 3:
                    print("Error: mul requires two numbers")
                    continue
                result = calc.multiply(float(parts[1]), float(parts[2]))
                print(f"Result: {result}")
            
            elif command == "div":
                if len(parts) < 3:
                    print("Error: div requires two numbers")
                    continue
                result = calc.divide(float(parts[1]), float(parts[2]))
                if result.error:
                    print(f"{result.message}")
                else:
                    print(f"Result: {result.value}")
            
            elif command == "pow":
                if len(parts) < 3:
                    print("Error: pow requires two numbers")
                    continue
                result = calc.power(float(parts[1]), float(parts[2]))
                print(f"Result: {result}")
            
            elif command == "mod":
                if len(parts) < 3:
                    print("Error: mod requires two numbers")
                    continue
                result = calc.modulo(float(parts[1]), float(parts[2]))
                if result.error:
                    print(f"{result.message}")
                else:
                    print(f"Result: {result.value}")
            
            else:
                print(f"Unknown command: {command}. Type 'help' for available commands.")
        
        except ValueError:
            print("Error: Invalid input. Please enter numbers only.")
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
