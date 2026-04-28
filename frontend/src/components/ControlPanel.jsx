import React from 'react';

function ControlPanel({ data, fileType }) {
  return (
    <div className="control-panel-component">
      <h3>⚙️ Control Panel</h3>
      <div className="info">
        <p><strong>Type:</strong> {fileType}</p>
        <p><strong>Records:</strong> {data.length}</p>
      </div>
      
      <div className="controls">
        <button onClick={() => console.log('Export clicked')}>
          📥 Export Data
        </button>
        <button onClick={() => console.log('Simulate clicked')}>
          ⚡ Run Simulation
        </button>
      </div>
    </div>
  );
}

export default ControlPanel;
