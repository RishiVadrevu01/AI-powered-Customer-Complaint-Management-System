import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { clearNotification } from '../store/complaintSlice';
import { CheckCircle2, X } from 'lucide-react';

export const NotificationToast = () => {
  const dispatch = useDispatch();
  const { successNotification } = useSelector((state) => state.complaint);

  useEffect(() => {
    if (successNotification) {
      const timer = setTimeout(() => {
        dispatch(clearNotification());
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [successNotification, dispatch]);

  if (!successNotification) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      background: 'rgba(16, 185, 129, 0.95)',
      color: '#ffffff',
      padding: '14px 20px',
      borderRadius: 'var(--radius-md)',
      boxShadow: '0 10px 25px rgba(16, 185, 129, 0.4)',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      zIndex: 1000,
      backdropFilter: 'blur(8px)',
      animation: 'slideUp 0.3s ease-out'
    }}>
      <CheckCircle2 size={20} />
      <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{successNotification}</span>
      <button 
        onClick={() => dispatch(clearNotification())}
        style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', marginLeft: '8px' }}
      >
        <X size={16} />
      </button>
    </div>
  );
};

export default NotificationToast;
