# LlamaIndex - Evaluation & Observability Reference

> This reference is loaded on demand from ../SKILL.md for evaluation and observability topics.

## Evaluation Discipline

**Before tuning anything:** create a fixed eval set of 20-50 hand-labeled query-answer pairs from your actual use cases. This is your ground truth. Never tune without it.

## Retrieval Metrics

### Hit Rate

Measures whether relevant documents appear in top-k results.

```python
def hit_rate(relevant_ids, retrieved_ids):
    """Return True if any relevant document was retrieved."""
    return len(relevant_ids & retrieved_ids) > 0

# Evaluate across dataset
def evaluate_hit_rate(queries_with_relevant, retriever, top_k=5):
    hits = 0
    for query, relevant_ids in queries_with_relevant:
        nodes = retriever.retrieve(query)
        retrieved_ids = {n.node.node_id for n in nodes}
        if hit_rate(relevant_ids, retrieved_ids):
            hits += 1
    return hits / len(queries_with_relevant)
```

### Recall@K

Measures what fraction of relevant documents were retrieved.

```python
def recall_at_k(relevant_ids, retrieved_ids, k):
    """Fraction of relevant docs retrieved."""
    relevant_in_top_k = relevant_ids & retrieved_ids
    return len(relevant_in_top_k) / len(relevant_ids)

# Evaluate
def evaluate_recall(queries_with_relevant, retriever, k=5):
    recalls = []
    for query, relevant_ids in queries_with_relevant:
        nodes = retriever.retrieve(query)
        retrieved_ids = {n.node.node_id for n in nodes}
        recalls.append(recall_at_k(relevant_ids, retrieved_ids, k))
    return sum(recalls) / len(recalls)
```

### MRR (Mean Reciprocal Rank)

Measures how high relevant documents rank.

```python
def reciprocal_rank(relevant_ids, retrieved_nodes):
    """1/rank of first relevant document, or 0 if none found."""
    for i, node in enumerate(retrieved_nodes):
        if node.node_id in relevant_ids:
            return 1 / (i + 1)
    return 0

def evaluate_mrr(queries_with_relevant, retriever, top_k=5):
    rrs = []
    for query, relevant_ids in queries_with_relevant:
        nodes = retriever.retrieve(query)[:top_k]
        rrs.append(reciprocal_rank(relevant_ids, nodes))
    return sum(rrs) / len(rrs)
```

## Response Quality Metrics

### Faithfulness Evaluation

Checks if responses are grounded in retrieved context (no hallucination).

```python
from llama_index.core.evaluation import FaithfulnessEvaluator
from llama_index.llms.openai import OpenAI

# Create evaluator
llm = OpenAI(model="gpt-4o", temperature=0.0)
evaluator = FaithfulnessEvaluator(llm=llm)

# Evaluate response
query_engine = index.as_query_engine()
response = query_engine.query("What are the key points?")

eval_result = evaluator.evaluate_response(response=response)

print(f"Passing: {eval_result.passing}")
print(f"Feedback: {eval_result.feedback}")
```

### Relevancy Evaluation

Checks if the response actually answers the query.

```python
from llama_index.core.evaluation import RelevancyEvaluator

evaluator = RelevancyEvaluator(llm=llm)

eval_result = evaluator.evaluate_response(
    query="What is the main topic?",
    response=response,
)

print(f"Passing: {eval_result.passing}")
print(f"Score: {eval_result.score}")
```

### Ragas Integration

Comprehensive RAG evaluation framework.

```python
from llama_index.core.evaluation import RagasEvaluator
from llama_index.core.evaluation.ragas import RagasMetric

# Create evaluator
evaluator = RagasEvaluator(
    metric=RagasMetric.FAITHFULNESS,
)

# Evaluate
result = evaluator.evaluate_response(
    query=query,
    response=response,
    contexts=[node.text for node in response.source_nodes],
)

print(f"Score: {result.score}")
```

## Latency and Cost Tracking

### Per-Query Latency

```python
import time

def measure_latency(query_engine, query):
    start = time.perf_counter()
    response = query_engine.query(query)
    end = time.perf_counter()
    return end - start

# Benchmark across eval set
latencies = [
    measure_latency(query_engine, query)
    for query, _ in eval_queries
]
print(f"Mean latency: {sum(latencies)/len(latencies):.2f}s")
print(f"P95 latency: {sorted(latencies)[int(len(latencies)*0.95)]:.2f}s")
```

### Token Cost Tracking

```python
from llama_index.core.callbacks import TokenCountingHandler
import tiktoken
from llama_index.core import Settings, CallbackManager

# Setup token counter
token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-4o").encode,
)
Settings.callback_manager = CallbackManager([token_counter])

# Run queries
response = query_engine.query("Your query")

# Get costs
total_llm_tokens = token_counter.total_llm_token_count
total_embedding_tokens = token_counter.total_embedding_token_count

# Calculate cost (adjust for your pricing)
cost = (total_llm_tokens / 1_000_000) * 0.03  # $0.03 per 1M tokens for gpt-4o
print(f"Cost per query: ${cost:.4f}")
```

## Batch Evaluation

Evaluate your entire eval set at once.

```python
from tqdm import tqdm

def batch_evaluate_retrieval(queries_with_relevant, retriever, top_k=5):
    """Evaluate retrieval metrics across dataset."""
    hit_rates = []
    recalls = []
    rrs = []

    for query, relevant_ids in tqdm(queries_with_relevant):
        nodes = retriever.retrieve(query)[:top_k]
        retrieved_ids = {n.node.node_id for n in nodes}

        # Hit rate
        if relevant_ids & retrieved_ids:
            hit_rates.append(1)
        else:
            hit_rates.append(0)

        # Recall
        recall = len(relevant_ids & retrieved_ids) / len(relevant_ids)
        recalls.append(recall)

        # MRR
        for i, node in enumerate(nodes):
            if node.node_id in relevant_ids:
                rrs.append(1 / (i + 1))
                break
        else:
            rrs.append(0)

    return {
        "hit_rate": sum(hit_rates) / len(hit_rates),
        "recall@k": sum(recalls) / len(recalls),
        "mrr": sum(rrs) / len(rrs),
    }

def batch_evaluate_responses(eval_set, query_engine, evaluator):
    """Evaluate response quality across dataset."""
    results = []

    for query, expected_answer in tqdm(eval_set):
        response = query_engine.query(query)
        result = evaluator.evaluate_response(
            query=query,
            response=response,
        )
        results.append(result)

    passing_rate = sum(1 for r in results if r.passing) / len(results)
    avg_score = sum(r.score for r in results if r.score) / len(results)

    return {
        "passing_rate": passing_rate,
        "average_score": avg_score,
        "results": results,
    }
```

## Observability

### Callbacks and Token Tracking

```python
from llama_index.core import Settings
from llama_index.core.callbacks import (
    CallbackManager,
    LlamaDebugHandler,
    TokenCountingHandler,
)
import tiktoken

# Create handlers
token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-4o").encode,
)
debug_handler = LlamaDebugHandler(print_trace_on_end=True)

# Set callback manager
Settings.callback_manager = CallbackManager([token_counter, debug_handler])

# Run query
response = query_engine.query("Your query")

# Get token counts
print(f"Total LLM tokens: {token_counter.total_llm_token_count}")
print(f"Embedding tokens: {token_counter.total_embedding_token_count}")
```

### LlamaIndex Debugging

```python
from llama_index.core.callbacks import LlamaDebugHandler

debug_handler = LlamaDebugHandler()
Settings.callback_manager = CallbackManager([debug_handler])

# Run query
response = query_engine.query("Your query")

# Get events
events = debug_handler.get_event_pairs()

for event in events:
    print(f"Event: {event[0].type}")
    print(f"Duration: {event[1].time - event[0].time}")
```

### LangSmith Integration

```python
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "YOUR_LANGSMITH_KEY"
os.environ["LANGCHAIN_PROJECT"] = "my-project"

# LlamaIndex automatically logs to LangSmith
response = query_engine.query("Your query")
```
