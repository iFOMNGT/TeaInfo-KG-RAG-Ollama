import os
import logging
from lightrag import LightRAG, QueryParam
from lightrag.llm import ollama_model_complete, ollama_embedding
from lightrag.utils import EmbeddingFunc
from save_latest_output import save_backup 

WORKING_DIR = ""

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=ollama_model_complete,
    llm_model_name="qwen2.5:32b",
    llm_model_max_async=16,
    llm_model_max_token_size=32768,
    chunk_token_size=600,
    entity_summary_to_max_tokens=800,
    llm_model_kwargs={"host": "http://localhost:11434", "options": {"num_ctx": 32768}},
    embedding_func=EmbeddingFunc(
        embedding_dim=1024,
        max_token_size=8192,
        func=lambda texts: ollama_embedding(
            texts, embed_model="bge-m3", host="http://localhost:11434"
        ),
    ),
)

with open("", "r", encoding="utf-8") as f:
    rag.insert(f.read())

save_backup()
