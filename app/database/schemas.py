from pydantic import BaseModel
import datetime

class MahasiswaBase(BaseModel):
    email: str
    nama: str
    nim: str

class MahasiswaCreate(MahasiswaBase):
    password: str

    class Config:
        orm_mode = True

class Mahasiswa(MahasiswaBase):
    id: int

class KelasBase(BaseModel):
    tutor_id: int
    semester: int
    nama_kelas: str
    waktumulai: datetime.datetime
    waktuselesai: datetime.datetime
    tipe: str

class KelasCreate(KelasBase):
    pass

class KelasOnlineBase(KelasBase):
    link_meet: str

class KelasOnline(KelasOnlineBase):
    id: int

class KelasOnlineCreate(KelasOnlineBase):
    pass

class KelasOnsiteBase(KelasBase):
    lokasi: str

class KelasOnsite(KelasOnsiteBase):
    id: int

class KelasOnsiteCreate(KelasOnsiteBase):
    pass

class KelasHybridBase(KelasBase):
    link_meet: str
    lokasi: str

class KelasHybrid(KelasHybridBase):
    id: int

class KelasHybridCreate(KelasHybridBase):
    pass

class UndanganBase(BaseModel):
    creator: str
    tutor_id: int
    nama_kelas: str
    semester: int

class UndanganCreate(UndanganBase):
    pass
