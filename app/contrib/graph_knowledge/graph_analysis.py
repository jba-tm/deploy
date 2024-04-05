from typing import List
from uuid import UUID
import networkx as nx
from app.contrib.graph_knowledge import DatasetChoices


def graph_analysis(graph, graph_id: UUID, search_term: str, filters: List[str], graph_type: DatasetChoices):
    # Basic Properties
    num_nodes = graph.number_of_nodes()
    num_edges = graph.number_of_edges()
    avg_degree = sum(dict(graph.degree()).values()) / num_nodes
    density = nx.density(graph)

    # Centrality Measures
    degree_centrality = nx.degree_centrality(graph)
    between_ness_centrality = nx.betweenness_centrality(graph)
    closeness_centrality = nx.closeness_centrality(graph)

    # Define the file name based on the graph ID
    output_file = f"graph_analysis_logs/graph_{graph_id}_analysis.txt"

    # Save the information to the output file
    with open(output_file, 'w') as file:

        file.write(f"Graph ID: {graph_id}\n\n")
        file.write(f"Graph Type: {graph_type.label}\n")
        file.write(f"Graph main node is: {search_term}\n")
        file.write(f"Implemented filters: {filters}\n")
        file.write(f"Number of Nodes: {num_nodes}\n")
        file.write(f"Number of Edges: {num_edges}\n")
        file.write(f"Average Degree: {avg_degree}\n")
        file.write(f"Density: {density}\n\n")

        file.write("Centrality Measures:\n")
        for node, centrality in degree_centrality.items():
            file.write(f"Node {node}: Degree Centrality = {centrality}\n")

        for node, centrality in between_ness_centrality.items():
            file.write(f"Node {node}: Between Centrality = {centrality}\n")

        for node, centrality in closeness_centrality.items():
            file.write(f"Node {node}: Closeness Centrality = {centrality}\n")

    print(f"Graph analysis results for ID {graph_id} saved to {output_file}")
