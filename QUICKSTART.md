# 🚀 Quick Start Guide - Blore Infrastructure Failure Cascade Detection

## Installation & Setup

### 1. Backend Setup (Python)

```bash
# Navigate to backend directory
cd backend

# Install required dependencies
pip install -r ../requirements.txt

# Verify installation
python -c "from ingestion import XMLParser; print('✅ All imports successful')"
```

### 2. Frontend Setup (React)

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Verify Vite configuration
cat vite.config.js
```

### 3. Sample Data

Sample OSM files are located in `data/raw/`:
- `power.osm` - Power infrastructure (substations)
- `water.osm` - Water infrastructure (treatment plants)

## Running the Application

### Option A: Interactive Parser (GUI)

```bash
cd backend
python xml_parser.py
```
- Opens file dialog to select OSM file
- Automatically parses and exports to Excel
- Saves to `data/processed/`

### Option B: Flask API Server + React Frontend

```bash
# Terminal 1 - Start Backend API
cd backend
python -m flask run --port=5000

# Terminal 2 - Start Frontend Development Server
cd frontend
npm run dev
```

Then open browser: http://localhost:3000

### Option C: Direct Testing

```bash
cd backend
python test_complete.py
```
Runs full validation on sample files

## 📊 Expected Output

### Power Infrastructure (Substations)
- ✅ 44 records extracted
- ✅ 12 columns: frequency, location, name, operator, power, rating, reference, start_date, substation, voltage, latitude, longitude
- ✅ 0 missing values
- ✅ Excel file: `power_output.xlsx`

### Water Infrastructure
- ✅ 53 records extracted
- ✅ 8 columns: type, node_ref, name, operator, man_made, landuse, latitude, longitude
- ✅ 0 missing values
- ✅ Smart type classification: Water Works, WTP, Reservoir, Water Tank
- ✅ Excel file: `water_output.xlsx`

## 🗂️ Project Structure

```
blore-infra-failure-cascade-detection/
├── backend/
│   ├── app.py                 # Flask REST API
│   ├── xml_parser.py          # Interactive GUI
│   ├── test_complete.py       # Validation tests
│   ├── test_upload.py         # Upload tests
│   ├── ingestion/
│   │   ├── xml_parser.py      # Core OSM parser
│   │   └── kml_parser.py      # KML parser (placeholder)
│   ├── graph/                 # Graph construction (placeholder)
│   ├── simulation/            # Cascade failure simulation (placeholder)
│   └── utils/                 # Utility functions
├── frontend/
│   ├── package.json           # React dependencies
│   ├── vite.config.js         # Vite build config
│   ├── public/
│   │   └── index.html         # HTML entry point
│   └── src/
│       ├── App.jsx            # Main React app
│       ├── main.jsx           # React entry
│       ├── App.css            # Styling
│       ├── index.css          # Global styles
│       ├── components/
│       │   ├── UploadXML.jsx  # XML upload form
│       │   ├── UploadKML.jsx  # KML upload form
│       │   ├── MapView.jsx    # Map visualization
│       │   ├── GraphView.jsx  # Graph visualization
│       │   └── ControlPanel.jsx # Controls
│       └── services/
│           ├── xmlApi.js      # XML API client
│           └── kmlApi.js      # KML API client
├── data/
│   ├── raw/                   # Sample OSM files
│   ├── processed/             # Output Excel/JSON
│   └── graphs/                # Graph outputs
├── requirements.txt           # Python dependencies
├── README.md                  # Main documentation
├── PARSER_GUIDE.md            # Parser details
└── FINAL_SOLUTION.md          # Implementation details
```

## 🔌 API Endpoints

### Health Check
```bash
GET /api/health
```

### Upload File
```bash
POST /api/upload
Content-Type: multipart/form-data
file: <osm-or-xml-file>
```

### Parse XML
```bash
POST /api/parse/xml
{
  "file_path": "/path/to/file.osm"
}
```

### Export Data
```bash
POST /api/export/json
{
  "file_path": "/path/to/file.osm"
}

# or export/excel
POST /api/export/excel
```

## ✅ Verification Checklist

- [ ] Python 3.11+ installed
- [ ] `pip install -r requirements.txt` completed
- [ ] `python test_complete.py` passes all tests
- [ ] Node.js 18+ installed (for frontend)
- [ ] `npm install` in frontend/ completed
- [ ] Backend imports work: `python -c "from ingestion import XMLParser"`
- [ ] Flask app imports work: `python -c "import app"`

## 📦 Dependencies

### Python (backend)
- Flask 2.3.2
- pandas 2.0.3
- openpyxl 3.1.2
- Flask-CORS 4.0.0

### Node.js (frontend)
- react 18.2.0
- react-dom 18.2.0
- axios (for API calls)
- leaflet (for maps)
- react-leaflet (React wrapper)
- recharts (for graphs)

See `requirements.txt` for Python and `frontend/package.json` for Node.js dependencies.

## 🐛 Troubleshooting

**Import Error: "No module named 'ingestion'"**
- Ensure you're in the `backend/` directory
- Run: `pip install -e .` to install in development mode

**Flask not found**
- Install: `pip install flask`
- Or run: `pip install -r requirements.txt`

**Port already in use (5000 or 3000)**
- Change Flask port: `python -m flask run --port=8000`
- Change Frontend port: Edit `vite.config.js` server.port

**File not found errors**
- Use absolute paths
- Or ensure files are in `data/raw/` directory

## 🚀 Next Steps

1. **Test with your own OSM files** - Use data from OpenStreetMap export
2. **Implement KML parser** - Uncomment in `backend/ingestion/kml_parser.py`
3. **Build graph structure** - Add NetworkX in `backend/graph/`
4. **Add simulation logic** - Implement cascade failure in `backend/simulation/`
5. **Complete frontend visualizations** - Implement Leaflet map in React

## 📞 Support

For issues or questions, refer to:
- `README.md` - Comprehensive documentation
- `PARSER_GUIDE.md` - Parser-specific details
- `FINAL_SOLUTION.md` - Implementation notes
