import React from 'react';
import './App.css';
import UploadXML from './components/UploadXML';
import MapView from './components/MapView';
import GraphView from './components/GraphView';
import ControlPanel from './components/ControlPanel';

function App() {
  const [data, setData] = React.useState(null);
  const [fileType, setFileType] = React.useState(null);

  return (
    <div className="app">
      <header>
        <h1>🏗️ Infrastructure Cascade Failure Detection</h1>
      </header>
      
      <main>
        <div className="upload-section">
          <UploadXML onSuccess={(data, type) => { setData(data); setFileType(type); }} />
        </div>
        
        {data && (
          <>
            <div className="control-panel">
              <ControlPanel data={data} fileType={fileType} />
            </div>
            
            <div className="views">
              <div className="map-view">
                <MapView data={data} />
              </div>
              
              <div className="graph-view">
                <GraphView data={data} />
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
