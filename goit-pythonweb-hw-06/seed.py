import random

from faker import Faker

from connect import session
from models import Grade, Group, Student, Subject, Teacher

fake = Faker()

GROUP_NAMES = ["AD-101", "PY-201", "JS-301"]
SUBJECT_NAMES = [
    "Mathematics", "Physics", "Chemistry", "Biology", "History",
    "English", "Programming", "Economics",
]
TEACHER_COUNT = 4
STUDENT_COUNT = 40
MAX_GRADES_PER_STUDENT = 20


def clear_data():
    session.query(Grade).delete()
    session.query(Subject).delete()
    session.query(Student).delete()
    session.query(Teacher).delete()
    session.query(Group).delete()
    session.commit()


def seed_groups():
    groups = [Group(name=name) for name in GROUP_NAMES]
    session.add_all(groups)
    session.commit()
    return groups


def seed_teachers():
    teachers = [Teacher(name=fake.name()) for _ in range(TEACHER_COUNT)]
    session.add_all(teachers)
    session.commit()
    return teachers


def seed_subjects(teachers):
    subjects = [
        Subject(name=name, teacher=random.choice(teachers))
        for name in SUBJECT_NAMES
    ]
    session.add_all(subjects)
    session.commit()
    return subjects


def seed_students(groups):
    students = [
        Student(name=fake.name(), group=random.choice(groups))
        for _ in range(STUDENT_COUNT)
    ]
    session.add_all(students)
    session.commit()
    return students


def seed_grades(students, subjects):
    grades = []
    for student in students:
        for _ in range(random.randint(1, MAX_GRADES_PER_STUDENT)):
            grades.append(
                Grade(
                    student=student,
                    subject=random.choice(subjects),
                    grade=random.randint(1, 12),
                    date_received=fake.date_between(start_date="-1y", end_date="today"),
                )
            )
    session.add_all(grades)
    session.commit()
    return grades


def main():
    clear_data()
    groups = seed_groups()
    teachers = seed_teachers()
    subjects = seed_subjects(teachers)
    students = seed_students(groups)
    grades = seed_grades(students, subjects)
    print(
        f"Seeded: {len(groups)} groups, {len(teachers)} teachers, "
        f"{len(subjects)} subjects, {len(students)} students, {len(grades)} grades"
    )


if __name__ == "__main__":
    main()
