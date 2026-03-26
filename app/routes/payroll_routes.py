from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import date

from ..extensions import db
from ..models.employee import Employee
from ..models.payroll import Debt, DebtStatus, PaymentMode
from ..models.salary_payment import SalaryPayment

# Blueprint
payroll_bp = Blueprint("payroll", __name__, url_prefix="/payroll")


# =========================================================
# PAYROLL DASHBOARD
# Route → /payroll/employee/<id>
# =========================================================
@payroll_bp.route("/employee/<int:id>", methods=["GET", "POST"])
@login_required
def payroll_dashboard(id):

    employee = Employee.query.get_or_404(id)

    # Pending Debts FIFO Order
    pending_debts = Debt.query.filter_by(
        employee_id=id,
        status=DebtStatus.PENDING
    ).order_by(Debt.date_taken.asc()).all()

    total_pending = sum(d.remaining_amount for d in pending_debts)

    # =====================================================
    # POST ACTIONS
    # =====================================================
    if request.method == "POST":

        try:
            # =================================================
            # GIVE ADVANCE / CREATE DEBT
            # =================================================
            if "give_advance" in request.form:

                amount = float(request.form["amount"])
                mode = request.form.get("mode", "Cash")
                reason = request.form.get("reason", "")

                if amount <= 0:
                    flash("Amount must be positive", "danger")
                    return redirect(request.url)

                debt = Debt(
                    employee_id=id,
                    amount=amount,
                    remaining_amount=amount,
                    mode=PaymentMode(mode),
                    reason=reason,
                    status=DebtStatus.PENDING
                )

                employee.total_advance_taken += amount

                db.session.add(debt)
                db.session.commit()

                flash("Advance added successfully", "success")

            # =================================================
            # PAY SALARY + CLEAR DEBT
            # =================================================
            if "pay_salary" in request.form:

                clear_amount = float(request.form.get("clear_amount", 0))
                payment_mode = request.form.get("payment_mode", "Cash")

                remaining_clear = clear_amount

                # FIFO Debt Clearing
                for debt in pending_debts:

                    if remaining_clear <= 0:
                        break

                    if debt.remaining_amount <= remaining_clear:

                        remaining_clear -= debt.remaining_amount

                        employee.total_debt_cleared += debt.remaining_amount

                        debt.remaining_amount = 0
                        debt.status = DebtStatus.PAID
                        debt.paid_on = date.today()

                    else:

                        debt.remaining_amount -= remaining_clear
                        employee.total_debt_cleared += remaining_clear
                        remaining_clear = 0

                # Recalculate Pending After Clear
                total_pending = sum(d.remaining_amount for d in pending_debts)

                net_salary = employee.salary - total_pending
                if net_salary < 0:
                    net_salary = 0

                # Salary Payment Record
                payment = SalaryPayment(
                    employee_id=id,
                    salary_month=date.today().strftime("%Y-%m"),
                    fixed_salary=employee.salary,
                    total_debt_deducted=clear_amount,
                    net_paid=net_salary,
                    payment_date=date.today(),
                    mode=payment_mode
                )

                employee.total_salary_paid += net_salary
                employee.overall_paid += net_salary

                db.session.add(payment)
                db.session.commit()

                flash(f"Salary Paid ₹ {net_salary}", "success")

            return redirect(url_for("payroll.payroll_dashboard", id=id))

        except Exception as e:
            db.session.rollback()
            flash(str(e), "danger")
            return redirect(request.url)

    # =====================================================
    # PAYMENT HISTORY
    # =====================================================
    payments = SalaryPayment.query.filter_by(
        employee_id=id
    ).order_by(SalaryPayment.payment_date.desc()).all()

    # =====================================================
    # LIFETIME SUMMARY
    # =====================================================
    lifetime = {
        "total_salary_paid": employee.total_salary_paid,
        "total_advance_taken": employee.total_advance_taken,
        "total_debt_cleared": employee.total_debt_cleared,
        "overall_paid": employee.overall_paid
    }

    return render_template(
        "employee/payroll.html",
        employee=employee,
        pending_debts=pending_debts,
        total_pending=total_pending,
        payments=payments,
        lifetime=lifetime
    )
