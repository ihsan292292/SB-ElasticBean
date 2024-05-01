"""
BSD 3-Clause License

Copyright (c) 2021, Grigory Leikin (reOiL)
All rights reserved.
"""
import firebase_admin
from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import Storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from firebase_admin import credentials, storage
import threading

class FirebaseStorage(Storage):
    def __init__(self):
        cred = credentials.Certificate(settings.FIREBASE_CERT_DATA)
        firebase = firebase_admin.initialize_app(cred, name=f'firebase-{threading.current_thread().name}')
        self.bucket = storage.bucket(settings.FIREBASE_STORAGE_BUCKET, firebase)

    def exists(self, name):
        return self.bucket.get_blob(name) != None

    def delete(self, name):
        if self.exists(name):
            self.bucket.blob(name).delete()

    def _save(self, name, content):
        blob = self.bucket.blob(name)
        if isinstance(content, InMemoryUploadedFile):
            blob.upload_from_string(content.read(), content_type=content.content_type)
        elif isinstance(content, File):
            blob.upload_from_string(content.read())
        else:
            raise ValueError(f"Undefined content type: {type(content)}")

        blob.make_public()
        return name

    def url(self, name):
        if not self.exists(name):
            return None
        return self.bucket.blob(name).public_url
