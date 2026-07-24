import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const initialExtractedData = {
  customer_name: "Awaiting AI extraction...",
  product_name: "Awaiting AI extraction...",
  batch_number: "Awaiting AI extraction...",
  manufacturing_date: "Awaiting AI extraction...",
  expiry_date: "Awaiting AI extraction...",
  facility: "Awaiting AI extraction...",
  impacted_material: "Awaiting AI extraction...",
  complaint_category: "Awaiting AI classification...",
  raw_complaint_text: "",
  qms_summary: "Awaiting AI extraction...",
  suggested_severity: "Awaiting AI classification...",
  risk_assessment: "Awaiting AI extraction...",
  recommended_action: "Awaiting AI extraction..."
};

export const processComplaint = createAsyncThunk(
  'complaint/processComplaint',
  async (text, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/complaints/process`, {
        complaint_text: text
      });
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to process complaint text');
    }
  }
);

export const uploadComplaintDoc = createAsyncThunk(
  'complaint/uploadComplaintDoc',
  async (file, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post(`${API_BASE_URL}/complaints/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to process uploaded file');
    }
  }
);

export const commitComplaint = createAsyncThunk(
  'complaint/commitComplaint',
  async (complaintData, { rejectWithValue }) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/complaints/commit`, complaintData);
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to commit complaint to QMS Ledger');
    }
  }
);

export const fetchCommittedComplaints = createAsyncThunk(
  'complaint/fetchCommittedComplaints',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/complaints`);
      return response.data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || 'Failed to fetch complaints ledger');
    }
  }
);

const complaintSlice = createSlice({
  name: 'complaint',
  initialState: {
    formData: { ...initialExtractedData },
    isExtracted: false,
    loading: false,
    error: null,
    committedLedger: [],
    isLedgerOpen: false,
    successNotification: null
  },
  reducers: {
    updateFormField: (state, action) => {
      const { field, value } = action.payload;
      state.formData[field] = value;
    },
    resetForm: (state) => {
      state.formData = { ...initialExtractedData };
      state.isExtracted = false;
      state.error = null;
    },
    toggleLedgerModal: (state, action) => {
      state.isLedgerOpen = action.payload !== undefined ? action.payload : !state.isLedgerOpen;
    },
    clearNotification: (state) => {
      state.successNotification = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Process Complaint Text
      .addCase(processComplaint.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(processComplaint.fulfilled, (state, action) => {
        state.loading = false;
        state.formData = action.payload;
        state.isExtracted = true;
      })
      .addCase(processComplaint.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Upload Document
      .addCase(uploadComplaintDoc.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadComplaintDoc.fulfilled, (state, action) => {
        state.loading = false;
        state.formData = action.payload;
        state.isExtracted = true;
      })
      .addCase(uploadComplaintDoc.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Commit Complaint
      .addCase(commitComplaint.pending, (state) => {
        state.loading = true;
      })
      .addCase(commitComplaint.fulfilled, (state, action) => {
        state.loading = false;
        state.committedLedger.unshift(action.payload);
        state.successNotification = `Complaint #${action.payload.id} successfully committed to QMS Ledger!`;
      })
      .addCase(commitComplaint.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch Ledger
      .addCase(fetchCommittedComplaints.fulfilled, (state, action) => {
        state.committedLedger = action.payload;
      });
  }
});

export const { updateFormField, resetForm, toggleLedgerModal, clearNotification } = complaintSlice.actions;
export default complaintSlice.reducer;
