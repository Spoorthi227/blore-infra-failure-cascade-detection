"""
FIXED power.py
=========================================
POWER CSV DATAFRAME → GRAPH CREATION + VISUALIZATION
Supports:
1. CSV input (new_nodes.csv and new_edges.csv)
2. Saves:
   - GraphML
   - Interactive HTML map
   - PNG graph
=========================================
"""

import json
import pandas as pd
from pathlib import Path
import networkx as nx
import folium
import matplotlib.pyplot as plt
import math

class PowerGraphBuilder:
    def __init__(self):
        # BASE_DIR is urban_el
        BASE_DIR = Path(__file__).resolve().parent.parent

        self.output_dir = BASE_DIR / "data" / "graphs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Graph output directory: {self.output_dir}")

    # =====================================
    # DISTANCE CALCULATOR (Haversine)
    # =====================================
    def calculate_distance(self, coord1, coord2):
        """Calculates distance between two (lat, lon) pairs in meters."""
        try:
            lat1, lon1 = coord1
            lat2, lon2 = coord2
            R = 6371000  # Earth radius in meters
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)
            a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c
        except Exception:
            return 0

    # =====================================
    # BUILD GRAPH FROM CSV
    # =====================================
    def build_graph_from_csv(self, nodes_path, edges_path):
        try:
            print(f"Loading nodes from {nodes_path}...")
            nodes_df = pd.read_csv(nodes_path)
            print(f"Loading edges from {edges_path}...")
            edges_df = pd.read_csv(edges_path)

            G = nx.Graph()

            # Add Nodes
            for _, row in nodes_df.iterrows():
                G.add_node(
                    str(row['node_id']),
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    category=str(row.get('category', 'N/A'))
                )

            # Add Edges
            for _, row in edges_df.iterrows():
                u, v = str(row['source_node']), str(row['target_node'])
                
                if u in G and v in G:
                    coord1 = (G.nodes[u]["latitude"], G.nodes[u]["longitude"])
                    coord2 = (G.nodes[v]["latitude"], G.nodes[v]["longitude"])
                    
                    dist = self.calculate_distance(coord1, coord2)
                    
                    G.add_edge(
                        u, v,
                        weight=dist,
                        edge_id=row.get('edge_id', 'N/A'),
                        voltage=str(row.get('voltage', 'N/A')),
                        type=str(row.get('infrastructure_type', 'line'))
                    )

            if G.number_of_nodes() == 0:
                print("No valid power nodes found.")
                return None

            print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
            
            graph_file = self.save_graph(G)
            html_map = self.visualize_interactive_map(G)
            png_graph = self.visualize_static_graph(G)

            return {
                "graph": G,
                "graphml": str(graph_file) if graph_file else None,
                "interactive_map": str(html_map) if html_map else None,
                "static_graph": str(png_graph) if png_graph else None,
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges()
            }

        except Exception as e:
            print(f"Error building power graph: {e}")
            import traceback
            traceback.print_exc()
            return None

    # =====================================
    # SAVE GRAPH
    # =====================================
    def save_graph(self, G):
        try:
            graph_path = self.output_dir / "power_network.graphml"
            nx.write_graphml(G, graph_path)
            print(f"GraphML saved at: {graph_path}")
            return graph_path
        except Exception as e:
            print(f"Error saving graph: {e}")
            return None

    # =====================================
    # INTERACTIVE MAP
    # =====================================
    def visualize_interactive_map(self, G):
        try:
            lats = [data["latitude"] for _, data in G.nodes(data=True)]
            lons = [data["longitude"] for _, data in G.nodes(data=True)]

            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)

            power_map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=12,
                tiles="cartodbpositron"
            )

            # Draw Edges
            for u, v, data in G.edges(data=True):
                point1 = (G.nodes[u]["latitude"], G.nodes[u]["longitude"])
                point2 = (G.nodes[v]["latitude"], G.nodes[v]["longitude"])

                folium.PolyLine(
                    locations=[point1, point2],
                    weight=2,
                    color="orange",
                    opacity=0.8,
                    tooltip=f"ID: {data.get('edge_id')} | {data.get('voltage')}"
                ).add_to(power_map)
                
            # Draw Substations as Markers
            for node, data in G.nodes(data=True):
                if 'substation' in str(data.get('category')).lower():
                    folium.CircleMarker(
                        location=[data["latitude"], data["longitude"]],
                        radius=5,
                        color="red",
                        fill=True,
                        fill_color="red",
                        popup=f"Substation: {node}"
                    ).add_to(power_map)

            map_path = self.output_dir / "power_network_map.html"
            power_map.save(str(map_path))
            print(f"Interactive map saved at: {map_path}")
            return map_path
        except Exception as e:
            print(f"Error visualizing map: {e}")
            return None

    # =====================================
    # STATIC GRAPH
    # =====================================
    def visualize_static_graph(self, G):
        try:
            plt.figure(figsize=(20, 16))
            pos = {
                node: (data["longitude"], data["latitude"])
                for node, data in G.nodes(data=True)
            }

            # Separate nodes by category for better visualization
            substations = [n for n, d in G.nodes(data=True) if 'substation' in str(d.get('category')).lower()]
            others = [n for n in G.nodes() if n not in substations]

            nx.draw_networkx_nodes(G, pos, nodelist=others, node_size=1, node_color='gray', alpha=0.5)
            nx.draw_networkx_nodes(G, pos, nodelist=substations, node_size=20, node_color='red', label='Substations')
            nx.draw_networkx_edges(G, pos, width=0.5, edge_color='orange', alpha=0.6)

            png_path = self.output_dir / "power_network_graph.png"
            plt.title("Power Infrastructure Network Visualization")
            plt.legend()
            plt.axis('off')
            plt.savefig(png_path, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"Static graph saved at: {png_path}")
            return png_path
        except Exception as e:
            print(f"Error visualizing static graph: {e}")
            return None

if __name__ == "__main__":
    builder = PowerGraphBuilder()
    
    # Paths to your latest CSV files
    current_dir = Path(__file__).resolve().parent
    nodes_csv = current_dir / "new_nodes.csv"
    edges_csv = current_dir / "new_edges.csv"
    
    results = builder.build_graph_from_csv(nodes_csv, edges_csv)
    
    if results:
        print("\n" + "="*30)
        print(" POWER GRAPH EXPORT COMPLETE ")
        print("="*30)
        print(f"Nodes: {results['nodes']}")
        print(f"Edges: {results['edges']}")
        print(f"GraphML: {results['graphml']}")
        print(f"HTML Map: {results['interactive_map']}")
        print(f"PNG Graph: {results['static_graph']}")
