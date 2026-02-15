from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

MODEL = SentenceTransformer("all-MiniLM-L6-v2")

CANONICAL_METRICS = {
    "employment": "number of employees jobs workforce size",
    "company_count": "number of firms companies providers",
    "revenue_eur": "annual revenue turnover income eur",
    "gross_value_added": "gross value added gva economic output",
    "investment": "investment funding capital raised",
    "growth_rate": "growth rate percentage annual increase"
}

canonical_keys = list(CANONICAL_METRICS.keys())
canonical_embeddings = MODEL.encode(list(CANONICAL_METRICS.values()))


def classify_metric_semantically(text):

    text_embedding = MODEL.encode([text])

    similarities = cosine_similarity(text_embedding, canonical_embeddings)[0]

    best_index = np.argmax(similarities)
    best_score = similarities[best_index]

    return canonical_keys[best_index], float(best_score)
