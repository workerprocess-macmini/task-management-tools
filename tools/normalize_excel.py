#!/usr/bin/env python3
"""
Excel Normalization Script - HRIS + Payroll Merger (v2.0)

Merges HRIS and multiple Payroll sheets from an Excel file into a single
normalized master sheet. Supports dynamic sheet selection, auto-detection,
and sequential multi-sheet merging.

Features:
- Dynamic sheet name specification (--hris-sheet, --payroll-sheets)
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
Version: 2.0
Usage: 
  python3 normalize_excel.py <input_file> [output_file] [--hris-sheet NAME] [--payroll-sheets SHEET1,SHEET2] [--merge-all] [--output-sheet NAME]
Examples:
  python3 normalize_excel.py employees.xlsx normalized.xlsx
  python3 normalize_excel.py employees.xlsx normalized.xlsx --hris-sheet HRIS_Employees --payroll-sheets Payroll_Employees,Bonus_Data
  python3 normalize_excel.py employees.xlsx normalized.xlsx --merge-all
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

    def __init__(self, input_file: str, hris_sheet: Optional[str] = None,
                 payroll_sheets: Optional[List[str]] = None,
                 output_sheet: Optional[str] = None,
                 merge_all: bool = False) -> None:
        """
        Initialize the normalizer with input file and optional sheet names.

        Args:
            input_file: Path to input Excel file
            hris_sheet: Override HRIS sheet name (default: HRIS_Employees)
            payroll_sheets: List of payroll sheet names (default: [Payroll_Employees])
            output_sheet: Override output sheet name (default: NORMALIZED_MASTER)
            merge_all: Auto-detect and merge all sheets (overrides payroll_sheets)

        Raises:
            FileNotFoundError: If input file does not exist
        """
        self.input_file = Path(input_file)
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        self.hris_sheet = hris_sheet or self.DEFAULT_HRIS_SHEET
        self.payroll_sheets = payroll_sheets or self.DEFAULT_PAYROLL_SHEETS
        self.output_sheet = output_sheet or self.DEFAULT_OUTPUT_SHEET
        self.merge_all = merge_all

        self.hris_df: Optional[pd.DataFrame] = None
        self.payroll_dfs: Dict[str, pd.DataFrame] = {}
        self.normalized_df: Optional[pd.DataFrame] = None
        self.all_sheet_names: List[str] = []

    def load_all_sheet_names(self) -> bool:
        """
        Load all sheet names from the Excel file.

        Returns:
            True if successful, False otherwise
        """
        try:
            wb = load_workbook(self.input_file)
            self.all_sheet_names = wb.sheetnames
            print(f"✓ Available sheets: {', '.join(self.all_sheet_names)}")
            return True
        except Exception as e:
            print(f"❌ Error loading sheet names: {e}")
            return False

    def find_sheet_name(self, target: str) -> Optional[str]:
        """
        Find sheet name in workbook using case-insensitive matching.

        Args:
            target: Sheet name or pattern to find

        Returns:
            Actual sheet name if found, None otherwise
        """
        target_lower = target.lower()

        # Exact match first (case-insensitive)
        for sheet_name in self.all_sheet_names:
            if sheet_name.lower() == target_lower:
                return sheet_name

        # Partial match (case-insensitive)
        for sheet_name in self.all_sheet_names:
            if target_lower in sheet_name.lower():
                return sheet_name

        return None

    def detect_primary_sheet(self) -> Optional[str]:
        """
        Auto-detect primary sheet (first sheet containing Employee_ID column).

        Returns:
            Sheet name if found, None otherwise
        """
        for sheet_name in self.all_sheet_names:
            try:
                df = pd.read_excel(self.input_file, sheet_name=sheet_name, nrows=0)
                if "Employee_ID" in df.columns:
                    return sheet_name
            except Exception:
                continue

        return None

    def load_hris_sheet(self) -> bool:
        """
        Load HRIS sheet with fallback to case-insensitive matching.

        Returns:
            True if successful, False otherwise
        """
        try:
            sheet_name = self.find_sheet_name(self.hris_sheet)

            if not sheet_name:
                raise ValueError(
                    f"HRIS sheet '{self.hris_sheet}' not found. "
                    f"Available sheets: {', '.join(self.all_sheet_names)}"
                )

            self.hris_df = pd.read_excel(self.input_file, sheet_name=sheet_name)
            print(f"✓ HRIS sheet loaded: '{sheet_name}' ({len(self.hris_df)} rows)")

            if "Employee_ID" not in self.hris_df.columns:
                raise ValueError(f"HRIS sheet must contain 'Employee_ID' column")

            return True

        except Exception as e:
            print(f"❌ Error loading HRIS sheet: {e}")
            return False

    def load_payroll_sheets(self) -> bool:
        """
        Load all payroll sheets with fallback to case-insensitive matching.

        Returns:
            True if all sheets loaded successfully, False otherwise
        """
        try:
            for payroll_sheet in self.payroll_sheets:
                sheet_name = self.find_sheet_name(payroll_sheet)

                if not sheet_name:
                    print(f"⚠ Payroll sheet '{payroll_sheet}' not found")
                    continue

                df = pd.read_excel(self.input_file, sheet_name=sheet_name)
                self.payroll_dfs[sheet_name] = df
                print(f"✓ Payroll sheet loaded: '{sheet_name}' ({len(df)} rows)")

            if not self.payroll_dfs:
                raise ValueError("No payroll sheets loaded")

            return True

        except Exception as e:
            print(f"❌ Error loading payroll sheets: {e}")
            return False

    def auto_merge_all_sheets(self) -> bool:
        """
        Auto-detect primary sheet and load all other sheets as payroll.

        Returns:
            True if successful, False otherwise
        """
        try:
            print("\n🔍 Auto-detecting sheets...")

            # Find primary sheet (has Employee_ID)
            primary = self.detect_primary_sheet()

            if not primary:
                raise ValueError("No sheet with 'Employee_ID' column found")

            self.hris_sheet = primary
            print(f"✓ Primary sheet detected: '{primary}'")

            # Load primary sheet
            self.hris_df = pd.read_excel(self.input_file, sheet_name=primary)
            print(f"✓ Primary sheet loaded: {len(self.hris_df)} rows")

            # Load all other sheets as payroll
            for sheet_name in self.all_sheet_names:
                if sheet_name != primary:
                    try:
                        df = pd.read_excel(self.input_file, sheet_name=sheet_name)
                        self.payroll_dfs[sheet_name] = df
                        print(f"✓ Secondary sheet loaded: '{sheet_name}' ({len(df)} rows)")
                    except Exception as e:
                        print(f"⚠ Skipping sheet '{sheet_name}': {e}")

            return True

        except Exception as e:
            print(f"❌ Error in auto-merge: {e}")
            return False

    def merge_payroll_sheets(self) -> bool:
        """
        Sequentially merge multiple payroll sheets with HRIS.
        Later sheets override earlier sheets on conflicts.

        Returns:
            True if merge successful, False otherwise
        """
        try:
            if self.hris_df is None:
                print("❌ HRIS sheet not loaded")
                return False

            if not self.payroll_dfs:
                print("❌ No payroll sheets loaded")
                return False

            print(f"\n🔗 Merging {len(self.payroll_dfs)} payroll sheet(s)...")

            # Start with HRIS as base
            self.normalized_df = self.hris_df.copy()

            # Sequentially merge each payroll sheet
            for idx, (sheet_name, payroll_df) in enumerate(self.payroll_dfs.items(), 1):
                print(f"  [{idx}/{len(self.payroll_dfs)}] Merging: '{sheet_name}'...")

                # Remove duplicate columns from payroll
                payroll_to_merge = payroll_df.drop(
                    columns=[col for col in self.DUPLICATE_COLUMNS
                             if col in payroll_df.columns],
                    errors='ignore'
                )

                # Merge by Employee_ID (left join - keep all HRIS rows)
                self.normalized_df = pd.merge(
                    self.normalized_df,
                    payroll_to_merge,
                    on="Employee_ID",
                    how="left",
                    suffixes=('', f'_payroll{idx}')  # Handle column name conflicts
                )

            print(f"✓ Merge complete: {len(self.normalized_df)} rows")
            return True

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
                print("❌ Merged data not available")
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

            print("✓ Data standardized")
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
                print("❌ Normalized data not available")
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
        print("  EXCEL NORMALIZATION - HRIS + PAYROLL MERGER v2.0")
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
        description="Excel Normalization - HRIS + Payroll Merger v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default behavior (backward compatible)
  python3 normalize_excel.py input.xlsx output.xlsx
  
  # Specify sheet names explicitly
  python3 normalize_excel.py input.xlsx output.xlsx \\
    --hris-sheet HRIS_Employees \\
    --payroll-sheets Payroll_Employees,Contractor_Payroll
  
  # Auto-merge all sheets
  python3 normalize_excel.py input.xlsx output.xlsx --merge-all
  
  # Custom output sheet name
  python3 normalize_excel.py input.xlsx output.xlsx \\
    --output-sheet MASTER_DATA
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
        "--hris-sheet",
        help="Override HRIS sheet name (default: HRIS_Employees)",
        default=None
    )

    parser.add_argument(
        "--payroll-sheets",
        help="Comma-separated payroll sheet names (default: Payroll_Employees)",
        default=None
    )

    parser.add_argument(
        "--merge-all",
        action="store_true",
        help="Auto-detect primary sheet and merge all others"
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

    # Parse payroll sheets
    payroll_sheets = None
    if args.payroll_sheets:
        payroll_sheets = [s.strip() for s in args.payroll_sheets.split(",")]

    # Run normalization
    try:
        normalizer = ExcelNormalizer(
            input_file=args.input_file,
            hris_sheet=args.hris_sheet,
            payroll_sheets=payroll_sheets,
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
