from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from app.db import db
from app.utils.oa2 import get_current_user
from ..schema import schemas


router = APIRouter(tags=["Obtain Pass"], prefix="/request_pass")


@router.get("/")
def get_all_pass_requests(cur_user:schemas.UserOutput = Depends(get_current_user)):

    pass_requests = db.passrequest.find_many(where={"user_id": cur_user.id},order={"created_at": "desc"})
    return pass_requests

@router.get("/admin", response_model=List[schemas.PassRequestOutput], status_code=status.HTTP_200_OK)
def get_all_pass_requests_by_admin(cur_user:schemas.UserOutput = Depends(get_current_user)):
    passes = db.passrequest.find_many(include={"user": True}, order={"created_at": "desc"})
    return passes


@router.patch("/", status_code=status.HTTP_200_OK)
def updated_elective_request(request_id: str, to_update: schemas.UpdateRequest, cur_user:schemas.UserOutput = Depends(get_current_user)):
    update = jsonable_encoder(to_update)
    updated_course = db.passrequest.update(data={ **update}, where={'id': request_id})
    return updated_course


@router.post("/", status_code=status.HTTP_201_CREATED)
def order_pass(pass_request: schemas.OrderPassRequest, cur_user:schemas.UserOutput = Depends(get_current_user)):
    guest_info = ""
    if pass_request.guests:
        guest_info ="*_*".join(pass_request.guests)

    requested_pass = db.passrequest.create(data={
        "user_id": cur_user.id,
        "description": pass_request.description,
        "requested_date": pass_request.requested_date.isoformat(),
        "guest_info": guest_info
    })

    return {"status": status.HTTP_201_CREATED, "detail": "Successfully created pass order", "data": requested_pass}


@router.delete("/", status_code=status.HTTP_200_OK)
def disconnect_pass_request(pass_request_id: str, cur_user:schemas.UserOutput = Depends(get_current_user)):
    pass_to_delete = db.passrequest.find_first(where={
        "id": pass_request_id,
        "user_id": cur_user.id
    })
    print(f"{pass_request_id} ---- {cur_user.id} ---- {pass_to_delete}")

    return db.passrequest.delete(where={
        "id": pass_to_delete.id
        })