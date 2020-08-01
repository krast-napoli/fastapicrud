import databases, sqlalchemy, uuid
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

DATABASE_URL = "postgresql://dbuser:dbpassword@127.0.0.1:5432/psqldbase"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "py_users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String),
    sqlalchemy.Column("gender", sqlalchemy.CHAR),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)

class UserList(BaseModel):
    id : str
    username : str
    gender : str
class UserEntry(BaseModel):
    username : str = Field (..., example="your name")
    gender : str = Field (..., example="M")
class UserUpdate(BaseModel):
    id : str = Field (..., example="Enter your ID")    
    username : str = Field (..., example="your name")
    gender : str = Field (..., example="M")
class UserDelete(BaseModel):
    id : str = Field (..., example="Enter your ID")
    

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/users", response_model=List[UserList])
async def find_all_users():
    query = users.select()
    return await database.fetch_all(query)

@app.post("/users", response_model=UserList)
async def register_user(user: UserEntry):
    gID = str(uuid.uuid1())
    query = users.insert().values(
        id = gID,
        username = user.username,
        gender = user.gender
    )

    await database.execute(query)
    return {
        "id": gID,
        **user.dict()
    }

@app.get("/users/{userId}/json", response_model=UserList)
async def find_user_by_id(userId: str):
    query = users.select().where(users.c.id == userId)
    return await database.fetch_one(query)

@app.put("/users", response_model=UserList)
async def update_user(user: UserUpdate):
    query = users.update().\
        where(users.c.id == user.id).\
        values(
            username = user.username,
            gender = user.gender
        )

    await database.execute(query)
    return await find_user_by_id(user.id)

@app.delete("/users/{userId}")
async def delete_user (user:UserDelete):
    query = users.delete().where(users.c.id == user.id)
    
    await database.execute(query)
    return {
        "message": "This user has been deleted successfully."
    }