from sqlalchemy.orm import Session
from starlette.datastructures import FormData
from utils.date import *
from datetime import datetime, date
from database import models, schemas
from utils.auth import auth_handler

class UndanganController:
    def get_undangan(self, db: Session, id: int) -> models.Undangan:
        undangan = db.query(models.Undangan).filter(models.Undangan.id == id).first()
        return undangan

    def create_undangan(self, db: Session, undangan: schemas.UndanganCreate):
        undanganbaru = models.Undangan(nama_kelas=undangan.nama_kelas, semester=undangan.semester, creator=undangan.creator, tutor_id=undangan.tutor_id)
        db.add(undanganbaru)
        db.commit()
        db.refresh(undanganbaru)
        return undanganbaru

    def acc_undangan(self, db: Session, id: int, kelas_id: int):
        undangan = self.get_undangan(db, id)
        undangan.is_created = 1
        undangan.kelas_id = kelas_id
        db.commit()
        db.refresh(undangan)
        return undangan

    def dec_undangan(self, db: Session, user: models.Mahasiswa, id: int):
        undangan = self.get_undangan(db, id)
        if user.id != undangan.tutor_id:
            return False
        undangan.is_created = 2
        db.commit()
        db.refresh(undangan)
        return undangan
