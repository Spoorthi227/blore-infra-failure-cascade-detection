# Walkthrough: Power Network Graph Pipeline

## Changes Made
- **Environment Setup**: Installed `networkx`, `shapely`, `pandas`, `openpyxl`, and `lxml`.
- **Pipeline Implementation**: Created `power_pipeline.py` which:
  - Parses `export_power.osm` for substation locations (XML).
  - Processes `power_with_location.xlsx` for supplementary facility data (Excel).
  - Includes a GeoJSON/JSON processor designed to preserve every coordinate along transmission lines as routing nodes and edges.
  - Implements centroid calculation for polygon-based facilities.
  - Computes edge lengths using the Haversine formula.

## Validation Results
- **OSM Processing**: Extracted substation centroids and classified nodes.
- **Excel Processing**: Successfully merged supplementary location data.
- **GeoJSON Processing**: Processed `power_network_geojson.json`, preserving all transmission path coordinates.
- **Output Files**: Generated final `nodes.csv` (**4231 nodes**) and `edges.csv` (**4032 edges**).

## Visualizing Output Structure
The generated `nodes.csv` includes category and metadata, while `edges.csv` includes voltage and segment lengths, ready for NetworkX graph construction.

```python
# Example of how to load the data into NetworkX
import networkx as nx
import pandas as pd

nodes_df = pd.read_csv('nodes.csv')
edges_df = pd.read_csv('edges.csv')

G = nx.Graph()
for _, node in nodes_df.iterrows():
    G.add_node(node['node_id'], lat=node['latitude'], lon=node['longitude'], cat=node['category'])

for _, edge in edges_df.iterrows():
    G.add_edge(edge['source_node'], edge['target_node'], length=edge['segment_length'])
```
