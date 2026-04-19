const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function parseResponse(response) {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'Request failed');
  }
  return response.json();
}

export async function sendAssistantMessage(payload) {
  const response = await fetch(`${API_BASE_URL}/api/ai/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return parseResponse(response);
}

export async function saveInteraction(payload) {
  const response = await fetch(`${API_BASE_URL}/api/interactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return parseResponse(response);
}

export async function fetchInteraction(interactionId) {
  const response = await fetch(`${API_BASE_URL}/api/interactions/${interactionId}`);
  return parseResponse(response);
}
