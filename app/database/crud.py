from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.datastructures import FormData
from . import models, schemas
from utils.auth import auth_handler
from utils.date import get_time_wib, split_date
from datetime import datetime, date


# def get_mahasiswa(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()

# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()

# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()

def create_mahasiswa(db: Session, user: schemas.MahasiswaCreate) -> models.Mahasiswa:
    hashed_password = auth_handler.get_password_hash(user.password)
    new_user= models.Mahasiswa(nim=user.nim, email=user.email, nama=user.nama, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_mahasiswa(db: Session, email: str = None, nim: str = None) -> models.Mahasiswa:
    if email:
        user = db.query(models.Mahasiswa).filter(models.Mahasiswa.email == email).first()
    elif nim:
        user = db.query(models.Mahasiswa).filter(models.Mahasiswa.nim == nim).first()
    else:
        return None
    return user

def changepassword(db: Session, user : models.Mahasiswa, passwd : str, newpasswd : str):
    if auth_handler.verify_password(passwd, user.hashed_password):
        newhashpasswd = auth_handler.get_password_hash(newpasswd)
        user.hashed_password = newhashpasswd
        db.commit()
        db.refresh(user)
        return user
    else:
        return False

def get_kelas(db: Session, id: int) -> models.Kelas :
    kelas = db.query(models.Kelas).filter(models.Kelas.id == id).first()
    return kelas

def get_undangan(db: Session, id: int) -> models.Undangan:
    undangan = db.query(models.Undangan).filter(models.Undangan.id == id).first()
    return undangan

def get_notifikasi(db: Session, user: models.Mahasiswa):
    notif = {'kelas': [], 'undangan': []}
    for kls in user.kelas_diikuti:
        if kls.waktumulai.date() == date.today():
            if kls.waktuselesai > datetime.now():
                notif['kelas'].append(kls)
    
    for udg in user.undangan:
        if not udg.is_created:
            notif['undangan'].append(udg)
    return notif

def search_kelas(db: Session, query: str) -> list:
    rightnow = get_time_wib()
    kelas_aktif = db.query(models.Kelas).filter(models.Kelas.waktuselesai > rightnow).filter(func.lower(models.Kelas.namakelas).contains(func.lower(query))).all()
    kelas_aktif = sorted(kelas_aktif, key=lambda obj: obj.waktumulai)
    return kelas_aktif

def get_kelas_aktif(db: Session) -> list:
    rightnow = get_time_wib()
    kelas_aktif = db.query(models.Kelas).filter(models.Kelas.waktuselesai > rightnow).all()
    kelas_aktif = sorted(kelas_aktif, key=lambda obj: obj.waktumulai)
    return kelas_aktif

def get_kelas_saya(db: Session, user: models.Mahasiswa) -> list:
    rightnow = get_time_wib()
    kelas_saya = user.kelas_ditutor
    kelas_saya = [obj for obj in kelas_saya if obj.waktuselesai > rightnow]
    kelas_saya = sorted(kelas_saya, key=lambda obj: obj.waktumulai)
    return kelas_saya

def get_kelas_diikuti(db: Session, user: models.Mahasiswa) -> list:
    rightnow = get_time_wib()
    kelas_diikuti = user.kelas_diikuti
    kelas_diikuti = [obj for obj in kelas_diikuti if obj.waktuselesai > rightnow]
    kelas_diikuti = sorted(kelas_diikuti, key=lambda obj: obj.waktumulai)
    return kelas_diikuti

def ikut_kelas(db: Session, user: models.Mahasiswa, kelas_id: int):
    kelas = get_kelas(db, kelas_id)
    user.kelas_diikuti.append(kelas)
    db.commit()
    db.refresh(user)
    db.refresh(kelas)

def login_mahasiswa(db: Session, email: str, password: str):
    user = get_mahasiswa(db, email)
    if (user is None) or (not auth_handler.verify_password(password, user.hashed_password)):
        return None
    token = auth_handler.encode_token(email)
    return { 'token': token }

def create_kelas(db: Session, kelas: schemas.KelasCreate, ext, **attr):
    if kelas.tipe == "hybrid":
        kelasbaru = models.KelasHybrid(tutor_id=kelas.tutor_id, namakelas=kelas.nama_kelas, semester=kelas.semester, waktumulai=kelas.waktumulai, waktuselesai=kelas.waktuselesai, tipe=kelas.tipe, link_meet=attr.get("link_meet"), lokasi=attr.get("lokasi"), kebutuhan=attr.get("kebutuhan"))
    elif kelas.tipe == "onsite":
        kelasbaru = models.KelasOnsite(tutor_id=kelas.tutor_id, namakelas=kelas.nama_kelas, semester=kelas.semester, waktumulai=kelas.waktumulai, waktuselesai=kelas.waktuselesai, tipe=kelas.tipe, lokasi=attr.get("lokasi"), kebutuhan=attr.get("kebutuhan"))
    else:
        kelasbaru = models.KelasOnline(tutor_id=kelas.tutor_id, namakelas=kelas.nama_kelas, semester=kelas.semester, waktumulai=kelas.waktumulai, waktuselesai=kelas.waktuselesai, tipe=kelas.tipe, link_meet=attr.get("link_meet"))
    db.add(kelasbaru)
    db.commit()
    db.refresh(kelasbaru)
    if ext:
        filename = f"banner_k{kelasbaru.id}.{ext}"
    else:
        filename = f"banner_default.jpg"
    kelasbaru.banner = filename
    db.commit()
    db.refresh(kelasbaru)
    return kelasbaru

def edit_kelas(db: Session, form: FormData):
    kelas = get_kelas(db, form.get("kelas_id"))
    if kelas.namakelas != form.get("namakelas"):
        kelas.namakelas = form.get('namakelas')
    if kelas.semester != int(form.get('semester')):
        kelas.semester = int(form.get('semester'))
    tanggal = form.get('tanggal')
    waktumulai = form.get('waktumulai')
    waktuselesai = form.get('waktuselesai')
    kelasmulai, kelasselesai = split_date(tanggal, waktumulai, waktuselesai)
    if kelas.waktumulai != kelasmulai:
        kelas.waktumulai = kelasmulai
    if kelas.waktuselesai != kelasselesai:
        kelas.waktuselesai = kelasselesai
    if kelas.tipe == 'online' or kelas.tipe == 'hybrid':
        if kelas.link_meet != form.get('link_meet'):
            kelas.link_meet = form.get('link_meet')
    if kelas.tipe == 'hybrid' or kelas.tipe == 'onsite':
        if kelas.lokasi != form.get('ruangan'):
            kelas.lokasi = form.get('ruangan')
        if kelas.kebutuhan != form.get('fasilitas'):
            kelas.kebutuhan = form.get('fasilitas')
    db.commit()
    db.refresh(kelas)

def hapus_kelas(db: Session, kelas: models.Kelas):
    kelas.waktumulai = datetime.min
    kelas.waktuselesai = datetime.min
    db.commit()
    db.refresh(kelas)

def create_undangan(db: Session, undangan: schemas.UndanganCreate):
    undanganbaru = models.Undangan(nama_kelas=undangan.nama_kelas, semester=undangan.semester, creator=undangan.creator, tutor_id=undangan.tutor_id)
    db.add(undanganbaru)
    db.commit()
    db.refresh(undanganbaru)
    return undanganbaru

def acc_undangan(db: Session, id: int, kelas_id: int):
    undangan = get_undangan(db, id)
    undangan.is_created = 1
    undangan.kelas_id = kelas_id
    db.commit()
    db.refresh(undangan)
    return undangan

def dec_undangan(db: Session, id: int):
    undangan = get_undangan(db, id)
    undangan.is_created = 2
    db.commit()
    db.refresh(undangan)
    return undangan
