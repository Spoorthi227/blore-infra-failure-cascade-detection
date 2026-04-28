"""
OSM XML Parser - Interactive File Upload & Excel Converter
Upload your OSM file and convert to Excel with proper data extraction
"""

import os
import sys
from pathlib import Path
from tkinter import Tk, filedialog, messagebox
from ingestion import XMLParser


def get_user_file():
    """Show file dialog to let user select OSM file"""
    
    # Create a hidden Tkinter window
    root = Tk()
    root.withdraw()  # Hide the window
    root.attributes('-topmost', True)  # Bring dialog to front
    
    # Open file dialog
    file_path = filedialog.askopenfilename(
        title="Select OSM File (Power or Water Infrastructure)",
        filetypes=[
            ("OSM Files", "*.osm"),
            ("XML Files", "*.xml"),
            ("All Files", "*.*")
        ],
        initialdir=os.path.expanduser("~")
    )
    
    root.destroy()
    
    if not file_path:
        print("\n❌ No file selected. Exiting...\n")
        sys.exit(0)
    
    return file_path


def parse_and_convert(file_path):
    """Parse the OSM file and convert to Excel"""
    
    print(f"\n⏳ Processing file: {os.path.basename(file_path)}")
    print("=" * 70)
    
    parser = XMLParser()
    
    try:
        # Parse and auto-convert to Excel
        result = parser.upload_and_convert(file_path, auto_export=True)
        
        if result['status'] == 'success':
            print(f"\n✅ SUCCESS! File processed successfully\n")
            
            print(f"📊 File Information:")
            print(f"   Input File: {os.path.basename(file_path)}")
            print(f"   Infrastructure Type: {result['file_type'].upper()}")
            print(f"   Records Parsed: {result['data_count']}")
            print(f"\n📁 Output Excel File:")
            print(f"   Location: {result['output_file']}")
            print(f"   File Name: {os.path.basename(result['output_file'])}")
            
            print(f"\n📋 Excel Columns ({len(result['columns'])} columns):")
            for i, col in enumerate(result['columns'], 1):
                print(f"   {i:2d}. {col}")
            
            print(f"\n📄 Data Preview (First Record):")
            if parser.data:
                for key, value in parser.data[0].items():
                    print(f"   • {key}: {value}")
            
            # Show more records if available
            if len(parser.data) > 1:
                print(f"\n... and {len(parser.data) - 1} more record(s)")
            
            print("\n" + "=" * 70)
            
            # Show success message in dialog
            messagebox.showinfo(
                "✅ Success",
                f"File processed successfully!\n\n"
                f"Type: {result['file_type'].upper()}\n"
                f"Records: {result['data_count']}\n\n"
                f"Output: {os.path.basename(result['output_file'])}\n\n"
                f"Location: {result['output_file']}"
            )
            return True
            
        else:
            print(f"\n❌ Error: {result['error_message']}")
            messagebox.showerror("❌ Error", f"Failed to parse file:\n{result['error_message']}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        messagebox.showerror("❌ Error", f"Error processing file:\n{str(e)}")
        return False


def show_instructions():
    """Show instructions to user"""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  OSM TO EXCEL CONVERTER - Infrastructure Data Parser  ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    print("\n📝 Instructions:")
    print("   1. A file dialog will open")
    print("   2. Select your OSM file (power.osm or water.osm)")
    print("   3. The parser will auto-detect the type and convert to Excel")
    print("   4. Output will be saved to: data/processed/")
    
    print("\n✨ Supported File Types:")
    print("   • Power Infrastructure (.osm or .xml)")
    print("   • Water Infrastructure (.osm or .xml)")
    
    print("\n✓ Exported Columns:")
    print("\n   Power Infrastructure (12 columns):")
    print("      frequency, location, name, operator, power, rating,")
    print("      reference, start_date, substation, voltage, latitude, longitude")
    print("\n   Water Infrastructure (8 columns):")
    print("      type, node_ref, name, operator, landuse, man_made, latitude, longitude")
    
    print("\n⏳ Opening file dialog...\n")


if __name__ == "__main__":
    show_instructions()
    
    while True:
        # Get file from user using dialog
        file_path = get_user_file()
        
        # Parse and convert
        success = parse_and_convert(file_path)
        
        if success:
            # Ask if user wants to process another file
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            another = messagebox.askyesno(
                "🔄 Continue?",
                "Process another file?"
            )
            root.destroy()
            
            if not another:
                print("\n✅ All files have been saved to: data/processed/")
                print("👋 Thank you for using OSM to Excel Converter!\n")
                sys.exit(0)
        else:
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            retry = messagebox.askyesno(
                "🔄 Retry?",
                "Try again with another file?"
            )
            root.destroy()
            
            if not retry:
                print("\n👋 Exiting...\n")
                sys.exit(0)
