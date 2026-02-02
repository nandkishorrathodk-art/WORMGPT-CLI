import networkx as nx
from typing import Any, Dict, List, Optional

class KnowledgeGraph:
    """Manages a knowledge graph of mission data, entities, and their relationships."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node_id: str, node_type: str, attributes: Dict[str, Any] = None):
        """Adds a node to the graph."""
        if attributes is None:
            attributes = {}
        self.graph.add_node(node_id, node_type=node_type, **attributes)

    def add_edge(self, source_id: str, target_id: str, relationship: str, attributes: Dict[str, Any] = None):
        """Adds a directed edge between two nodes."""
        if attributes is None:
            attributes = {}
        self.graph.add_edge(source_id, target_id, relationship=relationship, **attributes)

    def get_neighbors(self, node_id: str) -> List[str]:
        """Gets the neighbors of a given node."""
        if node_id not in self.graph:
            return []
        return list(self.graph.neighbors(node_id))

    def get_node_attributes(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Gets the attributes of a given node."""
        if node_id in self.graph:
            return self.graph.nodes[node_id]
        return None

    def get_edge_attributes(self, source_id: str, target_id: str) -> Optional[Dict[str, Any]]:
        """Gets the attributes of an edge between two nodes."""
        if self.graph.has_edge(source_id, target_id):
            return self.graph.edges[source_id, target_id]
        return None

    def save_graph(self, file_path: str):
        """Saves the graph to a file (e.g., in GraphML format)."""
        nx.write_graphml(self.graph, file_path)

    def load_graph(self, file_path: str):
        """Loads a graph from a file."""
        self.graph = nx.read_graphml(file_path)

    def to_json(self) -> Dict[str, Any]:
        """Converts the graph to a JSON-serializable format."""
        return nx.node_link_data(self.graph)
