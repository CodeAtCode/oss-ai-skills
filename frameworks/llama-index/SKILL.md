---
name: llama-index
description: Use when building RAG or LLM applications with LlamaIndex - data loaders, node parsing, vector stores, retrievers and rerankers, query engines, agents and workflows, streaming, or evaluation
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - llama-index
    - llm
    - rag
    - ai
    - python
    - vector-database
    - openai
    - agents
---

# LlamaIndex Development

Complete guide for building RAG applications with LlamaIndex framework.

## Overview

LlamaIndex is a data framework for LLM applications, providing tools for data ingestion, indexing, and retrieval.

**Key Characteristics:**
- RAG (Retrieval Augmented Generation) support
- Multiple data connectors (300+)
- Various index types
- Query and chat engines
- Vector store integrations
- Agent framework

## Installation

### Setup

```bash
# Basic installation (v0.14+)
pip install llama-index

# With OpenAI
pip install llama-index-llms-openai
pip install llama-index-embeddings-openai

# With workflow engine support
pip install llama-index-core

# With vector stores
pip install llama-index-vector-stores-chroma
pip install llama-index-vector-stores-pinecone
pip install llama-index-vector-stores-qdrant

# With evaluation
pip install llama-index-llms-openai ragas
```

### Version Notes

- Current stable: v0.14.x (rapid monthly releases)
- Import paths unified under `llama_index.core`
- Workflow engine added for complex multi-step operations

### Basic Configuration

```python
import os
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# Set API key
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

# Configure global settings
Settings.llm = OpenAI(model="gpt-4o", temperature=0.0)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.chunk_size = 512
Settings.chunk_overlap = 50
```

## Quick Start

### Basic RAG Pipeline (v0.14+)

```python
# Unified imports in v0.14+
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage

# Load documents
documents = SimpleDirectoryReader("./docs").load_data()

# Create index
index = VectorStoreIndex.from_documents(documents)

# Create query engine
query_engine = index.as_query_engine()

# Query
response = query_engine.query("What is the main topic?")
print(response)
```

### With Storage

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

# Setup ChromaDB
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("my-index")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load and index
documents = SimpleDirectoryReader("./docs").load_data()
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    embed_model=OpenAIEmbedding(),
)

# Persist
storage_context.persist()

# Load from disk
index = VectorStoreIndex.from_vector_store(
    vector_store,
    embed_model=OpenAIEmbedding(),
)
```

## Data Loading

### Document Loaders

```python
from llama_index.core import SimpleDirectoryReader, Document

# Load from directory
documents = SimpleDirectoryReader(
    input_dir="./docs",
    required_exts=[".pdf", ".txt", ".md"],
    exclude=["*.tmp"],
    recursive=True,
).load_data()

# Load specific files
documents = SimpleDirectoryReader(
    input_files=["./file1.pdf", "./file2.txt"]
).load_data()

# Create documents manually
documents = [
    Document(text="Content here", metadata={"source": "manual"}),
]

# With metadata extraction
def custom_metadata_func(file_path: str) -> dict:
    return {
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
    }

documents = SimpleDirectoryReader(
    input_dir="./docs",
    file_metadata=custom_metadata_func,
).load_data()
```

### Custom Data Connectors

```python
from llama_index.core import Document
from typing import List

class CustomDataReader:
    """Custom data loader."""

    def load_data(self, source: str) -> List[Document]:
        documents = []

        # Load from custom source
        # Example: API, database, etc.
        data = self._fetch_from_source(source)

        for item in data:
            doc = Document(
                text=item["content"],
                metadata={
                    "source": source,
                    "id": item["id"],
                    "timestamp": item["timestamp"],
                },
            )
            documents.append(doc)

        return documents

    def _fetch_from_source(self, source: str):
        # Implement data fetching
        pass

# Usage
reader = CustomDataReader()
documents = reader.load_data("api://endpoint")
```

## Chunking Decision Guide

Chunk boundaries directly determine citation quality and retrieval accuracy. Choose based on your data structure and query patterns.

### When Sentence Splitting Beats Semantic Chunking

**Use sentence splitting when:**
- Your documents have clear structural divisions (headings, sections, pages)
- You need predictable chunk sizes for cost/latency estimation
- Your queries are fact-based rather than concept-based
- You're working with technical documentation or legal texts

**Use semantic chunking when:**
- Your documents lack clear structure (emails, chat logs, unstructured notes)
- Query intent varies significantly within paragraphs
- You need to preserve thematic boundaries over structural ones
- You have budget for embedding-based splitting overhead

### Fixed-Size-with-Overlap Pitfalls

```python
# ❌ PITFALL: Ignoring semantic boundaries
splitter = SentenceSplitter(
    chunk_size=512,
    chunk_overlap=50,
    # No paragraph or section awareness
)

# ✅ BETTER: Respect document structure
splitter = SentenceSplitter(
    chunk_size=512,
    chunk_overlap=50,
    paragraph_separator="\n\n",  # Split on paragraphs first
    secondary_chunking_regex=r"\n#{1,6} ",  # Don't break across headings
)
```

**Common overlap mistakes:**
- Overlap too small (<10%): Context boundaries get cut mid-sentence
- Overlap too large (>30%): Redundant embeddings, higher cost, diluted relevance
- Fixed overlap ignores structure: Section headers appear in wrong chunks

### Metadata to Attach at Ingest Time

Metadata enables filtering and improves retrieval precision. Attach these at ingest:

| Metadata Field | Why It Matters |
|----------------|----------------|
| `source` (file path) | Cite exact document when answering |
| `section_heading` | Preserve document hierarchy in context |
| `page_number` | Critical for PDFs and scanned documents |
| `document_date` | Filter by recency for time-sensitive queries |
| `tenant_id` / `PROJECT_KEY` | Multi-tenant isolation via metadata filters |

```python
from llama_index.core import Document

def load_with_metadata(file_path: str) -> List[Document]:
    """Load documents with essential metadata for retrieval."""
    # Parse file to extract structure
    content, headings, page_numbers = parse_document(file_path)

    return [
        Document(
            text=chunk.text,
            metadata={
                "source": file_path,
                "section": chunk.section,
                "page": page_numbers[chunk.start_line],
                "tenant_id": "my-tenant",  # Replace with actual tenant
            },
        )
        for chunk in split_by_structure(content, headings)
    ]
```

### Evaluating Chunking Changes

Never guess whether a chunking change helped. Measure:

1. **Create a fixed eval set:** 20-50 query-answer pairs hand-labeled from your actual use cases
2. **Run retrieval before change:** Record which chunks are retrieved for each query
3. **Apply chunking change:** Re-index the same documents
4. **Run retrieval after change:** Compare hit rates on the same queries
5. **Measure:**
   - Hit rate: % of queries where relevant chunk appears in top-k
   - MRR (Mean Reciprocal Rank): How high relevant chunks rank
   - Citation quality: Do answers reference the correct source sections?

```python
# Simple hit rate evaluation
def evaluate_chunking(queries_with_relevant_chunks, retriever, top_k=5):
    hits = 0
    for query, relevant_ids in queries_with_relevant_chunks:
        nodes = retriever.retrieve(query)
        retrieved_ids = {n.node.node_id for n in nodes}
        if relevant_ids & retrieved_ids:  # Any overlap = hit
            hits += 1
    return hits / len(queries_with_relevant_chunks)
```

## Vector Stores

Vector store setup follows the same pattern across backends:

```python
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# 1. Initialize backend client
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("my-index")

# 2. Wrap as LlamaIndex vector store
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 3. Create index with storage context
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
```

**Backend-specific notes:**
- ChromaDB: Use `PersistentClient` for local storage, `EphemeralClient` for testing
- Pinecone: Create index with matching embedding dimensions (1536 for text-embedding-3-small)
- Qdrant: Specify `collection_name` and ensure vector size matches embed_model

For detailed setup per backend, see `references/retrieval.md`.

## Retrieval Debugging

Symptom-first guide to fixing retrieval problems.

### Answers Cite the Wrong Section

**Symptom:** Response references information from the wrong document or section.

**Check:**
1. Are metadata filters applied at query time?
2. Do chunks have accurate `source` and `section` metadata?
3. Is the LLM instructed to cite sources?

**Fix:**
```python
# Apply metadata filters to narrow retrieval
query_engine = index.as_query_engine(
    filters=MetadataFilter(
        key="tenant_id", value="my-tenant"  # Replace with actual filter
    )
)

# Or filter at retriever level
retriever = index.as_retriever(
    filters=MetadataFilter(key="source", value="specific-file.pdf")
)
```

### Retrieval Returns Nothing Relevant

**Symptom:** Query returns chunks that don't match the question intent.

**Check:**
1. Do embedding dimensions match at index and query time?
2. Is the embed_model the same for indexing and querying?
3. Is `similarity_top_k` too low?

**Fix:**
```python
# Ensure consistent embedding model
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# At index time
index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

# At query time (must match)
query_engine = index.as_query_engine(
    embed_model=embed_model,  # Same model as index time
    similarity_top_k=10,  # Retrieve more before reranking
)
```

### Answers Are Generic

**Symptom:** Responses lack specificity, sound like boilerplate.

**Check:**
1. Is `similarity_top_k` too low (<5)?
2. Is reranking enabled?
3. Are retrieved chunks too large (diluted relevance)?

**Fix:**
```python
from llama_index.core.postprocessor import SentenceTransformerRerank

# Retrieve more, then rerank
query_engine = index.as_query_engine(
    similarity_top_k=20,
    node_postprocessors=[
        SentenceTransformerRerank(
            model="cross-encoder/ms-marco-MiniLM-L-6-v2",
            top_n=5,
        ),
    ],
)
```

### Hybrid Search Behaves Inconsistently

**Symptom:** Keyword + vector search gives unpredictable results.

**Check:**
1. Is the BM25 weight tuned for your data?
2. Is the keyword index fresh (rebuilt after document updates)?
3. Are you using AND vs OR mode appropriately?

**Fix:**
```python
from llama_index.core.retrievers import QueryFusionRetriever

# Tune query fusion parameters
fusion_retriever = QueryFusionRetriever(
    retrievers=[vector_retriever, keyword_retriever],
    similarity_top_k=10,
    num_queries=3,
    mode="reciprocal_rerank",  # Or "weighted_sum"
)

# For strict matching, use AND mode
hybrid_retriever = HybridRetriever(
    vector_index, keyword_index, mode="AND"  # Only return nodes in both
)
```

## Deep Dives

Advanced topics are split into reference files loaded on demand:

- **references/retrieval.md** — Advanced retrievers (hybrid, query fusion, auto-merging), rerankers, query engines (router, sub-question, multi-step)
- **references/agents-workflows.md** — Agents (ReAct, function calling, custom tools), streaming, workflow engine, chat engines
- **references/evaluation-observability.md** — Evaluation (retrieval hit rate, recall@k, faithfulness, latency/cost tracking), observability (callbacks, LangSmith)

## Common Issues

### Chunk Size Problems

```python
# ❌ BAD: Too small chunks lose context
splitter = SentenceSplitter(chunk_size=64)

# ❌ BAD: Too large chunks dilute relevance
splitter = SentenceSplitter(chunk_size=8192)

# ✅ GOOD: Balanced chunk size
splitter = SentenceSplitter(
    chunk_size=512,  # For embeddings
    chunk_overlap=50,  # ~10% overlap
)
```

### Retrieval Quality

```python
# ❌ BAD: No reranking, few results
query_engine = index.as_query_engine(similarity_top_k=3)

# ✅ GOOD: Retrieve more, rerank
query_engine = index.as_query_engine(
    similarity_top_k=20,
    node_postprocessors=[
        SentenceTransformerRerank(top_n=5),
    ],
)
```

### Memory Issues

```python
# ❌ BAD: Load all documents at once
documents = SimpleDirectoryReader("./huge_folder").load_data()

# ✅ GOOD: Process in batches
from llama_index.core import StorageContext

for batch in document_batches:
    nodes = splitter.get_nodes_from_documents(batch)
    index.insert_nodes(nodes)
```

### Embedding Dimension Mismatch

```python
# ❌ BAD: Index created with different embedding
# Pinecone index: 1536 dimensions
# Using: 768 dimension embeddings

# ✅ GOOD: Match dimensions
embed_model = OpenAIEmbedding(model="text-embedding-3-small")  # 1536 dims
# Create Pinecone index with same dimensions
```

## Best Practices

1. **Use appropriate chunk sizes** (512-1024 for most use cases)
2. **Always add overlap** (5-10% of chunk size)
3. **Use rerankers** for better retrieval quality
4. **Enable streaming** for better UX
5. **Use async** for parallel queries
6. **Implement caching** for repeated queries
7. **Monitor token usage** with callbacks
8. **Test with evaluation** before production
9. **Use hybrid search** for better recall
10. **Keep context window** in mind for chat

## Resources

- **Documentation:** https://docs.llamaindex.ai/
- **GitHub:** https://github.com/run-llama/llama_index
- **Examples:** https://github.com/run-llama/llama_index/tree/main/docs/examples
- **Discord:** https://discord.gg/dGcwcsnxhU
- **Blog:** https://blog.llamaindex.ai/

## Quick Reference

### Common Imports

```python
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Document,
    Settings,
    StorageContext,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
```

### Common Patterns

```python
# Basic RAG
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("query")

# With reranking
query_engine = index.as_query_engine(
    similarity_top_k=20,
    node_postprocessors=[reranker],
)

# Streaming
query_engine = index.as_query_engine(streaming=True)
for token in query_engine.query("query").response_gen:
    print(token)

# Chat
chat_engine = index.as_chat_engine()
response = chat_engine.chat("message")

# Agent
agent = ReActAgent.from_tools(tools, llm=llm)
response = agent.chat("message")
```
