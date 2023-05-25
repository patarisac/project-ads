from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database import schemas
from utils.auth import auth_handler
import crud

router = APIRouter(tags=['core'])
frontends = Jinja2Templates(directory="frontends")

class Mahasiswa:

    @router.get("/changepassword")
    async def get_changepassword(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            context = {"request": request}
            user = crud.mahasiswa.get_mahasiswa(db, email=auth.get('user'))
            context["user"] = user
            if user == None:
                return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
            return frontends.TemplateResponse("chngpw.html", context)
        finally:
            db.close()
        

    @router.post("/changepassword")
    async def post_changepassword(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            context = {"request": request}
            user = crud.mahasiswa.get_mahasiswa(db, email=auth.get('user'))
            context["user"] = user
            if user == None:
                return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
            form = await request.form()
            passwd = form.get('passwd')
            newpasswd = form.get('newpasswd')
            cnewpasswd = form.get('cnewpasswd')
            if len(newpasswd) < 8:
                context['error'] = 'invalid_len_pass'
                return frontends.TemplateResponse("chngpw.html", context)
            if newpasswd != cnewpasswd:
                context['error'] = 'invalid_cpass'
                return frontends.TemplateResponse("chngpw.html", context)
            changepass = crud.mahasiswa.changepassword(db, user, passwd, newpasswd)
            if not changepass:
                context['error'] = 'invalid_pass'
                return frontends.TemplateResponse("chngpw.html", context)
            return RedirectResponse(url='/browse', status_code=status.HTTP_303_SEE_OTHER)
        finally:
            db.close()
