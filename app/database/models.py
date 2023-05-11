from typing import List
from sqlalchemy import Boolean, ForeignKey, Integer, String, Date, Table, Column
from sqlalchemy.orm import Mapped, relationship, mapped_column, has_inherited_table, declared_attr
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

ikut_kelas = Table(
    "ikut_kelas",
    Base.metadata,
    Column("kelas_id", ForeignKey("kelas.id"), primary_key=True),
    Column("mahasiswa_id", ForeignKey("mahasiswa.id"), primary_key=True),
)


class Mahasiswa(Base):
    __tablename__ = "mahasiswa"
    id = mapped_column(Integer, primary_key=True)
    nim = mapped_column(String(11), unique=True, nullable=False)
    email = mapped_column(String, nullable=False, unique=True)
    nama = mapped_column(String, nullable=False)
    hashed_password = mapped_column(String, nullable=False)
    kelas_diikuti : Mapped[List["Kelas"]] = relationship(secondary=ikut_kelas, back_populates="peserta")
    kelas_ditutor : Mapped[List["Kelas"]] = relationship(back_populates="tutor")


class HasIdMixin:
    @declared_attr.cascading
    def id(cls) -> Mapped[int]:
        if has_inherited_table(cls):
            return mapped_column(ForeignKey("kelas.id"), primary_key=True)
        else:
            return mapped_column(Integer, primary_key=True)

class Kelas(HasIdMixin, Base):
    __tablename__ = "kelas"
    tutor_id = mapped_column(Integer, ForeignKey("mahasiswa.id"))
    tutor : Mapped["Mahasiswa"] = relationship(back_populates="kelas_ditutor")
    namakelas = mapped_column(String, nullable=False)
    waktumulai = mapped_column(Date, nullable=False)
    waktuselesai = mapped_column(Date, nullable=False)
    peserta : Mapped[List["Mahasiswa"]] = relationship(secondary=ikut_kelas, back_populates="kelas_diikuti")
    tipe : Mapped[str]
    __mapper_args__ = {"polymorphic_on": "tipe"}

class KelasOnline(Kelas):
    __tablename__ = "kelasonline"
    lokasi = mapped_column(String, nullable=False)
    kebutuhan = mapped_column(String, nullable=False)
    __mapper_args__ = {"polymorphic_identity": "online"}

class KelasOnsite(Kelas):
    __tablename__ = "kelasonsite"
    link_meet = mapped_column(String, nullable=False)
    __mapper_args__ = {"polymorphic_identity": "offline"}

class Undangan(Base):
    __tablename__ = "undangan"
    id = mapped_column(Integer, primary_key=True)
    nama_kelas = mapped_column(String, nullable=False)
    is_created = mapped_column(Integer, nullable=True)
    creator_id = mapped_column(Integer, ForeignKey("mahasiswa.id"), nullable=False)
    tutor_id = mapped_column(Integer, ForeignKey("mahasiswa.id"), nullable=False)
    kelas_id = mapped_column(Integer, ForeignKey("kelas.id"), nullable=True)
