#!/usr/bin/env python3
"""
Excel Normalization Script - HRIS + Payroll Merger (v2.1)

Merges HRIS and multiple Payroll sheets from an Excel file into a single
normalized master sheet. Supports dynamic sheet selection, auto-detection,
and sequential multi-sheet merging.

Features:
- Simplified --sheets parameter for specifying sheets
- Multiple payroll sheets support (comma-separated list)
- Auto-merge all sheets (--merge-all flag)
- Left join HRIS (primary) with Payroll sheets (secondary)
- Removes duplicate columns from Payroll
- Fills missing values with "MISSING"
- Handles terminated employees (keeps them)
- Case-insensitive sheet name matching with fallback
- Comprehensive error handling and logging

Author: Developer Agent
Date: 2026-04-15
Version: 2.1
Usage:
  python3 normalize_excel.py <input_file> <output_file> [--sheets SHEET1,SHEET2,...] [--merge-all] [--output-sheet NAME]

Examples:
  # Default behavior (backward compatible)
  python3 normalize_excel.py input.xlsx output.xlsx

  # Specify sheet names (first=HRIS, rest=Payroll)
  python3 normalize_excel.py input.xlsx output.xlsx --sheets HRIS_Employees,Payroll_Employees

  # Multiple payroll sheets
  python3 normalize_excel.py input.xlsx output.xlsx --sheets HRIS_Employees,Payroll_Employees,Bonus_Data

  # Auto-merge all sheets
  python3 normalize_excel.py input.xlsx output.xlsx --merge-all

  # Custom output sheet name
  python3 normalize_excel.py input.xlsx output.xlsx --sheets HRIS_Employees,Payroll_Employees --output-sheet MY_DATA
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Set

try:
    import pandas as pd
    from openpyxl import load_workbook
except ImportError as e:
    print(f"❌ ERROR: Required library not installed: {e}")
    print("Install: pip install pandas openpyxl")
    sys.exit(1)


class ExcelNormalizer:
    """
    Handles normalization of HRIS and multiple Payroll Excel sheets.
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

    # Default sheet names
    DEFAULT_HRIS_SHEET = "HRIS_Employees"
    DEFAULT_PAYROLL_SHEETS = ["Payroll_Employees"]

    MISSING_VALUE = "MISSING"
    DEFAULT_OUTPUT_SHEET = "NORMALIZED_MASTER"

    def __init__(self, input_file: str, sheets: Optional[List[str]] = None,
                 output_sheet: Optional[str] = None,
                 merge_all: bool = False) -> None:
        """
        Initialize the normalizer with input file and optional sheet names.

        Args:
            input_file: Path to input Excel file
            sheets: List of sheet names where first=HRIS, rest=Payroll
                   Default: [HRIS_Employees, Payroll_Employees]
            output_sheet: Override output sheet name (default: NORMALIZED_MASTER)
            merge_all: Auto-detect and merge all sheets (overrides sheets parameter)

        Raises:
            FileNotFoundError: If input file does not exist
        """
        self.input_file = Path(input_file)
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Parse sheets: first is HRIS, rest are Payroll
        if sheets and len(sheets) > 0:
            self.hris_sheet = sheets[0]
            self.payroll_sheets = sheets[1:] if len(sheets) > 1 else self.DEFAULT_PAYROLL_SHEETS
        else:
            self.hris_sheet = self.DEFAULT_HRIS_SHEET
            self.payroll_sheets = self.DEFAULT_PAYROLL_SHEETS

        self.output_sheet = output_sheet or self.DEFAULT_OUTPUT_SHEET
        self.merge_all = merge_all

        self.hris_df: Optional[pd.DataFrame] = None
        self.payroll_dfs: Dict[str, pd.DataFrame] = {}
        self.normalized_df: Optional[pd.DataFrame] = None
        self.all_sheet_names: List[str] = []

    def load_all_sheet_names(self) -> bool:
        """
        Load all sheet names from input file.

        Returns:
            True if successful, False otherwise
        """
        try:
            workbook = load_workbook(self.input_file, read_only=True, data_only=True)
            self.all_sheet_names = workbook.sheetnames
            print(f"✓ Found {len(self.all_sheet_names)} sheets: {', '.join(self.all_sheet_names)}")
            return True
        except Exception as e:
            print(f"❌ Error loading sheet names: {e}")
            return False

    def find_sheet_name(self, target: str) -> Optional[str]:
        """
        Find sheet name with case-insensitive matching and fallback strategies.

        Args:
            target: Target sheet name to find

        Returns:
            Actual sheet name if found, None otherwise
        """
        # Exact match
        if target in self.all_sheet_names:
            return target

        # Case-insensitive match
        target_lower = target.lower()
        for sheet in self.all_sheet_names:
            if sheet.lower() == target_lower:
                return sheet

        # Partial match (for flexibility)
        for sheet in self.all_sheet_names:
            if target_lower in sheet.lower() or sheet.lower() in target_lower:
                return sheet

        return None

    def detect_primary_sheet(self) -> Optional[str]:
        """
        Auto-detect primary sheet (first sheet containing Employee_ID).

        Returns:
            Name of primary sheet if found, None otherwise
        """
        for sheet in self.all_sheet_names:
            try:
                df = pd.read_excel(self.input_file, sheet_name=sheet, nrows=1)
                if "Employee_ID" in df.columns:
                    print(f"✓ Primary sheet detected: {sheet}")
                    return sheet
            except Exception:
                continue
        return None

    def load_hris_sheet(self) -> bool:
        """
        Load HRIS sheet from Excel file.

        Returns:
            True if successful, False otherwise
        """
        try:
            sheet_name = self.find_sheet_name(self.hris_sheet)
            if not sheet_name:
                print(f"❌ HRIS sheet not found: {self.hris_sheet}")
                return False

            print(f"\n📂 Loading HRIS sheet: {sheet_name}")
            self.hris_df = pd.read_excel(self.input_file, sheet_name=sheet_name)

            if "Employee_ID" not in self.hris_df.columns:
                print(f"❌ Employee_ID column not found in {sheet_name}")
                return False

            print(f"✓ Loaded {len(self.hris_df)} rows from {sheet_name}")
            return True

        except Exception as e:
            print(f"❌ Error loading HRIS sheet: {e}")
            return False

    def load_payroll_sheets(self) -> bool:
        """
        Load all payroll sheets from Excel file.

        Returns:
            True if at least one sheet loaded, False otherwise
        """
        try:
            print(f"\n📂 Loading payroll sheets...")
            for payroll_sheet in self.payroll_sheets:
                sheet_name = self.find_sheet_name(payroll_sheet)
                if not sheet_name:
                    print(f"⚠️  Payroll sheet not found: {payroll_sheet}")
                    continue

                df = pd.read_excel(self.input_file, sheet_name=sheet_name)
                self.payroll_dfs[sheet_name] = df
                print(f"✓ Loaded {len(df)} rows from {sheet_name}")

            if not self.payroll_dfs:
                print("❌ No payroll sheets loaded")
                return False

            return True

        except Exception as e:
            print(f"❌ Error loading payroll sheets: {e}")
            return False

    def auto_merge_all_sheets(self) -> bool:
        """
        Auto-detect primary sheet and merge all other sheets as payroll.

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n📂 Auto-merge mode: Detecting primary sheet...")
            primary_sheet = self.detect_primary_sheet()

            if not primary_sheet:
                print("❌ Could not auto-detect primary sheet (no Employee_ID found)")
                return False

            # Set HRIS to primary
            self.hris_sheet = primary_sheet

            # Load HRIS
            if not self.load_hris_sheet():
                return False

            # Set payroll sheets to all others
            self.payroll_sheets = [s for s in self.all_sheet_names if s != primary_sheet]

            if not self.payroll_sheets:
                print("⚠️  No additional sheets found to merge as payroll")
                return True

            # Load payroll sheets
            return self.load_payroll_sheets()

        except Exception as e:
            print(f"❌ Error in auto-merge: {e}")
            return False

    def merge_payroll_sheets(self) -> bool:
        """
        Sequentially merge multiple payroll sheets with HRIS.
        Later sheets override earlier sheets on conflicts.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.hris_df is None:
                print("❌ HRIS data not loaded")
                return False

            if not self.payroll_dfs:
                print("⚠️  No payroll sheets to merge")
                self.normalized_df = self.hris_df.copy()
                return True

            print(f"\n🔗 Merging {len(self.payroll_dfs)} payroll sheet(s)...")
            result_df = self.hris_df.copy()

            for i, (sheet_name, payroll_df) in enumerate(self.payroll_dfs.items(), 1):
                # Remove duplicate columns
                cols_to_remove = [col for col in payroll_df.columns
                                 if col in self.DUPLICATE_COLUMNS and col != "Employee_ID"]
                payroll_df_clean = payroll_df.drop(columns=cols_to_remove, errors='ignore')

                # Merge
                result_df = pd.merge(
                    result_df,
                    payroll_df_clean,
                    on="Employee_ID",
                    how="left",
                    suffixes=("", f"_{sheet_name}")
                )
                print(f"✓ Merged {sheet_name} ({len(payroll_df)} rows)")

            self.normalized_df = result_df
            print(f"✓ Final merged result: {len(self.normalized_df)} rows, {len(self.normalized_df.columns)} columns")
            return True

        except Exception as e:
            print(f"❌ Error merging payroll sheets: {e}")
            return False

    def standardize_data(self) -> bool:
        """
        Standardize data types and handle missing values.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.normalized_df is None:
                print("❌ Normalized data not available")
                return False

            print(f"\n📋 Standardizing data...")

            # Fill missing values
            self.normalized_df = self.normalized_df.fillna(self.MISSING_VALUE)

            # Clean string columns
            string_columns = self.normalized_df.select_dtypes(include=['object']).columns
            for col in string_columns:
                self.normalized_df[col] = self.normalized_df[col].astype(str).str.strip()

            print(f"✓ Data standardized")
            return True

        except Exception as e:
            print(f"❌ Error standardizing data: {e}")
            return False

    def reorder_columns(self) -> bool:
        """
        Reorder columns to final standard order.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.normalized_df is None:
                print("❌ Normalized data not available")
                return False

            print(f"\n📊 Reordering columns...")

            # Get columns that exist in the dataframe
            existing_columns = [col for col in self.FINAL_COLUMN_ORDER
                               if col in self.normalized_df.columns]

            # Get any extra columns not in the final order
            extra_columns = [col for col in self.normalized_df.columns
                            if col not in self.FINAL_COLUMN_ORDER]

            # Reorder: final order columns first, then extras
            final_columns = existing_columns + extra_columns
            self.normalized_df = self.normalized_df[final_columns]

            print(f"✓ Columns reordered: {len(final_columns)} total")
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
                print("❌ Normalized data not available")
                return False

            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            print(f"\n💾 Exporting to: {output_path}")

            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                self.normalized_df.to_excel(
                    writer,
                    sheet_name=self.output_sheet,
                    index=False
                )

            print(f"✓ Exported successfully")
            print(f"  Sheet name: {self.output_sheet}")
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
        print("  EXCEL NORMALIZATION - HRIS + PAYROLL MERGER v2.1")
        print("=" * 70)

        return (
            self.load_all_sheet_names() and
            (self.auto_merge_all_sheets() if self.merge_all else
             (self.load_hris_sheet() and self.load_payroll_sheets())) and
            self.merge_payroll_sheets() and
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


def create_parser() -> argparse.ArgumentParser:
    """Create and return argument parser."""
    parser = argparse.ArgumentParser(
        description="Excel Normalization - HRIS + Payroll Merger v2.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default behavior (backward compatible)
  python3 normalize_excel.py input.xlsx output.xlsx

  # Specify sheet names (first=HRIS, rest=Payroll)
  python3 normalize_excel.py input.xlsx output.xlsx \\
    --sheets HRIS_Employees,Payroll_Employees

  # Multiple payroll sheets
  python3 normalize_excel.py input.xlsx output.xlsx \\
    --sheets HRIS_Employees,Payroll_Employees,Bonus_Data

  # Auto-merge all sheets
  python3 normalize_excel.py input.xlsx output.xlsx --merge-all

  # Custom output sheet name
  python3 normalize_excel.py input.xlsx output.xlsx \\
    --sheets HRIS_Employees,Payroll_Employees \\
    --output-sheet MY_DATA
        """
    )

    parser.add_argument(
        "input_file",
        help="Path to input Excel file"
    )

    parser.add_argument(
        "output_file",
        help="Path to output Excel file"
    )

    parser.add_argument(
        "--sheets",
        help="Comma-separated sheet names (first=HRIS, rest=Payroll). Default: HRIS_Employees,Payroll_Employees",
        default=None
    )

    parser.add_argument(
        "--merge-all",
        action="store_true",
        help="Auto-detect primary sheet and merge all other sheets"
    )

    parser.add_argument(
        "--output-sheet",
        help="Override output sheet name (default: NORMALIZED_MASTER)",
        default=None
    )

    return parser


def main() -> int:
    """
    Main entry point for the script.

    Returns:
        0 if successful, 1 if errors occurred
    """
    parser = create_parser()
    args = parser.parse_args()

    # Validate input file
    if not Path(args.input_file).exists():
        print(f"❌ Error: Input file not found: {args.input_file}")
        return 1

    # Parse sheets
    sheets = None
    if args.sheets:
        sheets = [s.strip() for s in args.sheets.split(",")]

    # Run normalization
    try:
        normalizer = ExcelNormalizer(
            input_file=args.input_file,
            sheets=sheets,
            output_sheet=args.output_sheet,
            merge_all=args.merge_all
        )

        success = normalizer.normalize(args.output_file)

        if success:
            stats = normalizer.get_statistics()
            print("\n" + "=" * 70)
            print("  NORMALIZATION COMPLETE ✓")
            print("=" * 70)
            print(f"Total Rows:        {stats['total_rows']}")
            print(f"Total Columns:     {stats['total_columns']}")
            print(f"Missing Values:    {stats['missing_cells']} ({stats['missing_percentage']:.2f}%)")
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
