import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { saveInteraction } from '../../services/assistantApi';

const initialState = {
  id: null,
  hcp_name: '',
  interaction_type: '',
  interaction_date: '',
  interaction_time: '',
  attendees: '',
  topics_discussed: '',
  sentiment: '',
  materials_shared: [],
  samples_distributed: [],
  outcomes: '',
  follow_up_actions: '',
  suggestions: [],
  saveStatus: 'idle',
  saveError: null,
  lastSavedAt: null
};

export const persistInteraction = createAsyncThunk(
  'form/persistInteraction',
  async (_, { getState, rejectWithValue }) => {
    try {
      const form = getState().form;
      const payload = {
        id: form.id,
        hcp_name: form.hcp_name,
        interaction_type: form.interaction_type,
        interaction_date: form.interaction_date || null,
        interaction_time: form.interaction_time || null,
        attendees: form.attendees,
        topics_discussed: form.topics_discussed,
        sentiment: form.sentiment,
        materials_shared: form.materials_shared,
        samples_distributed: form.samples_distributed,
        outcomes: form.outcomes,
        follow_up_actions: form.follow_up_actions,
        suggestions: form.suggestions
      };
      return await saveInteraction(payload);
    } catch (error) {
      return rejectWithValue(error.message || 'Unable to save interaction');
    }
  }
);

const interactionFormSlice = createSlice({
  name: 'form',
  initialState,
  reducers: {
    patchForm(state, action) {
      Object.entries(action.payload || {}).forEach(([key, value]) => {
        if (value !== undefined) {
          state[key] = value;
        }
      });
    },
    setSuggestions(state, action) {
      state.suggestions = action.payload || [];
    },
    resetForm() {
      return initialState;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(persistInteraction.pending, (state) => {
        state.saveStatus = 'loading';
        state.saveError = null;
      })
      .addCase(persistInteraction.fulfilled, (state, action) => {
        state.saveStatus = 'succeeded';
        state.saveError = null;
        state.id = action.payload.id;
        state.lastSavedAt = action.payload.saved_at;
      })
      .addCase(persistInteraction.rejected, (state, action) => {
        state.saveStatus = 'failed';
        state.saveError = action.payload || 'Unable to save interaction';
      });
  }
});

export const { patchForm, setSuggestions, resetForm } = interactionFormSlice.actions;
export default interactionFormSlice.reducer;
