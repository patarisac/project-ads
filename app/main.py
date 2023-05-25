from fastapi import FastAPI, Request, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
# from api.base import api_router
from database.db import get_db
from database.schemas import MahasiswaCreate, KelasHybridCreate, KelasOnlineCreate, KelasOnsiteCreate, KelasCreate, UndanganCreate
# from database.crud import create_kelas, get_kelas, get_kelas_aktif, get_kelas_saya, get_kelas_diikuti, get_undangan, create_undangan, respond_undangan, ikut_kelas, get_notifikasi, acc_undangan, dec_undangan, search_kelas, hapus_kelas, edit_kelas
from crud.mahasiswa import *
from crud.kelas import *
from crud.undangan import *
from crud.notifikasi import *
from utils.auth import auth_handler
from utils.date import split_date
from utils.files import save_img

from dotenv import load_dotenv
load_dotenv('.env')

app = FastAPI()
frontends = Jinja2Templates(directory="frontends")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/test")
async def get_test(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    context = {"request": request}
    user = auth.get("user")
    user = get_mahasiswa(db, email=user)
    if not user:
        return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
    notif = get_notifikasi(db, user)
    kelas_aktif = get_kelas_aktif(db)
    context["user"] = user
    context["kelas"] = kelas_aktif
    context["notif"] = notif
    return frontends.TemplateResponse("_old_chngpw.html", context)

@app.get("/")
async def get_index(request: Request, auth=Depends(auth_handler.auth_wrapper)):
    if auth.get("user"):
        return RedirectResponse(url='/browse')
    context = {"request": request}
    return frontends.TemplateResponse("index.html", context)

@app.get("/register")
async def get_register(request: Request):
    context = {"request": request}
    return frontends.TemplateResponse("register.html", context)

@app.get("/login")
async def get_login(request: Request, auth=Depends(auth_handler.auth_wrapper)):
    context = {"request": request}
    if auth.get("user"):
        return RedirectResponse(url='/browse')
    return frontends.TemplateResponse("login.html", context)

@app.post("/register")
async def post_register(request: Request, db: Session = Depends(get_db)):
    try:
        context = {"request": request}
        form = await request.form()
        nama = form.get('nama')
        context['nama'] = nama
        nim = form.get('nim')
        context['nim'] = nim
        email = form.get('email')
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
        user = MahasiswaCreate(nim = nim, email=email, nama=nama, password=password)
        user = create_mahasiswa(db, user)
        return RedirectResponse(url='/login', status_code=status.HTTP_302_FOUND)
    finally:
        db.close()

@app.post("/login")
async def post_login(request: Request, db: Session = Depends(get_db)):
    try:
        context = {"request": request}
        form = await request.form()
        email = form.get('email')
        context['email'] = email
        password = form.get('password')
        jwt = login_mahasiswa(db, email, password)
        if not jwt:
            context['error'] = "invalid_login"
            return frontends.TemplateResponse("login.html", context, status_code=401)
        token = jwt['token']
        resp = RedirectResponse(url='/browse', status_code=status.HTTP_302_FOUND)
        resp.set_cookie(key="access-token", value=token, max_age=3600*24, secure=True, httponly=True)
        return resp
    finally:
        db.close()

@app.get("/logout")
async def logout(request: Request, auth=Depends(auth_handler.auth_wrapper)):
    resp = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    if not auth.get("user"):
        return resp
    resp.delete_cookie(key="access-token")
    return resp

@app.get("/browse")
def get_browse(request: Request, search: str | None = None, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        context = {"request": request}
        user = get_mahasiswa(db, auth.get('user'))
        if not user:
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
        notif = get_notifikasi(db, user)
        if search:
            kelas_aktif = search_kelas(db, user, search)
        else:
            kelas_aktif = get_kelas_aktif(db, user)
        context["user"] = user
        context["kelas"] = kelas_aktif
        context["notif"] = notif
        return frontends.TemplateResponse("browse.html", context)
    finally:
        db.close()

@app.get("/kelasdiikuti")
async def get_kelasdiikuti(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        context = {"request": request}
        user = get_mahasiswa(db, email=auth.get('user'))
        if user == None:
            return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
        notif = get_notifikasi(db, user)
        kelas_diikuti = get_kelas_diikuti(db, user)
        context["user"] = user
        context["notif"] = notif
        context["kelas"] = kelas_diikuti
        return frontends.TemplateResponse("kelasDiikuti.html", context)
    finally:
        db.close()

@app.get("/kelassaya")
async def get_kelassaya(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        context = {"request": request}
        user = get_mahasiswa(db, email=auth.get('user'))
        if user == None:
            return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
        notif = get_notifikasi(db, user)
        kelas_saya = get_kelas_saya(db, user)
        context["user"] = user
        context["notif"] = notif
        context["kelas"] = kelas_saya
        return frontends.TemplateResponse("kelasSaya.html", context)
    finally:
        db.close()


@app.get("/changepassword")
async def get_changepassword(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        context = {"request": request}
        user = get_mahasiswa(db, email=auth.get('user'))
        context["user"] = user
        if user == None:
            return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
        return frontends.TemplateResponse("chngpw.html", context)
    finally:
        db.close()
    

@app.post("/changepassword")
async def post_changepassword(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        context = {"request": request}
        user = get_mahasiswa(db, email=auth.get('user'))
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
        changepass = changepassword(db, user, passwd, newpasswd)
        if not changepass:
            context['error'] = 'invalid_pass'
            return frontends.TemplateResponse("chngpw.html", context)
        return RedirectResponse(url='/browse', status_code=status.HTTP_303_SEE_OTHER)
    finally:
        db.close()


@app.get("/buatkelas")
async def get_buatkelas(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        context = {"request": request}
        user = get_mahasiswa(db, email=auth.get('user'))
        if user == None:
            return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
        context["user"] = user
        return frontends.TemplateResponse("newclass.html", context)
    finally:
        db.close()

@app.post("/buatkelas")
async def post_buatkelas(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        user = auth.get("user")
        user = get_mahasiswa(db, user)
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
        kelasbaru = KelasCreate(tutor_id=user.id, semester=semester, nama_kelas=nama_kelas, tipe=tipekelas, waktumulai=kelasmulai, waktuselesai=kelasselesai)
        if tipekelas == "hybrid":
            kelasbaru = create_kelas(db, kelasbaru, ext=ext, link_meet=link_meet, lokasi=ruangan, kebutuhan=fasilitas)
        elif tipekelas == "onsite":
            kelasbaru = create_kelas(db, kelasbaru, ext=ext, lokasi=ruangan, kebutuhan=fasilitas)
        elif tipekelas == "online":
            kelasbaru = create_kelas(db, kelasbaru, ext=ext, link_meet=link_meet)
        else:
            return {"error": "Tipe kelas tidak dikenal"}
        if undangan:
            acc_undangan(db, undangan, kelasbaru.id)

        if banner:
            filename = f"banner_k{kelasbaru.id}.{ext}"
            await save_img(banner, filename)

        return RedirectResponse(url="/kelassaya", status_code=status.HTTP_303_SEE_OTHER)
    finally:
        db.close()

@app.get("/editkelas/{kelas_id}")
async def get_editkelas(request: Request, kelas_id: int, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        context = {"request": request}
        user = get_mahasiswa(db, auth.get('user'))
        if not user:
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
        kelas = get_kelas(db, kelas_id)
        if kelas != None and kelas.tutor_id == user.id:
            context["user"] = user
            context["kelas"] = kelas
            return frontends.TemplateResponse("editclass.html", context)
        
        return RedirectResponse(url="/kelassaya", status_code=status.HTTP_303_SEE_OTHER)
    finally:
        db.close()

@app.post("/editkelas")
async def post_editkelas(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        context = {"request": request}
        user = get_mahasiswa(db, auth.get('user'))
        if not user:
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
        form = await request.form()
        kelas = get_kelas(db, form.get('kelas_id'))
        if kelas != None and kelas.tutor == user:
            await edit_kelas(db, form)
        return RedirectResponse(url='/kelassaya', status_code=status.HTTP_303_SEE_OTHER)
    finally:
        db.close()

@app.get("/ikutkelas/{kelas_id}")
async def get_ikut_kelas(request: Request, kelas_id: int, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        context = {"request": request}
        user = get_mahasiswa(db, auth.get('user'))
        if not user:
            return RedirectResponse(url="/logout", status_code=status.HTTP_303_SEE_OTHER)
        kelas = get_kelas(db, kelas_id)
        if (kelas != None) and (user not in kelas.peserta):
            ikut_kelas(db, user, kelas_id)
        return RedirectResponse(url="/browse", status_code=status.HTTP_303_SEE_OTHER)
    finally:
        db.close()

@app.post("/buat_undangan")
async def buat_undangan(request: Request, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        context = {"request": request}
        user = get_mahasiswa(db, auth.get('user'))
        if user == None:
            return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)


        form = await request.form()
        tutor_nim = form.get("tutor_nim")
        tutor = get_mahasiswa(db, nim=tutor_nim)
        if tutor == None:
            return RedirectResponse(url='/browse', status_code=status.HTTP_303_SEE_OTHER)
        nama_kelas = form.get("nama_kelas")
        semester = form.get("semester")

        undangan = UndanganCreate(creator=user.nama, tutor_id=tutor.id, nama_kelas=nama_kelas, semester=semester)
        undangan = create_undangan(db, undangan)
        return RedirectResponse(url='/browse', status_code=status.HTTP_303_SEE_OTHER)
    finally:
        db.close()

@app.get("/acc_undangan/{undangan_id}")
async def get_acc_undangan(request: Request, undangan_id: int, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        user = get_mahasiswa(db, email=auth.get('user'))
        context = {"request": request}
        ref = request.headers.get("referer").removeprefix(str(request.base_url)) 
        if user == None:
            RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
        undangan = get_undangan(db, undangan_id)
        context['undangan'] = undangan
        context['user'] = user
        return frontends.TemplateResponse("newclass.html", context)
    finally:
        db.close()

@app.get("/dec_undangan/{undangan_id}")
async def get_dec_undangan(request: Request, undangan_id: int, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        user = get_mahasiswa(db, email=auth.get('user'))
        context = {"request": request}
        ref = request.headers.get("referer").removeprefix(str(request.base_url)) 
        if user == None:
            return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
        dec_undangan(db, undangan_id)
        if ref:
            return RedirectResponse(url=f'/{ref}', status_code=status.HTTP_303_SEE_OTHER)
        else:
            return RedirectResponse(url='/browse', status_code=status.HTTP_303_SEE_OTHER)
    finally:
        db.close()

@app.get("/hapuskelas/{kelas_id}")
async def get_hapuskelas(request: Request, kelas_id: int, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        context = {"request": request}
        user = get_mahasiswa(db, email=auth.get('user'))
        if user == None:
            return RedirectResponse(url='/logout', status_code=status.HTTP_303_SEE_OTHER)
        kelas = get_kelas(db, kelas_id)
        if kelas != None and kelas.tutor_id == user.id:
            hapus_kelas(db, kelas)
        return RedirectResponse(url='/kelassaya')
    finally:
        db.close()

@app.get("/get_jadwal_ruangan/{tanggal}")
async def get_hapuskelas(request: Request, tanggal: str, db: Session = Depends(get_db), auth=Depends(auth_handler.auth_wrapper)):
    try:
        context = {"request": request}
        user = get_mahasiswa(db, email=auth.get('user'))
        if user == None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        print(tanggal)
        print(type(tanggal))
        resp = get_jadwal_ruangan(db, tanggal)
        return resp
    finally:
        db.close()
