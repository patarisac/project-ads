import aiofiles

async def save_img(file: bytes, filename: str):
    path = f"static/img/bannerkelas/{filename}"
    async with aiofiles.open(path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write
    return path
