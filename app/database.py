# Team Loophole -- Lucas Lee, Andrew Juang, Eliza Knapp, Ella Krechmer, Christopher Liu
# Softdev
# P04 -- Final Project
# 2022-06-15w

import sqlite3

DB_FILE = "loophole.db"


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
                    name        TEXT NOT NULL,
                    email       TEXT NOT NULL,
                    pronouns    TEXT,
                    title       TEXT,
                    schedule_id TEXT,
                    FOREIGN KEY(schedule_id) REFERENCES schedules(schedule_id)
                        ON DELETE SET NULL
                        ON UPDATE CASCADE
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
                "INSERT INTO teachers (teacher_id, name, email) VALUES (?, ?, ?)",
                (teacher_id, name, email),
            )

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
                "SELECT schedule_id FROM schedules WHERE teacher_id = (?)",
                (teacher_id,),
            ).fetchone()

            if schedule_id is not None:
                return schedule_id[0]
            return None


class Schedules:
    @staticmethod
    def create_db() -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS schedules(
                    schedule_id  TEXT PRIMARY KEY DEFAULT (hex(randomblob(8))),
                    teacher_id   TEXT UNIQUE NOT NULL,
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
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
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
    def drop_db() -> None:
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
                (schedule_id,),
            ).fetchone()

            if schedule is not None:
                return schedule
            return None

    @staticmethod
    def add_schedule_period(schedule_id: str, pd: int, text: str) -> None:
        if not (1 <= pd <= 10):
            return
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            c.execute(f"UPDATE schedules SET period_{pd} = (?) WHERE schedule_id = (?)",
                (text, schedule_id))

            db.commit()


class StarredTeachers:
    @staticmethod
    def create_db() -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS starred_teachers(
                    star_id    TEXT PRIMARY KEY DEFAULT (hex(randomblob(8))),
                    teacher_id TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id)
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
    def star_teacher(student_id: str, teacher_id: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                "INSERT INTO starred_teachers (teacher_id, student_id) VALUES (?, ?)",
                (teacher_id, student_id))
            db.commit()


    @staticmethod
    def unstar_teacher(student_id: str, teacher_id: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute(
                "DELETE FROM starred_teachers WHERE teacher_id = (?) AND student_id = (?)",
                (teacher_id, student_id))
            db.commit()



    @staticmethod
    def get_student_stars(student_id: str) -> tuple:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            teachers = c.execute(
                "SELECT teacher_id FROM starred_teachers WHERE student_id = (?)",
                (student_id,)
            ).fetchall()

            db.commit()

            if teachers is not None:
                return tuple(teacher[0] for teacher in teachers)
            return None



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
                    file        BLOB NOT NULL,
                    FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                )
                """
            )
            db.commit()

    @staticmethod
    def drop_db() -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            c.execute("DROP TABLE IF EXISTS files")
            db.commit()

    @staticmethod
    def add_teacher_file(teacher_id: str, filepath: str) -> None:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            with open(filepath, 'rb') as file:
                blobdata = file.read()

                c.execute("INSERT INTO files(teacher_id, filename, file) VALUES (?, ?, ?)",
                    (teacher_id, filepath, blobdata))
                db.commit()

    @staticmethod
    def get_teacher_files(teacher_id: str) -> list:
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()

            files = c.execute(
                "SELECT filename, file FROM files WHERE teacher_id = (?)",
                (teacher_id,)
            ).fetchall()


            for filename, file in files:
                with open(filename, 'wb') as f:
                    f.write(file)

            if files is not None:
                return [filename for filename, file in files]
            return None


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

# need to fix based on new schemas

Student.create_student("lucas_id", "Lucas Lee", "llee20@stuy.edu")
student_id = Student.get_student_id("llee20@stuy.edu")
print(student_id)

Teacher.create_teacher("sharaf_id", "Daisy Sharaf", "dsharaf@stuy.edu")
teacher_id = Teacher.get_teacher_id("dsharaf@stuy.edu")
print(teacher_id)

Schedules.create_teacher_schedule(teacher_id)
schedule_id = Teacher.get_teacher_schedule_id(teacher_id)
Schedules.add_schedule_period(schedule_id, 1, "rm 840")
schedule = Schedules.get_schedule_periods(schedule_id)
print(schedule)

StarredTeachers.star_teacher(student_id, teacher_id)
stars = StarredTeachers.get_student_stars(student_id)
print(stars)
StarredTeachers.unstar_teacher(student_id, teacher_id)
stars = StarredTeachers.get_student_stars(student_id)
print(stars)

Files.add_teacher_file(teacher_id, './README.md')
Files.get_teacher_files(teacher_id)

drop_dbs()
create_dbs()
