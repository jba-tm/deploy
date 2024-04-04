import pandas as pd
from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def search_clinical_data(query, final_cl_kg_searched_final, expanded_df_final, edge_filters=None):
    query = query.strip()
    # Check if query is an NCT number (assuming NCT number has a specific format)
    if query.startswith('NCT'):
        # Search for NCT number in the source column of final_cl_kg_searched_final
        matched_indices = final_cl_kg_searched_final[final_cl_kg_searched_final['source'].str.contains(query)].index
    else:
        # Find similar drug names
        unique_drugs = final_cl_kg_searched_final['target'].dropna().unique()

        similar_drugs = list(
            set([str(drug) for drug in unique_drugs if similar(str(drug).lower(), query.lower()) >= 0.9]))

        # Search these similar drugs in the target column
        matched_nct_numbers = final_cl_kg_searched_final[final_cl_kg_searched_final['target'].isin(similar_drugs)][
            'source'].unique()
        matched_indices_1 = final_cl_kg_searched_final[final_cl_kg_searched_final['source'].str.contains(query)].index

        # Search these NCT numbers in the source column
        matched_indices_2 = final_cl_kg_searched_final[
            final_cl_kg_searched_final['source'].isin(matched_nct_numbers)].index

        matched_indices = matched_indices_1.union(matched_indices_2)

    # Retrieve corresponding rows from expanded_df_final
    search_results = expanded_df_final.loc[matched_indices]

    # Apply edge filter if specified
    if edge_filters:
        search_results = search_results[search_results['edge'].isin(edge_filters)]

    return search_results


def search_drug_gk(query, drugs_df, kg_df):
    search_columns = ['name', 'pubmed-id', 'Gene Name', 'GenBank Protein ID', 'GenBank Gene ID', 'UniProt ID']
    matched_drugs = []
    query = query.strip()
    # Check if the query is in any of the search columns
    for col in search_columns:
        # Filter out rows with NaN values in the current column
        tmp_df = drugs_df[pd.notna(drugs_df[col])].copy()

        # Convert the column to string to ensure compatibility with str.contains
        tmp_df.loc[:, col] = tmp_df[col].astype(str)

        if col == 'pubmed-id' and query.isnumeric():
            # Search in 'pubmed-id' column, handling case-insensitivity
            matched_drugs.extend(tmp_df[tmp_df[col].str.contains(query, case=False, regex=False)]['name'].tolist())
        else:
            # Search in other columns, handling case-insensitivity
            tmp_df = drugs_df[pd.notna(drugs_df[col])].copy()

            # Convert the column to string to ensure compatibility with str.contains
            tmp_df.loc[:, col] = tmp_df[col].astype(str)

            for _, row in tmp_df.iterrows():
                if similar(query.lower(), row[col].lower()) >= 0.9:
                    matched_drugs.append(row['name'])

    # Remove duplicates
    matched_drugs = list(set(matched_drugs))

    # Search in the original KG dataset
    kg_search_results = kg_df[kg_df['source'].isin(matched_drugs) | kg_df['target'].isin(matched_drugs)]

    return kg_search_results
