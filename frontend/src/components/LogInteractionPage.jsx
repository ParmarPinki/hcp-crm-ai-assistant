import React from 'react';
import InteractionFormPanel from './InteractionFormPanel';
import AIAssistantPanel from './AIAssistantPanel';

export default function LogInteractionPage() {
  return (
    <div className="page-shell">
      <div className="topbar">
        <div>
          <div className="eyebrow">AI-First CRM</div>
          <h1>Log HCP Interaction</h1>
          <p>Use the AI assistant to populate and edit the interaction form. The form is read-only by design.</p>
        </div>
        <div className="status-chip">React + Redux + FastAPI + LangGraph + Groq + MySQL</div>
      </div>
      <div className="split-layout">
        <InteractionFormPanel />
        <AIAssistantPanel />
      </div>
    </div>
  );
}
