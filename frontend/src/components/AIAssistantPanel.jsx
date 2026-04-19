import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { addUserMessage, submitChatMessage } from '../features/assistant/aiChatSlice';

const starterPrompts = [
  'Today I met Dr. Smith and discussed Product X efficacy. Sentiment was positive and I shared brochures.',
  'Correction: the doctor was Dr. John and the sentiment was negative.',
  'Suggest next best actions for this HCP.',
  'I also distributed samples and want a follow up next week.'
];

export default function AIAssistantPanel() {
  const [message, setMessage] = useState('');
  const dispatch = useDispatch();
  const { messages, status, error, lastToolUsed } = useSelector((state) => state.chat);

  const handleSend = (text) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    dispatch(addUserMessage(trimmed));
    setMessage('');
    dispatch(submitChatMessage({ message: trimmed }));
  };

  return (
    <section className="panel assistant-panel">
      <div className="panel-header">
        <div>
          <h2>AI Assistant</h2>
          <p>LangGraph routes your request to CRM tools that populate the form on the left.</p>
        </div>
        {lastToolUsed ? <div className="badge green">Last tool: {lastToolUsed}</div> : null}
      </div>

      <div className="starter-prompts">
        {starterPrompts.map((prompt) => (
          <button key={prompt} className="ghost-btn" onClick={() => handleSend(prompt)}>
            {prompt}
          </button>
        ))}
      </div>

      <div className="chat-thread">
        {messages.map((msg) => (
          <div key={msg.id} className={`chat-bubble ${msg.role}`}>
            <div className="bubble-role">{msg.role === 'assistant' ? 'AI Assistant' : 'You'}</div>
            <div>{msg.content}</div>
          </div>
        ))}
        {status === 'loading' ? <div className="typing">Assistant is thinking...</div> : null}
      </div>

      {error ? <div className="error-box">{error}</div> : null}

      <div className="composer">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Describe an interaction or ask for edits..."
        />
        <button className="primary-btn" onClick={() => handleSend(message)} disabled={status === 'loading'}>
          {status === 'loading' ? 'Working...' : 'Send'}
        </button>
      </div>
    </section>
  );
}
