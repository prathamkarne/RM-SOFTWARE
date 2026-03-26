from ..extensions import db
from enum import Enum
from datetime import date


class EmployeeRole(Enum):
    MANAGER = "Manager"
    CHEF = "Chef"
    WAITER = "Waiter"
    CASHIER = "Cashier"
    HOUSEKEEPING = "Housekeeping"


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)

    aadhaar_no = db.Column(db.String(12), unique=True)

    salary = db.Column(db.Float, nullable=False)

    role = db.Column(db.Enum(EmployeeRole), nullable=False)

    hire_date = db.Column(db.Date, nullable=False)
    resign_date = db.Column(db.Date)

    # Bank Details
    bank_holder_name = db.Column(db.String(120))
    bank_account_number = db.Column(db.String(20))
    bank_linked_phone = db.Column(db.String(15))

    # Lifetime Totals
    total_salary_paid = db.Column(db.Float, default=0)
    total_advance_taken = db.Column(db.Float, default=0)
    total_debt_cleared = db.Column(db.Float, default=0)
    overall_paid = db.Column(db.Float, default=0)

    def __repr__(self):
        return f"<Employee {self.name}>"
