from typing import List, Optional
from dataclasses import dataclass

from langchain_core.documents import Document

import config
from rag.weaviate_client import WeaviateClientManager, Citation


@dataclass
class RetrievedContext:
    documents: List[Document]
    citations: List[Citation]


class CitationRetriever:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.index = WeaviateClientManager.get_or_create_index()

    def retrieve(self, query: str, top_k: int = None) -> RetrievedContext:
        if top_k is None:
            top_k = config.RETRIEVER_TOP_K

        response = self.index.query.hybrid(
            query=query,
            limit=top_k,
            filters={
                "path": ["session_id"],
                "operator": "Equal",
                "valueText": self.session_id
            }
        )

        documents = []
        citations = []

        for obj in response.objects:
            doc = Document(
                page_content=obj.properties.get("content", ""),
                metadata={
                    "source": obj.properties.get("source", ""),
                    "page": obj.properties.get("page"),
                }
            )
            documents.append(doc)
            
            citation = Citation(
                text=obj.properties.get("content", ""),
                source=obj.properties.get("source", ""),
                page=obj.properties.get("page"),
            )
            citations.append(citation)

        return RetrievedContext(documents=documents, citations=citations)

    def get_context_string(self, query: str, top_k: int = None) -> str:
        result = self.retrieve(query, top_k)
        
        context_parts = []
        for i, citation in enumerate(result.citations, 1):
            source_info = f"Page {citation.page}" if citation.page else citation.source
            context_parts.append(f"[{i}] ({source_info}): {citation.text}")
        
        return "\n\n".join(context_parts)

    def format_citations(self, citations: List[Citation]) -> str:
        if not citations:
            return ""
        
        formatted = []
        for i, citation in enumerate(citations, 1):
            source_info = f"Page {citation.page}" if citation.page else citation.source
            formatted.append(f"[{i}] {source_info}")
        
        return "; ".join(formatted)
