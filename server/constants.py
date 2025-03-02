import os

DATA_DIR = '../data'

UPLOAD_DIR = "uploads"

UPLOAD_PATH = os.path.join(DATA_DIR, UPLOAD_DIR)

os.makedirs(UPLOAD_PATH, exist_ok=True)
