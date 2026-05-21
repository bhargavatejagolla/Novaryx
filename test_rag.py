import sys
import logging
sys.path.insert(0, '.')
logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(message)s')

from system.rag_engine.chromadb_client import ChromaDBClient
from system.rag_engine.embedding_manager import OllamaEmbeddingFunction
from system.rag_engine.retriever import TemplateRetriever

print('--- Testing embed_query directly ---')
fn = OllamaEmbeddingFunction()
result = fn.embed_query(input='saas dashboard analytics')
print(f'embed_query result length: {len(result)}')

print('--- Testing collection.query via retriever ---')
client = ChromaDBClient(embedding_function=fn)
retriever = TemplateRetriever(client)
templates = retriever.find_best_template('saas', ['dashboard'], ['charts', 'dark mode'])
print(f'Templates found: {len(templates)}')
for t in templates:
    print(f"  - {t.get('id', '?')} dist={t.get('distance', '?'):.4f}")
print('ALL OK')
