import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from pydantic import EmailStr, Field
from enum import Enum, IntEnum
import random
from fastapi import Response
from typing import Annotated
from fastapi import Cookie


engine = create_engine("sqlite:///isdp.db")

with Session(engine) as session:
    session.execute(text("""CREATE TABLE IF NOT EXISTS Student (id INTEGER PRIMARY KEY, name TEXT, email TEXT, age INTEGER, gender TEXT, course TEXT)"""))
    session.execute(text("""INSERT INTO Student (name, email, age, gender, course) VALUES ('ali', 'ali@gmail.com', 20, 'male', 'python')"""))
    results=session.execute(text("""SELECT * FROM Student"""))
    for row in results:
        print(row)
    session.commit()

with Session(engine) as session:
    session.execute(text("""CREATE TABLE IF NOT EXISTS User (id INTEGER  PRIMARY KEY, username TEXT,password TEXT)"""))
    session.commit()

with Session(engine) as session:
    session.execute(text("""CREATE TABLE IF NOT EXISTS Session (id INTEGER PRIMARY KEY, session_id TEXT)"""))
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


class Register(BaseModel):
    username : str
    password : str

app = FastAPI()
database=[]


@app.post("/register") # I have written it
def register_user(register : Register ):
    with Session(engine) as session:
        result = session.execute(text("""SELECT * FROM User WHERE username = :username"""),{"username": register.username}).fetchone()
        
        if result:
            return {"message":"user already exists"}
        session.execute(text("""INSERT INTO User (username,password)VALUES(:username,:password)"""),register.dict())
        
        session.commit()
        return {"message": "User registered successfully"}
    
@app.post("/login")
def login(register : Register, response : Response):

    with Session (engine) as session:
        result = session.execute(text("""SELECT * FROM User WHERE username = :username AND password = :password"""),{"username":register.username,"password":register.password}).fetchone()
        
        if not result:
            return {"message":"invalid credentials"}
        
        sessionId = random.randint(1000,9999)

        session.execute(text("""INSERT INTO Session (session_id) VALUES (:sessionId)"""),{"sessionId":sessionId})

        session.commit()

        response.set_cookie(key="session_id",value=str(sessionId))
        
        return {"message":"Login Successfull"}


@app.get('/')
def read_root():
    return {"name":"ali","number1":1.1,"number2":1}

@app.get('/student')
def read_students(session_id:Annotated[str|None, Cookie()] = None):
    if session_id is None:
        return {"message":"Please login first"}
    
    with Session (engine) as session:
        valid_session = session.execute(text("""SELECT * FROM Session WHERE session_id = :session_id"""),{"session_id":session_id}).fetchone()

        if valid_session is None:
            return {"message":"invalid session.login"}

    with Session(engine) as session:
        result = session.execute(text("""SELECT * FROM Student"""))
        response=[]
        for row in result:
            response.append(row._asdict())
        return response

@app.post('/student')
def create_student(student: Student,session_id:Annotated[str|None,Cookie()]= None):

    if session_id is None:
        return {"message":"Please login first"}
    
    with Session(engine) as session:

        valid_session = session.execute(text("""SELECT * FROM Session WHERE session_id = :session_id"""),{"session_id":session_id}).fetchone()

        if valid_session is None:
            return {"message":"Invalid Session. Login"}
        
    with Session(engine) as session:
        session.execute(text("""INSERT INTO Student (name, email, age, gender, course) VALUES (:name, :email, :age, :gender, :course)"""), student.dict())
        session.commit()
    return student

@app.put('/student/{student_id}')
def update_student(student_id: int, student: Student,session_id:Annotated[str|None, Cookie()]=None):

    if session_id is None:
        return {"message":"please login first"}
    
    with Session (engine) as session:
        valid_session = session.execute(text("""SELECT * FROM Session WHERE session_id = :session_id"""),{"session_id":session_id}).fetchone()
        if valid_session is None:
            return {"message":"Invalid Session:login"}
        
    with Session(engine) as session:
        session.execute(text(f"""UPDATE Student SET name=:name, email=:email, age=:age, gender=:gender, course=:course WHERE id={student_id}"""), student.dict())
        session.commit()
    return student


@app.delete('/student/{student_id}')
def delete_student(student_id: int, session_id:Annotated[str|None, Cookie()]=None):

    if session_id is None:
        return {"message":"Please login first"}
    
    with Session (engine) as session:
        valid_session = session.execute(text("""SELECT * FROM Session WHERE session_id = :session_id"""),{"session_id":session_id}).fetchone()

        if valid_session is None:
            return {"message":"Invalid Session : Login First"}
        
    with Session(engine) as session:
        session.execute(text(f"""DELETE FROM Student WHERE id={student_id}"""))
        session.commit()
    return {"message": "Student deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)