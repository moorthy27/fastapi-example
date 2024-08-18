from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from sqlalchemy.orm import Session
from .database import engine, sessionLocal, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# class Post(BaseModel):
#     title: str
#     content: str
#     published: bool = True


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapidb",
            user="postgres",
            password="123",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("DB Conn Successfull...")
        break
    except Exception as e:
        print(f"Db Conn Failed : {e}")
        time.sleep(3)

    """
    # notes
    # Path opertions a.k.a Route
    # making
    # use plurals for path
    CRUD:

    Create: Post    : /posts    @app.post("/posts")
    Read:   Get     : /posts/:id    @app.get("/posts/{id}")
    Read:   Get     : /posts    @app.get("/posts")

        > For put we pass entire content to change, for patch we pass only the item to be canged"
    Update: Put/Patch   :   /posts/:id  @app.put("/posts/{id}")
    Delete: Delete  
    """


my_posts = [
    {"title": "Title of Post No : 1", "content": "content of post no 1", "id": 1},
    {"title": "Title of Post No : 2", "content": "content of post no 2", "id": 2},
    {"title": "Title of Post No : 3", "content": "content of post no 3", "id": 3},
    {"title": "Title of Post No : 4", "content": "content of post no 4", "id": 4},
    {"title": "Title of Post No : 5", "content": "content of post no 5", "id": 5},
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/")
def root():
    return {"message": "Hello world"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"status": posts}


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    out = cursor.fetchall()
    return {"message": out}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: models.Post, db: Session = Depends(get_db)):
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s,%s,%s) RETURNING * """,
    #     (post.title, post.content, post.published),
    # )
    # created_post = cursor.fetchone()
    # conn.commit()
    created_post = models.Post(**post.model_dump())
    # created_post = models.Post(**post.model_dump())
    db.add(created_post)
    db.commit()
    db.refresh(created_post)

    return {"created post": created_post}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts where id = %s""", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} was not found"
        )
    return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts where id = %s RETURNING *""", (str(id)))
    post = cursor.fetchone()
    conn.commit()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id : {id} does not exist!.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: models.Post):
    cursor.execute(
        """UPDATE posts set title = %s,content = %s,published = %s WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, str(id)),
    )
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id : {id} does not exist!.",
        )
    return {"message": updated_post}
