from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..oauth2 import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.get("/", response_model=List[schemas.PostOut])
def get_posts1(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    # posts = (
    #     db.query(models.Post)
    #     .filter(models.Post.title.contains(search))
    #     .limit(limit)
    #     .offset(skip)
    #     .all()
    # )

    posts_with_votes = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .all()
    )

    return posts_with_votes


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post,
)
def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    # print(current_user.id)
    created_post = models.Post(
        title=post.title,
        content=post.content,
        published=post.published,
        owner_id=current_user.id,
    )
    db.add(created_post)
    db.commit()
    db.refresh(created_post)
    return created_post


@router.get("/{id}")
def get_posts2(
    id: int,
    db: Session = Depends(get_db),
    response_model=schemas.Post,
    current_user: int = Depends(get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return post


@router.delete("/{id}")
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} Not Found"
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete.."
        )
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}")
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    response_model=schemas.Post,
    current_user: int = Depends(get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    queried_post = post_query.first()
    if queried_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found"
        )
    if queried_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update.."
        )
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()
