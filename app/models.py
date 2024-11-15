import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rollno = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    github_id = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    group_code = db.Column(db.String(4), nullable=True)
    password = db.Column(db.String(200), nullable=False)  # New password field
    # Password hashing method
    def set_password(self, password):
        self.password = generate_password_hash(password)
    # Password verification method
    def check_password(self, password):
        return check_password_hash(self.password, password)
class Group(db.Model):
    group_code = db.Column(db.String(4), primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    github_id = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    approval_status = db.Column(db.String(20), default='Pending')
    feedback = db.Column(db.Text, nullable=True)  # New field for feedback
    # Method to append feedback with a timestamp
    def append_feedback(self, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.feedback:
            self.feedback += f'\n[{timestamp}] {message}'
        else:
            self.feedback = f'[{timestamp}] {message}'
# Uncomment to create tables in the database
# db.create_all()
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_super = db.Column(db.Boolean, default=False )
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    # Password hashing method
    def set_password(self, password):
        self.password = generate_password_hash(password)
    # Password verification method
    def check_password(self, password):
        return check_password_hash(self.password, password)