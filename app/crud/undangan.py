from sqlalchemy.orm import Session
from starlette.datastructures import FormData
from datetime import datetime, date
from database import models, schemas
from utils.auth import auth_handler
from utils.date import *

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
