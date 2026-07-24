import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { toggleLedgerModal, fetchCommittedComplaints } from '../store/complaintSlice';
import { X, FileSpreadsheet, AlertTriangle, CheckCircle } from 'lucide-react';

export const QMSLedgerModal = () => {
  const dispatch = useDispatch();
  const { isLedgerOpen, committedLedger } = useSelector((state) => state.complaint);

  useEffect(() => {
    if (isLedgerOpen) {
      dispatch(fetchCommittedComplaints());
    }
  }, [isLedgerOpen, dispatch]);

  if (!isLedgerOpen) return null;

  return (
    <div className="modal-overlay" onClick={() => dispatch(toggleLedgerModal(false))}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="panel-header" style={{ padding: '20px 24px' }}>
          <div className="panel-title" style={{ fontSize: '1.1rem' }}>
            <FileSpreadsheet size={20} style={{ color: 'var(--accent-blue)' }} />
            <span>PostgreSQL QMS Complaint Ledger</span>
          </div>
          <button 
            onClick={() => dispatch(toggleLedgerModal(false))}
            className="btn-secondary"
            style={{ padding: '6px' }}
          >
            <X size={18} />
          </button>
        </div>

        <div style={{ padding: '20px 24px', overflowY: 'auto', flex: 1 }}>
          {committedLedger.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
              <FileSpreadsheet size={40} style={{ opacity: 0.3, marginBottom: '12px' }} />
              <p>No complaints committed to QMS Ledger yet.</p>
              <p style={{ fontSize: '0.8rem', marginTop: '4px' }}>
                Use the AI Copilot to log and commit a complaint to inspect database records here.
              </p>
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Customer</th>
                  <th>Product</th>
                  <th>Batch #</th>
                  <th>Category</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {committedLedger.map((item) => (
                  <tr key={item.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>#{item.id}</td>
                    <td>{item.customer_name || 'N/A'}</td>
                    <td style={{ fontWeight: 600 }}>{item.product_name || 'N/A'}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>
                      {item.batch_number || 'N/A'}
                    </td>
                    <td>{item.complaint_category || 'N/A'}</td>
                    <td>
                      <span className={`severity-pill ${
                        item.suggested_severity?.toLowerCase().includes('critical') ? 'severity-critical' :
                        item.suggested_severity?.toLowerCase().includes('major') ? 'severity-major' : 'severity-minor'
                      }`} style={{ fontSize: '0.7rem', padding: '2px 8px' }}>
                        {item.suggested_severity || 'Major'}
                      </span>
                    </td>
                    <td>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.78rem', color: '#10b981' }}>
                        <CheckCircle size={12} /> {item.status || 'Committed'}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {new Date(item.created_at ? (item.created_at.endsWith('Z') ? item.created_at : item.created_at + 'Z') : Date.now()).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default QMSLedgerModal;
