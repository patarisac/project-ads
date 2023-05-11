from fastapi import FastAPI, Request, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
# from api.base import api_router
from database.db import get_db
from database.schemas import MahasiswaCreate
from database.crud import create_mahasiswa, login_mahasiswa
from utils.auth import auth_handler

from dotenv import load_dotenv
load_dotenv('.env')

app = FastAPI()
frontends = Jinja2Templates(directory="frontends")
app.mount("/static", StaticFiles(directory="static"), name="static")
# app.include_router(api_router)

@app.get("/")
async def get_index(request: Request, auth=Depends(auth_handler.auth_wrapper)):
    context = {"request": request}
    return frontends.TemplateResponse("index.html", context)

@app.get("/register")
async def get_register(request: Request):
    context = {"request": request}
    return frontends.TemplateResponse("signup.html", context)

@app.get("/login")
async def get_register(request: Request):
    context = {"request": request}
    token = request.cookies.get("access-token")

    if not token:
        context = {"request": request}
        return frontends.TemplateResponse("login.html", context)
    

    return RedirectResponse("/protected")

@app.post("/register")
async def post_register(request: Request, db: Session = Depends(get_db)):
    context = {"request": request}
    form = await request.form()
    nama = form.get('nama')
    context['nama'] = nama
    nim = form.get('nim')
    context['nim'] = nim
    email = form.get('email')
    context['email'] = email
    password = form.get('password')
    cpassword = form.get('cpassword')
    if password != cpassword:
        context['error'] = 'Password yang diketik berbeda.'
        return frontends.TemplateResponse("signup.html", context)
    user = MahasiswaCreate(nim = nim, email=email, nama=nama, password=password)
    user = create_mahasiswa(db, user)
    return RedirectResponse(url='/login', status_code=status.HTTP_302_FOUND)

@app.post("/login")
async def post_login(request: Request, db: Session = Depends(get_db)):
    context = {"request": request}
    form = await request.form()
    email = form.get('email')
    context['email'] = email
    password = form.get('password')
    jwt = login_mahasiswa(db, email, password)
    if not jwt:
        context['error'] = "Incorrect username or password."
        return frontends.TemplateResponse("login.html", context, status_code=401)
    token = jwt['token']
    resp = RedirectResponse(url='/protected', status_code=status.HTTP_302_FOUND)
    resp.set_cookie(key="access-token", value=token, httponly=True)
    return resp

@app.get("/logout")
async def logout(request: Request, auth=Depends(auth_handler.auth_wrapper)):
    resp = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    if not auth.get("user"):
        return resp
    resp.delete_cookie(key="access-token")
    return resp

@app.get('/protected')
async def protected(request: Request, auth=Depends(auth_handler.auth_wrapper)):
    if auth.get("error"):
        return auth
    return auth

@app.get("/browse")
def get_browse(request: Request, auth=Depends(auth_handler.auth_wrapper)):
    return

@app.get("/home")
async def get_home(request: Request, auth=Depends(auth_handler.auth_wrapper)):
    if auth.get("error"):
        return auth
    context = {"request": request}
    return frontends.TemplateResponse("home.html", context)
