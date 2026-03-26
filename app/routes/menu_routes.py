# from flask import Blueprint, render_template, request, flash, redirect, url_for
# from flask_login import login_required
# from ..extensions import db
# from ..models.menu import Category, MenuItem
# from ..routes.decorators import role_required
#
# menu_bp = Blueprint('menu', __name__, url_prefix='/menu')
#
# @menu_bp.route('/')
# @login_required
# @role_required('Admin', 'Manager')
# def list():
#     categories = Category.query.order_by(Category.name).all()
#     return render_template('menu/employees_list.html', categories=categories)
#
# @menu_bp.route('/add', methods=['GET', 'POST'])
# @menu_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
# @role_required('Admin', 'Manager')
# def add_edit(id=None):
#     item = MenuItem.query.get_or_404(id) if id else None
#
#     if request.method == 'POST':
#         name = request.form.get('name', '').strip()
#         price_str = request.form.get('price', '')
#         available = 'available' in request.form
#         category_name = request.form.get('category_name', '').strip()
#
#         if not name or not category_name or not price_str:
#             flash('Item name, category, and price are required!', 'danger')
#             return render_template('menu/add_edit.html', item=item, category_name=category_name)
#
#         try:
#             price = float(price_str)
#         except ValueError:
#             flash('Invalid price format!', 'danger')
#             return render_template('menu/add_edit.html', item=item, category_name=category_name)
#
#         # Get or create category
#         category = Category.query.filter_by(name=category_name).first()
#         if not category:
#             category = Category(name=category_name)
#             db.session.add(category)
#             db.session.flush()  # Get category.id
#             flash(f'New category "{category_name}" created!', 'info')
#
#         # Create or update item
#         if item:
#             item.name = name
#             item.price = price
#             item.available = available
#             item.category_id = category.id
#             flash('Menu item updated successfully!', 'success')
#         else:
#             new_item = MenuItem(
#                 name=name,
#                 price=price,
#                 available=available,
#                 category_id=category.id
#             )
#             db.session.add(new_item)
#             flash('Menu item added successfully!', 'success')
#
#         db.session.commit()
#         return redirect(url_for('menu.list'))
#
#     # GET: prefill category name
#     current_category_name = item.category.name if item else ''
#     return render_template('menu/add_edit.html', item=item, category_name=current_category_name)
#
# @menu_bp.route('/delete/<int:id>')
# @login_required
# @role_required('Admin')
# def delete(id):
#     item = MenuItem.query.get_or_404(id)
#     db.session.delete(item)
#     db.session.commit()
#     flash('Menu item deleted successfully!', 'success')
#     return redirect(url_for('menu.list'))

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from ..extensions import db
from ..models.menu import Category, MenuItem
from ..routes.decorators import role_required

menu_bp = Blueprint('menu', __name__, url_prefix='/menu')


@menu_bp.route('/')
@login_required
@role_required('Admin', 'Manager')
def list():
    categories = Category.query.order_by(Category.name).all()
    return render_template('menu/list.html', categories=categories)  # ← Change to this

@menu_bp.route('/add', methods=['GET', 'POST'])
@menu_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Manager')
def add_edit(id=None):
    item = MenuItem.query.get_or_404(id) if id else None

    # All categories for Select2 dropdown
    all_categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price_str = request.form.get('price', '')
        available = 'available' in request.form
        category_name = request.form.get('category_name', '').strip()

        if not name or not category_name or not price_str:
            flash('Item name, category, and price are required!', 'danger')
            return render_template('menu/add_edit.html',
                                   item=item,
                                   category_name=category_name,
                                   all_categories=all_categories)

        try:
            price = float(price_str)
        except ValueError:
            flash('Invalid price format!', 'danger')
            return render_template('menu/add_edit.html',
                                   item=item,
                                   category_name=category_name,
                                   all_categories=all_categories)

        # Get or create category
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.flush()  # to get id
            flash(f'New category "{category_name}" created!', 'info')

        # Update or create item
        if item:
            item.name = name
            item.price = price
            item.available = available
            item.category_id = category.id
            flash('Menu item updated successfully!', 'success')
        else:
            new_item = MenuItem(
                name=name,
                price=price,
                available=available,
                category_id=category.id
            )
            db.session.add(new_item)
            flash('Menu item added successfully!', 'success')

        db.session.commit()
        return redirect(url_for('menu.list'))

    # GET request
    current_category_name = item.category.name if item else ''
    return render_template('menu/add_edit.html',
                           item=item,
                           category_name=current_category_name,
                           all_categories=all_categories)


@menu_bp.route('/delete/<int:id>')
@login_required
@role_required('Admin')
def delete(id):
    item = MenuItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Menu item deleted successfully!', 'success')
    return redirect(url_for('menu.list'))
