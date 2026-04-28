"""
XML Parser Module for Infrastructure Data
Handles parsing of OpenStreetMap XML files for power and water infrastructure
"""

import xml.etree.ElementTree as ET
import pandas as pd
from typing import Dict, List, Tuple, Optional
import json
import os


class XMLParser(object):
    """Parse OSM XML files for power and water infrastructure data"""
    
    def __init__(self):
        self.file_type = None
        self.data = []
    
    def detect_file_type(self, root) -> Optional[str]:
        """
        Detect whether XML file contains power or water infrastructure
        
        Args:
            root: XML root element
            
        Returns:
            str: 'power' or 'water' or None if unknown type
        """
        try:
            # Check ways first (more likely to have detailed info)
            for way in root.findall("way"):
                for tag in way.findall("tag"):
                    k = tag.get("k")
                    if k == "power":
                        return "power"
                    elif k in ["man_made", "landuse"]:
                        return "water"
            
            # Then check nodes
            for node in root.findall("node"):
                for tag in node.findall("tag"):
                    k = tag.get("k")
                    if k == "power":
                        return "power"
                    elif k in ["man_made", "landuse"]:
                        return "water"
            return None
        except Exception as e:
            raise ValueError(f"Error detecting file type: {str(e)}")
    
    def parse_power_infrastructure(self, root) -> List[Dict]:
        """
        Extract power infrastructure from XML (both nodes and ways)
        Only includes COMPLETE entries with all required fields
        Filters to substation/station types only
        
        Args:
            root: XML root element
            
        Returns:
            List[Dict]: List of complete power infrastructure data with required columns
        """
        data = []
        
        # Required fields - all must be present
        REQUIRED = [
            "frequency", "location", "name", "operator",
            "power", "rating", "ref", "start_date",
            "substation", "voltage"
        ]
        
        try:
            # 🔹 Step 1: Store all node coordinates for reference
            node_coords = {}
            for node in root.findall("node"):
                node_id = node.get("id")
                lat = node.get("lat")
                lon = node.get("lon")
                if lat and lon:
                    node_coords[node_id] = (lat, lon)
            
            # 🔹 Step 2: Helper function to extract tags
            def get_tags(element):
                return {tag.get("k"): tag.get("v") for tag in element.findall("tag")}
            
            # 🔹 Step 3: Process nodes and ways
            for element in list(root.findall("node")) + list(root.findall("way")):
                tags = get_tags(element)
                
                # ✅ Only process substation or station types
                if tags.get("power") in ["substation", "station"]:
                    
                    # ✅ Keep ONLY COMPLETE entries (all required fields present)
                    if all(field in tags for field in REQUIRED):
                        
                        lat, lon = "N/A", "N/A"
                        
                        # 📍 If node → direct lat/lon
                        if element.tag == "node":
                            lat = element.get("lat", "N/A")
                            lon = element.get("lon", "N/A")
                        
                        # 📍 If way → get from first node reference
                        elif element.tag == "way":
                            node_refs = [nd.get("ref") for nd in element.findall("nd")]
                            if node_refs and node_refs[0] in node_coords:
                                lat, lon = node_coords[node_refs[0]]
                        
                        # Append row with all required fields
                        row = {
                            "frequency": tags["frequency"],
                            "location": tags["location"],
                            "name": tags["name"],
                            "operator": tags["operator"],
                            "power": tags["power"],
                            "rating": tags["rating"],
                            "reference": tags["ref"],
                            "start_date": tags["start_date"],
                            "substation": tags["substation"],
                            "voltage": tags["voltage"],
                            "latitude": lat,
                            "longitude": lon
                        }
                        data.append(row)
            
            return data
        except Exception as e:
            raise ValueError(f"Error parsing power infrastructure: {str(e)}")
    
    def parse_water_infrastructure(self, root) -> List[Dict]:
        """
        Extract water infrastructure from XML (both nodes and ways)
        Uses name-based type classification and centroid calculation for ways
        
        Args:
            root: XML root element
            
        Returns:
            List[Dict]: List of water infrastructure data with columns:
            type, node_ref, name, operator, landuse, man_made, latitude, longitude
        """
        data = []
        
        try:
            # 🔹 STEP 1: Store all node coordinates for reference
            node_coords = {}
            for node in root.findall("node"):
                node_id = node.get("id")
                lat = node.get("lat")
                lon = node.get("lon")
                
                if node_id and lat and lon:
                    node_coords[node_id] = (float(lat), float(lon))
            
            # 🔹 STEP 2: Helper function to extract tags
            def get_tags(element):
                return {tag.get("k"): tag.get("v") for tag in element.findall("tag")}
            
            # 🔹 STEP 3: Compute centroid for ways
            def get_center(nd_refs):
                lats, lons = [], []
                
                for ref in nd_refs:
                    if ref in node_coords:
                        lat, lon = node_coords[ref]
                        lats.append(lat)
                        lons.append(lon)
                
                if lats and lons:
                    return sum(lats)/len(lats), sum(lons)/len(lons)
                
                return None, None
            
            # 🔹 STEP 4: Extract data
            for element in list(root.findall("node")) + list(root.findall("way")):
                
                tags = get_tags(element)
                
                # Only process water_works
                if tags.get("man_made") == "water_works":
                    
                    name = tags.get("name", "N/A").lower()
                    
                    # 🔥 TYPE CLASSIFICATION based on name keywords
                    if "tank" in name:
                        asset_type = "Water Tank"
                    elif "reservoir" in name:
                        asset_type = "Reservoir"
                    elif "plant" in name or "filter" in name:
                        asset_type = "WTP"
                    else:
                        asset_type = "Water Works"
                    
                    # 🔹 NODE case
                    if element.tag == "node":
                        lat = element.get("lat")
                        lon = element.get("lon")
                        node_refs = element.get("id")
                    
                    # 🔹 WAY case
                    else:
                        refs = [nd.get("ref") for nd in element.findall("nd")]
                        node_refs = ",".join(refs) if refs else None
                        lat, lon = get_center(refs)
                    
                    # 🔹 STORE FINAL STRUCTURED DATA
                    row = {
                        "type": asset_type,
                        "node_ref": node_refs,
                        "name": tags.get("name", "N/A"),
                        "operator": tags.get("operator", "N/A"),
                        "man_made": tags.get("man_made", "N/A"),
                        "landuse": tags.get("landuse", "N/A"),
                        "latitude": float(lat) if lat else None,
                        "longitude": float(lon) if lon else None
                    }
                    data.append(row)
            
            return data
        except Exception as e:
            raise ValueError(f"Error parsing water infrastructure: {str(e)}")
    
    def parse_file(self, file_path: str) -> Tuple[str, List[Dict]]:
        """
        Main method to parse XML file
        
        Args:
            file_path: Path to XML file
            
        Returns:
            Tuple[str, List[Dict]]: (file_type, parsed_data)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If XML parsing fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Detect file type
            file_type = self.detect_file_type(root)
            
            if file_type == "power":
                data = self.parse_power_infrastructure(root)
            elif file_type == "water":
                data = self.parse_water_infrastructure(root)
            else:
                raise ValueError("Unknown file type: Could not detect power or water infrastructure")
            
            self.file_type = file_type
            self.data = data
            
            return file_type, data
            
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing file: {str(e)}")
    
    def export_to_excel(self, file_path: str = None) -> str:
        """
        Export parsed data to Excel file in data/processed directory
        Includes data cleaning: dedup, remove empty coords, reset index
        
        Args:
            file_path: Optional custom output Excel file path. 
                      If not provided, auto-generates based on file type.
        
        Returns:
            str: Path to created Excel file
        """
        if not self.data:
            raise ValueError("No data to export")
        
        try:
            # Create DataFrame with columns in correct order
            df = pd.DataFrame(self.data)
            
            # 🔹 DATA CLEANING STEP 1: Remove duplicates
            if self.file_type == "water":
                # For water: remove duplicates by node_ref and name
                df.drop_duplicates(subset=["node_ref", "name"], inplace=True)
            elif self.file_type == "power":
                # For power: remove duplicates by reference and name
                df.drop_duplicates(subset=["reference", "name"], inplace=True)
            
            # 🔹 DATA CLEANING STEP 2: Remove rows without coordinates
            df.dropna(subset=["latitude", "longitude"], inplace=True)
            
            # 🔹 DATA CLEANING STEP 3: Reset index
            df.reset_index(drop=True, inplace=True)
            
            # Reorder columns based on file type
            if self.file_type == "power":
                column_order = [
                    "frequency", "location", "name", "operator", "power", 
                    "rating", "reference", "start_date", "substation", "voltage", 
                    "latitude", "longitude"
                ]
            elif self.file_type == "water":
                column_order = [
                    "type", "node_ref", "name", "operator", 
                    "man_made", "landuse", "latitude", "longitude"
                ]
            else:
                column_order = df.columns.tolist()
            
            # Select only columns that exist
            existing_columns = [col for col in column_order if col in df.columns]
            df = df[existing_columns]
            
            # If no file path provided, auto-generate based on file type
            if file_path is None:
                processed_dir = os.path.join(
                    os.path.dirname(__file__), 
                    '..', '..', 
                    'data', 'processed'
                )
                # Normalize path to resolve .. references
                processed_dir = os.path.normpath(processed_dir)
                os.makedirs(processed_dir, exist_ok=True)
                
                if self.file_type == "power":
                    file_path = os.path.join(processed_dir, "power_output.xlsx")
                elif self.file_type == "water":
                    file_path = os.path.join(processed_dir, "water_output.xlsx")
                else:
                    file_path = os.path.join(processed_dir, "output.xlsx")
            else:
                # Ensure directory exists for custom path
                output_dir = os.path.dirname(file_path)
                os.makedirs(output_dir, exist_ok=True)
            
            # Normalize the final path
            file_path = os.path.normpath(file_path)
            
            # Export to Excel
            df.to_excel(file_path, index=False)
            return file_path
        except Exception as e:
            raise ValueError(f"Error exporting to Excel: {str(e)}")
    
    def export_to_json(self, file_path: str) -> str:
        """
        Export parsed data to JSON file
        
        Args:
            file_path: Output JSON file path
            
        Returns:
            str: Path to created file
        """
        if not self.data:
            raise ValueError("No data to export")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.data, f, indent=2)
            return file_path
        except Exception as e:
            raise ValueError(f"Error exporting to JSON: {str(e)}")
    
    def get_data(self) -> List[Dict]:
        """Return parsed data as list of dictionaries"""
        return self.data
    
    def get_dataframe(self) -> pd.DataFrame:
        """Return parsed data as pandas DataFrame"""
        if not self.data:
            return pd.DataFrame()
        return pd.DataFrame(self.data)
    
    def upload_and_convert(self, file_path: str, auto_export: bool = True) -> Dict:
        """
        Upload XML file, parse it, and automatically convert to Excel
        
        Args:
            file_path: Path to uploaded XML file
            auto_export: If True, automatically export to Excel in data/processed
        
        Returns:
            Dict: Result information including file_type, output_path, and data_count
        """
        try:
            # Parse the file
            file_type, data = self.parse_file(file_path)
            
            # Get filename without extension
            filename = os.path.splitext(os.path.basename(file_path))[0]
            
            result = {
                "status": "success",
                "file_type": file_type,
                "input_file": file_path,
                "data_count": len(data),
                "columns": list(self.data[0].keys()) if self.data else []
            }
            
            # Auto-export to Excel if requested
            if auto_export:
                excel_path = self.export_to_excel()
                result["output_file"] = excel_path
                result["export_format"] = "Excel"
                result["export_status"] = "success"
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e)
            }


# Convenience functions for direct usage
def parse_xml_file(file_path: str) -> Tuple[str, List[Dict]]:
    """
    Parse an XML file and return (file_type, data)
    
    Args:
        file_path: Path to XML file
        
    Returns:
        Tuple[str, List[Dict]]: (file_type, parsed_data)
    """
    parser = XMLParser()
    return parser.parse_file(file_path)


def export_xml_to_excel(xml_file_path: str, output_excel_path: str) -> str:
    """
    Parse XML file and export to Excel
    
    Args:
        xml_file_path: Path to input XML file
        output_excel_path: Path to output Excel file
        
    Returns:
        str: Path to created Excel file
    """
    parser = XMLParser()
    parser.parse_file(xml_file_path)
    return parser.export_to_excel(output_excel_path)


def export_xml_to_json(xml_file_path: str, output_json_path: str) -> str:
    """
    Parse XML file and export to JSON
    
    Args:
        xml_file_path: Path to input XML file
        output_json_path: Path to output JSON file
        
    Returns:
        str: Path to created JSON file
    """
    parser = XMLParser()
    parser.parse_file(xml_file_path)
    return parser.export_to_json(output_json_path)