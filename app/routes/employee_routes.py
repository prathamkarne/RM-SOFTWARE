from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..extensions import db
from ..models.employee import Employee, EmployeeRole
from ..routes.decorators import role_required
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError

employee_bp = Blueprint('employee', __name__, url_prefix='/employees')

@employee_bp.route('/')
@login_required
@role_required('Admin', 'Manager')
def list():
    employees = Employee.query.order_by(Employee.name).all()
    return render_template('employee/employees_list.html', employees=employees)

@employee_bp.route("/employee/add", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        emp = Employee(
            name=request.form["name"],
            age=request.form["age"],
            phone=request.form["phone"],
            aadhaar_no=request.form["aadhaar_no"],
            address=request.form["address"],

            bank_holder_name=request.form["bank_holder_name"],
            bank_account_no=request.form["bank_account_no"],
            linked_mobile=request.form["linked_mobile"],

            role=request.form["role"],
            monthly_salary=request.form["monthly_salary"],

            join_date=request.form["join_date"],
            resign_date=request.form.get("resign_date") or None
        )

        db.session.add(emp)
        db.session.commit()

        flash("Employee Added Successfully!", "success")
        return redirect(url_for("employee_bp.employee_list"))

    return render_template("employee/add_employee.html")

@employee_bp.route('/add', methods=['GET', 'POST'])
@employee_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Manager')
def add_edit(id=None):
    employee = Employee.query.get_or_404(id) if id else None

    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            age_str = request.form.get('age', '')
            phone = request.form.get('phone', '').strip() or None
            address = request.form.get('address', '').strip() or None
            aadhaar_no = request.form.get('aadhaar_no', '').strip() or None
            salary_str = request.form.get('salary', '')
            role_str = request.form.get('role')
            hire_date_str = request.form.get('hire_date')
            resign_date_str = request.form.get('resign_date')

            bank_holder_name = request.form.get('bank_holder_name', '').strip() or None
            bank_account_number = request.form.get('bank_account_number', '').strip() or None
            bank_linked_phone = request.form.get('bank_linked_phone', '').strip() or None

            errors = []

            if not name: errors.append("Full Name is required")
            try:
                age = int(age_str) if age_str else None
                if age is None or age < 18: errors.append("Age must be 18 or older")
            except ValueError:
                errors.append("Age must be a valid number")

            try:
                salary = float(salary_str) if salary_str else None
                if salary is None or salary <= 0: errors.append("Salary must be a positive number")
            except ValueError:
                errors.append("Salary must be a valid number")

            if not hire_date_str: errors.append("Hire Date is required")
            if not role_str or role_str not in [r.value for r in EmployeeRole]:
                errors.append("Please select a valid role")

            resign_date = None
            if resign_date_str:
                try:
                    resign_date = datetime.strptime(resign_date_str, '%Y-%m-%d').date()
                except ValueError:
                    errors.append("Invalid Resign Date format")

            if errors:
                for err in errors: flash(err, 'danger')
                return render_template('employee/add_edit.html', employee=employee)

            hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
            role = EmployeeRole(role_str)

            if employee:
                employee.name = name
                employee.age = age
                employee.phone = phone
                employee.address = address
                employee.aadhaar_no = aadhaar_no
                employee.salary = salary
                employee.role = role
                employee.hire_date = hire_date
                employee.resign_date = resign_date
                employee.bank_holder_name = bank_holder_name
                employee.bank_account_number = bank_account_number
                employee.bank_linked_phone = bank_linked_phone
                flash('Employee updated successfully!', 'success')
            else:
                new_employee = Employee(
                    name=name, age=age, phone=phone, address=address, aadhaar_no=aadhaar_no,
                    salary=salary, role=role, hire_date=hire_date, resign_date=resign_date,
                    bank_holder_name=bank_holder_name, bank_account_number=bank_account_number,
                    bank_linked_phone=bank_linked_phone
                )
                db.session.add(new_employee)
                flash('Employee added successfully!', 'success')

            db.session.commit()
            return redirect(url_for('employee.list'))

        except IntegrityError:
            db.session.rollback()
            flash('Aadhaar number already exists!', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('employee/add_edit.html', employee=employee)

@employee_bp.route('/delete/<int:id>')
@login_required
@role_required('Admin')
def delete(id):
    employee = Employee.query.get_or_404(id)
    try:
        db.session.delete(employee)
        db.session.commit()
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting: {str(e)}', 'danger')
    return redirect(url_for('employee.list'))

@employee_bp.route('/attendance')
@login_required
@role_required('Admin', 'Manager')
def attendance():
    today = date.today()
    employees = Employee.query.filter(
        (Employee.resign_date == None) | (Employee.resign_date > today)
    ).order_by(Employee.name).all()
    return render_template('employee/attendance_select.html', employees=employees)