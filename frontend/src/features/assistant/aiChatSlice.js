import { createAsyncThunk, createSlice, nanoid } from '@reduxjs/toolkit';
import { sendAssistantMessage } from '../../services/assistantApi';
import { patchForm, setSuggestions } from '../form/interactionFormSlice';

const initialState = {
  sessionId: crypto.randomUUID ? crypto.randomUUID() : `session-${Date.now()}`,
  messages: [
    {
      id: nanoid(),
      role: 'assistant',
      content: 'Hi! Describe the HCP interaction here. I will use LangGraph tools to populate the CRM form on the left.',
      timestamp: new Date().toISOString()
    }
  ],
  status: 'idle',
  error: null,
  lastToolUsed: null
};

export const submitChatMessage = createAsyncThunk(
  'chat/submitChatMessage',
  async ({ message }, { getState, dispatch, rejectWithValue }) => {
    try {
      const state = getState();
      const payload = {
        session_id: state.chat.sessionId,
        message,
        current_form: state.form,
        chat_history: state.chat.messages.map((item) => ({
          role: item.role,
          content: item.content,
          timestamp: item.timestamp
        }))
      };
      const response = await sendAssistantMessage(payload);
      dispatch(patchForm(response.form_patch));
      dispatch(setSuggestions(response.suggestions || []));
      return response;
    } catch (error) {
      return rejectWithValue(error.message || 'Assistant request failed');
    }
  }
);

const aiChatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addUserMessage: {
      reducer(state, action) {
        state.messages.push(action.payload);
      },
      prepare(content) {
        return {
          payload: {
            id: nanoid(),
            role: 'user',
            content,
            timestamp: new Date().toISOString()
          }
        };
      }
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitChatMessage.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(submitChatMessage.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.lastToolUsed = action.payload.tool_used;
        state.messages.push({
          id: nanoid(),
          role: 'assistant',
          content: action.payload.assistant_message,
          timestamp: new Date().toISOString()
        });
      })
      .addCase(submitChatMessage.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Assistant request failed';
      });
  }
});

export const { addUserMessage } = aiChatSlice.actions;
export default aiChatSlice.reducer;
