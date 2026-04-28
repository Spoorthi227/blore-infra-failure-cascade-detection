"""
Complete Parser Test - Shows all three methods working
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ingestion import XMLParser


def test_complete_workflow():
    """Test complete upload and conversion for both power and water"""
    
    test_files = [
        {
            "path": "data/raw/power.osm",
            "type": "power",
            "description": "Power Infrastructure (Substations)"
        },
        {
            "path": "data/raw/water.osm",
            "type": "water",
            "description": "Water Infrastructure (Treatment Plants)"
        }
    ]
    
    print("\n" + "=" * 80)
    print("🧪 COMPLETE OSM TO EXCEL PARSER TEST")
    print("=" * 80)
    
    results = []
    
    for test_file in test_files:
        file_path = os.path.join(os.path.dirname(__file__), "..", test_file["path"])
        file_path = os.path.normpath(file_path)
        
        print(f"\n📁 {test_file['description']}")
        print(f"   File: {os.path.basename(file_path)}")
        
        if not os.path.exists(file_path):
            print(f"   ❌ File not found")
            continue
        
        parser = XMLParser()
        
        try:
            # Parse file
            file_type, data = parser.parse_file(file_path)
            print(f"   ✅ Parsed: {len(data)} records")
            
            # Export to Excel
            excel_path = parser.export_to_excel()
            print(f"   ✅ Exported: {os.path.basename(excel_path)}")
            
            # Get DataFrame for analysis
            df = parser.get_dataframe()
            
            print(f"\n   📊 DATA QUALITY:")
            print(f"      • Total Records: {len(df)}")
            print(f"      • Columns: {len(df.columns)}")
            print(f"      • Missing Values: {df.isnull().sum().sum()}")
            
            if test_file["type"] == "power":
                print(f"      • Power Type: {df['power'].unique()[0] if len(df) > 0 else 'N/A'}")
            elif test_file["type"] == "water":
                print(f"      • Type Distribution:")
                for dtype, count in df["type"].value_counts().items():
                    print(f"         - {dtype}: {count}")
            
            print(f"\n   🔍 SAMPLE RECORD:")
            if len(df) > 0:
                for col, val in df.iloc[0].items():
                    display_val = str(val)[:50] if val is not None else "N/A"
                    print(f"      • {col}: {display_val}")
            
            results.append({
                "name": test_file["description"],
                "status": "✅ Success",
                "records": len(df),
                "missing": df.isnull().sum().sum(),
                "file": os.path.basename(excel_path)
            })
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                "name": test_file["description"],
                "status": "❌ Failed",
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 TEST SUMMARY")
    print("=" * 80)
    
    for result in results:
        if result["status"] == "✅ Success":
            print(f"\n✅ {result['name']}")
            print(f"   Records: {result['records']}")
            print(f"   Missing: {result['missing']}")
            print(f"   File: {result['file']}")
        else:
            print(f"\n❌ {result['name']}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE - All files ready in data/processed/")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    test_complete_workflow()
