"""
Flask Upload API Test - Simulates file upload and conversion
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ingestion import XMLParser


def test_upload_and_convert():
    """Test the upload and conversion workflow"""
    
    test_files = [
        ("data/raw/power.osm", "power"),
        ("data/raw/water.osm", "water"),
    ]
    
    print("\n" + "=" * 70)
    print("🧪 TESTING UPLOAD & CONVERSION WORKFLOW")
    print("=" * 70)
    
    for file_path, expected_type in test_files:
        # Resolve path relative to this script
        full_path = os.path.join(os.path.dirname(__file__), "..", file_path)
        full_path = os.path.normpath(full_path)
        
        if not os.path.exists(full_path):
            print(f"\n❌ File not found: {full_path}")
            continue
        
        print(f"\n📁 Testing: {os.path.basename(full_path)}")
        print(f"   Path: {full_path}")
        
        parser = XMLParser()
        
        try:
            # Upload and convert (simulating the Flask workflow)
            result = parser.upload_and_convert(full_path, auto_export=True)
            
            print(f"\n✅ Success!")
            print(f"   Type: {result['file_type'].upper()}")
            print(f"   Records: {result['data_count']}")
            print(f"   Excel Output: {os.path.basename(result['output_file'])}")
            
            # Verify no missing data
            if parser.data:
                print(f"\n   📊 Data Quality Check:")
                df = parser.get_dataframe()
                
                missing_per_column = df.isnull().sum()
                if missing_per_column.sum() == 0:
                    print(f"   ✅ NO MISSING VALUES - All fields populated!")
                else:
                    print(f"   ⚠️  Missing values detected:")
                    for col, count in missing_per_column[missing_per_column > 0].items():
                        print(f"      • {col}: {count} missing")
                
                # Show first record
                print(f"\n   📄 First Record Sample:")
                for key, value in parser.data[0].items():
                    print(f"      • {key}: {value}")
        
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    print("\n" + "=" * 70)
    print("✅ Upload & Conversion Test Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_upload_and_convert()
