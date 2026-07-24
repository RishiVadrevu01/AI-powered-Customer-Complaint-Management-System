import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { toggleLedgerModal } from '../store/complaintSlice';
import { ShieldCheck, Database, FileSpreadsheet, Bot } from 'lucide-react';

export const Header = () => {
  const dispatch = useDispatch();
  const { committedLedger } = useSelector((state) => state.complaint);

  return (
    <header className="app-header">
      <div className="brand-container">
        <div className="brand-logo">
          <Bot size={22} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 className="brand-title">AIVOA</h1>
            <span className="brand-badge">LANGGRAPH CO-PILOT</span>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            AI-Powered Pharmaceutical QMS Complaint Intake System
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: '#10b981' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px #10b981' }}></span>
          LangGraph Workflow Active
        </div>

        <button 
          onClick={() => dispatch(toggleLedgerModal(true))}
          className="btn-secondary"
        >
          <FileSpreadsheet size={16} />
          <span>QMS Ledger</span>
          {committedLedger.length > 0 && (
            <span style={{ 
              background: 'var(--accent-blue)', 
              color: 'white', 
              borderRadius: '10px', 
              padding: '2px 6px', 
              fontSize: '0.72rem',
              fontWeight: 700
            }}>
              {committedLedger.length}
            </span>
          )}
        </button>
      </div>
    </header>
  );
};

export default Header;
