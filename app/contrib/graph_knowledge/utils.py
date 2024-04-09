import math
import json
import re

from uuid import uuid4
from typing import List

import pandas as pd
import networkx as nx
import plotly
import plotly.graph_objs as go

from app.contrib.graph_knowledge import DatasetChoices, DrugFilterChoices
# from app.db.session import gk_engine

from .data_preprocessing.search_funtions import search_drug_gk, search_clinical_data

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


def get_knowledge_graph(search: str):
    # knowledge_graph = pd.read_parquet(
    #     f"{data_path}/Structured data/knowledge_graph.parquet",
    #     engine="fastparquet"
    # )
    # all_drugs_df = pd.read_parquet(
    #     f"{data_path}/Structured data/final_merged_drugs.parquet",
    #     engine="fastparquet"
    # )
    # knowledge_graph = search_drug_gk_optimized(search, all_drugs_df, knowledge_graph)
    # filters = [i.label for i in api_filters]

    # return knowledge_graph
    return {}


def parquet_to_sql(engine, table_name: str, parquet_file: str, index: bool=False):
    df = pd.read_parquet(parquet_file, engine="fastparquet")

    result = df.to_sql(table_name, con=engine, index=index, if_exists='replace', chunksize=1000)
    return result
