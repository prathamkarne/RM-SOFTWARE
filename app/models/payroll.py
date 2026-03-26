from ..extensions import db
from enum import Enum
from datetime import date


class PaymentMode(Enum):
    CASH = 'Cash'
    ONLINE = 'Online'


class DebtStatus(Enum):
    PENDING = 'Pending'
    PAID = 'Paid'


# ---------------- PAYMENT MODEL ----------------
class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

    amount = db.Column(db.Float, nullable=False)
    date_paid = db.Column(db.Date, default=date.today)
    month = db.Column(db.String(7), nullable=False)  # YYYY-MM
    mode = db.Column(db.Enum(PaymentMode), default=PaymentMode.CASH)

    def __repr__(self):
        return f"<Payment ₹{self.amount}>"



# ---------------- DEBT MODEL ----------------
class Debt(db.Model):
    __tablename__ = 'debt'
    __table_args__ = {'extend_existing': True}   # ⭐ IMPORTANT FIX

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

    amount = db.Column(db.Float, nullable=False)
    date_taken = db.Column(db.Date, default=date.today)

    mode = db.Column(db.Enum(PaymentMode), default=PaymentMode.CASH)
    reason = db.Column(db.String(255))
    status = db.Column(db.Enum(DebtStatus), default=DebtStatus.PENDING)

    paid_on = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"<Debt ₹{self.amount} - {self.status.value}>"
