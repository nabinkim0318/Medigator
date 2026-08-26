# api/routers/rag.py
import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from api.core.config import settings
from api.core.exceptions import RAGServiceException
from api.core.safe_logging import log_error, log_info, log_warning
from api.services.rag import build_index, init_retriever, make_query, retrieve
from api.services.rag.retrieve import USE_RAG

# Get logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])


# Pydantic models
class SearchRequest(BaseModel):
    """RAG search request model"""

    query: str
    k: int | None = 4
    use_hybrid: bool | None = True


class SearchResponse(BaseModel):
    """RAG search response model"""

    results: list[dict[str, Any]]
    query: str
    total_results: int
    rag_enabled: bool


class IndexRequest(BaseModel):
    """Index building request model"""

    docs_dir: str = "docs"
    out_dir: str = "rag_index"
    chunk_size: int = 512
    overlap: int = 50
    max_docs: int | None = None


class IndexResponse(BaseModel):
    """Index building response model"""

    success: bool
    message: str
    stats: dict[str, Any]


class RAGStatusResponse(BaseModel):
    """RAG system status response"""

    model_config = {"protected_namespaces": ()}

    enabled: bool
    initialized: bool
    index_path: str | None = None
    index_size: int | None = None
    model_name: str | None = None


@router.get("/status", response_model=RAGStatusResponse)
async def get_rag_status():
    """Get RAG system status"""
    log_info(logger, "rag_status_check")

    try:
        status = {
            "enabled": USE_RAG,
            "initialized": False,
            "index_path": None,
            "index_size": None,
            "model_name": None,
        }

        if USE_RAG:
            try:
                init_retriever()
                status["initialized"] = True
                log_info(logger, "rag_initialized")
            except Exception:
                log_warning(logger, "rag_initialization_failed")
                status["initialized"] = False

        return RAGStatusResponse(**status)

    except Exception:
        log_error(logger, "rag_status_failed")
        raise RAGServiceException(message="Failed to get RAG status")


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search documents using RAG"""
    log_info(logger, "rag_search_requested")

    try:
        if not USE_RAG:
            log_warning(logger, "rag_search_disabled")
            return SearchResponse(
                results=[],
                query=request.query,
                total_results=0,
                rag_enabled=False,
            )

        # Initialize RAG if not already done
        try:
            init_retriever()
        except Exception:
            log_error(logger, "rag_initialization_failed")
            raise RAGServiceException(message="RAG system not available")

        # Create summary-like structure for query
        summary = {
            "query": request.query,
            "flags": {},
            "codes": {"icd": [], "cpt": [], "labels": []},
            "cc": request.query,
        }

        # Perform search
        k_value = request.k or 4  # Default to 4 if None
        results = retrieve(summary, k=k_value)
        log_info(logger, "rag_search_completed", result_count=len(results))

        # Convert results to response format
        search_results = []
        for result in results:
            chunk = result.get("chunk", {})
            search_results.append(
                {
                    "title": chunk.get("title", "Document"),
                    "text": chunk.get("text", ""),
                    "source": chunk.get("source", ""),
                    "url": chunk.get("url", ""),
                    "score": result.get("score", 0.0),
                    "year": chunk.get("year", ""),
                    "section": chunk.get("section", ""),
                    "tags": chunk.get("tags_json", {}),
                },
            )

        return SearchResponse(
            results=search_results,
            query=request.query,
            total_results=len(search_results),
            rag_enabled=True,
        )

    except RAGServiceException:
        raise
    except Exception:
        log_error(logger, "rag_search_failed")
        raise RAGServiceException(message="Search failed")


@router.post("/build-index", response_model=IndexResponse)
async def build_rag_index(request: IndexRequest):
    """Build RAG index from documents"""
    log_info(logger, "rag_index_build_requested")

    try:
        # Build index
        stats = build_index(
            docs_dir=request.docs_dir,
            out_dir=request.out_dir,
            chunk_size=request.chunk_size,
            overlap=request.overlap,
            max_docs=request.max_docs,
        )

        log_info(logger, "rag_index_built")

        return IndexResponse(
            success=True, message="Index built successfully", stats=stats
        )

    except Exception:
        log_error(logger, "rag_index_build_failed")
        raise RAGServiceException(message="Index build failed")


@router.get("/query-example")
async def get_query_example():
    """Get example of how to construct queries for RAG search"""
    log_info(logger, "rag_query_example")

    example_summary = {
        "flags": {"ischemic_features": True, "dm_followup": False},
        "codes": {
            "icd": ["I25.9", "E11.9"],
            "cpt": ["99213", "99214"],
            "labels": ["chest pain", "diabetes"],
        },
        "cc": "chest pain with exertion",
        "hpi": "Patient presents with chest pain that occurs with exertion and is relieved by rest.",
    }

    try:
        query = make_query(example_summary)
        log_info(logger, "rag_query_example_generated")

        return {
            "example_summary": example_summary,
            "generated_query": query,
            "description": "This shows how to structure input for RAG search",
        }

    except Exception:
        log_error(logger, "rag_query_example_failed")
        raise RAGServiceException(message="Failed to generate query example")


@router.get("/health")
async def health_check():
    """RAG service health check"""
    log_info(logger, "rag_health_check")

    try:
        health_status = {
            "service": "rag",
            "status": "healthy" if USE_RAG else "disabled",
            "rag_enabled": USE_RAG,
            "rag_retrieval_mode": settings.rag_retrieval_mode,
            "initialized": False,
        }

        if USE_RAG:
            try:
                init_retriever()
                health_status["initialized"] = True
                log_info(logger, "rag_health_ok")
            except Exception:
                health_status["status"] = "unhealthy"
                log_warning(logger, "rag_health_failed")

        return health_status

    except Exception:
        log_error(logger, "rag_health_failed")
        raise RAGServiceException(message="Health check failed")
