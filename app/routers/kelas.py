from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.db import get_db
from database import schemas
from utils.auth import auth_handler
from utils.date import split_date
from utils.files import save_img
import crud

router = APIRouter(tags=['core'])
frontends = Jinja2Templates(directory="frontends")

class Kelas:
    @router.get("/browse")
    def get_browse(request: Request, search: str | None = None, undang: str | None = None, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            context = {"request": request}
            user = crud.mahasiswa.get_mahasiswa(db, auth.get('user'))
            if not user:
                return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
            notif = crud.notifikasi.get_notifikasi(db, user)
            if undang:
                if undang == 'success':
                    context['undang'] = undang
                elif undang == 'failed':
                    context['undang'] = undang

            if search:
                context['search'] = search
                kelas_aktif = crud.kelas.search_kelas(db, user, search)
            else:
                kelas_aktif = crud.kelas.get_kelas_aktif(db, user)
            context["user"] = user
            context["kelas"] = kelas_aktif
            context["notif"] = notif
            return frontends.TemplateResponse("browse.html", context)
        finally:
            db.close()

    @router.get("/kelasdiikuti")
    async def get_kelasdiikuti(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            context = {"request": request}
            user = crud.mahasiswa.get_mahasiswa(db, email=auth.get('user'))
            if user == None:
                return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
            notif = crud.notifikasi.get_notifikasi(db, user)
            kelas_diikuti = crud.kelas.get_kelas_diikuti(db, user)
            context["user"] = user
            context["notif"] = notif
            context["kelas"] = kelas_diikuti
            return frontends.TemplateResponse("kelasDiikuti.html", context)
        finally:
            db.close()

    @router.get("/kelassaya")
    async def get_kelassaya(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            context = {"request": request}
            user = crud.mahasiswa.get_mahasiswa(db, email=auth.get('user'))
            if user == None:
                return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
            notif = crud.notifikasi.get_notifikasi(db, user)
            kelas_saya = crud.kelas.get_kelas_saya(db, user)
            context["user"] = user
            context["notif"] = notif
            context["kelas"] = kelas_saya
            return frontends.TemplateResponse("kelasSaya.html", context)
        finally:
            db.close()

    @router.get("/buatkelas")
    async def get_buatkelas(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            context = {"request": request}
            user = crud.mahasiswa.get_mahasiswa(db, email=auth.get('user'))
            if user == None:
                return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
            context["user"] = user
            return frontends.TemplateResponse("newclass.html", context)
        finally:
            db.close()

    @router.post("/buatkelas")
    async def post_buatkelas(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            user = auth.get("user")
            user = crud.mahasiswa.get_mahasiswa(db, user)
            context = {"request": request}
            form = await request.form()
            undangan = form.get('undangan')
            semester = form.get('semester')
            nama_kelas = form.get('namakelas')
            banner = form.get('banner')
            tipekelas = form.get('tipekelas')
            tanggal = form.get('tanggal')
            ruangan = form.get('ruangan')
            waktumulai = form.get('waktumulai')
            waktuselesai = form.get('waktuselesai')
            link_meet = form.get('link_meet')
            fasilitas = form.get('fasilitas')
            if tanggal == "" or tanggal == None:
                return {"error": "harap pilih tanggal"}
            kelasmulai, kelasselesai = split_date(tanggal, waktumulai, waktuselesai)
            ext = None

            if banner:
                ext = banner.filename.split(".")[-1]
            kelasbaru = schemas.KelasCreate(tutor_id=user.id, semester=semester, nama_kelas=nama_kelas, tipe=tipekelas, waktumulai=kelasmulai, waktuselesai=kelasselesai)
            if tipekelas == "hybrid":
                kelasbaru = crud.kelas.create_kelas(db, kelasbaru, ext=ext, link_meet=link_meet, lokasi=ruangan, kebutuhan=fasilitas)
            elif tipekelas == "onsite":
                kelasbaru = crud.kelas.create_kelas(db, kelasbaru, ext=ext, lokasi=ruangan, kebutuhan=fasilitas)
            elif tipekelas == "online":
                kelasbaru = crud.kelas.create_kelas(db, kelasbaru, ext=ext, link_meet=link_meet)
            else:
                return {"error": "Tipe kelas tidak dikenal"}
            if undangan:
                crud.undangan.acc_undangan(db, undangan, kelasbaru.id)

            if banner:
                filename = f"banner_k{kelasbaru.id}.{ext}"
                await save_img(banner, filename)

            return RedirectResponse(url="/kelassaya", status_code=status.HTTP_303_SEE_OTHER)
        finally:
            db.close()

    @router.get("/editkelas/{kelas_id}")
    async def get_editkelas(request: Request, kelas_id: int, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            context = {"request": request}
            user = crud.mahasiswa.get_mahasiswa(db, auth.get('user'))
            if not user:
                return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
            kelas = crud.kelas.get_kelas(db, kelas_id)
            if kelas != None and kelas.tutor_id == user.id:
                context["user"] = user
                context["kelas"] = kelas
                return frontends.TemplateResponse("editclass.html", context)
            
            return RedirectResponse(url="/kelassaya", status_code=status.HTTP_303_SEE_OTHER)
        finally:
            db.close()

    @router.post("/editkelas")
    async def post_editkelas(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            context = {"request": request}
            user = crud.mahasiswa.get_mahasiswa(db, auth.get('user'))
            if not user:
                return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
            form = await request.form()
            kelas = crud.kelas.get_kelas(db, form.get('kelas_id'))
            if kelas != None and kelas.tutor == user:
                await crud.kelas.edit_kelas(db, form)
            return RedirectResponse(url='/kelassaya', status_code=status.HTTP_303_SEE_OTHER)
        finally:
            db.close()

    @router.get("/ikutkelas/{kelas_id}")
    async def get_ikut_kelas(request: Request, kelas_id: int, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            context = {"request": request}
            user = crud.mahasiswa.get_mahasiswa(db, auth.get('user'))
            if not user:
                return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
            kelas = crud.kelas.get_kelas(db, kelas_id)
            if (kelas != None) and (user not in kelas.peserta):
                crud.kelas.ikut_kelas(db, user, kelas_id)
            return RedirectResponse(url="/browse", status_code=status.HTTP_303_SEE_OTHER)
        finally:
            db.close()

    @router.get("/hapuskelas/{kelas_id}")
    async def get_hapuskelas(request: Request, kelas_id: int, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            context = {"request": request}
            user = crud.mahasiswa.get_mahasiswa(db, email=auth.get('user'))
            if user == None:
                return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
            kelas = crud.kelas.get_kelas(db, kelas_id)
            if kelas != None and kelas.tutor_id == user.id:
                crud.kelas.hapus_kelas(db, kelas)
            return RedirectResponse(url='/kelassaya')
        finally:
            db.close()

    @router.get("/get_jadwal_ruangan/{tanggal}")
    async def get_hapuskelas(request: Request, tanggal: str, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
        try:
            context = {"request": request}
            user = crud.mahasiswa.get_mahasiswa(db, email=auth.get('user'))
            if user == None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            resp = crud.kelas.get_jadwal_ruangan(db, tanggal)
            return resp
        finally:
            db.close()
