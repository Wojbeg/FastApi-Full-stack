import sys
sys.path.append("..")
from models.models import Users
from routers.auth import get_current_user
from utils.hashing import verify_password, get_password_hash
from starlette import status
from starlette.responses import RedirectResponse
from fastapi import Depends, APIRouter, Request, Form
from db.database import get_db
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/users",
    tags=['users'],
    responses={404: {"description": "Not found"}}
)

templates = Jinja2Templates(directory="templates")

@router.get("/edit-password", response_class=HTMLResponse)
async def edit_current_user(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("change_password.html",
                                      {"request": request, "user": user})


@router.post("/edit-password", response_class=HTMLResponse)
async def user_password_change(request: Request, username: str = Form(...),
                               password: str = Form(...), password_repeat: str = Form(...),
                               db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_data = db.query(Users).filter(Users.username == username).first()

    msg = "Invalid username or password"

    if user_data is not None:
        if username == user_data.username and verify_password(password, user_data.hashed_password):
            user_data.hashed_password = get_password_hash(password_repeat)
            db.add(user_data)
            db.commit()
            msg = "Password updated"

    return templates.TemplateResponse("change_password.html", {"request": request, "user": user, "msg": msg})
