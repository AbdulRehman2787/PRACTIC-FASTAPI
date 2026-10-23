import json
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Student Management System")

DATA_FILE = "data.json"

# --- Helper Functions ---
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- 1. POST schema (name, age, mark, course) ---
class StudentCreate(BaseModel):
    name: str
    age: int
    mark: float
    course: str

# --- 2. PUT schema (Optional fields) ---
class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    mark: Optional[float] = None
    course: Optional[str] = None


# --- Endpoints ---

@app.get("/students")
def get_students():
    data = load_data()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No students found in the database."
        )
    return data

@app.get("/students/{student_id}")
def get_student(student_id: int):
    data = load_data()
    str_id = str(student_id)
    
    if str_id not in data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Student not found."
        )
    return data[str_id]

# POST Endpoint (Validation function ka hare)
@app.post("/students/{student_id}", status_code=status.HTTP_201_CREATED)
def create_student(student_id: int, student: StudentCreate):
    
    MIN_NAME_LENGTH = 2
    MAX_AGE = 100
    MIN_AGE = 1
    MIN_MARK = 0.0
    MAX_MARK = 100.0

    if len(student.name) < MIN_NAME_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Name length is below the minimum required limit of {MIN_NAME_LENGTH} characters."
        )
    if student.age < MIN_AGE or student.age > MAX_AGE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Age must be between {MIN_AGE} and {MAX_AGE}."
        )
    if student.mark < MIN_MARK or student.mark > MAX_MARK:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Mark must be between {MIN_MARK} and {MAX_MARK}."
        )

    data = load_data()
    str_id = str(student_id)
    
    if str_id in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Student with this ID already exists."
        )
    
    data[str_id] = student.dict()
    save_data(data)
    
    return {"message": "Student created successfully!", "student": student}

# PUT Endpoint (Validation function ka hare)
@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentUpdate):
    
    MIN_NAME_LENGTH = 2
    MAX_AGE = 100
    MIN_AGE = 1
    MIN_MARK = 0.0
    MAX_MARK = 100.0

    if student.name is not None and len(student.name) < MIN_NAME_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Name length is below the minimum required limit of {MIN_NAME_LENGTH} characters."
        )
    if student.age is not None and (student.age < MIN_AGE or student.age > MAX_AGE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Age must be between {MIN_AGE} and {MAX_AGE}."
        )
    if student.mark is not None and (student.mark < MIN_MARK or student.mark > MAX_MARK):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Mark must be between {MIN_MARK} and {MAX_MARK}."
        )

    data = load_data()
    str_id = str(student_id)
    
    if str_id not in data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Student not found for update."
        )
    
    stored_student = data[str_id]
    update_data = student.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        stored_student[key] = value
        
    data[str_id] = stored_student
    save_data(data)
    
    return {"message": "Student updated successfully!", "student": stored_student}

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    data = load_data()
    str_id = str(student_id)
    
    if str_id not in data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Student not found for deletion."
        )
    
    del data[str_id]
    save_data(data)
    return {"message": "Student deleted successfully!"}