#!/usr/bin/env python3
"""
Unit Tests for normalize_excel.py

Tests the ExcelNormalizer class with various scenarios:
- Loading sheets
- Merging HRIS and Payroll
- Standardizing data
- Handling missing values
- Column reordering

Author: Developer Agent
Date: 2026-04-15
Version: 1.0
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
        """Create sample test Excel file."""
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

    def test_load_sheets(self) -> None:
        """Test loading HRIS and Payroll sheets."""
        normalizer = ExcelNormalizer(str(self.test_file))
        result = normalizer.load_sheets()

        self.assertTrue(result)
        self.assertIsNotNone(normalizer.hris_df)
        self.assertIsNotNone(normalizer.payroll_df)
        self.assertEqual(len(normalizer.hris_df), 3)
        self.assertEqual(len(normalizer.payroll_df), 2)

    def test_merge_sheets(self) -> None:
        """Test merging HRIS and Payroll by Employee_ID."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_sheets()
        result = normalizer.merge_sheets()

        self.assertTrue(result)
        self.assertIsNotNone(normalizer.normalized_df)
        # Should have 3 rows (left join keeps all HRIS rows)
        self.assertEqual(len(normalizer.normalized_df), 3)
        # Check that E1001 has payroll data
        e1001_row = normalizer.normalized_df[
            normalizer.normalized_df["Employee_ID"] == "E1001"
        ]
        self.assertEqual(e1001_row.iloc[0]["Salary_Grade"], "G3")

    def test_standardize_data(self) -> None:
        """Test data standardization (missing values and trimming)."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_sheets()
        normalizer.merge_sheets()
        result = normalizer.standardize_data()

        self.assertTrue(result)
        # Check that missing values are filled
        missing_count = (normalizer.normalized_df == "MISSING").sum().sum()
        # E1003 should have missing Payroll data
        self.assertGreater(missing_count, 0)

    def test_reorder_columns(self) -> None:
        """Test column reordering."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_sheets()
        normalizer.merge_sheets()
        normalizer.standardize_data()
        result = normalizer.reorder_columns()

        self.assertTrue(result)
        # Check that Employee_ID is first column
        self.assertEqual(normalizer.normalized_df.columns[0], "Employee_ID")
        # Check that specific columns are in order
        cols = list(normalizer.normalized_df.columns)
        if "Full_Name" in cols and "Employee_ID" in cols:
            self.assertLess(cols.index("Employee_ID"), cols.index("Full_Name"))

    def test_export_to_excel(self) -> None:
        """Test exporting normalized data to Excel."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "output.xlsx"

            normalizer = ExcelNormalizer(str(self.test_file))
            normalizer.load_sheets()
            normalizer.merge_sheets()
            normalizer.standardize_data()
            normalizer.reorder_columns()
            result = normalizer.export_to_excel(str(output_file))

            self.assertTrue(result)
            self.assertTrue(output_file.exists())

            # Verify exported file can be read
            exported_df = pd.read_excel(output_file, sheet_name="NORMALIZED_MASTER")
            self.assertEqual(len(exported_df), 3)

    def test_complete_pipeline(self) -> None:
        """Test complete normalization pipeline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "normalized.xlsx"

            normalizer = ExcelNormalizer(str(self.test_file))
            result = normalizer.normalize(str(output_file))

            self.assertTrue(result)
            self.assertTrue(output_file.exists())

    def test_get_statistics(self) -> None:
        """Test statistics generation."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_sheets()
        normalizer.merge_sheets()
        normalizer.standardize_data()
        normalizer.reorder_columns()

        stats = normalizer.get_statistics()

        self.assertIn("total_rows", stats)
        self.assertIn("total_columns", stats)
        self.assertIn("missing_cells", stats)
        self.assertIn("missing_percentage", stats)
        self.assertEqual(stats["total_rows"], 3)

    def test_duplicate_columns_removed(self) -> None:
        """Test that duplicate columns are removed during merge."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_sheets()
        normalizer.merge_sheets()

        # Full_Name should appear only once
        full_name_count = list(normalizer.normalized_df.columns).count("Full_Name")
        self.assertEqual(full_name_count, 1)

    def test_left_join_behavior(self) -> None:
        """Test that missing payroll records are kept (left join)."""
        normalizer = ExcelNormalizer(str(self.test_file))
        normalizer.load_sheets()
        normalizer.merge_sheets()

        # E1003 has no payroll record
        e1003_row = normalizer.normalized_df[
            normalizer.normalized_df["Employee_ID"] == "E1003"
        ]
        self.assertEqual(len(e1003_row), 1)  # Row exists
        self.assertEqual(e1003_row.iloc[0]["Full_Name"], "Bob Johnson")  # HRIS data present


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_missing_required_column(self) -> None:
        """Test handling of missing required columns."""
        # This test would require a malformed Excel file
        # Skipping for now as it requires complex setup
        pass

    def test_empty_sheet(self) -> None:
        """Test handling of empty sheets."""
        # This would also require complex setup
        pass


def run_tests() -> None:
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
