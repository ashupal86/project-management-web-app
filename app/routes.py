from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, Student, Group

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        rollno = request.form.get('rollno')
        phone = request.form.get('phone')
        email = request.form.get('email')
        github_id = request.form.get('github_id')
        branch = request.form.get('branch')
        password = request.form.get('password')
        
        # Check if the email already exists
        if Student.query.filter_by(email=email).first():
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for('main.register'))
        
        # Create a new student instance
        new_student = Student(
            name=name,
            rollno=rollno,
            phone=phone,
            email=email,
            github_id=github_id,
            branch=branch
        )
        
        # Set and hash the password
        new_student.set_password(password)
        
        db.session.add(new_student)
        db.session.commit()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email == 'admin' and password == 'admin@ashu':
            # Admin login
            session['role'] = 'admin'
            return redirect(url_for('main.admin_dashboard'))
        else:
            # Student login
            student = Student.query.filter_by(email=email).first()
            if student and student.check_password(password):
                session['role'] = 'student'
                session['student_id'] = student.id
                session['code']=student.group_code
                if student.group_code:
                    return redirect(url_for('main.group_details', code=student.group_code))
                return redirect(url_for('main.student_dashboard'))
            else:
                flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

@main.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('main.login'))
    return render_template('student_dashboard.html')

@main.route('/create_group', methods=['GET', 'POST'])
def create_group():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        project_name = request.form.get('project_name')
        description = request.form.get('description')
        github_id = request.form.get('github_id')

        # Generate a random 4-digit group code
        group_code = str(random.randint(1000, 9999))

        # Create new group
        new_group = Group(
            project_name=project_name,
            description=description,
            github_id=github_id,
            created_by=session['student_id'],
            group_code=group_code,
            mainroval_status='Pending'
        )
        db.session.add(new_group)
        db.session.commit()

        # Update student to reflect they belong to the group
        student = Student.query.get(session['student_id'])
        student.group_code = group_code
        db.session.commit()

        flash(f"Group created successfully! Your group code is: {group_code}", "success")
        return redirect(url_for('group_details', code=group_code))

    return render_template('create_group.html')
@main.route('/join_group', methods=['GET', 'POST'])
def join_group():
    if 'student_id' not in session:
        # Redirect to login if the user is not logged in
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        group_code = request.form.get('group_code')
        student_id = session['student_id']
        
        # Check if the group exists
        group = Group.query.filter_by(group_code=group_code).first()
        if group:
            # Update the student record to add the group code
            student = Student.query.get(student_id)
            student.group_code = group_code
            db.session.commit()
            flash("Successfully joined the group!", "success")
            return redirect(url_for('main.group_details', code=group_code))
        else:
            flash("Invalid group code. Please try again.", "danger")

    return render_template('join_group.html')

@main.route('/group/details/<code>')
def group_details(code):
    group = Group.query.filter_by(group_code=code).first()
    members = Student.query.filter_by(group_code=code).all()
    return render_template('group_details.html', group=group, members=members)

@main.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('main.login'))
    groups = Group.query.all()
    students = Student.query.all()
    return render_template('admin_dashboard.html', groups=groups, students=students)

@main.route('/admin/group/<group_code>/mainrove', methods=['POST'])
def mainrove_group(group_code):
    group = Group.query.filter_by(group_code=group_code).first()
    if group:
        group.mainroval_status = "mainroved"
        db.session.commit()
        flash(f"Group {group_code} has been mainroved!", "success")
    return redirect(url_for('admin_dashboard'))


@main.route('/deny_group/<group_code>', methods=['POST'])
def deny_group(group_code):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    # Fetch the group by code
    group = Group.query.filter_by(group_code=group_code).first()
    if not group:
        flash("Group not found.", "danger")
        return redirect(url_for('admin_dashboard'))

    # Handle feedback submission
    feedback = request.form.get('feedback')
    if not feedback:
        flash("Please provide feedback before denying the group.", "danger")
        return redirect(url_for('admin_dashboard'))

    # mainend the feedback with a timestamp
    group.append_feedback(feedback)
    group.mainroval_status = 'Denied'
    db.session.commit()

    # Notify group members about the denial
    students_in_group = Student.query.filter_by(group_code=group_code).all()
    for student in students_in_group:
        flash(f"Your group with code {group_code} has been denied. Admin feedback: {feedback}", "danger")

    flash("Group has been denied and feedback has been provided.", "success")
    return redirect(url_for('main.admin_dashboard'))


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))