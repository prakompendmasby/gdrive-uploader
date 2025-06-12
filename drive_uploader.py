from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json


def upload_to_drive(file_path):
    credentials_info = os.getenv("GOOGLE_CREDENTIALS")
    if not credentials_info:
        raise Exception("Missing GOOGLE_CREDENTIALS env var")

    creds = service_account.Credentials.from_service_account_info(json.loads(credentials_info))
    service = build('drive', 'v3', credentials=creds)

    folder_id = os.getenv("GDRIVE_FOLDER_ID")
    file_metadata = {'name': os.path.basename(file_path), 'parents': [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    file_id = file.get('id')
    return f"https://drive.google.com/file/d/{file_id}/view"
