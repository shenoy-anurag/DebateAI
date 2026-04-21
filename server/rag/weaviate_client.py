from typing import Optional, List, Any
from dataclasses import dataclass

import weaviate
from weaviate import WeaviateClient
from weaviate.classes.init import Auth
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate.retrievers import WeaviateHybridSearchRetriever

import config


@dataclass
class Citation:
    text: str
    source: str
    page: Optional[int] = None


class WeaviateClientManager:
    _instance: Optional[WeaviateClient] = None
    _embeddings: Optional[OpenAIEmbeddings] = None

    @classmethod
    def get_client(cls) -> WeaviateClient:
        if cls._instance is None:
            auth = Auth.api_key(config.WEAVIATE_API_KEY) if config.WEAVIATE_API_KEY else None
            
            cls._instance = weaviate.connect_to_custom(
                url=config.WEAVIATE_URL,
                auth_credentials=auth,
            )
        return cls._instance

    @classmethod
    def get_embeddings(cls) -> OpenAIEmbeddings:
        if cls._embeddings is None:
            cls._embeddings = OpenAIEmbeddings(
                model=config.OPENAI_EMBEDDING_MODEL,
                api_key=config.OPENAI_API_KEY
            )
        return cls._embeddings

    @classmethod
    def close(cls):
        if cls._instance:
            cls._instance.close()
            cls._instance = None

    @classmethod
    def create_schema(cls):
        client = cls.get_client()
        
        if client.collections.exists(config.WEAVIATE_INDEX_NAME):
            return
        
        client.collections.create(
            name=config.WEAVIATE_INDEX_NAME,
            vectorizer_config=[
                weaviate.classes.config.Vectorizer.text2vec_transformers(
                    vectorize_collection_name=config.WEAVIATE_INDEX_NAME
                )
            ],
            property=[
                weaviate.classes.config.Property(
                    name="content",
                    data_type=weaviate.classes.config.DataType.TEXT
                ),
                weaviate.classes.config.Property(
                    name="source",
                    data_type=weaviate.classes.config.DataType.TEXT
                ),
                weaviate.classes.config.Property(
                    name="page",
                    data_type=weaviate.classes.config.DataType.INT
                ),
                weaviate.classes.config.Property(
                    name="session_id",
                    data_type=weaviate.classes.config.DataType.TEXT
                ),
            ]
        )

    @classmethod
    def get_or_create_index(cls):
        client = cls.get_client()
        try:
            return client.collections.get(config.WEAVIATE_INDEX_NAME)
        except:
            cls.create_schema()
            return client.collections.get(config.WEAVIATE_INDEX_NAME)
