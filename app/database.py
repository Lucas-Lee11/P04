# Team Loophole -- Lucas Lee, Andrew Juang, Eliza Knapp, Ella Krechmer, Christopher Liu
# Softdev
# P04 -- Final Project
# 2022-06-15w

import sqlite3
import os
from xmlrpc.client import boolean
from werkzeug.utils import secure_filename
import shutil

from flask import g

DB_FILE = "loophole.db"
UPLOAD_FOLDER = "./app/uploads"

class Student:
    @staticmethod
    def create_db() -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS students(
                    student_id  TEXT PRIMARY KEY,
                    name        TEXT NOT NULL,
                    email       TEXT NOT NULL
                )
                """
            )
            db.commit()

    @staticmethod
    def drop_db() -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute("DROP TABLE IF EXISTS students")
            db.commit()

    @staticmethod
    def create_student(student_id: str, name: str, email: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                "INSERT INTO students (student_id, name, email) VALUES (?, ?, ?)",
                (student_id, name, email),
            )

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
    def create_db() -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS teachers(
                    teacher_id  TEXT PRIMARY KEY,
                    teacher_hex TEXT DEFAULT (hex(randomblob(8))),
                    name        TEXT NOT NULL,
                    email       TEXT NOT NULL,
                    pronouns    TEXT,
                    title       TEXT,
                    period_1    TEXT,
                    period_2    TEXT,
                    period_3    TEXT,
                    period_4    TEXT,
                    period_5    TEXT,
                    period_6    TEXT,
                    period_7    TEXT,
                    period_8    TEXT,
                    period_9    TEXT,
                    period_10   TEXT
                )
                """
            )
            db.commit()

    @staticmethod
    def drop_db() -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute("DROP TABLE IF EXISTS teachers")
            db.commit()

    @staticmethod
    def create_teacher(teacher_id: str, name: str, email: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                "INSERT OR IGNORE INTO teachers (teacher_id, name, email) VALUES (?, ?, ?)",
                (teacher_id, name, email),
            )

    @staticmethod
    def verify_teacher(teacher_id: str) -> bool:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            teacher = c.execute(
                "SELECT * FROM teachers WHERE teacher_id = (?)", (teacher_id,)
            ).fetchone()
            if teacher is not None:
                return True
            return False

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
    def hex_to_teacher_id(hex: str) -> str:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            teacher_id = c.execute(
                "SELECT teacher_id FROM teachers WHERE teacher_hex = (?)", (hex,)
            ).fetchone()

            if teacher_id is not None:
                return teacher_id[0]
            return None

    @staticmethod
    def teacher_id_to_hex(id: str) -> str:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            hex = c.execute(
                "SELECT teacher_hex FROM teachers WHERE teacher_id = (?)", (id,)
            ).fetchone()

            if hex is not None:
                return hex[0]
            return None

    @staticmethod
    def get_teacher_id_name(name: str) -> str:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            # search by last name

            teacher_ids = c.execute(
                f"SELECT teacher_id FROM teachers WHERE name LIKE '%{name}%'"
            ).fetchall()

            print(teacher_ids)

            if teacher_ids is not None:
                return teacher_ids

            return None



    @staticmethod
    def get_teacher_list() -> list:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            teachers = c.execute(
                """
                SELECT teacher_hex, name FROM teachers
                """
            ).fetchall()

            if teachers is not None:
                return teachers
            return None


    @staticmethod
    def get_schedule_periods(teacher_id: str) -> tuple:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            schedule = c.execute(
                """
                SELECT period_1, period_2, period_3, period_4, period_5, period_6, period_7 , period_8, period_9, period_10
                FROM teachers WHERE teacher_id = (?)
                """,
                (teacher_id,),
            ).fetchone()

            if schedule is not None:
                return schedule
            return None

    @staticmethod
    def get_teacher_info(teacher_id: str) -> tuple:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            info = c.execute(
                "SELECT name, email, pronouns, title FROM teachers WHERE teacher_id = (?)",
                (teacher_id,),
            ).fetchone()

            if info is not None:
                return tuple("" if data is None else data for data in info)
            return None

    @staticmethod
    def get_teacher_name(teacher_id: str) -> str:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            name = c.execute(
                "SELECT name FROM teachers WHERE teacher_id = (?)",
                (teacher_id,),
            ).fetchone()

            if name is not None:
                return name[0]
            return None

    @staticmethod
    def add_schedule_period(teacher_id: str, pd: int, text: str) -> None:
        if not (1 <= pd <= 10):
            return

        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            c.execute(
                f"UPDATE teachers SET period_{pd} = (?) WHERE teacher_id = (?)",
                (text, teacher_id),
            )

            db.commit()

    @staticmethod
    def add_teacher_pronouns(teacher_id: str, pronouns: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            c.execute(
                "UPDATE teachers SET pronouns = (?) WHERE teacher_id = (?)",
                (pronouns, teacher_id),
            )

            db.commit()

    @staticmethod
    def add_teacher_title(teacher_id: str, title: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            c.execute(
                "UPDATE teachers SET title = (?) WHERE teacher_id = (?)",
                (title, teacher_id),
            )

            db.commit()

    @staticmethod
    def add_teacher_name(teacher_id: str, name: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            c.execute(
                "UPDATE teachers SET name = (?) WHERE teacher_id = (?)",
                (name, teacher_id),
            )

            db.commit()

    @staticmethod
    def add_teacher_email(teacher_id: str, email: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            c.execute(
                "UPDATE teachers SET email = (?) WHERE teacher_id = (?)",
                (email, teacher_id),
            )

            db.commit()

class StarredTeachers:
    @staticmethod
    def create_db() -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS starred_teachers(
                    star_id     TEXT PRIMARY KEY DEFAULT (hex(randomblob(8))),
                    teacher_hex TEXT NOT NULL,
                    student_id  TEXT NOT NULL,
                    FOREIGN KEY(teacher_hex) REFERENCES teachers(teacher_hex)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE,
                    FOREIGN KEY(student_id) REFERENCES students(student_id)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
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

    @staticmethod
    def star_teacher(student_id: str, teacher_hex: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                "INSERT OR IGNORE INTO starred_teachers (teacher_hex, student_id) VALUES (?, ?)",
                (teacher_hex, student_id),
            )
            db.commit()

    @staticmethod
    def unstar_teacher(student_id: str, teacher_hex: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                "DELETE FROM starred_teachers WHERE teacher_hex = (?) AND student_id = (?)",
                (teacher_hex, student_id),
            )
            db.commit()

    @staticmethod
    def get_student_stars(student_id: str) -> tuple:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            teachers = c.execute(
                "SELECT teacher_hex FROM starred_teachers WHERE student_id = (?)",
                (student_id,),
            ).fetchall()

            db.commit()

            if teachers is not None:
                return tuple(teacher[0] for teacher in teachers)
            return None

    @staticmethod
    def starred_relationship_exists(student_id: str, teacher_hex: str) -> bool:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            starred = c.execute(
                "SELECT * FROM starred_teachers WHERE teacher_hex = (?) AND student_id = (?)",
                (teacher_hex, student_id),
            ).fetchone()

            if starred is not None:
                return True
            return False



class Files:
    @staticmethod
    def create_db() -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS files(
                    file_id     TEXT PRIMARY KEY DEFAULT (hex(randomblob(8))),
                    teacher_id  TEXT NOT NULL,
                    filename    TEXT NOT NULL,
                    FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                )
                """
            )
            db.commit()

    @staticmethod
    def drop_db() -> None:
        if os.path.exists(UPLOAD_FOLDER):
            shutil.rmtree(UPLOAD_FOLDER)

        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute("DROP TABLE IF EXISTS files")
            db.commit()

    @staticmethod
    def add_teacher_file(teacher_id: str, file) -> None:
        filename = secure_filename(file.filename)

        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            id = c.execute(
                "INSERT INTO files(teacher_id, filename) VALUES (?, ?) RETURNING file_id",
                (teacher_id, filename),
            ).fetchone()[0]

            path = os.path.join(UPLOAD_FOLDER, teacher_id, filename)

            if not os.path.exists(os.path.join(UPLOAD_FOLDER, teacher_id)):
                os.makedirs( os.path.join(UPLOAD_FOLDER, teacher_id))

            file.save(path)

            db.commit()

    @staticmethod
    def get_teacher_files(teacher_id: str) -> list:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            files = c.execute(
                "SELECT file_id, filename FROM files WHERE teacher_id = (?)", (teacher_id,)
            ).fetchall()

            if files is not None:
                return files
            return None

    @staticmethod
    def remove_teacher_file(teacher_id:str, file_id: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                "DELETE FROM files WHERE teacher_id = (?) AND file_id = (?)",
                (teacher_id, file_id)
            )
            _, filename = Files.get_file_info(file_id)

            path = os.path.join(UPLOAD_FOLDER, teacher_id, filename)
            if os.path.exists(path):
                os.remove(path)

            db.commit()

    @staticmethod
    def get_file_info(file_id: str) -> tuple:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            id, filename = c.execute(
                "SELECT teacher_id, filename FROM files WHERE file_id = (?)", (file_id,)
            ).fetchone()

            if filename is not None:
                return id, filename
            return None


def create_dbs():
    Student.create_db()
    Teacher.create_db()
    StarredTeachers.create_db()
    Files.create_db()


def drop_dbs():
    Student.drop_db()
    Teacher.drop_db()
    StarredTeachers.drop_db()
    Files.drop_db()


# Testing
drop_dbs()
create_dbs()

# need to fix based on new schemas

Student.create_student("lucas_id", "Lucas Lee", "llee20@stuy.edu")
student_id = Student.get_student_id("llee20@stuy.edu")
print(student_id)

Teacher.create_teacher("sharaf_id", "Daisy Sharaf", "dsharaf@stuy.edu")
teacher_id = Teacher.get_teacher_id("dsharaf@stuy.edu")
Teacher.add_schedule_period(teacher_id, 1, "rm 840")
schedule = Teacher.get_schedule_periods(teacher_id)
print(schedule)

Teacher.add_teacher_pronouns(teacher_id, "she/her")
Teacher.add_teacher_title(teacher_id, "Ms.")
name, email, pronouns, title = Teacher.get_teacher_info(teacher_id)
print(pronouns, title)


# StarredTeachers.student_star_teacher(student_id, teacher_id)
# stars = StarredTeachers.get_student_stars(student_id)
# print(stars)
# StarredTeachers.student_unstar_teacher(student_id, teacher_id)
# stars = StarredTeachers.get_student_stars(student_id)
# print(stars)

# Files.add_teacher_file(teacher_id, "./README.md")
Files.get_teacher_files(teacher_id)

drop_dbs()
create_dbs()
