import logging
from app.extractors.layout_engine import build_ast
from app.extractors.table_engine import extract_tables
from app.extractors.chart_engine import extract_charts
from app.classification.embedding_classifier import classify_metric_semantically
from app.classification.taxonomy_mapper import map_to_taxonomy
from app.services.confidence_engine import compute_confidence
from app.services.reconciliation_service import reconcile
from app.derivation.gva_engine import reconstruct_gva
from app.services.longitudinal_builder import build_longitudinal_dataset
from app.db.database import SessionLocal
from app.db.models import Metric


def run_pipeline(pdf_path, document_id):

    logging.info("Building AST...")
    build_ast(pdf_path)

    logging.info("Extracting tables...")
    table_metrics = extract_tables(pdf_path, document_id)

    logging.info("Extracting charts...")
    chart_metrics = extract_charts(pdf_path, document_id)

    all_metrics = table_metrics + chart_metrics

    enriched_metrics = []

    for metric in all_metrics:

        raw_text = metric.get("raw_text", "")

        original_key = metric.get("metric_key")

        if original_key in [None, "table_metric"]:
            predicted_key, similarity = classify_metric_semantically(raw_text)
            metric["metric_key"] = predicted_key
        else:
            similarity = 1.0 # structured extraction confidence

        metric = map_to_taxonomy(metric)

        metric["confidence_score"] = compute_confidence(
            metric,
            similarity_score=similarity
        )

        enriched_metrics.append(metric)

    reconciled = reconcile(enriched_metrics)

    # 🔥 Derived metrics
    derived_metrics = reconstruct_gva(reconciled)

    final_metrics = reconciled + derived_metrics

    # 🔥 Build longitudinal dataset
    longitudinal_df = build_longitudinal_dataset(final_metrics)

    db = SessionLocal()

    for metric in final_metrics:
        db.add(Metric(**metric))

    db.commit()
    db.close()

    logging.info("Phase 5 completed.")

    return longitudinal_df
