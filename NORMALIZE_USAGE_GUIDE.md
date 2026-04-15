# 📖 Excel Normalization Script - Usage Guide

## 🎯 Overview (ภาพรวม)

**normalize_excel.py** เป็น script ที่ใช้รวม (merge) ข้อมูล HRIS และ Payroll จากไฟล์ Excel ที่มี 2 sheets เข้าเป็น 1 sheet ที่ normalized (เรียบร้อยและมาตรฐาน)

---

## 📋 What It Does (มันทำอะไร?)

### Input (ขาเข้า):
- ไฟล์ Excel ที่มี **2 sheets**:
  - Sheet 1: `HRIS_Employees` (ข้อมูลพนักงานทั่วไป)
  - Sheet 2: `Payroll_Employees` (ข้อมูลเงินเดือน)

### Process (ขั้นตอน):
1. **อ่านข้อมูล** — อ่าน 2 sheets จากไฟล์ Excel
2. **ลบคอลัมน์ซ้ำ** — ลบคอลัมน์ที่ซ้ำกันจาก Payroll sheet
3. **รวมข้อมูล** — รวม HRIS + Payroll โดยใช้ Employee_ID เป็น key
4. **เติมค่าที่หายไป** — ถ้าหายค่า ใส่ "MISSING"
5. **ตั้งลำดับคอลัมน์** — จัดเรียงคอลัมน์ให้อยู่ในลำดับที่เหมาะสม
6. **บันทึก** — บันทึกผลลัพธ์ลงในไฟล์ Excel ใหม่

### Output (ขาออก):
- ไฟล์ Excel ใหม่ที่มี **1 sheet** (NORMALIZED_MASTER)
- ข้อมูลที่รวมกันอย่างเรียบร้อย 26 คอลัมน์

---

## 🚀 Quick Start (เริ่มต้นใช้งาน)

### Step 1: ติดตั้ง Dependencies (ค่อนข้างอ่านแบบ One-time)
```bash
python3 -m pip install --break-system-packages pandas openpyxl
```

### Step 2: รัน Script
```bash
python ~/Downloads/task-management-tools/tools/normalize_excel.py \
  ~/Downloads/hr_normalization_sample.xlsx \
  ~/Downloads/normalized_output.xlsx
```

### Step 3: ตรวจสอบผลลัพธ์
- ไฟล์ output: `~/Downloads/normalized_output.xlsx`
- Sheet name: `NORMALIZED_MASTER`
- ตัวอักษรจำนวนแถว, คอลัมน์ เป็นเท่าไหร่

---

## 💡 Usage Examples (ตัวอย่างการใช้)

### Example 1: Basic Usage (ใช้ง่าย ๆ)
```bash
python normalize_excel.py input.xlsx output.xlsx
```
- **Input:** input.xlsx
- **Output:** output.xlsx (ชื่อ sheet: NORMALIZED_MASTER)

### Example 2: Default Output Name
```bash
python normalize_excel.py input.xlsx
```
- **Input:** input.xlsx
- **Output:** normalized_input.xlsx (ใช้ชื่อ input + "normalized_" prefix)

### Example 3: From Different Directory
```bash
cd ~/Downloads
python ../task-management-tools/tools/normalize_excel.py \
  hr_sample.xlsx \
  hr_normalized.xlsx
```

### Example 4: With Absolute Path
```bash
python /Users/chatmongkol/Downloads/task-management-tools/tools/normalize_excel.py \
  /Users/chatmongkol/Downloads/input.xlsx \
  /Users/chatmongkol/Downloads/output.xlsx
```

---

## 📊 Data Structure (โครงสร้างข้อมูล)

### Input Sheets:
```
HRIS_Employees (15 rows, 20 columns)
├── Employee_ID
├── National_ID
├── Full_Name
├── Preferred_Name
├── Gender
├── Birth_Date
├── Department_Code
├── Department_Name
├── Cost_Center
├── Job_Title
├── Employment_Type
├── Manager_ID
├── Manager_Name
├── Work_Location
├── Hire_Date
├── Email
├── Phone
└── Status

Payroll_Employees (15 rows, 19 columns)
├── Payroll_Emp_Code
├── Employee_ID
├── Full_Name (duplicate - will be removed)
├── Department_Name (duplicate - will be removed)
├── Cost_Center (duplicate - will be removed)
├── Job_Title (duplicate - will be removed)
├── Employment_Type (duplicate - will be removed)
├── Bank_Name
├── Bank_Account_Last4
├── Tax_ID
├── Salary_Grade
├── Base_Salary
├── Pay_Frequency
├── Manager_Name (duplicate - will be removed)
├── Work_Location (duplicate - will be removed)
├── Email (duplicate - will be removed)
├── Status (duplicate - will be removed)
└── Effective_Date
```

### Output Sheet (NORMALIZED_MASTER):
```
26 columns:
1.  Employee_ID
2.  National_ID
3.  Full_Name
4.  Preferred_Name
5.  Gender
6.  Birth_Date
7.  Department_Code
8.  Department_Name
9.  Cost_Center
10. Job_Title
11. Employment_Type
12. Manager_ID
13. Manager_Name
14. Work_Location
15. Hire_Date
16. Email
17. Phone
18. Status
19. Payroll_Emp_Code
20. Bank_Name
21. Bank_Account_Last4
22. Tax_ID
23. Salary_Grade
24. Base_Salary
25. Pay_Frequency
26. Effective_Date
```

---

## 🔧 Features (ฟีเจอร์ที่มี)

### ✅ Automatic Duplicate Removal
- ลบคอลัมน์ที่ซ้ำกันอัตโนมัติ
- เก็บข้อมูลจาก HRIS เป็นหลัก

### ✅ Case-Insensitive Sheet Matching
- หาชื่อ sheet ได้แม้ว่าตัวพิมพ์ไม่ตรง
- ตัวอย่าง: "HRIS_Employees", "hris_employees", "Hris_Employees" ล้วนได้

### ✅ Missing Value Handling
- เติมค่าที่หายไปด้วย "MISSING"
- ตัวอย่าง: ถ้า Payroll ไม่มี Employee บาง คน ก็จะใส่ "MISSING"

### ✅ Comprehensive Error Handling
- ตรวจสอบไฟล์มีอยู่หรือไม่
- ตรวจสอบ sheet มีอยู่หรือไม่
- ตรวจสอบ Employee_ID column มีอยู่หรือไม่

### ✅ Data Standardization
- ลบ whitespace ที่ไม่ต้องการ
- ทำให้ข้อมูลเรียบร้อยและมาตรฐาน

### ✅ Flexible Output
- สามารถระบุชื่อไฟล์ output ได้
- หรือใช้ชื่อ default

---

## ⚠️ Important Notes (เรื่องที่สำคัญ)

### Sheet Names (ชื่อ Sheet)
Script ต้องการ sheet ที่มีชื่อคล้ายกับ:
- **HRIS sheet:** ต้องมีคำว่า "HRIS" (เช่น HRIS_Employees, HRIS_Data)
- **Payroll sheet:** ต้องมีคำว่า "Payroll" (เช่น Payroll_Employees, Payroll_Data)

### Key Column (คอลัมน์สำคัญ)
- ต้องมี **Employee_ID** column ในทั้ง 2 sheets
- ใช้ Employee_ID เป็น join key

### Duplicate Columns (คอลัมน์ที่ซ้ำ)
ลบออกอัตโนมัติ:
- Full_Name, Department_Name, Cost_Center
- Job_Title, Employment_Type, Manager_Name
- Work_Location, Email, Status

### Missing Values (ค่าที่หายไป)
- เติม "MISSING" เมื่อไม่มีข้อมูล
- ไม่ใช่ empty cell หรือ null

---

## 🧪 Testing (การทดสอบ)

### Run Unit Tests
```bash
cd ~/Downloads/task-management-tools
python tools/normalize_excel_test.py
```

**ผลลัพธ์ที่คาดหวัง:**
```
13/13 tests PASSED ✅
```

---

## 📈 Example Run (ตัวอย่างการรัน)

```bash
$ python normalize_excel.py input.xlsx output.xlsx

📖 Loading sheets from: input.xlsx
✓ HRIS_Employees loaded: 15 rows
✓ Payroll_Employees loaded: 15 rows

🔗 Merging HRIS and Payroll sheets...
✓ Merged successfully: 15 rows
  HRIS only: 15 rows
  Both sheets: 13 rows

🔧 Standardizing data...
✓ Data standardized (missing values filled, whitespace trimmed)

📊 Reordering columns...
✓ Columns reordered: 26 total

💾 Exporting to Excel...
✓ Data exported to: output.xlsx
✓ Sheet name: NORMALIZED_MASTER
✓ Rows: 15 | Columns: 26

✅ Process completed successfully!
```

---

## 🐛 Troubleshooting (แก้ปัญหา)

### Error: "command not found: python3"
```
Solution: ใช้ python แทน python3 หรือ /usr/bin/python3
```

### Error: "pandas not found"
```
Solution: ติดตั้ง: python3 -m pip install --break-system-packages pandas openpyxl
```

### Error: "Sheet not found"
```
Solution: ตรวจสอบชื่อ sheet เป็น HRIS_Employees หรือ Payroll_Employees หรือไม่
```

### Error: "Employee_ID column not found"
```
Solution: ต้องมี Employee_ID column ในทั้ง 2 sheets
```

### Output file is empty
```
Solution: ตรวจสอบว่ามีข้อมูลใน input sheets หรือไม่
```

---

## 📞 Support (ช่วยเหลือ)

- **Code Location:** `~/Downloads/task-management-tools/tools/normalize_excel.py`
- **Tests:** `~/Downloads/task-management-tools/tools/normalize_excel_test.py`
- **Git Branch:** `feature/excel-normalization-hris-payroll`

---

**Version:** 1.0  
**Last Updated:** 2026-04-15  
**Status:** ✅ Production Ready
