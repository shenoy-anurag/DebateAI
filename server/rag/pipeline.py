import uuid
from typing import List, Optional
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config
from rag.weaviate_client import WeaviateClientManager


class RAGPipeline:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
        )

    def load_document(self, file_path: Path) -> List[Document]:
        if file_path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif file_path.suffix.lower() == ".txt":
            loader = TextLoader(str(file_path), encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        return loader.load()

    def split_documents(self, documents: List[Document]) -> List[Document]:
        return self.text_splitter.split_documents(documents)

    def process_and_store(
        self, 
        file_path: Path, 
        session_id: str,
        paper_title: str = "Untitled"
    ) -> int:
        docs = self.load_document(file_path)
        split_docs = self.split_documents(docs)

        index = WeaviateClientManager.get_or_create_index()

        with_index = index.batch.dynamic()
        
        for doc in split_docs:
            page = doc.metadata.get("page")
            
            with_index.add(
                properties={
                    "content": doc.page_content,
                    "source": paper_title,
                    "page": page,
                    "session_id": session_id,
                }
            )

        with_index.flush()
        
        return len(split_docs)

    def delete_session(self, session_id: str) -> bool:
        index = WeaviateClientManager.get_or_create_index()
        
        response = index.query.fetch_objects(
            filters={
                "path": ["session_id"],
                "operator": "Equal",
                "valueText": session_id
            }
        )
        
        if not response.objects:
            return False
        
        for obj in response.objects:
            index.data.delete_by_id(obj.uuid)
        
        return True
