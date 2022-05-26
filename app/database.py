# Team Loophole -- Lucas Lee, Andrew Juang, Eliza Knapp, Ella Krechmer, Christopher Liu
# Softdev
# P04 -- Final Project
# 2022-06-15w

import sqlite3

DB_FILE = "loophole.db"


class Student:
    @staticmethod
    def create_db():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS students(
                    student_id          TEXT PRIMARY KEY DEFAULT (hex(randomblob(8))),
                    email               TEXT
                )
                """
            )
            db.commit()

    @staticmethod
    def drop_db():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute("DROP TABLE IF EXISTS students")
            db.commit()

    @staticmethod
    def create_student(email: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            # some kind of validation? also need more info about what OAuth sends back

            c.execute("INSERT INTO students (email) VALUES (?)", (email,))

    @staticmethod
    def get_student_id(email: str) -> str:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            student_id = c.execute(
                "SELECT student_id FROM students WHERE email = (?)", (email,)
            ).fetchone()

            if student_id is not None:
                return student_id[0]
            return None


class Teacher:
    @staticmethod
    def create_db():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS teachers(
                    teacher_id  TEXT PRIMARY KEY DEFAULT (hex(randomblob(8))),
                    name        TEXT,
                    email       TEXT,
                    pronouns    TEXT,
                    title       TEXT,
                    schedule_id TEXT,
                    FOREIGN KEY(schedule_id) REFERENCES schedules(schedule_id)
                        ON DELETE CASCADE
                )
                """
            )
            db.commit()

    @staticmethod
    def drop_db():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute("DROP TABLE IF EXISTS teachers")
            db.commit()

    @staticmethod
    def create_teacher(email: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            # some kind of validation? also need more info about what OAuth sends back

            c.execute("INSERT INTO teachers(email) VALUES (?)", (email,))

    @staticmethod
    def get_teacher_id(email: str) -> str:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            teacher_id = c.execute(
                "SELECT teacher_id FROM teachers WHERE email = (?)", (email,)
            ).fetchone()

            if teacher_id is not None:
                return teacher_id[0]
            return None

    @staticmethod
    def get_teacher_schedule_id(teacher_id: str) -> str:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            schedule_id = c.execute(
                "SELECT schedule_id FROM schedules WHERE teacher_id = (?)", (teacher_id,)
            ).fetchone()

            if schedule_id is not None:
                return schedule_id[0]
            return None


class Schedules:
    @staticmethod
    def create_db():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS schedules(
                    schedule_id  TEXT PRIMARY KEY DEFAULT (hex(randomblob(8))),
                    teacher_id   TEXT,
                    period_1     TEXT,
                    period_2     TEXT,
                    period_3     TEXT,
                    period_4     TEXT,
                    period_5     TEXT,
                    period_6     TEXT,
                    period_7     TEXT,
                    period_8     TEXT,
                    period_9     TEXT,
                    period_10    TEXT,
                    FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id)
                        ON DELETE SET NULL
                )
                """
            )
            db.commit()

    @staticmethod
    def create_teacher_schedule(teacher_id: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            # some kind of validation? also need more info about what OAuth sends back

            c.execute("INSERT INTO schedules(teacher_id) VALUES (?)", (teacher_id,))

    @staticmethod
    def drop_db():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute("DROP TABLE IF EXISTS schedules")
            db.commit()

    @staticmethod
    def get_schedule_periods(schedule_id: str) -> tuple:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            schedule = c.execute(
                """
                SELECT period_1, period_2, period_3, period_4, period_5, period_6, period_7 , period_8, period_9, period_10
                FROM schedules WHERE schedule_id = (?)
                """,
                (schedule_id,)

            ).fetchone()

            if schedule is not None:
                return schedule
            return None



class StarredTeachers:
    @staticmethod
    def create_db():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS starred_teachers(
                    star_id    TEXT PRIMARY KEY DEFAULT (hex(randomblob(8))),
                    teacher_id TEXT,
                    student_id TEXT,
                    FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id),
                    FOREIGN KEY(student_id) REFERENCES students(student_id)
                )
                """
            )
            db.commit()

    @staticmethod
    def drop_db():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute("DROP TABLE IF EXISTS starred_teachers")
            db.commit()

class Files:
    @staticmethod
    def create_db():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS files(
                    file_id     TEXT PRIMARY KEY DEFAULT (hex(randomblob(8))),
                    teacher_id  TEXT,
                    FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id)
                )
                """
            )
            db.commit()

    @staticmethod
    def drop_db():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute("DROP TABLE IF EXISTS files")
            db.commit()

def create_dbs():
    Student.create_db()
    Teacher.create_db()
    Schedules.create_db()
    StarredTeachers.create_db()
    Files.create_db()

def drop_dbs():
    Student.drop_db()
    Teacher.drop_db()
    Schedules.drop_db()
    StarredTeachers.drop_db()
    Files.drop_db()

# Testing
drop_dbs()
create_dbs()

Student.create_student("llee20@stuy.edu")
student_id = Student.get_student_id("llee20@stuy.edu")
print(student_id)

Teacher.create_teacher("dsharaf@stuy.edu")
teacher_id = Teacher.get_teacher_id("dsharaf@stuy.edu")
print(teacher_id)

Schedules.create_teacher_schedule(teacher_id)
schedule_id = Teacher.get_teacher_schedule_id(teacher_id)
schedule = Schedules.get_schedule_periods(schedule_id)
print(schedule)
