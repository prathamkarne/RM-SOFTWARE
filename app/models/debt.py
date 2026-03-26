# from ..extensions import db
# from enum import Enum
# from datetime import date
#
#
# class PaymentMode(Enum):
#     CASH = "Cash"
#     ONLINE = "Online"
#
#
# class DebtStatus(Enum):
#     PENDING = "Pending"
#     PAID = "Paid"
#
#
# class Debt(db.Model):
#     __tablename__ = "debt"
#
#     id = db.Column(db.Integer, primary_key=True)
#
#     employee_id = db.Column(
#         db.Integer,
#         db.ForeignKey("employee.id"),
#         nullable=False
#     )
#
#     amount = db.Column(db.Float, nullable=False)
#
#     # For Partial Clear Support
#     remaining_amount = db.Column(db.Float, nullable=False)
#
#     date_taken = db.Column(db.Date, default=date.today)
#
#     mode = db.Column(db.Enum(PaymentMode))
#     reason = db.Column(db.String(255))
#
#     status = db.Column(
#         db.Enum(DebtStatus),
#         default=DebtStatus.PENDING
#     )
#
#     paid_on = db.Column(db.Date, nullable=True)
#
#     def __repr__(self):
#         return f"<Debt ₹{self.remaining_amount}>"
