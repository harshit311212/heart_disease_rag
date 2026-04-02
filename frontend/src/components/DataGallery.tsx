import React from 'react';
import type { PatientData } from '../App';

interface DataGalleryProps {
  data: PatientData[];
  isError: boolean;
}

const DataGallery: React.FC<DataGalleryProps> = ({ data, isError }) => {
  if (isError) {
    return (
      <div className="error-brutalist">
        Sorry I can't find anything relevant to this question
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ opacity: 0.2, textAlign: 'center' }}>
        <h3 className="signage-text" style={{ fontSize: '18px', letterSpacing: '4px' }}>WAITING FOR DATA</h3>
        <p style={{ marginTop: '10px' }}>3D SPATIAL GALAXY</p>
      </div>
    );
  }

  return (
    <div className="gallery-container">
      {data.map((patient, index) => {
        // Evaluate risk for highlighting
        const isHighRisk = patient.HeartDisease == "1" || patient.HeartDisease === 1;

        return (
          <div key={index} className={`patient-card ${isHighRisk ? 'risk-high' : ''}`}>
            <div className="card-header">
              <span>Patient Record #{patient.row_id}</span>
              {isHighRisk && <span style={{ color: 'var(--accent-red)' }}>HIGH RISK</span>}
            </div>
            
            <div className="card-grid">
              <div className="metric-box">
                <div className="metric-label">Age & Sex</div>
                <div className="metric-value">{patient.Age} {patient.Sex}</div>
              </div>
              <div className="metric-box">
                <div className="metric-label">Cholesterol</div>
                <div className="metric-value">{patient.Cholesterol} mg/dl</div>
              </div>
              <div className="metric-box">
                <div className="metric-label">Resting BP</div>
                <div className="metric-value">{patient.RestingBP} mm Hg</div>
              </div>
              <div className="metric-box">
                <div className="metric-label">Max Heart Rate</div>
                <div className="metric-value">{patient.MaxHR} bpm</div>
              </div>
              <div className="metric-box">
                <div className="metric-label">Chest Pain</div>
                <div className="metric-value">{patient.ChestPainType}</div>
              </div>
              <div className="metric-box">
                <div className="metric-label">ECG</div>
                <div className="metric-value">{patient.RestingECG}</div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default DataGallery;
