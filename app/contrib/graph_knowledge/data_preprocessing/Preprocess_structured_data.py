import pandas as pd
import numpy as np
from tqdm import tqdm
import re
import pathlib

drugs_file = "../data/Structured data/drugs.csv"
protein_file = "../data/Structured data/protien_id.csv"
drugs_side_effects_file = "../data/Structured data/drugs-side-effects.xlsx"

# Read the CSV file into a DataFrame
df = pd.read_csv(protein_file)

# Split the 'Drug IDs' column into a list of IDs
df['Drug IDs'] = df['Drug IDs'].str.split('; ')

# Explode the DataFrame
df_exploded = df.explode('Drug IDs')

# Save the modified DataFrame to a new CSV file
new_file_path = "../data/Structured data/target.parquet"  # Replace with your desired new file path
df_exploded.to_parquet(new_file_path, engine="fastparquet", index=False)

print("File saved as:", new_file_path)

# Load the data from the CSV file
drugs_1_df = pd.read_csv(drugs_file)

# Load the data from the Excel file
drugs_2_df = pd.read_excel(drugs_side_effects_file)[['Medicine', 'Treated Diseases/Conditions', 'Side effects']]
target_dataset = pd.read_parquet("../data/Structured data/target.parquet", engine='fastparquet')[
    ['Name', 'Gene Name', 'GenBank Protein ID', 'GenBank Gene ID', 'UniProt ID', 'Uniprot Title', 'GenAtlas ID',
     'Species', 'Drug IDs']]

# Merge the dataframes

merged_df = drugs_1_df.merge(drugs_2_df, left_on='name', right_on='Medicine', how='left')
merged_df = merged_df.merge(target_dataset, left_on='ID', right_on='Drug IDs', how='left')

# Drop the redundant 'Medicine' column
merged_df.drop(['Medicine', 'Drug IDs'], axis=1, inplace=True)

# Identify rows with empty or 'Null' values in 'Treated Diseases/Conditions' and 'Side effects'
null_values_df = merged_df[
    ((merged_df['Side effects'] == 'Null') & (merged_df['Treated Diseases/Conditions'] == 'Null')) |
    (merged_df['Side effects'].isna() & merged_df['Treated Diseases/Conditions'].isna()) |
    merged_df['Name'].isna() &
    merged_df['Gene Name'].isna() &
    merged_df['GenBank Protein ID'].isna() &
    merged_df['GenBank Gene ID'].isna() &
    merged_df['UniProt ID'].isna() &
    merged_df['Uniprot Title'].isna() &
    merged_df['GenAtlas ID'].isna() &
    merged_df['Species'].isna()]
non_null_values_df = merged_df.drop(null_values_df.index).sort_values(by='name')

# Sort the null_values_df by 'name'
null_values_df = null_values_df.sort_values(by='name')

# Concatenate the dataframes back together
final_df = pd.concat([non_null_values_df, null_values_df], ignore_index=True)

final_df = final_df.drop_duplicates(keep='first')
final_df = final_df.replace("Null", np.nan)
final_df = final_df.replace("None", np.nan)
final_df = final_df.replace("null", np.nan)
final_df = final_df.replace("none", np.nan)
final_df = final_df[final_df['name'].str.lower() != np.nan]

final_df.reset_index(inplace=True, drop=True)

# Save the final dataframe to a new CSV file
final_df.to_parquet("../data/Structured data/final_merged_drugs.parquet", engine="fastparquet", index=False)


# Function to clean, explode, and create a DataFrame for a specific edge
def explode_and_create_df(col1, col2, edge_name):
    temp_df = final_df[[col1, col2]].copy()

    # Drop rows with null values in either column
    temp_df.dropna(subset=[col1, col2], inplace=True)
    temp_df = temp_df[temp_df[col2].str.lower() != 'nan']
    temp_df = temp_df[temp_df[col2].str.lower() != np.nan]

    # Drop duplicates
    temp_df.drop_duplicates(inplace=True)

    # Replace consecutive separators with a single separator and split
    temp_df[col2] = temp_df[col2].str.replace(r'\|\|+', '|', regex=True).str.split('|')

    # Explode the DataFrame based on col1 and col2
    temp_df = temp_df.explode(col1).explode(col2)

    # Remove empty strings if any
    temp_df = temp_df[temp_df[col1].str.strip() != '']
    temp_df = temp_df[temp_df[col2].str.strip() != '']

    # Rename columns and create an edge column
    temp_df.rename(columns={col1: 'source', col2: 'target'}, inplace=True)
    temp_df['edge'] = edge_name

    return temp_df


# Function to clean, match, explode, and create a DataFrame
def match_explode_and_create_df(source_col, target_col, edge_name):
    temp_df = final_df[[source_col, target_col]].copy()
    temp_df.dropna(subset=[source_col, target_col], inplace=True)
    temp_df = temp_df[temp_df[target_col].str.lower() != 'nan']
    temp_df = temp_df[temp_df[target_col].str.lower() != np.nan]
    temp_df.drop_duplicates(inplace=True)
    # Split each column by '||' and strip whitespace
    temp_df[source_col] = temp_df[source_col].astype(str).str.strip().str.split('\|\|')
    temp_df[target_col] = temp_df[target_col].astype(str).str.strip().str.split('\|\|')

    # List to store the new rows
    new_rows = []

    # Iterate over each row and create matched pairs
    for _, row in tqdm(temp_df.iterrows()):
        sources = row[source_col]
        targets = row[target_col]

        # if len(sources) == len(targets):
        for source, target in zip(sources, targets):
            new_rows.append({'source': source, 'target': target, 'edge': edge_name})

    # Create a new DataFrame from the list of new rows
    exploded_df = pd.DataFrame(new_rows)

    return exploded_df


def create_genes_df(df, source_col, target_col, edge_name, gene_info_cols=None):
    # Create a new DataFrame
    new_rows = []

    for _, row in df.iterrows():
        source = row[source_col]
        target = row[target_col]

        # Skip if either source or target is NaN
        if pd.isna(source) or pd.isna(target):
            continue

        # Initialize the gene information string
        gene_info = ""

        # Check if gene information columns are provided
        if gene_info_cols:
            gene_info_pieces = []
            for col in gene_info_cols:
                if pd.notna(row[col]):
                    gene_info_pieces.append(f"{col}:- {row[col]}")
            gene_info = "<br>".join(gene_info_pieces)

        new_row = {
            'source': source,
            'target': target,
            'edge': edge_name,
            'Full Gene Name': gene_info
        }

        new_rows.append(new_row)

    return pd.DataFrame(new_rows)


# Explode the specified columns with cleaning
synonyms_df = explode_and_create_df('name', 'synonym', 'has synonym')
diseases_df = explode_and_create_df('name', 'Treated Diseases/Conditions', 'used for')
side_effects_df = explode_and_create_df('name', 'Side effects', 'has side effect')
kingdom_df = explode_and_create_df('name', 'kingdom', 'Kingdom')
supclass_df = explode_and_create_df('name', 'subclass', 'Subclass')
superclass_df = explode_and_create_df('name', 'superclass', 'Superclass')
class_df = explode_and_create_df('name', 'class', 'Class')
marketed_name_df = explode_and_create_df('name', 'medicine name', 'marketed name')
manufacturer_df = match_explode_and_create_df('medicine name', 'manufacturer', 'manufacturer')
# medicine_source_df = match_explode_and_create_df('medicine name', 'medicine source', 'source')
country_df = match_explode_and_create_df('manufacturer', 'Country of manufacture', 'country')
gene_info_columns = ['Name', 'GenBank Protein ID', 'GenBank Gene ID', 'UniProt ID', 'Uniprot Title', 'GenAtlas ID']
gene_name_df = create_genes_df(final_df, 'name', 'Gene Name', 'Targets gene', gene_info_cols=gene_info_columns)
species_df = create_genes_df(final_df, 'name', 'Species', 'Effective in species', gene_info_cols=None)

# Concatenate all DataFrames
knowledge_graph = pd.concat(
    [synonyms_df, diseases_df, side_effects_df, kingdom_df, supclass_df, superclass_df, class_df, marketed_name_df,
     manufacturer_df, country_df, gene_name_df, species_df])
# Merge the 'description' column from df into knowledge_graph on 'name' and 'source'
knowledge_graph = knowledge_graph.merge(final_df[['name', 'description']], left_on='source', right_on='name',
                                        how='left')

# Drop the extra 'name' column if not needed
knowledge_graph.drop('name', axis=1, inplace=True)
knowledge_graph.reset_index(inplace=True, drop=True)

# Drop rows where source equals target for 'has synonym' relationship
condition = (knowledge_graph['source'] == knowledge_graph['target']) & (knowledge_graph['edge'] == 'has synonym')
knowledge_graph = knowledge_graph.drop(knowledge_graph[condition].index)
knowledge_graph.reset_index(inplace=True, drop=True)
# Save the knowledge graph to a new CSV file
knowledge_graph.to_parquet("../data/Structured data/knowledge_graph.parquet", engine="fastparquet", index=False)

phase_files = ['Early_Phase_I.csv', 'Phase_I.csv', 'Phase_II.csv', 'Phase_III.csv', 'Phase_IV.csv']
dfs = [pd.read_csv("../data/Structured data/" + file, low_memory=False) for file in phase_files]

# Concatenate all the dataframes
df = pd.concat(dfs, ignore_index=True)

df = df.dropna(subset=['Phases'])
df = df[~df['Phases'].str.contains('\|')]
df = df.reset_index(drop=True)


# Function to process interventions and create edge names
def process_interventions(row):
    interventions = row['Interventions'].split('|')
    new_rows = []
    for intervention in interventions:
        match = re.match(r'([a-zA-Z ]+): (.+)', intervention)
        if match:
            prefix, actual_intervention = match.groups()
            prefix_formatted = prefix.lower()
            edge_name = f"tested {prefix_formatted}"
            new_rows.append({'source': row['NCT Number'], 'target': actual_intervention.strip(), 'edge': edge_name,
                             'title': row['Title']})
        else:
            new_rows.append(
                {'source': row['NCT Number'], 'target': intervention, 'edge': 'tested unknown', 'title': row['Title']})
    return new_rows


# Apply the function to each row
expanded_df = pd.DataFrame(
    [new_row for _, row in df.iterrows() for new_row in process_interventions(row)]
).reset_index(drop=True)

tested_with_relationships = []
for _, row in df.iterrows():
    nct_number = row['NCT Number']
    interventions = row['Interventions'].split('|')
    cleaned_interventions = [re.sub(r'^[a-zA-Z ]+: ', '', intervention).strip() for intervention in interventions]

    for i, intervention_i in enumerate(cleaned_interventions):
        for j, intervention_j in enumerate(cleaned_interventions):
            if i != j:
                tested_with_relationships.append({
                    'source': intervention_i,
                    'target': intervention_j,
                    'edge': 'tested with',
                    'title': None  # Assuming no title is needed for these relationships
                })

# Convert to DataFrame
tested_with_df = pd.DataFrame(tested_with_relationships)

phase_drug_relationships = []
for _, row in df.iterrows():
    phase = row['Phases']
    interventions = row['Interventions'].split('|')
    cleaned_interventions = [re.sub(r'^[a-zA-Z ]+: ', '', intervention).strip() for intervention in interventions]

    for intervention in cleaned_interventions:
        phase_drug_relationships.append({
            'source': intervention,
            'target': phase,
            'edge': 'in phase',
            'title': None
        })

# Convert to DataFrame and concatenate with expanded_df_final
phase_drug_df = pd.DataFrame(phase_drug_relationships)

# Combine with the existing expanded_df
expanded_df = pd.concat([expanded_df, tested_with_df, phase_drug_df]).reset_index(drop=True)

single_value_columns_df = pd.DataFrame({})

# Columns with single values per row
single_value_columns = ['Status', 'Gender', 'Age', 'Enrollment', 'Start Date', 'Completion Date']
edge_names = {
    'Status': 'trial status',
    'Gender': 'gender of volunteers',
    'Age': 'ages of volunteers',
    'Enrollment': 'number of volunteers',
    'Start Date': 'trial start date',
    'Completion Date': 'trial completion date'
}
single_values = []
for col in single_value_columns:
    single_value_columns_df = pd.DataFrame({})
    single_value_columns_df['source'] = df['Phases']
    single_value_columns_df['target'] = df[col]
    single_value_columns_df['edge'] = edge_names[col]
    single_value_columns_df['title'] = None

    single_values.append(single_value_columns_df)

single_values.insert(0, expanded_df)

expanded_df_final = pd.concat(single_values).reset_index(drop=True)

multi_value_columns = ['Conditions', 'Funded By', 'Sponsor/Collaborators']
edge_names_multi = {
    'Conditions': 'tested condition',
    'Funded By': 'funded by',
    'Sponsor/Collaborators': 'collaborates with'
}

multi_value_columns_dfs = []
for col in multi_value_columns:
    temp_df = df[['Phases', col]].dropna()
    temp_df = temp_df.assign(target=temp_df[col].str.split('|')).explode('target')
    temp_df = temp_df.assign(edge=edge_names_multi[col], title=None)
    multi_value_columns_dfs.append(temp_df[['Phases', 'target', 'edge', 'title']].rename(columns={'Phases': 'source'}))


def process_study_designs(row):
    designs = row['Study Designs'].split('|')
    return pd.DataFrame([{'source': row['Phases'], 'target': design.split(': ')[1],
                          'edge': design.split(': ')[0].lower(), 'title': None} for design in designs if
                         ': ' in design])


study_designs_df = pd.concat(df.apply(process_study_designs, axis=1).tolist()).reset_index(drop=True)

expanded_df_final = pd.concat([expanded_df_final] + multi_value_columns_dfs).reset_index(drop=True)
expanded_df_final = pd.concat([expanded_df_final, study_designs_df]).reset_index(drop=True)

expanded_df_final['target'] = expanded_df_final['target'].astype(str)  # Convert 'target' column to string
expanded_df_final.to_parquet("../data/Structured data/clinical_trials_kg_df.parquet", engine="fastparquet", index=False)


# Function to process each row to create relationships
def process_row(row):
    new_rows = []
    interventions = row['Interventions'].split('|')

    # Append NCT number to drug names for 'tested_with' edges
    for intervention in interventions:
        actual_intervention = re.sub(r'^[a-zA-Z ]+: ', '', intervention).strip()
        match = re.match(r'([a-zA-Z ]+): (.+)', intervention)
        edge_name = f"tested {match.groups()[0].lower()}" if match else 'tested unknown'

        new_rows.append(
            {'source': row['NCT Number'], 'target': actual_intervention, 'edge': edge_name, 'title': row['Title']})

    return new_rows


final_cl_kg_searched_df = pd.DataFrame(
    [new_row for _, row in df.iterrows() for new_row in process_row(row)]).reset_index(drop=True)

tested_with_relationships_searched = []
for _, row in df.iterrows():
    nct_number = row['NCT Number']
    interventions = row['Interventions'].split('|')
    cleaned_interventions = [re.sub(r'^[a-zA-Z ]+: ', '', intervention).strip() for intervention in interventions]

    for i, intervention_i in enumerate(cleaned_interventions):
        for j, intervention_j in enumerate(cleaned_interventions):
            if i != j:
                tested_with_relationships_searched.append({
                    'source': f"{intervention_i}_{nct_number}",
                    'target': intervention_j,
                    'edge': 'tested with',
                    'title': None  # Assuming no title is needed for these relationships
                })

# Convert to DataFrame
tested_with_searched_df = pd.DataFrame(tested_with_relationships_searched)

phase_drug_relationships_searched = []
for _, row in df.iterrows():
    phase = row['Phases']
    nct_number = row['NCT Number']
    interventions = row['Interventions'].split('|')
    cleaned_interventions = [re.sub(r'^[a-zA-Z ]+: ', '', intervention).strip() for intervention in interventions]

    for intervention in cleaned_interventions:
        phase_drug_relationships_searched.append({
            'source': f"{intervention}_{nct_number}",
            'target': phase,
            'edge': 'in phase',
            'title': None
        })

# Convert to DataFrame and concatenate with final_cl_kg_searched_final
phase_drug_searched_df = pd.DataFrame(phase_drug_relationships_searched)
final_cl_kg_searched_final = pd.concat(
    [final_cl_kg_searched_df, tested_with_searched_df, phase_drug_searched_df]).reset_index(drop=True)

for col in single_value_columns:
    temp_df_searched = df.copy()
    temp_df_searched['source'] = temp_df_searched.apply(lambda
                                                            row: f"{row['Phases']}_{row['NCT Number']}_{'_'.join([re.sub(r'^[a-zA-Z ]+: ', '', i).strip() for i in row['Interventions'].split('|')])}",
                                                        axis=1)
    temp_df_searched = temp_df_searched.rename(columns={col: 'target'}).assign(edge=edge_names[col], title=None)
    final_cl_kg_searched_final = pd.concat(
        [final_cl_kg_searched_final, temp_df_searched[['source', 'target', 'edge', 'title']]]).reset_index(drop=True)

for col in multi_value_columns:
    temp_df_searched = df.copy()
    temp_df_searched['source'] = temp_df_searched.apply(lambda
                                                            row: f"{row['Phases']}_{row['NCT Number']}_{'_'.join([re.sub(r'^[a-zA-Z ]+: ', '', i).strip() for i in row['Interventions'].split('|')])}",
                                                        axis=1)
    temp_df_searched = temp_df_searched.assign(target=temp_df_searched[col].str.split('|')).explode('target')
    temp_df_searched = temp_df_searched.assign(edge=edge_names_multi[col], title=None)
    final_cl_kg_searched_final = pd.concat(
        [final_cl_kg_searched_final, temp_df_searched[['source', 'target', 'edge', 'title']]]).reset_index(drop=True)


def process_study_designs_searched(row):
    designs = row['Study Designs'].split('|')
    phase_nct_drugs = f"{row['Phases']}_{row['NCT Number']}_{'_'.join([re.sub(r'^[a-zA-Z ]+: ', '', i).strip() for i in row['Interventions'].split('|')])}"
    return pd.DataFrame([{'source': phase_nct_drugs, 'target': design.split(': ')[1],
                          'edge': design.split(': ')[0].lower(), 'title': None} for design in designs if
                         ': ' in design])


study_designs_searched_df = pd.concat(df.apply(process_study_designs_searched, axis=1).tolist()).reset_index(drop=True)
final_cl_kg_searched_final = pd.concat([final_cl_kg_searched_final, study_designs_searched_df]).reset_index(drop=True)

final_cl_kg_searched_final['target'] = final_cl_kg_searched_final['target'].astype(
    str)  # Convert 'target' column to string
final_cl_kg_searched_final.to_parquet("../data/Structured data/clinical_trials_searched_kg_df.parquet",
                                      engine="fastparquet", index=False)
