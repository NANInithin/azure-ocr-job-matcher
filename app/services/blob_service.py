from azure.storage.blob import BlobServiceClient, ContentSettings
from app.core.config import settings


class BlobStorageService:
    def __init__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        self.container_name = settings.azure_storage_container_raw
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

    def ensure_container_exists(self):
        if not self.container_client.exists():
            self.container_client.create_container()

    def upload_file(self, blob_name: str, data: bytes, content_type: str | None = None):
        self.ensure_container_exists()
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type) if content_type else None,
        )
        return blob_client.url