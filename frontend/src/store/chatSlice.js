import { createSlice } from '@reduxjs/toolkit';

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [
      {
        id: 1,
        sender: 'assistant',
        text: 'Paste a customer complaint, upload a PDF, or upload a complaint report. I will extract the data and perform an initial risk assessment.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]
  },
  reducers: {
    addMessage: (state, action) => {
      state.messages.push({
        id: Date.now(),
        sender: action.payload.sender,
        text: action.payload.text,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });
    },
    clearChat: (state) => {
      state.messages = [
        {
          id: Date.now(),
          sender: 'assistant',
          text: 'Paste a customer complaint, upload a PDF, or upload a complaint report. I will extract the data and perform an initial risk assessment.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ];
    }
  }
});

export const { addMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
