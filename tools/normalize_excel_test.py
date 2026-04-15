#!/usr/bin/env python3
"""
Unit Tests for normalize_excel.py (v2.0)

Tests the ExcelNormalizer class with various scenarios:
- Loading sheets
- Dynamic sheet names
- Multiple payroll sheets
- Auto-merge all sheets
- Merging HRIS and Payroll
- Standardizing data
- Handling missing values
- Column reordering
- Case-insensitive sheet matching

Author: Developer Agent
Date: 2026-04-15
Version: 2.0
"""

import unittest
import tempfile
from pathlib import Path
import pandas as pd
from normalize_excel import ExcelNormalizer


class TestExcelNormalizer(unittest.TestCase):
    """Test suite for ExcelNormalizer class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create sample test Excel file with multiple sheets."""
        # Create sample HRIS data
        cls.hris_data = {
            "Employee_ID": ["E1001", "E1002", "E1003"],
            "National_ID": ["1234567890", "1234567891", "1234567892"],
            "Full_Name": ["John Smith", "Jane Doe", "Bob Johnson"],
            "Preferred_Name": ["John", "Jane", "Bob"],
            "Gender": ["M", "F", "M"],
            "Birth_Date": ["1990-01-15", "1988-05-20", "1992-03-10"],
            "Department_Code": ["HR", "IT", "FIN"],
            "Department_Name": ["Human Resources", "Information Tech", "Finance"],
            "Cost_Center": ["CC001", "CC002", "CC003"],
            "Job_Title": ["HR Manager", "Senior Dev", "Accountant"],
            "Employment_Type": ["FT", "FT", "FT"],
            "Manager_ID": ["M001", "M002", "M001"],
            "Manager_Name": ["Alice Brown", "Charlie Davis", "Alice Brown"],
            "Work_Location": ["Bangkok", "Bangkok", "Chiang Mai"],
            "Hire_Date": ["2015-06-01", "2018-02-15", "2020-11-03"],
            "Email": ["john.smith@company.com", "jane.doe@company.com", "bob.johnson@company.com"],
            "Phone": ["66-800-1001", "66-800-1002", "66-800-1003"],
            "Status": ["Active", "Active", "Active"]
        }

        # Create sample Payroll data
        cls.payroll_data = {
            "Payroll_Emp_Code": ["P001", "P002"],
            "Employee_ID": ["E1001", "E1002"],
            "Full_Name": ["John Smith", "Jane Doe"],
            "Department_Name": ["Human Resources", "Information Tech"],
            "Cost_Center": ["CC001", "CC002"],
            "Job_Title": ["HR Manager", "Senior Dev"],
            "Employment_Type": ["FT", "FT"],
            "Bank_Name": ["Bank A", "Bank B"],
            "Bank_Account_Last4": ["1234", "5678"],
            "Tax_ID": ["TAX001", "TAX002"],
            "Salary_Grade": ["G3", "G4"],
            "Base_Salary": [50000, 75000],
            "Pay_Frequency": ["Monthly", "Monthly"],
            "Manager_Name": ["Alice Brown", "Charlie Davis"],
            "Work_Location": ["Bangkok", "Bangkok"],
            "Email": ["john.smith@company.com", "jane.doe@company.com"],
            "Status": ["Active", "Active"],
            "Effective_Date": ["2025-01-01", "2025-01-01"]
        }

        # Create sample Bonus data (additional payroll sheet)
        cls.bonus_data = {
            "Employee_ID": ["E1001", "E1002", "E1003"],
            "Bonus_Year": [2025, 2025, 2025],
            "Bonus_Amount": [5000, 10000, 2000],
            "Bonus_Type": ["Annual", "Annual", "Annual"]
        }

        # Create temporary Excel file
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.test_file = Path(cls.temp_dir.name) / "test_data.xlsx"

        with pd.ExcelWriter(cls.test_file, engine='openpyxl') as writer:
            pd.DataFrame(cls.hris_data).to_excel(
                writer, sheet_name="HRIS_Employees", index=False
            )
            pd.DataFrame(cls.payroll_data).to_excel(
                writer, sheet_name="Payroll_Employees", index=False
            )
            pd.DataFrame(cls.bonus_data).to_excel(
                writer, sheet_name="Bonus_Data", index=False
            )

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up temporary files."""
        cls.temp_dir.cleanup()

    def test_init_valid_file(self) -> None:
        """Test initialization with valid file."""
        normalizer = ExcelNormalizer(str(self.test_file))
        self.assertIsNotNone(normalizer)
        self.assertEqual(normalizer.input_file, self.test_file)

    def test_init_invalid_file(self) -> None:
        """Test initialization with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            ExcelNormalizer("non_existent_file.xlsx")

    def test_load_all_sheet_names(self) -> None:
        """Test loading all available sheet names."""
        normalizer = ExcelNormalizer(str(self.test_file))
        result = normalizer.load_all_sheet_names()

        self.assertTrue(result)
        self.assertGreater(len(normalizer.all_sheet_names), 0)
        self.assertIn("HRIS_Employees", normalizer.all_sheet_names)
        self.assertIn("Payroll_Employees", normalizer.all_sheet_names)
        self.assertIn("Bonus_Data", normalizer.all_sheet_names)

    def test_find_sheet_name_exact_match(self) -> None:
        """Test finding sheet with exact name."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_all_sheet_names()

        result = normalizer.find_sheet_name("HRIS_Employees")
        self.assertEqual(result, "HRIS_Employees")

    def test_find_sheet_name_case_insensitive(self) -> None:
        """Test finding sheet with case-insensitive matching."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_all_sheet_names()

        result = normalizer.find_sheet_name("hris_employees")
        self.assertEqual(result, "HRIS_Employees")

    def test_find_sheet_name_partial_match(self) -> None:
        """Test finding sheet with partial matching."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_all_sheet_names()

        result = normalizer.find_sheet_name("payroll")
        self.assertEqual(result, "Payroll_Employees")

    def test_detect_primary_sheet(self) -> None:
        """Test auto-detection of primary sheet."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_all_sheet_names()

        primary = normalizer.detect_primary_sheet()
        self.assertEqual(primary, "HRIS_Employees")

    def test_load_hris_sheet(self) -> None:
        """Test loading HRIS sheet."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_all_sheet_names()
        result = normalizer.load_hris_sheet()

        self.assertTrue(result)
        self.assertIsNotNone(normalizer.hris_df)
        self.assertEqual(len(normalizer.hris_df), 3)
        self.assertIn("Employee_ID", normalizer.hris_df.columns)

    def test_load_payroll_sheets(self) -> None:
        """Test loading multiple payroll sheets."""
        normalizer = ExcelNormalizer(
            str(self.test_file),
            payroll_sheets=["Payroll_Employees", "Bonus_Data"]
        )
        normalizer.load_all_sheet_names()
        result = normalizer.load_payroll_sheets()

        self.assertTrue(result)
        self.assertEqual(len(normalizer.payroll_dfs), 2)
        self.assertIn("Payroll_Employees", normalizer.payroll_dfs)
        self.assertIn("Bonus_Data", normalizer.payroll_dfs)

    def test_auto_merge_all_sheets(self) -> None:
        """Test auto-merge all sheets functionality."""
        normalizer = ExcelNormalizer(str(self.test_file), merge_all=True)
        normalizer.load_all_sheet_names()
        result = normalizer.auto_merge_all_sheets()

        self.assertTrue(result)
        self.assertIsNotNone(normalizer.hris_df)
        self.assertGreater(len(normalizer.payroll_dfs), 0)

    def test_merge_payroll_sheets(self) -> None:
        """Test merging multiple payroll sheets with HRIS."""
        normalizer = ExcelNormalizer(
            str(self.test_file),
            payroll_sheets=["Payroll_Employees", "Bonus_Data"]
        )
        normalizer.load_all_sheet_names()
        normalizer.load_hris_sheet()
        normalizer.load_payroll_sheets()
        result = normalizer.merge_payroll_sheets()

        self.assertTrue(result)
        self.assertIsNotNone(normalizer.normalized_df)
        # Should have 3 rows (left join keeps all HRIS rows)
        self.assertEqual(len(normalizer.normalized_df), 3)

    def test_standardize_data(self) -> None:
        """Test data standardization."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_all_sheet_names()
        normalizer.load_hris_sheet()
        normalizer.load_payroll_sheets()
        normalizer.merge_payroll_sheets()
        result = normalizer.standardize_data()

        self.assertTrue(result)
        # Check that missing values are filled
        missing_count = (normalizer.normalized_df == "MISSING").sum().sum()
        # E1003 should have missing Payroll data
        self.assertGreater(missing_count, 0)

    def test_reorder_columns(self) -> None:
        """Test column reordering."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_all_sheet_names()
        normalizer.load_hris_sheet()
        normalizer.load_payroll_sheets()
        normalizer.merge_payroll_sheets()
        normalizer.standardize_data()
        result = normalizer.reorder_columns()

        self.assertTrue(result)
        # Check that Employee_ID is first column
        self.assertEqual(normalizer.normalized_df.columns[0], "Employee_ID")

    def test_export_to_excel(self) -> None:
        """Test exporting normalized data to Excel."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "output.xlsx"

            normalizer = ExcelNormalizer(str(self.test_file))
            normalizer.load_all_sheet_names()
            normalizer.load_hris_sheet()
            normalizer.load_payroll_sheets()
            normalizer.merge_payroll_sheets()
            normalizer.standardize_data()
            normalizer.reorder_columns()
            result = normalizer.export_to_excel(str(output_file))

            self.assertTrue(result)
            self.assertTrue(output_file.exists())

            # Verify exported file can be read
            exported_df = pd.read_excel(output_file, sheet_name="NORMALIZED_MASTER")
            self.assertEqual(len(exported_df), 3)

    def test_complete_pipeline_default(self) -> None:
        """Test complete normalization pipeline with default settings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "normalized.xlsx"

            normalizer = ExcelNormalizer(str(self.test_file))
            result = normalizer.normalize(str(output_file))

            self.assertTrue(result)
            self.assertTrue(output_file.exists())

    def test_complete_pipeline_custom_sheets(self) -> None:
        """Test complete pipeline with custom sheet names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "normalized.xlsx"

            normalizer = ExcelNormalizer(
                str(self.test_file),
                payroll_sheets=["Payroll_Employees", "Bonus_Data"]
            )
            result = normalizer.normalize(str(output_file))

            self.assertTrue(result)
            self.assertTrue(output_file.exists())

    def test_complete_pipeline_merge_all(self) -> None:
        """Test complete pipeline with --merge-all flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "normalized.xlsx"

            normalizer = ExcelNormalizer(str(self.test_file), merge_all=True)
            result = normalizer.normalize(str(output_file))

            self.assertTrue(result)
            self.assertTrue(output_file.exists())

    def test_custom_output_sheet_name(self) -> None:
        """Test custom output sheet name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "output.xlsx"

            normalizer = ExcelNormalizer(
                str(self.test_file),
                output_sheet="CUSTOM_MASTER"
            )
            normalizer.load_all_sheet_names()
            normalizer.load_hris_sheet()
            normalizer.load_payroll_sheets()
            normalizer.merge_payroll_sheets()
            normalizer.standardize_data()
            normalizer.reorder_columns()
            result = normalizer.export_to_excel(str(output_file))

            self.assertTrue(result)

            # Verify custom sheet name in output
            exported_df = pd.read_excel(output_file, sheet_name="CUSTOM_MASTER")
            self.assertEqual(len(exported_df), 3)

    def test_get_statistics(self) -> None:
        """Test statistics generation."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_all_sheet_names()
        normalizer.load_hris_sheet()
        normalizer.load_payroll_sheets()
        normalizer.merge_payroll_sheets()
        normalizer.standardize_data()
        normalizer.reorder_columns()

        stats = normalizer.get_statistics()

        self.assertIn("total_rows", stats)
        self.assertIn("total_columns", stats)
        self.assertIn("missing_cells", stats)
        self.assertIn("missing_percentage", stats)
        self.assertEqual(stats["total_rows"], 3)

    def test_left_join_behavior(self) -> None:
        """Test that missing payroll records are kept (left join)."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_all_sheet_names()
        normalizer.load_hris_sheet()
        normalizer.load_payroll_sheets()
        normalizer.merge_payroll_sheets()

        # E1003 has no payroll record
        e1003_row = normalizer.normalized_df[
            normalizer.normalized_df["Employee_ID"] == "E1003"
        ]
        self.assertEqual(len(e1003_row), 1)  # Row exists
        self.assertEqual(e1003_row.iloc[0]["Full_Name"], "Bob Johnson")  # HRIS data present

    def test_duplicate_columns_removed(self) -> None:
        """Test that duplicate columns are removed during merge."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_all_sheet_names()
        normalizer.load_hris_sheet()
        normalizer.load_payroll_sheets()
        normalizer.merge_payroll_sheets()

        # Full_Name should appear only once
        full_name_count = list(normalizer.normalized_df.columns).count("Full_Name")
        self.assertEqual(full_name_count, 1)


def run_tests() -> None:
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
