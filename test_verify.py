import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
import database
from components.employee_dialog import EmployeeDialog

# Monkey-patch QMessageBox to avoid blocking
QMessageBox.information = lambda *args, **kwargs: None
QMessageBox.warning = lambda *args, **kwargs: None

app = QApplication.instance() or QApplication(sys.argv)
database.init_db()

# Test 1: Open EmployeeDialog
dlg = EmployeeDialog(emp_id=None)
assert dlg.input_dept.isEditable(), "input_dept must be editable!"
print("Check 1: input_dept is editable -> PASS")

# Test 2: Set custom department
test_custom_dept = "Cosmetic Dentistry"
dlg.input_name.setText("Dr. Test Dentist")
dlg.input_kh_name.setText("ដុកទ័រ តេស្ត")
dlg.input_dept.setEditText(test_custom_dept)

# Test 3: Save employee
dlg.save_employee_data()
print("Check 2: Employee saved with custom department -> PASS")

# Test 4: Verify in database
all_depts = database.get_all_departments()
assert test_custom_dept in all_depts, f"{test_custom_dept} not found in all_depts: {all_depts}"
print("Check 3: Custom department found in get_all_departments() -> PASS")

# Clean up test employee
c = database.get_connection()
emp = c.execute("SELECT id FROM employees WHERE name = ?", ("Dr. Test Dentist",)).fetchone()
if emp:
    database.delete_employee(emp[0])
    print("Cleaned up test employee successfully")
c.close()
dlg.close()
print("ALL TESTS PASSED SUCCESSFULLY!")
