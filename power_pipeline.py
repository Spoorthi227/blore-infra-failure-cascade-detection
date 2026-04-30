import xml.etree.ElementTree as ET
import json
import pandas as pd
import os
from shapely.geometry import shape, Point
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class PowerNetworkPipeline:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.node_id_counter = 0
        self.coord_to_node = {}

    def get_or_create_node(self, lat, lon, category="intermediate", metadata=None):
        # Use 7 decimal places for coordinate mapping (~1cm precision)
        key = (round(float(lat), 7), round(float(lon), 7))
        if key in self.coord_to_node:
            return self.coord_to_node[key]
        
        node_id = f"node_{self.node_id_counter:04d}"
        self.node_id_counter += 1
        self.nodes.append({
            'node_id': node_id,
            'latitude': lat,
            'longitude': lon,
            'category': category,
            'metadata': json.dumps(metadata or {}, ensure_ascii=False)
        })
        self.coord_to_node[key] = node_id
        return node_id

    def process_osm(self, osm_path):
        """Extracts major infrastructure from OSM XML."""
        if not os.path.exists(osm_path):
            print(f"OSM file not found: {osm_path}")
            return

        print(f"Processing OSM: {osm_path}")
        tree = ET.parse(osm_path)
        root = tree.getroot()
        
        # Mapping OSM node IDs to their coordinates for reference in ways
        osm_nodes_coords = {}
        for node in root.findall('node'):
            node_id = node.get('id')
            lat, lon = float(node.get('lat')), float(node.get('lon'))
            osm_nodes_coords[node_id] = (lat, lon)
            
            tags = {tag.get('k'): tag.get('v') for tag in node.findall('tag')}
            if 'power' in tags:
                self.get_or_create_node(lat, lon, category=tags['power'], metadata=tags)

        # Process ways (substations, boundaries)
        for way in root.findall('way'):
            tags = {tag.get('k'): tag.get('v') for tag in way.findall('tag')}
            if 'power' in tags:
                # Get coordinates for all nodes in the way
                way_coords = []
                for nd in way.findall('nd'):
                    ref = nd.get('ref')
                    if ref in osm_nodes_coords:
                        way_coords.append(osm_nodes_coords[ref])
                
                if not way_coords: continue
                
                # If it's a closed loop (polygon), calculate centroid
                if way_coords[0] == way_coords[-1] and len(way_coords) > 2:
                    # Simple centroid calculation for the polygon
                    avg_lat = sum(p[0] for p in way_coords[:-1]) / (len(way_coords) - 1)
                    avg_lon = sum(p[1] for p in way_coords[:-1]) / (len(way_coords) - 1)
                    self.get_or_create_node(avg_lat, avg_lon, category=f"{tags['power']}_centroid", metadata=tags)
                else:
                    # For line-based ways in OSM (if any)
                    prev_node = None
                    for lat, lon in way_coords:
                        curr_node = self.get_or_create_node(lat, lon, category="intermediate_path_node", metadata=tags)
                        if prev_node:
                            self.add_edge(prev_node, curr_node, tags)
                        prev_node = curr_node

    def process_geojson(self, geojson_path):
        """Processes transmission geometry from GeoJSON/JSON."""
        if not os.path.exists(geojson_path):
            print(f"GeoJSON file not found: {geojson_path}")
            return

        print(f"Processing GeoJSON: {geojson_path}")
        with open(geojson_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        features = data.get('features', [])
        for feature in features:
            geom = feature.get('geometry')
            props = feature.get('properties', {})
            if not geom: continue
            
            g_type = geom['type']
            coords = geom['coordinates']
            
            if g_type == 'Point':
                self.get_or_create_node(coords[1], coords[0], category=props.get('type', 'point_facility'), metadata=props)
            
            elif g_type == 'MultiPoint':
                for pt in coords:
                    self.get_or_create_node(pt[1], pt[0], category=props.get('type', 'point_facility'), metadata=props)
            
            elif g_type == 'LineString':
                self.process_line(coords, props)
            
            elif g_type == 'MultiLineString':
                for line in coords:
                    self.process_line(line, props)
            
            elif g_type in ['Polygon', 'MultiPolygon']:
                # Use shapely to find representative point or centroid
                s = shape(geom)
                centroid = s.centroid
                self.get_or_create_node(centroid.y, centroid.x, category=props.get('power', 'facility_boundary'), metadata=props)

    def process_line(self, coords, props):
        prev_node = None
        for pt in coords:
            # coords are [lon, lat]
            curr_node = self.get_or_create_node(pt[1], pt[0], category="intermediate_path_node", metadata=props)
            if prev_node:
                self.add_edge(prev_node, curr_node, props)
            prev_node = curr_node

    def add_edge(self, source, target, props):
        # Find coordinates to calculate length
        s_data = next(n for n in self.nodes if n['node_id'] == source)
        t_data = next(n for n in self.nodes if n['node_id'] == target)
        length = haversine(s_data['latitude'], s_data['longitude'], t_data['latitude'], t_data['longitude'])
        
        self.edges.append({
            'edge_id': f"edge_{len(self.edges):05d}",
            'source_node': source,
            'target_node': target,
            'infrastructure_type': props.get('power', 'line'),
            'voltage': props.get('voltage', 'unknown'),
            'geometry_parent_id': props.get('id', props.get('osm_id', 'unknown')),
            'segment_length': round(length, 2)
        })

    def process_xlsx(self, xlsx_path):
        """Processes supplementary infrastructure data from Excel."""
        if not os.path.exists(xlsx_path): return
        print(f"Processing XLSX: {xlsx_path}")
        df = pd.read_excel(xlsx_path)
        for _, row in df.iterrows():
            metadata = row.to_dict()
            lat, lon = row['latitude'], row['longitude']
            self.get_or_create_node(lat, lon, category=row.get('power', 'substation'), metadata=metadata)

    def export(self, nodes_csv, edges_csv):
        pd.DataFrame(self.nodes).to_csv(nodes_csv, index=False)
        pd.DataFrame(self.edges).to_csv(edges_csv, index=False)
        print(f"Exported {len(self.nodes)} nodes and {len(self.edges)} edges.")

if __name__ == "__main__":
    pipeline = PowerNetworkPipeline()
    
    # Files present in the workspace
    osm_file = 'd:/urban_el/export_power.osm'
    xlsx_file = 'd:/urban_el/power_with_location.xlsx'
    # Updated GeoJSON file path
    geojson_file = 'd:/urban_el/power_network_geojson.json' 
    
    pipeline.process_osm(osm_file)
    pipeline.process_xlsx(xlsx_file)
    pipeline.process_geojson(geojson_file)
    
    pipeline.export('d:/urban_el/nodes.csv', 'd:/urban_el/edges.csv')
