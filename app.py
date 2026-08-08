from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import date, datetime

from config import Config
from models import db, User, Student, Attendance, Inventory, PropertyLoan
from forms import LoginForm, StudentForm, AttendanceForm, InventoryForm, LoanForm, ReturnForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- Role-based decorator ----------------
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ---------------- Auth Routes ----------------
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}_dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(url_for(f'{user.role}_dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ---------------- Admin Dashboard ----------------
@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    total_students = Student.query.count()
    total_users = User.query.count()
    total_items = Inventory.query.count()
    borrowed = PropertyLoan.query.filter_by(status='borrowed').count()
    return render_template('admin/dashboard.html',
                           total_students=total_students,
                           total_users=total_users,
                           total_items=total_items,
                           borrowed=borrowed)


@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


# ---------------- Registrar Routes ----------------
@app.route('/register')
@login_required
@role_required('register', 'admin')
def register_dashboard():
    students = Student.query.order_by(Student.created_at.desc()).limit(10).all()
    total = Student.query.count()
    return render_template('registrar/dashboard.html', students=students, total=total)


@app.route('/register/students')
@login_required
@role_required('register', 'admin')
def student_list():
    students = Student.query.order_by(Student.full_name).all()
    return render_template('registrar/students.html', students=students)


@app.route('/register/students/add', methods=['GET', 'POST'])
@login_required
@role_required('register', 'admin')
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        existing = Student.query.filter_by(student_id=form.student_id.data).first()
        if existing:
            flash('Student ID already exists!', 'danger')
        else:
            student = Student(
                student_id=form.student_id.data,
                full_name=form.full_name.data,
                grade=form.grade.data,
                section=form.section.data,
                gender=form.gender.data,
                phone=form.phone.data
            )
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('student_list'))
    return render_template('registrar/student_form.html', form=form, title='Add Student')


@app.route('/register/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('register', 'admin')
def edit_student(id):
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    if form.validate_on_submit():
        student.student_id = form.student_id.data
        student.full_name = form.full_name.data
        student.grade = form.grade.data
        student.section = form.section.data
        student.gender = form.gender.data
        student.phone = form.phone.data
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('student_list'))
    return render_template('registrar/student_form.html', form=form, title='Edit Student')


@app.route('/register/students/delete/<int:id>', methods=['POST'])
@login_required
@role_required('register', 'admin')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted.', 'info')
    return redirect(url_for('student_list'))


# ---------------- Attendance Routes ----------------
@app.route('/attendance')
@login_required
@role_required('attendance', 'admin')
def attendance_dashboard():
    today = date.today()
    today_records = Attendance.query.filter_by(date=today).count()
    present = Attendance.query.filter_by(date=today, status='Present').count()
    absent = Attendance.query.filter_by(date=today, status='Absent').count()
    late = Attendance.query.filter_by(date=today, status='Late').count()
    return render_template('attendance/dashboard.html',
                           today=today, today_records=today_records,
                           present=present, absent=absent, late=late)


@app.route('/attendance/mark', methods=['GET', 'POST'])
@login_required
@role_required('attendance', 'admin')
def mark_attendance():
    form = AttendanceForm()
    form.student_id.choices = [(s.id, f"{s.student_id} - {s.full_name}") for s in Student.query.order_by(Student.full_name).all()]
    if form.validate_on_submit():
        # Check if already recorded for this student on this date
        existing = Attendance.query.filter_by(student_id=form.student_id.data, date=form.date.data).first()
        if existing:
            existing.status = form.status.data
            existing.recorded_by = current_user.id
            flash('Attendance updated!', 'success')
        else:
            record = Attendance(
                student_id=form.student_id.data,
                date=form.date.data,
                status=form.status.data,
                recorded_by=current_user.id
            )
            db.session.add(record)
            flash('Attendance recorded!', 'success')
        db.session.commit()
        return redirect(url_for('attendance_list'))
    return render_template('attendance/mark.html', form=form)


@app.route('/attendance/list')
@login_required
@role_required('attendance', 'admin')
def attendance_list():
    records = Attendance.query.order_by(Attendance.date.desc(), Attendance.id.desc()).limit(50).all()
    return render_template('attendance/list.html', records=records)


# ---------------- Property Routes ----------------
@app.route('/property')
@login_required
@role_required('property', 'admin')
def property_dashboard():
    total_items = Inventory.query.count()
    total_qty = db.session.query(db.func.sum(Inventory.quantity)).scalar() or 0
    borrowed = PropertyLoan.query.filter_by(status='borrowed').count()
    returned = PropertyLoan.query.filter_by(status='returned').count()
    return render_template('property/dashboard.html',
                           total_items=total_items, total_qty=total_qty,
                           borrowed=borrowed, returned=returned)


@app.route('/property/inventory')
@login_required
@role_required('property', 'admin')
def inventory_list():
    items = Inventory.query.order_by(Inventory.item_name).all()
    return render_template('property/inventory.html', items=items)


@app.route('/property/inventory/add', methods=['GET', 'POST'])
@login_required
@role_required('property', 'admin')
def add_inventory():
    form = InventoryForm()
    if form.validate_on_submit():
        item = Inventory(
            item_name=form.item_name.data,
            quantity=form.quantity.data,
            description=form.description.data
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('inventory_list'))
    return render_template('property/inventory_form.html', form=form, title='Add Item')


@app.route('/property/loans')
@login_required
@role_required('property', 'admin')
def loan_list():
    loans = PropertyLoan.query.order_by(PropertyLoan.borrowed_date.desc()).all()
    return render_template('property/loans.html', loans=loans)


@app.route('/property/loans/issue', methods=['GET', 'POST'])
@login_required
@role_required('property', 'admin')
def issue_loan():
    form = LoanForm()
    form.student_id.choices = [(s.id, f"{s.student_id} - {s.full_name}") for s in Student.query.order_by(Student.full_name).all()]
    form.item_id.choices = [(i.id, f"{i.item_name} (Qty: {i.quantity})") for i in Inventory.query.filter(Inventory.quantity > 0).all()]
    
    if form.validate_on_submit():
        item = Inventory.query.get(form.item_id.data)
        if item.quantity < 1:
            flash('Item out of stock!', 'danger')
        else:
            loan = PropertyLoan(
                student_id=form.student_id.data,
                item_id=form.item_id.data,
                borrowed_date=form.borrowed_date.data,
                issued_by=current_user.id,
                status='borrowed'
            )
            item.quantity -= 1
            db.session.add(loan)
            db.session.commit()
            flash('Item issued successfully!', 'success')
            return redirect(url_for('loan_list'))
    return render_template('property/loan_form.html', form=form)


@app.route('/property/loans/return/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('property', 'admin')
def return_loan(id):
    loan = PropertyLoan.query.get_or_404(id)
    if loan.status == 'returned':
        flash('This item is already returned.', 'info')
        return redirect(url_for('loan_list'))
    
    form = ReturnForm()
    if form.validate_on_submit():
        loan.return_date = form.return_date.data
        loan.status = 'returned'
        loan.item.quantity += 1
        db.session.commit()
        flash('Item marked as returned!', 'success')
        return redirect(url_for('loan_list'))
    return render_template('property/return_form.html', form=form, loan=loan)


# ---------------- Error Handlers ----------------
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


# ---------------- Initialize DB & Default Users ----------------
def create_tables_and_users():
    with app.app_context():
        db.create_all()
        
        # Create default users if they don't exist
        defaults = [
            {'username': 'admin', 'password': 'admin123', 'role': 'admin', 'full_name': 'System Admin'},
            {'username': 'registrar', 'password': 'reg123', 'role': 'register', 'full_name': 'Registrar Officer'},
            {'username': 'attendance', 'password': 'att123', 'role': 'attendance', 'full_name': 'Attendance Controller'},
            {'username': 'property', 'password': 'prop123', 'role': 'property', 'full_name': 'Property Officer'},
        ]
        for u in defaults:
            if not User.query.filter_by(username=u['username']).first():
                user = User(username=u['username'], role=u['role'], full_name=u['full_name'])
                user.set_password(u['password'])
                db.session.add(user)
        db.session.commit()
        print("Database initialized with default users.")


if __name__ == '__main__':
    create_tables_and_users()
    app.run(debug=True, host='0.0.0.0', port=5000)
