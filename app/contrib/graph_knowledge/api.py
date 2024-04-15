
import json
import pandas as pd
import networkx as nx
import plotly
import plotly.graph_objs as go
from sqlalchemy import text
from fastapi import APIRouter, Depends

from app.routers.dependency import get_active_user, get_gk_engine
from app.contrib.account.models import User
from .schema import GraphKnowledgeMedicineBase, GraphKnowledgeClinicalTrialsBase
from .utils import (
    add_directed_edges, add_edge_labels, add_line_breaks_to_long_text,
    relationship_colors, relationship_display_names, is_nct_number
)

api = APIRouter()

medicine_sql_text = text("""
        WITH search_columns AS (
        SELECT 'name' AS column_name
        UNION ALL
        SELECT 'pubmed-id' AS column_name
        UNION ALL
        SELECT 'Gene Name' AS column_name
        UNION ALL
        SELECT 'GenBank Protein ID' AS column_name
        UNION ALL
        SELECT 'GenBank Gene ID' AS column_name
        UNION ALL
        SELECT 'UniProt ID' AS column_name
),
filtered_drugs AS (
    SELECT
        name,
        "pubmed-id",
        "Gene Name",
        "GenBank Protein ID",
        "GenBank Gene ID",
        "UniProt ID"
    FROM
        final_merged_drugs
    JOIN
        search_columns sc
    ON
        sc.column_name IN ('name', 'pubmed-id', 'Gene Name', 'GenBank Protein ID', 'GenBank Gene ID', 'UniProt ID')
    WHERE
        (sc.column_name = 'pubmed-id' AND :query ~ '^[0-9]+$' AND "pubmed-id" = :query)
        OR
        (sc.column_name != 'pubmed-id' AND (name LIKE CONCAT('%', :query, '%') OR "Gene Name" LIKE CONCAT('%', :query, '%')))
)
SELECT DISTINCT
    kg.*
FROM
    knowledge_graph kg
JOIN
    filtered_drugs fd
ON
    kg.source = fd.name OR kg.target = fd.name;

    """)


@api.post('/generate/medicine/', name="gk-generate-medicine", response_model=dict)
async def generate_graph_knowledge(
        obj_in: GraphKnowledgeMedicineBase,
        user: User = Depends(get_active_user),
        gk_engine=Depends(get_gk_engine)
):
    # knowledge_graph = pd.read_sql_table('knowledge_graph', gk_engine)
    # all_drugs_df = pd.read_sql_table("final_merged_drugs", gk_engine)
    # knowledge_graph = search_drug_kg(search_term, all_drugs_df, knowledge_graph)
    if obj_in.filters:
        filters = [filter.label in filter in obj_in.filters]
    else:
        filters = tuple()
    knowledge_graph = pd.read_sql_query(medicine_sql_text, gk_engine, params={
        "query": obj_in.search, "edge_filters": tuple(filters)
    })

    if len(knowledge_graph) < 100:
        single_entry_edges = [
            edge for edge in filters if
            len(knowledge_graph[knowledge_graph['edge'] == edge]) <= 5
        ]
        multiple_entry_edges = [
            edge for edge in filters if
            len(knowledge_graph[knowledge_graph['edge'] == edge]) > 5
        ]
        filtered_dfs = {
            edge: knowledge_graph[knowledge_graph['edge'] == edge] for edge in multiple_entry_edges
        }

        if filtered_dfs:
            min_count = min(len(df) for df in filtered_dfs.values())

            if min_count > 150:
                min_count = 150
            # Sample rows from each multiple-entry edge group

            samples = [
                edge_df.sample(min(min_count, len(edge_df)), random_state=1) for edge_df in
                filtered_dfs.values()
            ]
        else:
            samples = []

        for edge in single_entry_edges:
            samples.append(knowledge_graph[knowledge_graph['edge'] == edge])

            # Combine the samples into a single DataFrame
        final_sample = pd.concat(samples)
        knowledge_graph = final_sample.sample(frac=1).reset_index(drop=True)
    graph = nx.from_pandas_edgelist(knowledge_graph, 'source', 'target', edge_attr=True, create_using=nx.DiGraph())
    layout = nx.spring_layout(graph, k=0.20, iterations=50, seed=42)
    # Create a Plotly figure
    fig = go.Figure()

    add_edge_labels(graph, layout, fig)

    # Add edges with arrowheads
    add_directed_edges(graph, layout, fig)

    node_hover_descriptions = {}

    # Populate hover text for source nodes
    for source, description in zip(knowledge_graph['source'], knowledge_graph['description']):
        node_hover_descriptions[source] = add_line_breaks_to_long_text(description) if pd.notna(description) else ''

    # Populate hover text for target nodes with edge "Targets gene"
    if 'Targets gene' in filters:
        gene_target_edges = knowledge_graph[knowledge_graph['edge'] == 'Targets gene']
        for target, full_gene_name in zip(gene_target_edges['target'], gene_target_edges['Full Gene Name']):
            node_hover_descriptions[target] = f"Full Gene Name:- {full_gene_name}" if pd.notna(
                full_gene_name) else ''

    node_relationships = {}
    for edge in graph.edges(data=True):
        source, target, data = edge
        relationship = data['edge']
        node_relationships[target] = relationship

    # Iterate over the nodes to create node traces
    for node in graph.nodes():
        x, y = layout[node]
        relationship = node_relationships.get(node, None)
        node_color = relationship_colors.get(relationship, '#FF5733')  # Default color if not found

        node_trace = go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            text=[str(node)],
            hoverinfo='text',
            hovertext=[node_hover_descriptions.get(node, '')],
            marker=dict(color=node_color, size=20, opacity=0.8, line=dict(width=0.7, color="black")),
            showlegend=False  # Hide these traces from the legend
        )
        fig.add_trace(node_trace)

    # Update layout and show figure
    fig.update_layout(
        title='<br>Interactive Knowledge Graph For Drugs Dataset',
        font_size=16,
        showlegend=False,
        font_family="Courier New",
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        width=3000,  # Adjust the width here
        height=900  # Adjust the height here
    )

    # Define your default node color and its display name
    default_node_color = '#FF5733'  # Replace with your default color
    default_node_display_name = 'Drugs'  # Replace with your preferred display name

    # Add a trace for the default color in the legend
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color=default_node_color),
        name=default_node_display_name,  # Use the display name for default color
        showlegend=True
    ))

    # Add a trace for each relationship color in the legend
    filtered_relationships = set(knowledge_graph['edge'])
    for relationship, color in relationship_colors.items():
        display_name = relationship_display_names.get(relationship, relationship)  # Get display name
        if relationship in filtered_relationships:
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=10, color=color),
                name=display_name,  # Use the display name in the legend
                showlegend=True
            ))

    # Update layout for the legend
    fig.update_layout(
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    # graph_analysis(graph, uuid4(), obj_in.search, filters, graph_type=DatasetChoices.DRUG)
    # Convert the Plotly graph to JSON
    graph_json_string = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    result = json.loads(graph_json_string)
    return result


@api.post('/generate/clinical-trials/', name="gk-generate-clinical-trials", response_model=dict)
async def generate_clinical_trials(
        obj_in: GraphKnowledgeClinicalTrialsBase,
        user: User = Depends(get_active_user),
        gk_engine=Depends(get_gk_engine),
):
    # clinical_trials_kg_df = pd.read_sql_table('clinical_trials', gk_engine)
    # searched_clinical_trials_kg_df = pd.read_sql_table('clinical_trials_searched', gk_engine)

    filters = [i.label for i in obj_in.filters]
    all_filters = filters + [
        'in phase', 'tested behavioral', 'tested biological', 'tested combination product',
        'tested device', 'tested diagnostic test', 'tested dietary supplement', 'tested drug',
        'tested genetic', 'tested other', 'tested procedure', 'tested radiation',
        'tested unknown', 'tested with'
    ]
    # clinical_trials_kg_df = search_clinical_data(
    #     obj_in.search, searched_clinical_trials_kg_df, clinical_trials_kg_df,
    #     all_filters
    # )
    query = obj_in.search
    if query.startswith("NCT"):
        sql_query = text("""
            with matched_indices as (
                    SELECT index
                    FROM clinical_trials_searched
                    WHERE source LIKE CONCAT('%', :query, '%')
            ),
            search_results AS (
                SELECT *
                FROM clinical_trials
                WHERE index IN (SELECT index FROM matched_indices)
            )
            SELECT *
            FROM search_results
            WHERE edge IN :edge_filters;
            """)
    else:
        sql_query = text("""
            WITH similar_drugs AS (
                SELECT DISTINCT target
                FROM clinical_trials_searched
                WHERE target IS NOT NULL
                  AND SIMILARITY(LOWER(target), LOWER(:query)) >= 0.9
            ),
            matched_nct_numbers AS (
                SELECT DISTINCT source
                FROM clinical_trials_searched
                WHERE target IN (SELECT target FROM similar_drugs)
            ),
            matched_indices_1 AS (
                SELECT index
                FROM clinical_trials_searched
                WHERE source LIKE CONCAT('%', :query, '%')
            ),
            matched_indices AS (
                SELECT index FROM matched_indices_1
                UNION
                SELECT index
                FROM clinical_trials_searched
                WHERE source IN (SELECT source FROM matched_nct_numbers)
            ),
            search_results AS (
                SELECT *
                FROM clinical_trials
                WHERE index IN (SELECT index FROM matched_indices)
            )
            SELECT *
            FROM search_results
            WHERE edge IN :edge_filters;
        """)
    clinical_trials_kg_df = pd.read_sql_query(sql_query, gk_engine,
                                              params={'query': query, "edge_filters": tuple(all_filters)})

    if len(clinical_trials_kg_df) < 100:
        single_entry_edges = []
        multiple_entry_edges = []
        filtered_dfs = {}
        for edge in all_filters:
            if len(clinical_trials_kg_df[clinical_trials_kg_df['edge'] == edge]) <= 5:
                single_entry_edges.append(edge)
            else:
                multiple_entry_edges.append(edge)
                filtered_dfs[edge] = clinical_trials_kg_df[clinical_trials_kg_df['edge'] == edge]
        if filtered_dfs:
            min_count = min(len(df) for df in filtered_dfs.values())
            if min_count > 150:
                min_count = 150

            # Sample rows from each multiple-entry edge group
            samples = [edge_df.sample(min(min_count, len(edge_df)), random_state=1) for edge_df in
                       filtered_dfs.values()]

        else:
            min_count = 0
            samples = []

        for edge in single_entry_edges:
            samples.append(clinical_trials_kg_df[clinical_trials_kg_df['edge'] == edge])

            # Combine the samples into a single DataFrame
        final_sample = pd.concat(samples)
        clinical_trials_kg_df = final_sample.sample(frac=1).reset_index(drop=True)

    # print(set(clinical_trials_kg_df.edge.values))
    graph = nx.from_pandas_edgelist(
        clinical_trials_kg_df, 'source', 'target', edge_attr=True,
        create_using=nx.DiGraph()
    )
    layout = nx.spring_layout(graph, k=0.50, iterations=100, seed=42)

    fig = go.Figure()

    add_edge_labels(graph, layout, fig)

    # Add edges with arrowheads
    add_directed_edges(graph, layout, fig)

    node_hover_titles = {}

    # Populate hover text for source nodes

    for source, title in zip(clinical_trials_kg_df['source'], clinical_trials_kg_df['title']):
        if is_nct_number(source) and pd.notna(title):
            node_hover_titles[source] = add_line_breaks_to_long_text(title)
        else:
            node_hover_titles[source] = ''

    node_relationships = {}
    for edge in graph.edges(data=True):
        source, target, data = edge
        relationship = data['edge']
        node_relationships[target] = relationship

    # Iterate over the nodes to create node traces
    for node in graph.nodes():
        x, y = layout[node]
        relationship = node_relationships.get(node, None)
        node_color = relationship_colors.get(relationship, '#FF5733')  # Default color if not found

        node_trace = go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            text=[str(node)],
            hoverinfo='text',
            hovertext=[node_hover_titles.get(node, '')],
            marker=dict(color=node_color, size=20, opacity=0.8, line=dict(width=0.7, color="black")),
            showlegend=False  # Hide these traces from the legend
        )
        fig.add_trace(node_trace)

    # Update layout and show figure
    fig.update_layout(
        title='<br>Interactive Knowledge Graph For Clinical trials Dataset',
        font_size=16,
        font_family="Courier New",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        width=3000,  # Adjust the width here
        height=900  # Adjust the height here
    )

    # Define your default node color and its display name
    default_node_color = '#FF5733'  # Replace with your default color
    default_node_display_name = 'NCT number'  # Replace with your preferred display name

    # Add a trace for the default color in the legend
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color=default_node_color),
        name=default_node_display_name,  # Use the display name for default color
        showlegend=True
    ))

    # Add a trace for each relationship color in the legend
    added_colors = set()

    # Add a trace for each relationship color in the legend
    filtered_relationships = set(clinical_trials_kg_df['edge'])
    for relationship, color in relationship_colors.items():
        display_name = relationship_display_names.get(relationship, relationship)  # Get display name
        if relationship in filtered_relationships and color not in added_colors:
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=10, color=color),
                name=display_name,  # Use the display name in the legend
                showlegend=True
            ))
            added_colors.add(color)  # Mark this color as added

    # Update layout for the legend
    fig.update_layout(
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    # graph_analysis(
    #     graph, uuid4(), obj_in.search, obj_in.filters,
    #     graph_type=DatasetChoices.CLINICAL_TRIALS
    # )
    graph_json_string = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    result = json.loads(graph_json_string)
    return result
    # result = {}
    # with open("response_1712344366538.json", "r") as f:
    #     data = f.read()
    #     result = json.loads(data)
    # return result
