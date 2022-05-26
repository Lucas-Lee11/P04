# Team Loophole -- Lucas Lee, Andrew Juang, Eliza Knapp, Ella Krechmer, Christopher Liu
# Softdev
# P04 -- PROJECT NAME!?!
# 2022-05-23

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
    def create_student(email: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            # some kind of validation? also need more info about what OAuth sends back

            c.execute(
                "INSERT INTO students(email) VALUES (?)", (email)
            )

    @staticmethod
    def get_student_id(email: str) -> str:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            student_id = c.execute(
                "SELECT student_id FROM students WHERE email=:email", {"email": email}
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
                    schedule    INTEGER,
                    FOREIGN KEY(schedule) REFERENCES schedules(schedule_id)
                        ON DELETE CASCADE
                )
                """
            )
            db.commit()

    @staticmethod
    def create_teacher(email: str) -> None:
            # some kind of validation? also need more info about what OAuth sends back

            c.execute(
                "INSERT INTO teachers(email) VALUES (?)", (email)
            )


class Schedules:

    @staticmethod
    def create_db():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS schedules(
                    schedule_id  TEXT PRIMARY KEY DEFAULT (hex(randomblob(8))),
                    teacher      INTEGER,
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
                    FOREIGN KEY(teacher) REFERENCES teachers(teacher_id)
                        ON DELETE SET NULL
                )
                """
            )
            db.commit()

class StarredTeachers:

    @staticmethod
    def create_db():
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS starred_teachers(
                    star_id  TEXT PRIMARY KEY DEFAULT (hex(randomblob(8))),
                    teacher  INTEGER,
                    student  INTEGER,
                    FOREIGN KEY(teacher) REFERENCES teachers(teacher_id),
                    FOREIGN KEY(student) REFERENCES students(teacher_id)
                )
                """
            )
            db.commit()



Student.create_db()
Teacher.create_db()
Schedules.create_db()
StarredTeachers.create_db()

print("created dbs")
