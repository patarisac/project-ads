from pydantic import BaseModel

class MahasiswaBase(BaseModel):
    nim: str

class MahasiswaCreate(MahasiswaBase):
    email: str
    nama: str
    password: str

class Mahasiswa(MahasiswaBase):
    id: int
    email: str
    nama: str
