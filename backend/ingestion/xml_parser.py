import xml.etree.ElementTree as ET
import pandas as pd


def parse_osm(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # STEP 1: Store node coordinates
    node_coords = {}

    for node in root.findall("node"):
        node_id = node.get("id")
        lat = node.get("lat")
        lon = node.get("lon")

        if node_id and lat and lon:
            node_coords[node_id] = (float(lat), float(lon))

    data = []

    # STEP 2: Extract tags
    def get_tags(element):
        return {tag.get("k"): tag.get("v") for tag in element.findall("tag")}

    # STEP 3: Compute centroid for ways
    def get_center(refs):
        lats, lons = [], []

        for ref in refs:
            if ref in node_coords:
                lat, lon = node_coords[ref]
                lats.append(lat)
                lons.append(lon)

        if lats and lons:
            return sum(lats) / len(lats), sum(lons) / len(lons)

        return None, None

    # STEP 4: Extract data
    for element in root.findall("node") + root.findall("way"):

        tags = get_tags(element)

        if tags.get("man_made") != "water_works":
            continue

        name = tags.get("name", "").lower()

        # TYPE CLASSIFICATION
        if "tank" in name:
            asset_type = "Water Tank"
        elif "reservoir" in name:
            asset_type = "Reservoir"
        elif "plant" in name or "filter" in name or "treatment" in name:
            asset_type = "WTP"
        else:
            asset_type = "Water Works"

        # NODE case
        if element.tag == "node":
            node_refs = element.get("id")
            lat = float(element.get("lat"))
            lon = float(element.get("lon"))

        # WAY case
        else:
            refs = [nd.get("ref") for nd in element.findall("nd")]
            node_refs = ",".join(refs)
            lat, lon = get_center(refs)

        data.append({
            "type": asset_type,
            "node_ref": node_refs,
            "name": tags.get("name", "N/A"),
            "operator": tags.get("operator", "N/A"),
            "man_made": tags.get("man_made", "N/A"),
            "landuse": tags.get("landuse", "N/A"),
            "latitude": lat,
            "longitude": lon
        })

    # STEP 5: DataFrame
    df = pd.DataFrame(data)

    # STEP 6: Clean data
    df.drop_duplicates(subset=["node_ref", "name"], inplace=True)
    df.dropna(subset=["latitude", "longitude"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


if __name__ == "__main__":
    input_file = "../../data/raw/water.osm"
    output_file = "../../data/processed/water_data.xlsx"

    df = parse_osm(input_file)
    df.to_excel(output_file, index=False)

    print("Excel file created successfully!")
    print("Total rows:", len(df))
    print("\nType distribution:")
    print(df["type"].value_counts())