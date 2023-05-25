from sqlalchemy.orm import Session
from starlette.datastructures import FormData
from utils.date import *
from datetime import datetime, date
from database import models, schemas
from utils.auth import auth_handler

class NotifikasiController:

    def get_notifikasi(self, db: Session, user: models.Mahasiswa):
        notif = {'kelas': [], 'undangan': []}
        for kls in user.kelas_diikuti:
            if kls.waktumulai.date() == date.today():
                if kls.waktuselesai > datetime.now():
                    notif['kelas'].append(kls)
        
        for udg in user.undangan:
            if not udg.is_created:
                notif['undangan'].append(udg)
        return notif
