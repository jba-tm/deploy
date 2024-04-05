import math
import json
import re

from uuid import uuid4

import pandas as pd
import networkx as nx
import plotly
import plotly.graph_objs as go

from fastapi import APIRouter, Depends

from app.routers.dependency import get_active_user
from app.contrib.account.models import User
from app.contrib.graph_knowledge import DatasetChoices

from .schema import GraphKnowledgeMedicineBase, GraphKnowledgeClinicalTrialsBase
from .data_preprocessing.search_funtions import search_drug_gk, search_clinical_data
from .graph_analysis import graph_analysis

api = APIRouter()

data_path = "app/contrib/graph_knowledge/data"


def is_nct_number(source):
    """ Check if the source is an NCT number. """
    return bool(re.match(r'^NCT\d+$', source))


def add_line_breaks_to_long_text(long_text, max_segment_length=40):
    if pd.isna(long_text):
        return ""

    if len(long_text) <= max_segment_length:
        return long_text

    words = long_text.split()
    broken_description = ""
    current_length = 0

    for word in words:
        if current_length + len(word) > max_segment_length and current_length > 0:
            broken_description += '<br>'  # Add a line break
            current_length = 0
        broken_description += word + ' '
        current_length += len(word) + 1  # Plus one for the space

    return broken_description.strip()


def add_directed_edges(graph, layout, fig, edge_color='#888', arrow_size=0.007):
    for i, edge in enumerate(graph.edges(data=True)):
        x0, y0 = layout[edge[0]]  # Source node position
        x1, y1 = layout[edge[1]]  # Target node position
        edge_name = edge[2]['edge']
        # Line segment for edge
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode='lines',
            opacity=0.8,
            line=dict(width=0.7, color=edge_color),
            hoverinfo='none',
            showlegend=False,
            customdata=[{"source": edge[0], "target": edge[1], "edge": f"{edge_name}_{i}"}]  # Include edge information
        ))

        # Calculate arrowhead direction and position
        dx = x1 - x0
        dy = y1 - y0
        d = math.sqrt(dx ** 2 + dy ** 2)

        # Normalize to control the size of the arrowhead
        dx /= d
        dy /= d

        # Adjusting the size and angle to make the arrowhead sharper
        angle = math.pi / 6  # 30 degrees for a sharper arrowhead
        arrow_size_adjusted = arrow_size / math.sin(angle)

        # Arrowhead points (triangle)
        arrow_x = [x1, x1 - arrow_size_adjusted * (dx * math.cos(angle) + dy * math.sin(angle)),
                   x1 - arrow_size_adjusted * (dx * math.cos(angle) - dy * math.sin(angle)), x1]
        arrow_y = [y1, y1 - arrow_size_adjusted * (dy * math.cos(angle) - dx * math.sin(angle)),
                   y1 - arrow_size_adjusted * (dy * math.cos(angle) + dx * math.sin(angle)), y1]

        fig.add_trace(go.Scatter(
            x=arrow_x, y=arrow_y,
            mode='lines',
            line=dict(width=0.7, color=edge_color),
            fill='toself',
            showlegend=False,
            hoverinfo='none'
        ))


def add_edge_labels(graph, layout, fig, text_font_size=10, text_font_color='black'):
    for edge in graph.edges(data=True):
        x0, y0 = layout[edge[0]]
        x1, y1 = layout[edge[1]]
        midpoint_x = (x0 + x1) / 2
        midpoint_y = (y0 + y1) / 2
        edge_name = edge[2]['edge']  # Assuming the edge name is stored in the 'edge' attribute

        fig.add_trace(go.Scatter(
            x=[midpoint_x], y=[midpoint_y],
            text=edge_name,
            mode='text',
            opacity=0.8,
            textposition='bottom center',
            hoverinfo='none',
            showlegend=False,
            textfont=dict(size=text_font_size, color=text_font_color)
        ))


relationship_colors = {
    'has synonym': '#07F410',
    'used for': '#0971BC',
    'has side effect': '#A129FE',
    'Kingdom': '#F10FD6',
    'Subclass': '#F12A0F',
    'Superclass': '#DAF7A6',
    'marketed name': '#29F0FE',
    'manufacturer': '#307368',
    'country': '#D4FF05',
    'Targets gene': '#5C70FC',
    'Effective in species': '#0AF6AC',
    'allocation': '#07F410',
    'funded by': '#0971BC',
    'intervention model': '#A129FE',
    'number of volunteers': '#F10FD6',
    'primary purpose': '#DAF7A6',
    'ages of volunteers': '#29F0FE',
    'gender of volunteers': '#307368',
    'trial completion date': '#D4FF05',
    'trial start date': '#5C70FC',
    'trial status': '#0AF6AC',
    'masking': '#00FFEE',
    'collaborates with': '#FF0078',
    'tested condition': '#F8FF00',
    'in phase': '#9D9E7A',
    'tested behavioral': '#0076FF',
    'tested biological': '#0076FF',
    'tested combination product': '#0076FF',
    'tested device': '#0076FF',
    'tested diagnostic test': '#0076FF',
    'tested dietary supplement': '#0076FF',
    'tested drug': '#0076FF',
    'tested genetic': '#0076FF',
    'tested other': '#0076FF',
    'tested procedure': '#0076FF',
    'tested radiation': '#0076FF',
    'tested unknown': '#0076FF',
    'tested with': '#0076FF'

    # Add more relationships and their corresponding colors here
}

relationship_display_names = {
    'used for': 'Disease/Case',
    'has synonym': 'Synonym',
    'has side effect': 'Side Effect',
    'Kingdom': 'belong to kingdom',
    'Subclass': 'Subclass of',
    'Superclass': 'Superclass of',
    'marketed name': 'Marketed name',
    'manufacturer': 'Manufacturer',
    'country': 'Manufacturer country',
    'Targets gene': 'Gene Name',
    'Effective in species': 'Specie Type',
    'allocation': 'Allocation Type',
    'funded by': 'Sponsor',
    'intervention model': 'Intervention Model',
    'number of volunteers': 'Number of volunteers',
    'primary purpose': 'Primary Purpose',
    'ages of volunteers': 'Age of volunteers',
    'gender of volunteers': 'Gender of volunteers',
    'trial completion date': 'Completion data',
    'trial start date': 'Start date',
    'trial status': 'trial status',
    'masking': 'Masking type',
    'collaborates with': 'Collaborator',
    'tested condition': 'Condition',
    'in phase': 'Phase number',
    'tested behavioral': 'Tested sample',
    'tested biological': 'Tested sample',
    'tested combination product': 'Tested sample',
    'tested device': 'Tested sample',
    'tested diagnostic test': 'Tested sample',
    'tested dietary supplement': 'Tested sample',
    'tested drug': 'Tested sample',
    'tested genetic': 'Tested sample',
    'tested other': 'Tested sample',
    'tested procedure': 'Tested sample',
    'tested radiation': 'Tested sample',
    'tested unknown': 'Tested sample',
    'tested with': 'Tested sample'
}


@api.post('/generate/medicine/', name="gk-generate-medicine", response_model=dict)
async def generate_graph_knowledge(
        obj_in: GraphKnowledgeMedicineBase,
        user: User = Depends(get_active_user),
):
    knowledge_graph = pd.read_parquet(
        f"{data_path}/Structured data/knowledge_graph.parquet", engine="fastparquet"
    )
    all_drugs_df = pd.read_parquet(
        f"{data_path}/Structured data/final_merged_drugs.parquet", engine="fastparquet"
    )
    knowledge_graph = search_drug_gk(obj_in.search, all_drugs_df, knowledge_graph)
    filters = [i.label for i in obj_in.filters]
    if obj_in.filters:
        knowledge_graph = knowledge_graph[knowledge_graph['edge'].isin(filters)]

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
    graph_analysis(graph, uuid4(), obj_in.search, filters, graph_type=DatasetChoices.DRUG)
    # Convert the Plotly graph to JSON
    graph_json_string = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    result = json.loads(graph_json_string)
    return result


@api.post('/generate/clinical-trials/', name="gk-generate-clinical-trials", response_model=dict)
async def generate_clinical_trials(
        obj_in: GraphKnowledgeClinicalTrialsBase,
        user: User = Depends(get_active_user),
):
    clinical_trials_kg_df = pd.read_parquet(
        f"{data_path}/Structured data/clinical_trials_kg_df.parquet",
        engine="fastparquet"
    )

    searched_clinical_trials_kg_df = pd.read_parquet(
        f"{data_path}/Structured data/clinical_trials_searched_kg_df.parquet",
        engine="fastparquet"
    )
    filters = [i.label for i in obj_in.filters]
    all_filters = filters + [
        'in phase', 'tested behavioral', 'tested biological', 'tested combination product',
        'tested device', 'tested diagnostic test', 'tested dietary supplement', 'tested drug',
        'tested genetic', 'tested other', 'tested procedure', 'tested radiation',
        'tested unknown', 'tested with'
    ]

    clinical_trials_kg_df = search_clinical_data(
        obj_in.search, searched_clinical_trials_kg_df, clinical_trials_kg_df,
        all_filters
    )

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

    graph_analysis(
        graph, uuid4(), obj_in.search, obj_in.filters,
        graph_type=DatasetChoices.CLINICAL_TRIALS
    )
    graph_json_string = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    result = json.loads(graph_json_string)
    return result
