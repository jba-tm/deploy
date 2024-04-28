import pandas as pd
from app.db.session import gk_engine
from app.contrib.graph_knowledge.utils import parquet_to_sql


def trials_to_sql():
    data_path = "data"

    parquet_file = f"{data_path}/Structured data/clinical_trials_kg_df.parquet"

    parquet_to_sql(gk_engine, "clinical_trials", parquet_file, index=True)

    clinical_trials_searched = f"{data_path}/Structured data/clinical_trials_searched_kg_df.parquet"
    parquet_to_sql(gk_engine, "clinical_trials_searched", clinical_trials_searched, index=True)


if __name__ == "__main__":
    trials_to_sql()
