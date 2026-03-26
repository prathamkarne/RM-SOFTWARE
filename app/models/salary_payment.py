from ..extensions import db
from datetime import date


class SalaryPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"))

    salary_month = db.Column(db.String(7))  # YYYY-MM
    fixed_salary = db.Column(db.Float)

    total_debt_deducted = db.Column(db.Float)
    net_paid = db.Column(db.Float)

    payment_date = db.Column(db.Date, default=date.today)
    mode = db.Column(db.String(20))
