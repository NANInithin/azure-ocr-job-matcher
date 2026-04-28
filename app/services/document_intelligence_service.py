from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

from app.core.config import settings


class DocumentIntelligenceService:
    def __init__(self):
        self.client = DocumentIntelligenceClient(
            endpoint=settings.azure_document_intelligence_endpoint,
            credential=AzureKeyCredential(settings.azure_document_intelligence_key),
        )
        self.default_model = getattr(settings, "azure_document_intelligence_model", "prebuilt-layout")

    def analyze_from_bytes(self, content: bytes, model_id: str | None = None) -> dict:
        selected_model = model_id or self.default_model

        poller = self.client.begin_analyze_document(
            selected_model,
            body=content,
        )
        result = poller.result()
        result_dict = result.as_dict()

        return {
            "model_id": result.model_id,
            "full_text": result.content if getattr(result, "content", None) else "",
            "page_count": len(result.pages) if getattr(result, "pages", None) else 0,
            "raw_dict": result_dict,
        }