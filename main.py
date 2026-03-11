from fastapi import FastAPI, Depends, HTTPException
from schemas import TaskCreate
from database import SessionLocal, Base, engine

from models import Task

app = FastAPI()

# create all tables defined in models during app startup
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

# create new task
@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate, db = Depends(get_db)):
    db_task = Task(title=task.title)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# get all existing tasks
@app.get("/tasks")
def get_tasks(db = Depends(get_db)):
    return db.query(Task).all()

# get task by id
@app.get("/tasks/{task_id}")
def get_task(task_id: int, db = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=404, 
            detail=f"Task with id {task_id} doesn't exist!"
    )
    return task

# delete task by id
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=404, detail=f"Task with id {task_id} doesn't exist!"
        )
    
    db.delete(task)
    db.commit()

    return {"message": f"Task with id {task_id} deleted!"}
