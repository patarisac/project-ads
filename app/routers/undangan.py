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

class Undangan:
    @router.post("/buat_undangan")
    async def buat_undangan(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            context = {"request": request}
            user = crud.mahasiswa.get_mahasiswa(db, auth.get('user'))
            if user == None:
                return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)


            form = await request.form()
            tutor_nim = form.get("tutor_nim")
            tutor = crud.mahasiswa.get_mahasiswa(db, nim=tutor_nim.upper())
            if tutor == None:
                return RedirectResponse(url='/browse?undang=failed', status_code=status.HTTP_303_SEE_OTHER)
            nama_kelas = form.get("nama_kelas")
            semester = form.get("semester")

            undangan = schemas.UndanganCreate(creator=user.nama, tutor_id=tutor.id, nama_kelas=nama_kelas, semester=semester)
            undangan = crud.undangan.create_undangan(db, undangan)
            return RedirectResponse(url='/browse?undang=success', status_code=status.HTTP_303_SEE_OTHER)
        finally:
            db.close()

    @router.get("/acc_undangan/{undangan_id}")
    async def get_acc_undangan(request: Request, undangan_id: int, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            user = crud.mahasiswa.get_mahasiswa(db, email=auth.get('user'))
            context = {"request": request}
            ref = request.headers.get("referer").removeprefix(str(request.base_url)) 
            if user == None:
                RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
            undangan = crud.undangan.get_undangan(db, undangan_id)
            context['undangan'] = undangan
            context['user'] = user
            return frontends.TemplateResponse("newclass.html", context)
        finally:
            db.close()

    @router.get("/dec_undangan/{undangan_id}")
    async def get_dec_undangan(request: Request, undangan_id: int, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            user = crud.mahasiswa.get_mahasiswa(db, email=auth.get('user'))
            context = {"request": request}
            ref = request.headers.get("referer").removeprefix(str(request.base_url)) 
            if user == None:
                return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
            crud.undangan.dec_undangan(db, undangan_id)
            if ref:
                return RedirectResponse(url=f'/{ref}', status_code=status.HTTP_303_SEE_OTHER)
            else:
                return RedirectResponse(url='/browse', status_code=status.HTTP_303_SEE_OTHER)
        finally:
            db.close()
