import React from 'react';

function GraphView({ data }) {
  // TODO: Implement graph visualization with Recharts
  
  return (
    <div className="graph-view-component">
      <h3>📊 Graph View</h3>
      <p>Graph visualization coming soon...</p>
      {data && <p>Records loaded: {data.length}</p>}
    </div>
  );
}

export default GraphView;
