from app.models import db,Admin
from run import app
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        
        hased_password = generate_password_hash('admin@ashu')
        admin = Admin(username='admin',password=hased_password,email='admin@gmail.com',is_super=True,department='CSE')
        db.session.add(admin)
        db.session.commit()
        print("Admin created successfully")

create_admin()