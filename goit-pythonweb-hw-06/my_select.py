from sqlalchemy import func, select
from connect import session
from models import Grade, Group, Student, Subject, Teacher


def select_1():
    avg_grade = func.round(func.avg(Grade.grade), 2).label("avg_grade")
    stmt = (
        select(Student.name, avg_grade)
        .join(Grade)
        .group_by(Student.id)
        .order_by(avg_grade.desc())
        .limit(5)
    )
    return session.execute(stmt).all()


def select_2(subject_name):
    avg_grade = func.round(func.avg(Grade.grade), 2).label("avg_grade")
    stmt = (
        select(Student.name, avg_grade)
        .join(Grade)
        .join(Subject)
        .where(Subject.name == subject_name)
        .group_by(Student.id)
        .order_by(avg_grade.desc())
        .limit(1)
    )
    return session.execute(stmt).first()


def select_3(subject_name):
    avg_grade = func.round(func.avg(Grade.grade), 2).label("avg_grade")
    stmt = (
        select(Group.name, avg_grade)
        .join(Student, Student.group_id == Group.id)
        .join(Grade, Grade.student_id == Student.id)
        .join(Subject, Subject.id == Grade.subject_id)
        .where(Subject.name == subject_name)
        .group_by(Group.id)
    )
    return session.execute(stmt).all()


def select_4():
    stmt = select(func.round(func.avg(Grade.grade), 2))
    return session.execute(stmt).scalar()


def select_5(teacher_name):
    stmt = select(Subject.name).join(Teacher).where(Teacher.name == teacher_name)
    return session.execute(stmt).scalars().all()


def select_6(group_name):
    stmt = select(Student.name).join(Group).where(Group.name == group_name)
    return session.execute(stmt).scalars().all()


def select_7(group_name, subject_name):
    stmt = (
        select(Student.name, Grade.grade, Grade.date_received)
        .join(Student, Grade.student_id == Student.id)
        .join(Group, Student.group_id == Group.id)
        .join(Subject, Grade.subject_id == Subject.id)
        .where(Group.name == group_name, Subject.name == subject_name)
    )
    return session.execute(stmt).all()


def select_8(teacher_name):
    stmt = (
        select(func.round(func.avg(Grade.grade), 2))
        .join(Subject, Grade.subject_id == Subject.id)
        .join(Teacher, Subject.teacher_id == Teacher.id)
        .where(Teacher.name == teacher_name)
    )
    return session.execute(stmt).scalar()


def select_9(student_name):
    stmt = (
        select(Subject.name)
        .join(Grade, Grade.subject_id == Subject.id)
        .join(Student, Grade.student_id == Student.id)
        .where(Student.name == student_name)
        .distinct()
    )
    return session.execute(stmt).scalars().all()


def select_10(teacher_name, student_name):
    stmt = (
        select(Subject.name)
        .join(Teacher, Subject.teacher_id == Teacher.id)
        .join(Grade, Grade.subject_id == Subject.id)
        .join(Student, Grade.student_id == Student.id)
        .where(Teacher.name == teacher_name, Student.name == student_name)
        .distinct()
    )
    return session.execute(stmt).scalars().all()


if __name__ == "__main__":
    sample_group = session.execute(select(Group.name).limit(1)).scalar()
    sample_subject = session.execute(select(Subject.name).limit(1)).scalar()
    sample_teacher = session.execute(select(Teacher.name).limit(1)).scalar()
    sample_student = session.execute(select(Student.name).limit(1)).scalar()

    print("select_1:", select_1())
    print("select_2:", select_2(sample_subject))
    print("select_3:", select_3(sample_subject))
    print("select_4:", select_4())
    print("select_5:", select_5(sample_teacher))
    print("select_6:", select_6(sample_group))
    print("select_7:", select_7(sample_group, sample_subject))
    print("select_8:", select_8(sample_teacher))
    print("select_9:", select_9(sample_student))
    print("select_10:", select_10(sample_teacher, sample_student))
