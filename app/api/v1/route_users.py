from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from database.schemas import MahasiswaCreate

routercok = APIRouter()

@routercok.post("/daftarcoy")
def create_mahasiswa(user: MahasiswaCreate, db: Session):
    pass
