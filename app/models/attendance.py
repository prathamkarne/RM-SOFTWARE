# from ..extensions import db
# from enum import Enum
#
# class AttendanceStatus(Enum):
#     PRESENT = 'Present'
#     ABSENT = 'Absent'
#     HALF_DAY = 'Half Day'
#
# # In models/attendance.py
#
# class Attendance(db.Model):
#     __tablename__ = 'attendance'
#     __table_args__ = {'extend_existing': True}   # ← this line is very important here
#
#     id = db.Column(db.Integer, primary_key=True)
#     employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     status = db.Column(db.Enum(AttendanceStatus), nullable=False)

from enum import Enum
from datetime import date
from ..extensions import db

class AttendanceStatus(Enum):
    PRESENT = 'Present'
    ABSENT = 'Absent'
    HALF_DAY = 'Half Day'

class Attendance(db.Model):
    __tablename__ = 'attendance'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.Enum(AttendanceStatus), nullable=False)
