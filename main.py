import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from pydantic import EmailStr, Field
from enum import Enum, IntEnum

engine = create_engine("sqlite:///isdp.db")

with Session(engine) as session:
    session.execute(text("""CREATE TABLE IF NOT EXISTS Student (id INTEGER PRIMARY KEY, name TEXT, email TEXT, age INTEGER, gender TEXT, course TEXT)"""))
    session.execute(text("""INSERT INTO Student (name, email, age, gender, course) VALUES ('ali', 'ali@gmail.com', 20, 'male', 'python')"""))
    results=session.execute(text("""SELECT * FROM Student"""))
    for row in results:
        print(row)
    session.commit()


class Session(Session):
    pass    



    

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
class Student(BaseModel):
    name: str
    email: EmailStr
    age: int
    gender: GenderEnum
    course: str

app = FastAPI()
database=[]

@app.get('/')
def read_root():
    return {"name":"ali","number1":1.1,"number2":1}

@app.get('/student')
def read_students():
    with Session(engine) as session:
        result = session.execute(text("""SELECT * FROM Student"""))
        response=[]
        for row in result:
            response.append(row._asdict())
        return response

@app.post('/student')
def create_student(student: Student):
    with Session(engine) as session:
        session.execute(text("""INSERT INTO Student (name, email, age, gender, course) VALUES (:name, :email, :age, :gender, :course)"""), student.dict())
        session.commit()
    return student

@app.put('/student/{student_id}')
def update_student(student_id: int, student: Student):
    with Session(engine) as session:
        session.execute(text(f"""UPDATE Student SET name=:name, email=:email, age=:age, gender=:gender, course=:course WHERE id={student_id}"""), student.dict())
        session.commit()
    return student

@app.delete('/student/{student_id}')
def delete_student(student_id: int):
    with Session(engine) as session:
        session.execute(text(f"""DELETE FROM Student WHERE id={student_id}"""))
        session.commit()
    return {"message": "Student deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)