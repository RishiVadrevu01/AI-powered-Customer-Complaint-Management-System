import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { updateFormField, commitComplaint, resetForm } from '../store/complaintSlice';
import { FileText, Save, CheckCircle2, AlertTriangle, RefreshCw, Cpu } from 'lucide-react';

export const ComplaintForm = () => {
  const dispatch = useDispatch();
  const { formData, isExtracted, loading } = useSelector((state) => state.complaint);

  const handleInputChange = (field, value) => {
    dispatch(updateFormField({ field, value }));
  };

  const handleCommit = (e) => {
    e.preventDefault();
    dispatch(commitComplaint(formData));
  };

  const getSeverityBadgeClass = (severity) => {
    if (!severity || severity.includes('Awaiting')) return 'severity-pill';
    const sev = severity.toLowerCase();
    if (sev.includes('critical')) return 'severity-pill severity-critical';
    if (sev.includes('major')) return 'severity-pill severity-major';
    return 'severity-pill severity-minor';
  };

  const isAwaiting = (val) => typeof val === 'string' && val.includes('Awaiting');

  return (
    <div className="panel-card">
      <div className="panel-header">
        <div className="panel-title">
          <FileText size={18} className="text-blue-400" />
          <span>Log Customer Complaint</span>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {isExtracted ? (
            <span style={{ fontSize: '0.75rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <CheckCircle2 size={14} /> AI Form Populated
            </span>
          ) : (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Cpu size={14} /> Ready for Input
            </span>
          )}
          {isExtracted && (
            <button 
              type="button"
              onClick={() => dispatch(resetForm())}
              className="btn-secondary"
              style={{ padding: '4px 8px', fontSize: '0.75rem' }}
              title="Clear & Reset Form"
            >
              <RefreshCw size={12} /> Reset
            </button>
          )}
        </div>
      </div>

      <div className="panel-body">
        <form onSubmit={handleCommit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Metadata Grid */}
          <div className="form-grid">
            
            {/* Customer Name */}
            <div className="form-group">
              <label className="form-label">Customer / Reporting Source</label>
              <input
                type="text"
                className={`form-input ${isAwaiting(formData.customer_name) ? 'awaiting' : isExtracted ? 'highlighted' : ''}`}
                value={formData.customer_name || ''}
                onChange={(e) => handleInputChange('customer_name', e.target.value)}
                placeholder="Awaiting AI extraction..."
              />
            </div>

            {/* Product Name */}
            <div className="form-group">
              <label className="form-label">Product Name & Dosage</label>
              <input
                type="text"
                className={`form-input ${isAwaiting(formData.product_name) ? 'awaiting' : isExtracted ? 'highlighted' : ''}`}
                value={formData.product_name || ''}
                onChange={(e) => handleInputChange('product_name', e.target.value)}
                placeholder="Awaiting AI extraction..."
              />
            </div>

            {/* Batch Number */}
            <div className="form-group">
              <label className="form-label">Batch / Lot Number</label>
              <input
                type="text"
                className={`form-input ${isAwaiting(formData.batch_number) ? 'awaiting' : isExtracted ? 'highlighted' : ''}`}
                value={formData.batch_number || ''}
                onChange={(e) => handleInputChange('batch_number', e.target.value)}
                placeholder="Awaiting AI extraction..."
              />
            </div>

            {/* Complaint Category */}
            <div className="form-group">
              <label className="form-label">Complaint Category</label>
              <input
                type="text"
                className={`form-input ${isAwaiting(formData.complaint_category) ? 'awaiting' : isExtracted ? 'highlighted' : ''}`}
                value={formData.complaint_category || ''}
                onChange={(e) => handleInputChange('complaint_category', e.target.value)}
                placeholder="Awaiting AI classification..."
              />
            </div>

            {/* Manufacturing Date */}
            <div className="form-group">
              <label className="form-label">Manufacturing Date</label>
              <input
                type="text"
                className={`form-input ${isAwaiting(formData.manufacturing_date) ? 'awaiting' : ''}`}
                value={formData.manufacturing_date || ''}
                onChange={(e) => handleInputChange('manufacturing_date', e.target.value)}
                placeholder="Awaiting AI extraction..."
              />
            </div>

            {/* Expiry Date */}
            <div className="form-group">
              <label className="form-label">Expiry Date</label>
              <input
                type="text"
                className={`form-input ${isAwaiting(formData.expiry_date) ? 'awaiting' : ''}`}
                value={formData.expiry_date || ''}
                onChange={(e) => handleInputChange('expiry_date', e.target.value)}
                placeholder="Awaiting AI extraction..."
              />
            </div>

            {/* Facility */}
            <div className="form-group">
              <label className="form-label">Manufacturing Facility</label>
              <input
                type="text"
                className={`form-input ${isAwaiting(formData.facility) ? 'awaiting' : ''}`}
                value={formData.facility || ''}
                onChange={(e) => handleInputChange('facility', e.target.value)}
                placeholder="Awaiting AI extraction..."
              />
            </div>

            {/* Impacted Material */}
            <div className="form-group">
              <label className="form-label">Impacted Material</label>
              <input
                type="text"
                className={`form-input ${isAwaiting(formData.impacted_material) ? 'awaiting' : ''}`}
                value={formData.impacted_material || ''}
                onChange={(e) => handleInputChange('impacted_material', e.target.value)}
                placeholder="Awaiting AI extraction..."
              />
            </div>
          </div>

          {/* AI QMS Rewritten Summary */}
          <div className="form-group full-width">
            <label className="form-label">
              <span>QMS Formal Description (AI Rewritten)</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--accent-cyan)' }}>Quality Standard Format</span>
            </label>
            <textarea
              rows={3}
              className={`form-textarea ${isAwaiting(formData.qms_summary) ? 'awaiting' : isExtracted ? 'highlighted' : ''}`}
              value={formData.qms_summary || ''}
              onChange={(e) => handleInputChange('qms_summary', e.target.value)}
              placeholder="Awaiting AI extraction..."
            />
          </div>

          {/* Severity & Risk Assessment */}
          <div style={{ 
            background: 'rgba(15, 23, 42, 0.6)', 
            border: '1px solid var(--border-color)', 
            borderRadius: 'var(--radius-md)', 
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: 600 }}>
                <AlertTriangle size={16} style={{ color: '#f59e0b' }} />
                <span>AI Risk & Severity Evaluation</span>
              </div>
              <div className={getSeverityBadgeClass(formData.suggested_severity)}>
                {formData.suggested_severity || 'Awaiting'}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Potential Root Cause / Risk Assessment</label>
              <textarea
                rows={2}
                className={`form-textarea ${isAwaiting(formData.risk_assessment) ? 'awaiting' : ''}`}
                value={formData.risk_assessment || ''}
                onChange={(e) => handleInputChange('risk_assessment', e.target.value)}
                placeholder="Awaiting AI extraction..."
              />
            </div>

            <div className="form-group">
              <label className="form-label">Recommended Next Action Step</label>
              <input
                type="text"
                className={`form-input ${isAwaiting(formData.recommended_action) ? 'awaiting' : ''}`}
                value={formData.recommended_action || ''}
                onChange={(e) => handleInputChange('recommended_action', e.target.value)}
                placeholder="Awaiting AI extraction..."
              />
            </div>
          </div>

          {/* Action Button */}
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !isExtracted}
            style={{ width: '100%', marginTop: '8px' }}
          >
            {loading ? (
              <>
                <RefreshCw size={18} className="animate-spin" /> Saving to Database...
              </>
            ) : (
              <>
                <Save size={18} /> Commit to QMS Ledger
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ComplaintForm;
