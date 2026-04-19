import { configureStore } from '@reduxjs/toolkit';
import formReducer from '../features/form/interactionFormSlice';
import chatReducer from '../features/assistant/aiChatSlice';

export const store = configureStore({
  reducer: {
    form: formReducer,
    chat: chatReducer
  }
});
