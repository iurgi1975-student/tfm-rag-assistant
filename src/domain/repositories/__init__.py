"""Repository interfaces - Abstract contracts for data access.

Repositories define HOW to access data, but not WHERE or HOW it's stored.
This allows switching between Chroma, PostgreSQL, in-memory, etc. without changing business logic.
"""
from .vector_store_repository import VectorStoreRepository
from .llm_repository import LLMRepository

__all__ = ["VectorStoreRepository", "LLMRepository"]