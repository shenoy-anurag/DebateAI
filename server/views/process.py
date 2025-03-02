import os, shutil
from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import APIRouter
from fastapi import status

from constants import UPLOAD_DIR
from ingest.ingester import process_files

router = APIRouter(
    prefix="/process",
    tags=["process"]
)


@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(file: UploadFile):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"✅ File uploaded successfully: {file_path}")

        # Check if file is readable
        with open(file_path, "r", encoding="utf-8") as f:
            print(f"🔍 File preview: {f.read(500)}")

        process_files()

        return {"message": f"{file.filename} uploaded and processed successfully!"}

    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        return {"error": "Failed to process the file"}
