import os
import glob
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.models import Source, RAGResult


CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "chroma_db")
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "documents")


OPENROUTER_BASE = "https://openrouter.ai/api/v1"


def get_embeddings():
    try:
        api_key = os.environ.get("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
    except Exception:
        api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    try:
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=api_key,
            openai_api_base=OPENROUTER_BASE,
            default_headers={"HTTP-Referer": "https://jernih.app", "X-Title": "JERNIH"},
        )
    except Exception:
        return None



@st.cache_resource
def initialize_vector_store():
    embeddings = get_embeddings()
    if embeddings is None:
        return None

    if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        try:
            return Chroma(
                persist_directory=CHROMA_DIR,
                embedding_function=embeddings,
            )
        except Exception:
            import shutil
            shutil.rmtree(CHROMA_DIR, ignore_errors=True)
            pass

    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR, exist_ok=True)
        return None

    txt_files = glob.glob(os.path.join(DOCS_DIR, "**", "*.txt"), recursive=True)
    if not txt_files:
        return None

    documents = []
    for file_path in txt_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            if text.strip():
                metadata = {"source": os.path.basename(file_path)}
                documents.append(Document(page_content=text, metadata=metadata))
        except Exception:
            continue

    if not documents:
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    os.makedirs(CHROMA_DIR, exist_ok=True)
    try:
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_DIR,
        )
        vector_store.persist()
        return vector_store
    except Exception:
        return None


def query_rag(query: str, top_k: int = 5) -> RAGResult:
    vector_store = initialize_vector_store()
    if vector_store is None:
        return RAGResult(
            context="",
            sources=[],
            confidence=0.0,
        )

    try:
        results = vector_store.similarity_search_with_relevance_scores(
            query, k=top_k
        )
    except Exception:
        try:
            results = vector_store.similarity_search_with_score(query, k=top_k)
        except Exception:
            return RAGResult(context="", sources=[], confidence=0.0)

    if not results:
        return RAGResult(context="", sources=[], confidence=0.0)

    context_parts = []
    seen_sources = {}
    total_score = 0.0

    for i, result in enumerate(results):
        if len(result) == 2:
            doc, score = result
        else:
            doc = result
            score = 0.0

        relevance = max(0.0, min(1.0, float(score))) if isinstance(score, (int, float)) else 0.5
        total_score += relevance

        context_parts.append(doc.page_content)

        source_name = doc.metadata.get("source", f"Sumber {i+1}")
        if source_name not in seen_sources:
            seen_sources[source_name] = Source(
                title=source_name,
                url="",
                source_type="dokumen",
            )

    context = "\n\n---\n\n".join(context_parts[:3])
    avg_confidence = (total_score / len(results)) * 100 if results else 0.0

    return RAGResult(
        context=context,
        sources=list(seen_sources.values()),
        confidence=min(avg_confidence, 99.0),
    )
