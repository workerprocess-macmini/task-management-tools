#!/usr/bin/env python3
"""
Excel Normalization Script - HRIS + Payroll Merger

Merges HRIS_EMPLOYEES and PAYROLL_EMPLOYEES sheets from an Excel file
into a single normalized master sheet. Handles missing data, removes
duplicate columns, and standardizes data types.

Features:
- Left join HRIS (primary) with Payroll (secondary) by Employee_ID
- Removes duplicate columns from Payroll
- Fills missing values with "MISSING"
- Handles terminated employees (keeps them)
- Command-line interface with optional output file specification
- Comprehensive error handling and logging

Author: Developer Agent
Date: 2026-04-15
Version: 1.0
Usage: python3 normalize_excel.py <input_file> [output_file]
Example: python3 normalize_excel.py employees.xlsx normalized_employees.xlsx
"""

import sys
import os
from pathlib import Path
from typing import Tuple, Optional, List

try:
    import pandas as pd
    from openpyxl import Workbook, load_workbook
    from openpyxl.utils.dataframe import dataframe_to_rows
except ImportError as e:
    print(f"❌ ERROR: Required library not installed: {e}")
    print("Install: pip install pandas openpyxl")
    sys.exit(1)


class ExcelNormalizer:
    """
    Handles normalization of HRIS and Payroll Excel sheets.
    """

    # Define columns that should be removed from Payroll (duplicates)
    DUPLICATE_COLUMNS = {
        "Full_Name", "Department_Name", "Cost_Center", "Job_Title",
        "Employment_Type", "Manager_Name", "Work_Location", "Email", "Status"
    }

    # Define final column order for output
    FINAL_COLUMN_ORDER = [
        "Employee_ID", "National_ID", "Full_Name", "Preferred_Name",
        "Gender", "Birth_Date", "Department_Code", "Department_Name",
        "Cost_Center", "Job_Title", "Employment_Type", "Manager_ID",
        "Manager_Name", "Work_Location", "Hire_Date", "Email", "Phone",
        "Status", "Bank_Name", "Bank_Account_Last4", "Tax_ID",
        "Salary_Grade", "Base_Salary", "Pay_Frequency", "Effective_Date"
    ]

    MISSING_VALUE = "MISSING"
    HRIS_SHEET = "HRIS_Employees"  # Case-sensitive: actual sheet name in data
    PAYROLL_SHEET = "Payroll_Employees"  # Case-sensitive: actual sheet name in data
    OUTPUT_SHEET = "NORMALIZED_MASTER"

    def __init__(self, input_file: str) -> None:
        """
        Initialize the normalizer with input file path.

        Args:
            input_file: Path to input Excel file

        Raises:
            FileNotFoundError: If input file does not exist
        """
        self.input_file = Path(input_file)
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        self.hris_df: Optional[pd.DataFrame] = None
        self.payroll_df: Optional[pd.DataFrame] = None
        self.normalized_df: Optional[pd.DataFrame] = None

    def get_sheet_name(self, workbook_path: Path, target_pattern: str) -> Optional[str]:
        """
        Find sheet name in workbook using case-insensitive matching.

        Args:
            workbook_path: Path to Excel file
            target_pattern: Pattern to match (e.g., 'hris', 'payroll')

        Returns:
            Actual sheet name if found, None otherwise
        """
        try:
            from openpyxl import load_workbook as openpyxl_load
            wb = openpyxl_load(workbook_path)
            target_lower = target_pattern.lower()

            for sheet_name in wb.sheetnames:
                if target_lower in sheet_name.lower():
                    return sheet_name

            return None
        except Exception:
            return None

    def load_sheets(self) -> bool:
        """
        Load HRIS and Payroll sheets from Excel file.
        Uses case-insensitive sheet name matching for robustness.

        Returns:
            True if both sheets loaded successfully, False otherwise
        """
        try:
            print(f"📖 Loading sheets from: {self.input_file}")

            # Try exact sheet names first, then case-insensitive matching
            hris_sheet = self.HRIS_SHEET
            payroll_sheet = self.PAYROLL_SHEET

            # Try to find sheets (case-insensitive)
            try:
                self.hris_df = pd.read_excel(self.input_file, sheet_name=hris_sheet)
            except ValueError:
                # Sheet not found with exact name, try case-insensitive
                found_sheet = self.get_sheet_name(self.input_file, "hris")
                if found_sheet:
                    self.hris_df = pd.read_excel(self.input_file, sheet_name=found_sheet)
                    print(f"ℹ  Found HRIS sheet as: '{found_sheet}'")
                else:
                    raise ValueError(f"HRIS sheet not found (tried: {hris_sheet})")

            print(f"✓ HRIS_Employees loaded: {len(self.hris_df)} rows")

            # Load Payroll sheet
            try:
                self.payroll_df = pd.read_excel(self.input_file, sheet_name=payroll_sheet)
            except ValueError:
                # Sheet not found with exact name, try case-insensitive
                found_sheet = self.get_sheet_name(self.input_file, "payroll")
                if found_sheet:
                    self.payroll_df = pd.read_excel(self.input_file, sheet_name=found_sheet)
                    print(f"ℹ  Found Payroll sheet as: '{found_sheet}'")
                else:
                    raise ValueError(f"Payroll sheet not found (tried: {payroll_sheet})")

            print(f"✓ Payroll_Employees loaded: {len(self.payroll_df)} rows")

            return True

        except ValueError as e:
            print(f"❌ Sheet not found: {e}")
            return False
        except Exception as e:
            print(f"❌ Error loading sheets: {e}")
            return False

    def merge_sheets(self) -> bool:
        """
        Merge HRIS and Payroll sheets by Employee_ID (left join).

        Returns:
            True if merge successful, False otherwise
        """
        try:
            if self.hris_df is None or self.payroll_df is None:
                print("❌ Sheets not loaded. Call load_sheets() first.")
                return False

            print("\n🔗 Merging HRIS and Payroll sheets...")

            # Remove duplicate columns from Payroll
            payroll_to_merge = self.payroll_df.drop(
                columns=[col for col in self.DUPLICATE_COLUMNS
                         if col in self.payroll_df.columns],
                errors='ignore'
            )

            # Perform left join (HRIS is primary)
            self.normalized_df = pd.merge(
                self.hris_df,
                payroll_to_merge,
                on="Employee_ID",
                how="left"
            )

            print(f"✓ Merged successfully: {len(self.normalized_df)} rows")
            print(f"  HRIS only: {len(self.hris_df)}")
            print(f"  Both sheets: {len(self.normalized_df[self.normalized_df['Payroll_Emp_Code'].notna()])}")

            return True

        except KeyError as e:
            print(f"❌ Column not found: {e}")
            return False
        except Exception as e:
            print(f"❌ Error during merge: {e}")
            return False

    def standardize_data(self) -> bool:
        """
        Standardize and clean data.

        Returns:
            True if standardization successful, False otherwise
        """
        try:
            if self.normalized_df is None:
                print("❌ Merged data not available.")
                return False

            print("\n🔧 Standardizing data...")

            # Fill missing values with "MISSING"
            self.normalized_df = self.normalized_df.fillna(self.MISSING_VALUE)

            # Trim whitespace from string columns
            string_columns = self.normalized_df.select_dtypes(include=['object']).columns
            for col in string_columns:
                self.normalized_df[col] = self.normalized_df[col].apply(
                    lambda x: str(x).strip() if isinstance(x, str) else x
                )

            print("✓ Data standardized (missing values filled, whitespace trimmed)")
            return True

        except Exception as e:
            print(f"❌ Error during standardization: {e}")
            return False

    def reorder_columns(self) -> bool:
        """
        Reorder columns to match final column order specification.

        Returns:
            True if reordering successful, False otherwise
        """
        try:
            if self.normalized_df is None:
                print("❌ Normalized data not available.")
                return False

            print("\n📋 Reordering columns...")

            # Get columns that exist in the dataframe
            existing_columns = [col for col in self.FINAL_COLUMN_ORDER
                               if col in self.normalized_df.columns]

            # Get any extra columns not in the final order
            extra_columns = [col for col in self.normalized_df.columns
                            if col not in self.FINAL_COLUMN_ORDER]

            # Reorder: final order columns first, then extras
            final_columns = existing_columns + extra_columns
            self.normalized_df = self.normalized_df[final_columns]

            print(f"✓ Columns reordered: {len(final_columns)} total columns")
            return True

        except Exception as e:
            print(f"❌ Error reordering columns: {e}")
            return False

    def export_to_excel(self, output_file: str) -> bool:
        """
        Export normalized data to Excel file.

        Args:
            output_file: Path to output Excel file

        Returns:
            True if export successful, False otherwise
        """
        try:
            if self.normalized_df is None:
                print("❌ Normalized data not available.")
                return False

            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            print(f"\n💾 Exporting to: {output_path}")

            # Write to Excel with openpyxl for better control
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                self.normalized_df.to_excel(
                    writer,
                    sheet_name=self.OUTPUT_SHEET,
                    index=False
                )

            print(f"✓ Exported successfully to: {output_path}")
            print(f"  Sheet name: {self.OUTPUT_SHEET}")
            print(f"  Rows: {len(self.normalized_df)}")
            print(f"  Columns: {len(self.normalized_df.columns)}")

            return True

        except Exception as e:
            print(f"❌ Error exporting to Excel: {e}")
            return False

    def normalize(self, output_file: str) -> bool:
        """
        Execute complete normalization pipeline.

        Args:
            output_file: Path to output Excel file

        Returns:
            True if entire pipeline successful, False otherwise
        """
        print("=" * 70)
        print("  EXCEL NORMALIZATION - HRIS + PAYROLL MERGER")
        print("=" * 70)

        return (
            self.load_sheets() and
            self.merge_sheets() and
            self.standardize_data() and
            self.reorder_columns() and
            self.export_to_excel(output_file)
        )

    def get_statistics(self) -> dict:
        """
        Get statistics about the normalized data.

        Returns:
            Dictionary with normalization statistics
        """
        if self.normalized_df is None:
            return {}

        missing_count = (self.normalized_df == self.MISSING_VALUE).sum().sum()
        total_cells = len(self.normalized_df) * len(self.normalized_df.columns)

        return {
            "total_rows": len(self.normalized_df),
            "total_columns": len(self.normalized_df.columns),
            "missing_cells": missing_count,
            "missing_percentage": (missing_count / total_cells * 100) if total_cells > 0 else 0,
            "columns": list(self.normalized_df.columns)
        }


def print_usage() -> None:
    """Print usage instructions."""
    print("\n" + "=" * 70)
    print("USAGE: python3 normalize_excel.py <input_file> [output_file]")
    print("=" * 70)
    print("\nArguments:")
    print("  input_file   - Path to Excel file with HRIS and Payroll sheets")
    print("  output_file  - Path to output file (default: normalized_<input_file>)")
    print("\nExample:")
    print("  python3 normalize_excel.py employees.xlsx normalized_employees.xlsx")
    print("\nThe script will:")
    print("  1. Read HRIS_EMPLOYEES and PAYROLL_EMPLOYEES sheets")
    print("  2. Merge by Employee_ID (left join)")
    print("  3. Remove duplicate columns")
    print("  4. Fill missing values with 'MISSING'")
    print("  5. Export to NORMALIZED_MASTER sheet in output file")
    print("=" * 70 + "\n")


def main() -> int:
    """
    Main entry point for the script.

    Returns:
        0 if successful, 1 if errors occurred
    """
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print_usage()
        return 1

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"normalized_{Path(input_file).name}"

    # Validate input file
    if not Path(input_file).exists():
        print(f"❌ Error: Input file not found: {input_file}")
        return 1

    # Run normalization
    try:
        normalizer = ExcelNormalizer(input_file)
        success = normalizer.normalize(output_file)

        if success:
            stats = normalizer.get_statistics()
            print("\n" + "=" * 70)
            print("  NORMALIZATION COMPLETE ✓")
            print("=" * 70)
            print(f"Total Rows: {stats['total_rows']}")
            print(f"Total Columns: {stats['total_columns']}")
            print(f"Missing Values: {stats['missing_cells']} ({stats['missing_percentage']:.2f}%)")
            print("=" * 70 + "\n")
            return 0
        else:
            print("\n❌ Normalization failed. Check error messages above.")
            return 1

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
