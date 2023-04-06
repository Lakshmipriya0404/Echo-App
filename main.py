from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
import databases
import sqlalchemy
from datetime import datetime

DATABASE_URL = "sqlite:///./store.db"
metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)

register = sqlalchemy.Table(
    "register",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String(500)),
    sqlalchemy.Column("date_created", sqlalchemy.DateTime())
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)
app = FastAPI()

@app.on_event("startup")
async def connect():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

class InputTextIn(BaseModel):
    text: str = Field(...)

class InputText(BaseModel):
    id: int
    text: str
    date_created: datetime 

@app.get("/")
def index():
    return {"Hello!":"Home page"}

@app.post("/echo")
async def display_input(r: InputTextIn = Depends()):
    #taking input text as query as a necessary parameter
    query = register.insert().values(
        text=r.text,
        date_created=datetime.now()
    )
    record_id = await database.execute(query)
    #testing database schema
    query = register.select().where(register.c.id == record_id)
    row = await database.fetch_one(query)
    print(row)
    return {"echo": r.text} #displaying output in json format