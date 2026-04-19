from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, StateGraph

from app.services.llm_service import llm_service


class AgentState(TypedDict, total=False):
    session_id: str
    user_message: str
    current_form: Dict[str, Any]
    intent: str
    tool_used: str
    form_patch: Dict[str, Any]
    suggestions: List[str]
    assistant_message: str


def route_intent(state: AgentState) -> AgentState:
    message = state['user_message'].lower()
    if any(keyword in message for keyword in ['correction', 'actually', 'update', 'change', 'sorry']):
        state['intent'] = 'edit_interaction'
    elif any(keyword in message for keyword in ['suggest', 'next best', 'follow-up', 'follow up']):
        state['intent'] = 'suggest_follow_up'
    else:
        state['intent'] = 'log_interaction'
    return state


def log_interaction_tool(state: AgentState) -> AgentState:
    patch = llm_service.structured_extract(state['user_message'], state.get('current_form', {}), 'log_interaction')
    state['tool_used'] = 'log_interaction'
    state['form_patch'] = patch
    return state


def edit_interaction_tool(state: AgentState) -> AgentState:
    patch = llm_service.structured_extract(state['user_message'], state.get('current_form', {}), 'edit_interaction')
    state['tool_used'] = 'edit_interaction'
    state['form_patch'] = patch
    return state


# def resolve_hcp_tool(state: AgentState) -> AgentState:
#     patch = state.get('form_patch', {})
#     if patch.get('hcp_name'):
#         normalized = patch['hcp_name'].replace('  ', ' ').strip()
#         patch['hcp_name'] = normalized
#     state['form_patch'] = patch
#     return state

def resolve_hcp_tool(state: AgentState) -> AgentState:
    patch = state.get('form_patch', {}) or {}
    current_form = state.get('current_form', {}) or {}

    def normalize_person_name(name: str) -> str:
        if not name:
            return ""

        normalized = " ".join(str(name).split()).strip()
        lower_name = normalized.lower()

        if normalized and not lower_name.startswith("dr."):
            if lower_name.startswith("dr "):
                normalized = "Dr. " + normalized[3:].strip()
            else:
                normalized = "Dr. " + normalized

        words = normalized.split()
        normalized_words = []
        for i, word in enumerate(words):
            if i == 0 and word.lower() in ["dr.", "dr"]:
                normalized_words.append("Dr.")
            else:
                normalized_words.append(word.capitalize())

        return " ".join(normalized_words)

    old_hcp_name = (current_form.get("hcp_name") or "").strip()
    old_attendees = (current_form.get("attendees") or "").strip()

    # Normalize HCP name
    if patch.get("hcp_name"):
        patch["hcp_name"] = normalize_person_name(patch["hcp_name"])

    # Normalize attendees if present in patch
    if patch.get("attendees"):
        patch["attendees"] = normalize_person_name(patch["attendees"])

    # If attendees not explicitly present, but old attendees mirrored old HCP,
    # keep them in sync with new HCP name
    if "attendees" not in patch:
        new_hcp_name = (patch.get("hcp_name") or "").strip()
        if old_attendees and old_hcp_name and old_attendees == old_hcp_name:
            patch["attendees"] = new_hcp_name

    state["form_patch"] = patch
    return state

def search_materials_tool(state: AgentState) -> AgentState:
    patch = state.get('form_patch', {})
    normalized = []
    for material in patch.get('materials_shared', []):
        label = material.lower()
        if 'brochure' in label:
            normalized.append('Approved Brochure')
        elif 'pdf' in label:
            normalized.append('Clinical PDF')
        elif 'deck' in label or 'slide' in label:
            normalized.append('Efficacy Deck')
        else:
            normalized.append(material)
    if normalized:
        patch['materials_shared'] = sorted(set(normalized))
    state['form_patch'] = patch
    return state


def suggest_follow_up_tool(state: AgentState) -> AgentState:
    form = {**state.get('current_form', {}), **state.get('form_patch', {})}
    suggestions = []
    topic = form.get('topics_discussed')
    sentiment = (form.get('sentiment') or '').lower()
    if topic:
        suggestions.append(f'Send approved follow-up material for: {topic}.')
    if sentiment == 'positive':
        suggestions.append('Schedule a follow-up visit in 2 weeks.')
    elif sentiment == 'negative':
        suggestions.append('Capture objections and plan targeted re-engagement.')
    else:
        suggestions.append('Ask one more qualifying question before closing the interaction.')
    suggestions.append('Review whether a medical science liaison follow-up is needed.')
    state['suggestions'] = suggestions
    if state.get('intent') == 'suggest_follow_up':
        state['tool_used'] = 'suggest_follow_up'
    return state


def finalize_response(state: AgentState) -> AgentState:
    tool_used = state.get('tool_used', 'log_interaction')
    patch = state.get('form_patch', {})
    if tool_used == 'edit_interaction':
        assistant_message = 'Updated the interaction form using the edit_interaction tool.'
    elif tool_used == 'suggest_follow_up':
        assistant_message = 'I reviewed the interaction and generated next best actions.'
    else:
        assistant_message = 'I logged the interaction and populated the form using AI.'

    if not patch and tool_used != 'suggest_follow_up':
        assistant_message = 'I could not extract structured fields confidently. Try adding more detail.'

    state['assistant_message'] = assistant_message
    return state


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node('route_intent', route_intent)
    graph.add_node('log_interaction_tool', log_interaction_tool)
    graph.add_node('edit_interaction_tool', edit_interaction_tool)
    graph.add_node('resolve_hcp_tool', resolve_hcp_tool)
    graph.add_node('search_materials_tool', search_materials_tool)
    graph.add_node('suggest_follow_up_tool', suggest_follow_up_tool)
    graph.add_node('finalize_response', finalize_response)

    graph.set_entry_point('route_intent')

    def router(state: AgentState):
        return state.get('intent', 'log_interaction')

    graph.add_conditional_edges(
        'route_intent',
        router,
        {
            'log_interaction': 'log_interaction_tool',
            'edit_interaction': 'edit_interaction_tool',
            'suggest_follow_up': 'suggest_follow_up_tool'
        }
    )

    graph.add_edge('log_interaction_tool', 'resolve_hcp_tool')
    graph.add_edge('edit_interaction_tool', 'resolve_hcp_tool')
    graph.add_edge('resolve_hcp_tool', 'search_materials_tool')
    graph.add_edge('search_materials_tool', 'suggest_follow_up_tool')
    graph.add_edge('suggest_follow_up_tool', 'finalize_response')
    graph.add_edge('finalize_response', END)
    return graph.compile()


graph_app = build_graph()
