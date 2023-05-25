from sqlalchemy.orm import Session
from starlette.datastructures import FormData
from datetime import datetime, date
from database import models, schemas
from utils.auth import auth_handler
from utils.date import *


def create_mahasiswa(db: Session, user: schemas.MahasiswaCreate) -> models.Mahasiswa:
    hashed_password = auth_handler.get_password_hash(user.password)
    new_user = models.Mahasiswa(nim=user.nim, email=user.email, nama=user.nama, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_mahasiswa(db: Session, email: str, password: str):
    user = get_mahasiswa(db, email)
    if (user is None) or (not auth_handler.verify_password(password, user.hashed_password)):
        return None
    token = auth_handler.encode_token(email)
    return {"token": token}


def get_mahasiswa(db: Session, email: str = None, nim: str = None) -> models.Mahasiswa:
    if email:
        user = db.query(models.Mahasiswa).filter(models.Mahasiswa.email == email).first()
    elif nim:
        user = db.query(models.Mahasiswa).filter(models.Mahasiswa.nim == nim).first()
    else:
        return None
    return user


def changepassword(db: Session, user: models.Mahasiswa, passwd: str, newpasswd: str):
    if auth_handler.verify_password(passwd, user.hashed_password):
        newhashpasswd = auth_handler.get_password_hash(newpasswd)
        user.hashed_password = newhashpasswd
        db.commit()
        db.refresh(user)
        return user
    else:
        return False
