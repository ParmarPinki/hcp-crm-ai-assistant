import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { persistInteraction, resetForm } from '../features/form/interactionFormSlice';

function Field({ label, value, multiline = false, pills = false }) {
  return (
    <div className="field-block">
      <label>{label}</label>
      {pills ? (
        <div className="pill-wrap">
          {(value || []).length ? (value || []).map((item) => <span className="pill" key={item}>{item}</span>) : <span className="placeholder">No value captured yet</span>}
        </div>
      ) : multiline ? (
        <textarea readOnly value={value || ''} placeholder="Will be filled by AI" />
      ) : (
        <input readOnly value={value || ''} placeholder="Will be filled by AI" />
      )}
    </div>
  );
}

export default function InteractionFormPanel() {
  const dispatch = useDispatch();
  const form = useSelector((state) => state.form);

  return (
    <section className="panel form-panel">
      <div className="panel-header">
        <div>
          <h2>Interaction Details</h2>
          <p>AI-generated structured summary for CRM logging</p>
        </div>
        <div className="badge">Read only</div>
      </div>

      <div className="form-grid two-col">
        <Field label="HCP Name" value={form.hcp_name} />
        <Field label="Interaction Type" value={form.interaction_type} />
        <Field label="Date" value={form.interaction_date} />
        <Field label="Time" value={form.interaction_time} />
      </div>

      <div className="form-grid one-col">
        <Field label="Attendees" value={form.attendees} />
        <Field label="Topics Discussed" value={form.topics_discussed} multiline />
      </div>

      <div className="form-grid two-col">
        <Field label="Materials Shared" value={form.materials_shared} pills />
        <Field label="Samples Distributed" value={form.samples_distributed} pills />
      </div>

      <div className="form-grid two-col">
        <Field label="Sentiment" value={form.sentiment} />
        <Field label="Outcomes" value={form.outcomes} multiline />
      </div>

      <div className="form-grid one-col">
        <Field label="Follow-up Actions" value={form.follow_up_actions} multiline />
      </div>

      <div className="suggestion-box">
        <h3>AI Suggestions</h3>
        {form.suggestions?.length ? (
          <ul>
            {form.suggestions.map((item) => <li key={item}>{item}</li>)}
          </ul>
        ) : (
          <p>No follow-up suggestions yet.</p>
        )}
      </div>

      <div className="actions-row">
        <button
          className="primary-btn"
          onClick={() => dispatch(persistInteraction())}
          disabled={form.saveStatus === 'loading'}
        >
          {form.saveStatus === 'loading' ? 'Saving...' : 'Save Interaction'}
        </button>
        <button className="secondary-btn" onClick={() => dispatch(resetForm())}>Reset Draft</button>
      </div>

      {form.saveStatus === 'succeeded' && form.lastSavedAt ? (
        <div className="success-box">Saved to MySQL-backed API at {new Date(form.lastSavedAt).toLocaleString()}.</div>
      ) : null}
      {form.saveError ? <div className="error-box">{form.saveError}</div> : null}
    </section>
  );
}
