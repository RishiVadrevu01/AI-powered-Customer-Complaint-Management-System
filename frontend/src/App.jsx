import React from 'react';
import Header from './components/Header';
import ComplaintForm from './components/ComplaintForm';
import AICopilotChat from './components/AICopilotChat';
import QMSLedgerModal from './components/QMSLedgerModal';
import NotificationToast from './components/NotificationToast';

export function App() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <main className="app-container">
        <div className="split-layout">
          {/* Left Side: Customer Complaint Form */}
          <ComplaintForm />
          {/* Right Side: AI Copilot Chat (LangGraph Powered) */}
          <AICopilotChat />
        </div>
      </main>
      <QMSLedgerModal />
      <NotificationToast />
    </div>
  );
}

export default App;
