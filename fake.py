import random
from faker import Faker
from app import create_app, db
from app.models import Student, Group

# Initialize Faker
fake = Faker()

# Create app context
app = create_app()

with app.app_context():
    def generate_students(num=10):
        """Generate temporary student data."""
        for _ in range(num):
            name = fake.name()
            rollno = f"{random.randint(10000, 99999)}"
            phone = fake.phone_number()
            email = fake.unique.email()
            github_id = fake.user_name()
            branch = random.choice(['CSE', 'ECE', 'ME', 'CE', 'IT'])
            password = "password123"  # Use a default password for all
            group_code = None  # Students start without a group

            student = Student(
                name=name,
                rollno=rollno,
                phone=phone,
                email=email,
                github_id=github_id,
                branch=branch,
                group_code=group_code
            )
            student.set_password(password)
            db.session.add(student)

        db.session.commit()
        print(f"{num} students added.")

    def generate_groups(num=5):
        """Generate temporary group data."""
        student_ids = [student.id for student in Student.query.all()]

        for _ in range(num):
            if not student_ids:
                print("No students available to create groups.")
                return

            group_code = f"{random.randint(1000, 9999)}"
            project_name = fake.catch_phrase()
            description = fake.text(max_nb_chars=200)
            github_id = fake.user_name()
            created_by = random.choice(student_ids)
            student_ids.remove(created_by)  # Prevent reusing the same student

            group = Group(
                group_code=group_code,
                project_name=project_name,
                description=description,
                github_id=github_id,
                created_by=created_by,
                approval_status="Pending"
            )
            db.session.add(group)

            # Assign the group_code to the creator
            creator = Student.query.get(created_by)
            creator.group_code = group_code
            db.session.commit()

        print(f"{num} groups added.")

    # Generate data
    print("Seeding the database...")
    generate_students(10)
    generate_groups(5)
    print("Database seeding complete!")
