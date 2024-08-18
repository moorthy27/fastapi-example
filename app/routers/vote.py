from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, database, models

# from oauth2 import get_current_user
from ..oauth2 import get_current_user

router = APIRouter(
    prefix="/vote",
    tags=["Vote"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: schemas.Vote,
    db: Session = Depends(database.get_db),
    current_user: Session = Depends(get_current_user),
):
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id
    )
    founded_vote = vote_query.first()
    if vote.dir == 1:
        if founded_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"user {current_user.id} has already voted on post {vote.post_id}",
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "successfully Voted"}
    else:
        if not founded_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="vote does not exist"
            )
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully UnVoted"}
