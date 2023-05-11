from fastapi import Depends
from sqlalchemy.orm import Session
from . import models, schemas
from utils.auth import auth_handler


# def get_mahasiswa(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()

# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()

# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()

def create_mahasiswa(db: Session, user: schemas.MahasiswaCreate):
    hashed_password = auth_handler.get_password_hash(user.password)
    new_user= models.Mahasiswa(nim=user.nim, email=user.email, nama=user.nama, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_mahasiswa(db: Session, email: str):
    user = db.query(models.Mahasiswa).filter(models.Mahasiswa.email == email).first()
    return user

def login_mahasiswa(db: Session, email: str, password: str):
    user = get_mahasiswa(db, email)
    if (user is None) or (not auth_handler.verify_password(password, user.hashed_password)):
        return None
    token = auth_handler.encode_token(email)
    return { 'token': token }


