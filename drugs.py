from app.db.session import gk_engine
from app.contrib.graph_knowledge.utils import parquet_to_sql


def drugs_to_sql():
    data_path = "app/contrib/graph_knowledge/data"

    # parquet_file = f"{data_path}/Structured data/knowledge_graph.parquet"
    #
    # parquet_to_sql(gk_engine, "knowledge_graph", parquet_file, index=True)

    all_drugs_parquet = f"{data_path}/Structured data/final_merged_drugs.parquet"
    parquet_to_sql(gk_engine, "final_merged_drugs", all_drugs_parquet, index=True)


if __name__ == "__main__":
    drugs_to_sql()
