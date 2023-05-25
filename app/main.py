from fastapi import FastAPI, Request, Depends, UploadFile, File, HTTPException, status
from fastapi.staticfiles import StaticFiles
from routers import core, kelas, mahasiswa, undangan

app = FastAPI(title="StudyBuddy")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(core.router)
app.include_router(kelas.router)
app.include_router(mahasiswa.router)
app.include_router(undangan.router)
