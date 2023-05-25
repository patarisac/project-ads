from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database import schemas
from utils.auth import auth_handler
import controllers

router = APIRouter(tags=['core'])
frontends = Jinja2Templates(directory="frontends")

class Core:
    @router.get("/")
    async def get_index(request: Request, auth=Depends(auth_handler.auth_wrapper)):
        if auth.get("user"):
            return RedirectResponse(url='/browse')
        context = {"request": request}
        return frontends.TemplateResponse("index.html", context)

    @router.get("/register")
    async def get_register(request: Request):
        context = {"request": request}
        return frontends.TemplateResponse("register.html", context)

    @router.get("/login")
    async def get_login(request: Request, auth=Depends(auth_handler.auth_wrapper)):
        context = {"request": request}
        if auth.get("user"):
            return RedirectResponse(url='/browse')
        return frontends.TemplateResponse("login.html", context)



    @router.post("/register")
    async def post_register(request: Request, db: Session = Depends(get_db)):
        try:
            context = {"request": request}
            form = await request.form()
            nama = form.get('nama')
            context['nama'] = nama
            nim = form.get('nim')
            context['nim'] = nim
            email = form.get('email')
            if nama == None or nama == "":
                return frontends.TemplateResponse("register.html", context)
            if not email.endswith("@apps.ipb.ac.id"):
                context['error'] = 'invalid_email'
                return frontends.TemplateResponse("register.html", context)
            context['email'] = email
            password = form.get('password')
            if len(password) < 8:
                context['error'] = 'invalid_len_pass'
                return frontends.TemplateResponse("register.html", context)
            cpassword = form.get('cpassword')
            if password != cpassword:
                context['error'] = 'invalid_cpass'
                return frontends.TemplateResponse("register.html", context)
            user = schemas.MahasiswaCreate(nim = nim.upper(), email=email, nama=nama, password=password)
            user = controllers.mahasiswa.create_mahasiswa(db, user)
            token = auth_handler.encode_token(user.email)
            resp = RedirectResponse(url='/login', status_code=status.HTTP_302_FOUND)
            resp.set_cookie(key="access-token", value=token, max_age=3600*24, secure=True, httponly=True)
            return resp
        finally:
            db.close()

    @router.post("/login")
    async def post_login(request: Request, db: Session = Depends(get_db)):
        try:
            context = {"request": request}
            form = await request.form()
            email = form.get('email')
            context['email'] = email
            password = form.get('password')
            token = controllers.mahasiswa.login_mahasiswa(db, email, password)
            if not token:
                context['error'] = "invalid_login"
                return frontends.TemplateResponse("login.html", context, status_code=401)
            resp = RedirectResponse(url='/browse', status_code=status.HTTP_302_FOUND)
            resp.set_cookie(key="access-token", value=token, max_age=3600*24, secure=True, httponly=True)
            return resp
        finally:
            db.close()

    @router.get("/logout")
    async def logout(request: Request, auth=Depends(auth_handler.auth_wrapper)):
        resp = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        if not auth.get("user"):
            return resp
        resp.delete_cookie(key="access-token")
        return resp

