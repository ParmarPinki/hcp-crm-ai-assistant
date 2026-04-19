# import json
# from typing import Any, Dict

# from app.core.config import settings
# from app.services.mock_nlp import infer_patch_from_text

# try:
#     from langchain_groq import ChatGroq
# except Exception:
#     ChatGroq = None


# class LLMService:
#     def __init__(self):
#         self.client = None
#         if settings.groq_api_key and ChatGroq is not None:
#             self.client = ChatGroq(
#                 groq_api_key=settings.groq_api_key,
#                 model_name=settings.model_name,
#                 temperature=0
#             )

#     def structured_extract(self, user_message: str, current_form: Dict[str, Any], intent: str) -> Dict[str, Any]:
#         if self.client is None:
#             if settings.allow_mock_llm:
#                 return infer_patch_from_text(user_message, current_form)
#             raise RuntimeError('Groq API key is missing and mock mode is disabled.')

#         system_prompt = (
#             'You are an AI CRM assistant for life-science field reps. '
#             'Return valid JSON only with a top-level key named patch. '
#             'Extract only supported fields: hcp_name, interaction_type, interaction_date, interaction_time, '
#             'attendees, topics_discussed, sentiment, materials_shared, samples_distributed, outcomes, follow_up_actions. '
#             'If intent is edit_interaction, return only changed fields. Do not hallucinate missing values.'
#         )
#         user_prompt = json.dumps({
#             'intent': intent,
#             'current_form': current_form,
#             'user_message': user_message
#         })
#         response = self.client.invoke([
#             ('system', system_prompt),
#             ('human', user_prompt)
#         ])
#         content = response.content if hasattr(response, 'content') else str(response)

#         print("RAW LLM CONTENT....................:", repr(content))
#         parsed = json.loads(content)
#         return parsed.get('patch', {})


# llm_service = LLMService()



# import json
# import re
# from typing import Any, Dict

# from app.core.config import settings
# from app.services.mock_nlp import infer_patch_from_text

# try:
#     from langchain_groq import ChatGroq
# except Exception:
#     ChatGroq = None


# from datetime import datetime, timedelta

# def _normalize_relative_date(value: str) -> str:
#     if not value:
#         return ""

#     v = str(value).strip().lower()
#     today = datetime.today().date()

#     if v == "today":
#         return today.isoformat()
#     if v == "tomorrow":
#         return (today + timedelta(days=1)).isoformat()
#     if v == "yesterday":
#         return (today - timedelta(days=1)).isoformat()

#     return value

# class LLMService:
#     def __init__(self):
#         self.client = None
#         if settings.groq_api_key and ChatGroq is not None:
#             self.client = ChatGroq(
#                 groq_api_key=settings.groq_api_key,
#                 model_name=settings.model_name,
#                 temperature=0
#             )

#     def _extract_json_object(self, text: str) -> Dict[str, Any]:
#         if not text or not str(text).strip():
#             raise ValueError("LLM returned empty content")

#         text = str(text).strip()

#         # Case 1: JSON inside ```json ... ```
#         fenced_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
#         if fenced_match:
#             return json.loads(fenced_match.group(1))

#         # Case 2: JSON inside generic ``` ... ```
#         generic_fenced_match = re.search(r"```\s*(\{.*?\})\s*```", text, re.DOTALL)
#         if generic_fenced_match:
#             return json.loads(generic_fenced_match.group(1))

#         # Case 3: Whole response is already JSON
#         try:
#             return json.loads(text)
#         except json.JSONDecodeError:
#             pass

#         # Case 4: Response has extra text before/after JSON, extract first JSON object
#         start = text.find("{")
#         end = text.rfind("}")
#         if start != -1 and end != -1 and end > start:
#             candidate = text[start:end + 1]
#             return json.loads(candidate)

#         raise ValueError(f"No valid JSON object found in LLM response: {text}")

#     def _normalize_patch(self, patch: Dict[str, Any]) -> Dict[str, Any]:
#         if not isinstance(patch, dict):
#             return {}

#         interaction_type = patch.get("interaction_type", "")
#         if isinstance(interaction_type, str) and interaction_type:
#             interaction_type = interaction_type.title()

#         sentiment = patch.get("sentiment", "")
#         if isinstance(sentiment, str):
#             sentiment = sentiment.lower()

#         return {
#             "hcp_name": patch.get("hcp_name", ""),
#             "interaction_type": interaction_type,
#             "interaction_date": _normalize_relative_date(patch.get("interaction_date", patch.get("date", ""))),
#             "interaction_time": patch.get("interaction_time", patch.get("time", "")),
#             "attendees": patch.get("attendees", ""),
#             "topics_discussed": patch.get("topics_discussed", ""),
#             "sentiment": sentiment,
#             "materials_shared": patch.get("materials_shared", []),
#             "samples_distributed": patch.get("samples_distributed", []),
#             "outcomes": patch.get("outcomes", ""),
#             "follow_up_actions": patch.get("follow_up_actions", "")
#         }

#     def structured_extract(self, user_message: str, current_form: Dict[str, Any], intent: str) -> Dict[str, Any]:
#         if self.client is None:
#             if settings.allow_mock_llm:
#                 return infer_patch_from_text(user_message, current_form)
#             raise RuntimeError("Groq API key is missing and mock mode is disabled.")

#         system_prompt = (
#             "You are an AI CRM assistant for life-science field reps. "
#             "Return ONLY valid JSON. "
#             "Do not wrap JSON in markdown code fences. "
#             "Do not add notes, explanations, or extra text before or after the JSON. "
#             "Return a top-level JSON object with a single key named 'patch'. "
#             "Extract only these supported fields inside patch: "
#             "hcp_name, interaction_type, interaction_date, interaction_time, "
#             "attendees, topics_discussed, sentiment, materials_shared, "
#             "samples_distributed, outcomes, follow_up_actions. "
#             "If intent is edit_interaction, return only changed fields inside patch. "
#             "Do not hallucinate missing values. "
#             "Sentiment must be one of: positive, neutral, negative. "
#             "interaction_type should be one of: Meeting, Call, Email, Conference, Other when inferable."
#         )

#         user_prompt = json.dumps({
#             "intent": intent,
#             "current_form": current_form,
#             "user_message": user_message
#         })

#         response = self.client.invoke([
#             ("system", system_prompt),
#             ("human", user_prompt)
#         ])

#         content = response.content if hasattr(response, "content") else str(response)
#         print("RAW LLM CONTENT....................:", repr(content))

#         try:
#             parsed = self._extract_json_object(content)
#             patch = parsed.get("patch", {}) if isinstance(parsed, dict) else {}
#             return self._normalize_patch(patch)
#         except Exception as e:
#             print("LLM JSON PARSE ERROR:", str(e))
#             print("FAILING CONTENT:", repr(content))

#             if settings.allow_mock_llm:
#                 print("Falling back to mock NLP parser...")
#                 return infer_patch_from_text(user_message, current_form)

#             raise


# llm_service = LLMService()



# -----------------------v3

# import json
# import re
# from datetime import datetime, timedelta
# from typing import Any, Dict

# from app.core.config import settings
# from app.services.mock_nlp import infer_patch_from_text

# try:
#     from langchain_groq import ChatGroq
# except Exception:
#     ChatGroq = None


# class LLMService:
#     def __init__(self):
#         self.client = None
#         if settings.groq_api_key and ChatGroq is not None:
#             self.client = ChatGroq(
#                 groq_api_key=settings.groq_api_key,
#                 model_name=settings.model_name,
#                 temperature=0
#             )

#     def _extract_json_object(self, text: str) -> Dict[str, Any]:
#         if not text or not str(text).strip():
#             raise ValueError("LLM returned empty content")

#         text = str(text).strip()

#         fenced_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
#         if fenced_match:
#             return json.loads(fenced_match.group(1))

#         generic_fenced_match = re.search(r"```\s*(\{.*?\})\s*```", text, re.DOTALL)
#         if generic_fenced_match:
#             return json.loads(generic_fenced_match.group(1))

#         try:
#             return json.loads(text)
#         except json.JSONDecodeError:
#             pass

#         start = text.find("{")
#         end = text.rfind("}")
#         if start != -1 and end != -1 and end > start:
#             candidate = text[start:end + 1]
#             return json.loads(candidate)

#         raise ValueError(f"No valid JSON object found in LLM response: {text}")

#     def _normalize_relative_date(self, value: str) -> str:
#         if not value:
#             return ""

#         v = str(value).strip().lower()
#         today = datetime.today().date()

#         if v == "today":
#             return today.isoformat()
#         if v == "tomorrow":
#             return (today + timedelta(days=1)).isoformat()
#         if v == "yesterday":
#             return (today - timedelta(days=1)).isoformat()

#         return value

#     def _normalize_patch(self, patch: Dict[str, Any]) -> Dict[str, Any]:
#         if not isinstance(patch, dict):
#             return {}

#         normalized = {}

#         if "hcp_name" in patch:
#             normalized["hcp_name"] = patch.get("hcp_name")

#         if "interaction_type" in patch:
#             interaction_type = patch.get("interaction_type")
#             if isinstance(interaction_type, str) and interaction_type:
#                 interaction_type = interaction_type.title()
#             normalized["interaction_type"] = interaction_type

#         if "interaction_date" in patch or "date" in patch:
#             interaction_date = patch.get("interaction_date", patch.get("date", ""))
#             normalized["interaction_date"] = self._normalize_relative_date(interaction_date)

#         if "interaction_time" in patch or "time" in patch:
#             normalized["interaction_time"] = patch.get("interaction_time", patch.get("time", ""))

#         if "attendees" in patch:
#             normalized["attendees"] = patch.get("attendees")

#         if "topics_discussed" in patch:
#             normalized["topics_discussed"] = patch.get("topics_discussed")

#         if "sentiment" in patch:
#             sentiment = patch.get("sentiment")
#             if isinstance(sentiment, str):
#                 sentiment = sentiment.lower()
#             normalized["sentiment"] = sentiment

#         if "materials_shared" in patch:
#             normalized["materials_shared"] = patch.get("materials_shared", [])

#         if "samples_distributed" in patch:
#             normalized["samples_distributed"] = patch.get("samples_distributed", [])

#         if "outcomes" in patch:
#             normalized["outcomes"] = patch.get("outcomes")

#         if "follow_up_actions" in patch:
#             normalized["follow_up_actions"] = patch.get("follow_up_actions")

#         return normalized

#     def structured_extract(self, user_message: str, current_form: Dict[str, Any], intent: str) -> Dict[str, Any]:
#         if self.client is None:
#             if settings.allow_mock_llm:
#                 return infer_patch_from_text(user_message, current_form)
#             raise RuntimeError("Groq API key is missing and mock mode is disabled.")

#         system_prompt = (
#             "You are an AI CRM assistant for life-science field reps. "
#             "Return ONLY valid JSON. "
#             "Do not wrap JSON in markdown code fences. "
#             "Do not add notes, explanations, or extra text before or after the JSON. "
#             "Return a top-level JSON object with a single key named 'patch'. "
#             "Extract only these supported fields inside patch: "
#             "hcp_name, interaction_type, interaction_date, interaction_time, "
#             "attendees, topics_discussed, sentiment, materials_shared, "
#             "samples_distributed, outcomes, follow_up_actions. "
#             "If intent is edit_interaction, return ONLY the changed fields inside patch. "
#             "Do not include unchanged fields. "
#             "Do not hallucinate missing values. "
#             "Sentiment must be one of: positive, neutral, negative. "
#             "interaction_type should be one of: Meeting, Call, Email, Conference, Other when inferable."
#         )

#         user_prompt = json.dumps({
#             "intent": intent,
#             "current_form": current_form,
#             "user_message": user_message
#         })

#         response = self.client.invoke([
#             ("system", system_prompt),
#             ("human", user_prompt)
#         ])

#         content = response.content if hasattr(response, "content") else str(response)
#         print("RAW LLM CONTENT....................:", repr(content))

#         try:
#             parsed = self._extract_json_object(content)
#             patch = parsed.get("patch", {}) if isinstance(parsed, dict) else {}
#             return self._normalize_patch(patch)
#         except Exception as e:
#             print("LLM JSON PARSE ERROR:", str(e))
#             print("FAILING CONTENT:", repr(content))

#             if settings.allow_mock_llm:
#                 print("Falling back to mock NLP parser...")
#                 return infer_patch_from_text(user_message, current_form)

#             raise


# llm_service = LLMService()


#--------------------------v4

import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict

from app.core.config import settings
from app.services.mock_nlp import infer_patch_from_text

try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None


class LLMService:
    def __init__(self):
        self.client = None
        if settings.groq_api_key and ChatGroq is not None:
            self.client = ChatGroq(
                groq_api_key=settings.groq_api_key,
                model_name=settings.model_name,
                temperature=0
            )

    def _extract_json_object(self, text: str) -> Dict[str, Any]:
        if not text or not str(text).strip():
            raise ValueError("LLM returned empty content")

        text = str(text).strip()

        fenced_match = re.search(
            r"```json\s*(\{.*?\})\s*```",
            text,
            re.DOTALL | re.IGNORECASE
        )
        if fenced_match:
            return json.loads(fenced_match.group(1))

        generic_fenced_match = re.search(
            r"```\s*(\{.*?\})\s*```",
            text,
            re.DOTALL
        )
        if generic_fenced_match:
            return json.loads(generic_fenced_match.group(1))

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            return json.loads(candidate)

        raise ValueError(f"No valid JSON object found in LLM response: {text}")

    def _normalize_relative_date(self, value: str) -> str:
        if not value:
            return ""

        v = str(value).strip().lower()
        today = datetime.today().date()

        if v == "today":
            return today.isoformat()
        if v == "tomorrow":
            return (today + timedelta(days=1)).isoformat()
        if v == "yesterday":
            return (today - timedelta(days=1)).isoformat()

        return value

    def _normalize_patch(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(patch, dict):
            return {}

        normalized = {}

        if "hcp_name" in patch:
            normalized["hcp_name"] = patch.get("hcp_name")

        if "interaction_type" in patch:
            interaction_type = patch.get("interaction_type")
            if isinstance(interaction_type, str) and interaction_type:
                interaction_type = interaction_type.title()
            normalized["interaction_type"] = interaction_type

        if "interaction_date" in patch or "date" in patch:
            interaction_date = patch.get("interaction_date", patch.get("date", ""))
            normalized["interaction_date"] = self._normalize_relative_date(interaction_date)

        if "interaction_time" in patch or "time" in patch:
            normalized["interaction_time"] = patch.get("interaction_time", patch.get("time", ""))

        if "attendees" in patch:
            normalized["attendees"] = patch.get("attendees")

        if "topics_discussed" in patch:
            normalized["topics_discussed"] = patch.get("topics_discussed")

        if "sentiment" in patch:
            sentiment = patch.get("sentiment")
            if isinstance(sentiment, str):
                sentiment = sentiment.lower()
            normalized["sentiment"] = sentiment

        if "materials_shared" in patch:
            normalized["materials_shared"] = patch.get("materials_shared", [])

        if "samples_distributed" in patch:
            normalized["samples_distributed"] = patch.get("samples_distributed", [])

        if "outcomes" in patch:
            normalized["outcomes"] = patch.get("outcomes")

        if "follow_up_actions" in patch:
            normalized["follow_up_actions"] = patch.get("follow_up_actions")

        return normalized

    def _apply_edit_smart_sync(
        self,
        normalized_patch: Dict[str, Any],
        current_form: Dict[str, Any],
        intent: str
    ) -> Dict[str, Any]:
        if intent != "edit_interaction":
            return normalized_patch

        old_hcp = (current_form.get("hcp_name") or "").strip()
        new_hcp = (normalized_patch.get("hcp_name") or "").strip()
        current_attendees = (current_form.get("attendees") or "").strip()

        if (
            new_hcp
            and old_hcp
            and new_hcp != old_hcp
            and "attendees" not in normalized_patch
            and current_attendees == old_hcp
        ):
            normalized_patch["attendees"] = new_hcp

        return normalized_patch

    def structured_extract(
        self,
        user_message: str,
        current_form: Dict[str, Any],
        intent: str
    ) -> Dict[str, Any]:
        if self.client is None:
            if settings.allow_mock_llm:
                return infer_patch_from_text(user_message, current_form)
            raise RuntimeError("Groq API key is missing and mock mode is disabled.")

        system_prompt = (
            "You are an AI CRM assistant for life-science field reps. "
            "Return ONLY valid JSON. "
            "Do not wrap JSON in markdown code fences. "
            "Do not add notes, explanations, or extra text before or after the JSON. "
            "Return a top-level JSON object with a single key named 'patch'. "
            "Extract only these supported fields inside patch: "
            "hcp_name, interaction_type, interaction_date, interaction_time, "
            "attendees, topics_discussed, sentiment, materials_shared, "
            "samples_distributed, outcomes, follow_up_actions. "
            "If intent is edit_interaction, return ONLY the changed fields inside patch. "
            "Do not include unchanged fields. "
            "If the corrected HCP name also implies the attendees field should change, include attendees as well. "
            "Do not hallucinate missing values. "
            "Sentiment must be one of: positive, neutral, negative. "
            "interaction_type should be one of: Meeting, Call, Email, Conference, Other when inferable."
        )

        user_prompt = json.dumps({
            "intent": intent,
            "current_form": current_form,
            "user_message": user_message
        })

        response = self.client.invoke([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        content = response.content if hasattr(response, "content") else str(response)
        print("RAW LLM CONTENT....................:", repr(content))

        try:
            parsed = self._extract_json_object(content)
            patch = parsed.get("patch", {}) if isinstance(parsed, dict) else {}
            normalized_patch = self._normalize_patch(patch)
            normalized_patch = self._apply_edit_smart_sync(
                normalized_patch,
                current_form,
                intent
            )
            return normalized_patch
        except Exception as e:
            print("LLM JSON PARSE ERROR:", str(e))
            print("FAILING CONTENT:", repr(content))

            if settings.allow_mock_llm:
                print("Falling back to mock NLP parser...")
                return infer_patch_from_text(user_message, current_form)

            raise


llm_service = LLMService()

