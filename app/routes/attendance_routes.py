import calendar

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import date, datetime
from calendar import Calendar
from sqlalchemy import func

from ..extensions import db
from ..models.employee import Employee
from ..models.attendance import Attendance, AttendanceStatus
from ..models.payroll import Payment, Debt, DebtStatus, PaymentMode   # assuming this exists

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")


@attendance_bp.route("/list/<int:employee_id>", methods=["GET", "POST"])
@login_required
def list(employee_id):

    employee = Employee.query.get_or_404(employee_id)
    today = date.today()

    # ---------------- POST ACTIONS ----------------
    if request.method == "POST":

        # -------- MARK ATTENDANCE --------
        if "mark_attendance" in request.form:
            att_date_str = request.form.get("date")
            status_str = request.form.get("status")

            try:
                att_date = date.fromisoformat(att_date_str)
            except (ValueError, TypeError):
                flash("Invalid date format", "danger")
                return redirect(request.url)

            existing = Attendance.query.filter_by(
                employee_id=employee.id,
                date=att_date
            ).first()

            if existing:
                flash("Attendance already marked for this date", "warning")
            else:
                try:
                    new_att = Attendance(
                        employee_id=employee.id,
                        date=att_date,
                        status=AttendanceStatus[status_str.upper().replace(" ", "_")]
                    )
                    db.session.add(new_att)
                    db.session.commit()
                    flash("Attendance marked successfully", "success")
                except KeyError:
                    flash("Invalid attendance status", "danger")

            return redirect(request.url)

        # -------- ADD DEBT --------
        if "add_debt" in request.form:
            try:
                amount = float(request.form.get("debt_amount"))
                reason = request.form.get("reason") or None

                debt = Debt(
                    employee_id=employee.id,
                    amount=amount,
                    reason=reason,
                    date_taken=today,           # ← usually good to record when debt was given
                    status=DebtStatus.PENDING
                )
                db.session.add(debt)
                db.session.commit()
                flash("Advance / Debt recorded", "success")
            except (ValueError, TypeError):
                flash("Invalid amount", "danger")

            return redirect(request.url)

        # -------- MARK SALARY PAID --------
        if "mark_paid" in request.form:
            total_salary = calculate_salary(employee.id)
            total_debt = get_total_pending_debt(employee.id)
            net = total_salary - total_debt

            if net <= 0:
                flash("Nothing to pay this month (or negative balance)", "warning")
                return redirect(request.url)

            payment = Payment(
                employee_id=employee.id,
                amount=net,
                month=today.strftime("%Y-%m"),
                date_paid=today,
                mode=PaymentMode.CASH   # you may want to let user choose mode later
            )

            db.session.add(payment)

            # Mark all pending debts as paid
            pending_debts = Debt.query.filter_by(
                employee_id=employee.id,
                status=DebtStatus.PENDING
            ).all()

            for d in pending_debts:
                d.status = DebtStatus.PAID
                d.paid_on = today

            db.session.commit()
            flash(f"Salary of ₹{net:,.2f} marked as paid", "success")
            return redirect(request.url)

    # ---------------- GET: prepare view data ----------------

    # Calendar (current month by default)
    def get_calendar_data(emp_id, year=None, month=None):
        today = date.today()
        target_year = year or today.year
        target_month = month or today.month

        # We still need Calendar for the grid
        cal = Calendar(firstweekday=6)

        month_days = []
        for week in cal.monthdatescalendar(target_year, target_month):
            for day in week:
                if day.month != target_month:
                    month_days.append({"number": None, "status": None, "date": None})
                else:
                    att = Attendance.query.filter_by(employee_id=emp_id, date=day).first()
                    status = att.status.value if att else None
                    month_days.append({
                        "number": day.day,
                        "status": status,
                        "date": day
                    })

        month_name = calendar.month_name[target_month]  # ← this is correct

        return month_days, month_name, target_year

    calendar_days, month_name, year = get_calendar_data(employee.id)

    # Other data
    summary = calculate_summary(employee.id)
    total_debt = get_total_pending_debt(employee.id)

    existing_payment_this_month = Payment.query.filter_by(
        employee_id=employee.id,
        month=today.strftime("%Y-%m")
    ).first()

    # You may keep these if still used in template (but calendar mostly replaces them)
    attendances = Attendance.query.filter_by(employee_id=employee.id).order_by(Attendance.date.desc()).all()
    debts = Debt.query.filter_by(employee_id=employee.id).order_by(Debt.id.desc()).all()
    payments = Payment.query.filter_by(employee_id=employee.id).order_by(Payment.id.desc()).all()

    return render_template(
        "employee/attendance_detail.html",
        employee=employee,
        today=today,
        calendar_days=calendar_days,
        month_name=month_name,
        year=year,
        summary=summary,
        total_debt=total_debt,
        existing_payment=existing_payment_this_month,
        # optional - remove if not needed anymore
        attendances=attendances,
        debts=debts,
        payments=payments,
    )


# ---------------- HELPER FUNCTIONS ----------------

def calculate_summary(employee_id):
    present = Attendance.query.filter_by(employee_id=employee_id, status=AttendanceStatus.PRESENT).count()
    half    = Attendance.query.filter_by(employee_id=employee_id, status=AttendanceStatus.HALF_DAY).count()
    absent  = Attendance.query.filter_by(employee_id=employee_id, status=AttendanceStatus.ABSENT).count()

    employee = Employee.query.get(employee_id)
    daily = employee.salary / 30 if employee and employee.salary else 0

    salary = present * daily + half * (daily / 2)

    return {
        "present": present,
        "half": half,
        "absent": absent,
        "calculated_salary": salary
    }


def calculate_salary(employee_id):
    return calculate_summary(employee_id)["calculated_salary"]


def get_total_pending_debt(employee_id):
    total = db.session.query(
        func.coalesce(func.sum(Debt.amount), 0)
    ).filter(
        Debt.employee_id == employee_id,
        Debt.status == DebtStatus.PENDING
    ).scalar()
    return total or 0