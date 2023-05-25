from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.datastructures import FormData
from utils.date import *
from datetime import datetime, date
from database import models, schemas
from utils.auth import auth_handler
from utils.files import save_img

class KelasController:

    def get_kelas(self, db: Session, id: int) -> models.Kelas :
        kelas = db.query(models.Kelas).filter(models.Kelas.id == id).first()
        return kelas

    def search_kelas(self, db: Session, user: models.Mahasiswa, query: str) -> list:
        rightnow = get_time_wib()
        kelas_aktif = db.query(models.Kelas).filter(models.Kelas.waktuselesai > rightnow).filter(func.lower(models.Kelas.namakelas).contains(func.lower(query))).filter(models.Kelas.tutor != user).all()
        sudah_diikuti = [kls for kls in user.kelas_diikuti]
        kelas_aktif = [kls for kls in kelas_aktif if kls not in sudah_diikuti]
        kelas_aktif = sorted(kelas_aktif, key=lambda obj: obj.waktumulai)
        return kelas_aktif

    def get_kelas_aktif(self, db: Session, user: models.Mahasiswa) -> list:
        rightnow = get_time_wib()
        kelas_aktif = db.query(models.Kelas).filter(models.Kelas.waktuselesai > rightnow).filter(models.Kelas.tutor != user).all()
        sudah_diikuti = [kls for kls in user.kelas_diikuti]
        kelas_aktif = [kls for kls in kelas_aktif if kls not in sudah_diikuti]
        kelas_aktif = sorted(kelas_aktif, key=lambda obj: obj.waktumulai)
        return kelas_aktif

    def get_kelas_saya(self, db: Session, user: models.Mahasiswa) -> list:
        rightnow = get_time_wib()
        kelas_saya = user.kelas_ditutor
        kelas_saya = [obj for obj in kelas_saya if obj.waktuselesai > rightnow]
        kelas_saya = sorted(kelas_saya, key=lambda obj: obj.waktumulai)
        return kelas_saya

    def get_kelas_diikuti(self, db: Session, user: models.Mahasiswa) -> list:
        rightnow = get_time_wib()
        kelas_diikuti = user.kelas_diikuti
        kelas_diikuti = [obj for obj in kelas_diikuti if obj.waktuselesai > rightnow]
        kelas_diikuti = sorted(kelas_diikuti, key=lambda obj: obj.waktumulai)
        return kelas_diikuti

    def ikut_kelas(self, db: Session, user: models.Mahasiswa, kelas_id: int):
        kelas = self.get_kelas(db, kelas_id)
        user.kelas_diikuti.append(kelas)
        db.commit()
        db.refresh(user)
        db.refresh(kelas)

    def create_kelas(self, db: Session, kelas: schemas.KelasCreate, ext, **attr):
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

    async def edit_kelas(self, db: Session, form: FormData):
        kelas = self.get_kelas(db, form.get("kelas_id"))
        banner = form.get('banner')
        if banner.filename != "":
            banner = form.get("banner")
            ext = banner.filename.split(".")[-1]
            filename = f"banner_k{kelas.id}.{ext}"
            await save_img(banner, filename)
            kelas.banner = filename
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

    def hapus_kelas(self, db: Session, kelas: models.Kelas):
        kelas.waktumulai = datetime.min
        kelas.waktuselesai = datetime.min
        db.commit()
        db.refresh(kelas)

    def get_jadwal_ruangan(self, db: Session, tanggal: str) -> list:
        try:
            awal = datetime.fromisoformat(tanggal+'T00:00:00')
            akhir = datetime.fromisoformat(tanggal+'T23:59:59.999999')
            kelas = db.query(models.Kelas).filter(models.Kelas.tipe != "online").filter(models.Kelas.waktumulai > awal).filter(models.Kelas.waktuselesai < akhir).all()
            resp = {"data": []}
            for kls in kelas:
                data = []
                data.append(kls.lokasi)
                data.append(kls.waktumulai.strftime('%H:%M'))
                data.append(kls.waktuselesai.strftime('%H:%M'))
                resp['data'].append(data)
            return resp
        except Exception as e:
            print(e)
            return None
