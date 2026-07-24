import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { processComplaint, uploadComplaintDoc } from '../store/complaintSlice';
import { addMessage } from '../store/chatSlice';
import { Bot, Send, Upload, Sparkles, User, FileText, Loader2 } from 'lucide-react';

export const AICopilotChat = () => {
  const dispatch = useDispatch();
  const { messages } = useSelector((state) => state.chat);
  const { loading } = useSelector((state) => state.complaint);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput('');

    // Add user message to chat
    dispatch(addMessage({ sender: 'user', text: userText }));

    // Trigger LangGraph backend processing
    try {
      const resultAction = await dispatch(processComplaint(userText));
      if (processComplaint.fulfilled.match(resultAction)) {
        const payload = resultAction.payload;
        dispatch(addMessage({
          sender: 'assistant',
          text: payload.copilot_message || "Complaint parsed successfully. I've extracted the product details, mapped the batch information, and generated an initial risk assessment."
        }));
      } else {
        dispatch(addMessage({
          sender: 'assistant',
          text: `⚠️ Error processing complaint: ${resultAction.payload || 'Unknown error'}`
        }));
      }
    } catch (err) {
      dispatch(addMessage({
        sender: 'assistant',
        text: `⚠️ Network error: Could not reach LangGraph server.`
      }));
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    dispatch(addMessage({ sender: 'user', text: `Uploaded document: 📄 ${file.name}` }));

    try {
      const resultAction = await dispatch(uploadComplaintDoc(file));
      if (uploadComplaintDoc.fulfilled.match(resultAction)) {
        const payload = resultAction.payload;
        dispatch(addMessage({
          sender: 'assistant',
          text: payload.copilot_message || `Document '${file.name}' processed successfully. Form auto-populated with extracted metadata.`
        }));
      } else {
        dispatch(addMessage({
          sender: 'assistant',
          text: `⚠️ Error reading file: ${resultAction.payload}`
        }));
      }
    } catch (err) {
      dispatch(addMessage({
        sender: 'assistant',
        text: `⚠️ Upload error occurred.`
      }));
    }
  };

  return (
    <div className="panel-card">
      <div className="panel-header">
        <div className="panel-title">
          <Bot size={18} style={{ color: 'var(--accent-cyan)' }} />
          <span>AI Copilot Chat (LangGraph Powered)</span>
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Pharmaceutical Intake Assistant
        </span>
      </div>

      {/* Messages Stream */}
      <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div className="chat-messages" style={{ flex: 1 }}>
          {messages.map((msg) => (
            <div key={msg.id} className={`chat-bubble ${msg.sender}`}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', fontSize: '0.75rem', opacity: 0.8 }}>
                {msg.sender === 'assistant' ? <Bot size={14} /> : <User size={14} />}
                <span style={{ fontWeight: 600 }}>{msg.sender === 'assistant' ? 'AI Copilot' : 'Quality Agent'}</span>
                <span>• {msg.timestamp}</span>
              </div>
              <p style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</p>
            </div>
          ))}

          {loading && (
            <div className="chat-bubble assistant">
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', fontSize: '0.75rem', opacity: 0.8 }}>
                <Bot size={14} />
                <span style={{ fontWeight: 600 }}>AI Copilot</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--accent-blue)', fontWeight: 500 }}>is thinking...</span>
              </div>
              <div className="typing-indicator">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
              </div>
            </div>
          )}


          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input Area */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ position: 'relative' }}>
            <textarea
              rows={3}
              className="form-textarea"
              placeholder="Paste unstructured customer complaint, report text, or details here..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
              style={{ paddingRight: '45px' }}
            />

            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              accept=".pdf,.txt,.doc,.docx"
              onChange={handleFileUpload}
            />

            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="btn-secondary"
              style={{
                position: 'absolute',
                right: '8px',
                bottom: '8px',
                padding: '6px 10px',
                borderRadius: 'var(--radius-sm)'
              }}
              title="Upload PDF or Document Report"
            >
              <Upload size={14} />
            </button>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-subtle)' }}>
              Press Enter to send • Shift+Enter for new line
            </span>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading || !input.trim()}
              style={{ padding: '8px 18px', fontSize: '0.85rem' }}
            >
              <span>Process Complaint</span>
              <Send size={14} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AICopilotChat;
