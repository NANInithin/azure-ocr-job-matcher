from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

from app.core.config import settings


class DocumentIntelligenceService:
    def __init__(self):
        self.client = DocumentIntelligenceClient(
            endpoint=settings.azure_document_intelligence_endpoint,
            credential=AzureKeyCredential(settings.azure_document_intelligence_key),
        )

    def analyze_read_from_bytes(self, content: bytes):
        poller = self.client.begin_analyze_document(
            "prebuilt-read",
            body=content,
        )
        result = poller.result()

        return {
            "raw_result": result,
            "raw_dict": result.as_dict(),
            "model_id": result.model_id,
            "full_text": result.content if hasattr(result, "content") else "",
            "page_count": len(result.pages) if getattr(result, "pages", None) else 0,
        }