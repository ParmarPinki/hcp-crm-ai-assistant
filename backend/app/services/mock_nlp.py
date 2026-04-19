import re
from datetime import datetime

SENTIMENTS = ['positive', 'neutral', 'negative']
MATERIAL_KEYWORDS = ['brochure', 'brochures', 'leaflet', 'pdf', 'deck', 'slide']
SAMPLE_KEYWORDS = ['sample', 'samples', 'starter pack']


def infer_patch_from_text(message: str, current_form: dict | None = None) -> dict:
    current_form = current_form or {}
    patch = {}
    lower = message.lower()

    name_match = re.search(r'(dr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message)
    if name_match:
        patch['hcp_name'] = name_match.group(1).replace('Dr ', 'Dr. ').replace('Dr..', 'Dr.')

    if 'today' in lower and not current_form.get('interaction_date'):
        patch['interaction_date'] = datetime.now().strftime('%Y-%m-%d')

    time_match = re.search(r'(\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?)', message)
    if time_match:
        patch['interaction_time'] = time_match.group(1).upper()

    if 'call' in lower:
        patch['interaction_type'] = 'Call'
    elif 'email' in lower:
        patch['interaction_type'] = 'Email'
    elif 'conference' in lower:
        patch['interaction_type'] = 'Conference'
    elif any(token in lower for token in ['met', 'visit', 'meeting']):
        patch['interaction_type'] = 'In-person Visit'

    for sentiment in SENTIMENTS:
        if sentiment in lower:
            patch['sentiment'] = sentiment
            break

    materials = [keyword.title() for keyword in MATERIAL_KEYWORDS if keyword in lower]
    if materials:
        patch['materials_shared'] = sorted(set(materials))

    samples = [keyword.title() for keyword in SAMPLE_KEYWORDS if keyword in lower]
    if samples:
        patch['samples_distributed'] = sorted(set(samples))

    discussed_match = re.search(r'discussed\s+(.+?)(?:\.|,| and | sentiment| shared|$)', lower)
    if discussed_match:
        patch['topics_discussed'] = discussed_match.group(1).strip().capitalize()

    if 'follow up' in lower or 'next step' in lower or 'next week' in lower:
        patch['follow_up_actions'] = 'Follow up requested by field rep.'

    if 'outcome' in lower:
        outcome_match = re.search(r'outcome(?:s)?\s*(?:was|were|:)?\s*(.+)', message, re.IGNORECASE)
        if outcome_match:
            patch['outcomes'] = outcome_match.group(1).strip()

    return patch
