"""Ollama chat client with deterministic offline behavior and typed JSON output."""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Any, Optional, get_args

import httpx
from pydantic import BaseModel, create_model

from app.config import settings
from app.llm.prompts import Classification


class LLMStructuredError(ValueError):
    """The model failed to return a value matching the requested schema."""


class LLMUnavailableError(RuntimeError):
    """The configured local model could not be reached."""


@dataclass(frozen=True)
class LLMResult:
    text: str
    parsed: Any = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    model: str = ""
    llm_calls: int = 0


def _question(messages: list[dict[str, str]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            content = message.get("content", "")
            if "QUESTION:" in content:
                return content.rsplit("QUESTION:", 1)[-1].strip()
            return content
    return ""


def _classification(question: str) -> dict[str, Any]:
    text = question.casefold()
    course = re.search(r"\b([A-Z]{2,3}\d{3})\b", question, re.IGNORECASE)
    self_referential = bool(re.search(r"\b(my|me|i|mine|am i|do i|can i)\b", text))
    if any(part in text for part in ("if i", "what if", "suppose i", "multi-step")) and any(part in text for part in ("placement", "supplementary", "eligible")):
        category = "multi_step"
    elif "eligible" in text or "eligibility" in text:
        category = "personal_eligibility"
    elif self_referential and "supplementary" in text:
        category = "personal_eligibility"
    elif self_referential and any(word in text for word in ("attendance", "result", "grade", "cgpa", "backlog", "profile")):
        category = "personal_data"
    elif any(word in text for word in ("policy", "regulation", "minimum", "requirement", "threshold", "rule")):
        category = "policy_fact"
    elif any(word in text for word in ("apply", "application", "procedure", "how do i", "how to")):
        category = "procedure"
    elif any(word in text for word in ("scholarship", "fee", "course")):
        category = "policy_fact"
    elif "attendance" in text and not self_referential:
        category = "policy_fact"
    else:
        category = "other"
    needs_identity = category in {"personal_data", "personal_eligibility", "multi_step"} and self_referential
    return {"category": category, "course_code": course.group(1).upper() if course else None, "needs_identity": needs_identity}


def _python_type(spec: dict[str, Any]):
    alternatives = spec.get("anyOf") or spec.get("oneOf")
    if alternatives:
        non_null = [item for item in alternatives if item.get("type") != "null"]
        if len(non_null) == 1 and len(non_null) != len(alternatives):
            return Optional[_python_type(non_null[0])]
    schema_type = spec.get("type", "string")
    nullable = isinstance(schema_type, list) and "null" in schema_type
    if isinstance(schema_type, list):
        schema_type = next((value for value in schema_type if value != "null"), "string")
    enum_values = spec.get("enum")
    if enum_values:
        from typing import Literal
        annotation = Literal.__getitem__(tuple(enum_values))
        return Optional[annotation] if nullable else annotation
    if schema_type == "integer":
        annotation = int
    elif schema_type == "number":
        annotation = float
    elif schema_type == "boolean":
        annotation = bool
    elif schema_type == "array":
        annotation = list[Any]
    elif schema_type == "object":
        annotation = dict[str, Any]
    else:
        annotation = str
    return Optional[annotation] if nullable else annotation


def _schema_model(schema: Any) -> tuple[type[BaseModel] | None, dict[str, Any] | None]:
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        return schema, schema.model_json_schema()
    if isinstance(schema, dict):
        # For ordinary object JSON Schemas, build a Pydantic v2 model so values
        # are validated instead of trusting a JSON-only parse.
        properties = schema.get("properties", {})
        if schema.get("type") == "object" and isinstance(properties, dict):
            required = set(schema.get("required", []))
            fields = {
                name: (_python_type(spec), ... if name in required else None)
                for name, spec in properties.items()
            }
            return create_model("RequestedJSONSchema", **fields), schema
    return None, schema if isinstance(schema, dict) else None


def _mock_payload(schema: Any, parsed_model: type[BaseModel] | None, question: str):
    if parsed_model is Classification or (parsed_model and {"category", "course_code", "needs_identity"}.issubset(parsed_model.model_fields)):
        return _classification(question)
    if parsed_model and {"tool", "course_code", "semester"}.issubset(parsed_model.model_fields):
        from app.tools.selection import select_tool
        plan = select_tool(question)
        return {
            "tool": plan["tool"],
            "course_code": plan.get("input", {}).get("course_code"),
            "semester": plan.get("input", {}).get("semester"),
        }
    if parsed_model is None:
        return {}
    payload = {}
    for name, field in parsed_model.model_fields.items():
        if field.default is not None and str(field.default) != "PydanticUndefined":
            payload[name] = field.default
        elif name == "category":
            payload[name] = "other"
        elif name == "course_code":
            payload[name] = None
        elif name == "needs_identity":
            payload[name] = False
        elif field.annotation is bool:
            payload[name] = False
        elif field.annotation is int:
            payload[name] = 0
        elif field.annotation is float:
            payload[name] = 0.0
        elif get_args(field.annotation):
            payload[name] = None
        elif field.annotation is list:
            payload[name] = []
        elif field.annotation is dict:
            payload[name] = {}
        else:
            payload[name] = ""
    return payload


class LLMClient:
    """Synchronous client for Ollama's non-streaming chat endpoint."""

    def __init__(self, *, config=settings, http_client: Any = None, mock: bool | None = None):
        self.config = config
        self.http_client = http_client or httpx.Client(timeout=30.0)
        self.mock = config.MOCK_LLM if mock is None else mock

    def _endpoint(self) -> str:
        root = self.config.OLLAMA_URL.rstrip("/")
        return root + "/chat" if root.endswith("/api") else root + "/api/chat"

    def _remote(self, messages, schema):
        payload = {
            "model": self.config.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0},
        }
        if schema is not None:
            payload["format"] = schema
        try:
            response = self.http_client.post(self._endpoint(), json=payload)
            response.raise_for_status()
            data = response.json()
            return data, str((data.get("message") or {}).get("content", ""))
        except Exception as exc:
            if self.config.CLOUD_FALLBACK:
                raise NotImplementedError("CLOUD_FALLBACK=true, but no cloud provider is implemented.") from exc
            raise LLMUnavailableError("The configured local Ollama service is unavailable.") from exc

    def chat(self, messages, json_schema=None) -> LLMResult:
        """Send messages to Ollama, validating structured results with Pydantic.

        A structured response gets one initial attempt and at most two repair
        attempts. In mock mode no network request is made.
        """
        normalized = [{"role": str(message["role"]), "content": str(message["content"])} for message in messages]
        model, schema = _schema_model(json_schema) if json_schema is not None else (None, None)
        start = time.perf_counter()
        if self.mock:
            question = _question(normalized)
            if json_schema is None:
                text = "I can explain only the facts supplied to me."
                return LLMResult(text, None, 0, 0, round((time.perf_counter() - start) * 1000, 3), self.config.OLLAMA_MODEL)
            payload = _mock_payload(json_schema, model, question)
            try:
                parsed = model.model_validate(payload) if model else payload
            except Exception as exc:
                raise LLMStructuredError("Mock response could not satisfy the requested JSON schema.") from exc
            text = json.dumps(parsed.model_dump() if isinstance(parsed, BaseModel) else parsed, ensure_ascii=False)
            return LLMResult(text, parsed, 0, 0, round((time.perf_counter() - start) * 1000, 3), self.config.OLLAMA_MODEL)

        repair_messages = list(normalized)
        validation_error: Exception | None = None
        prompt_tokens = 0
        completion_tokens = 0
        for attempt in range(3 if json_schema is not None else 1):
            response_data, text = self._remote(repair_messages, schema)
            prompt_tokens += int(response_data.get("prompt_eval_count") or 0)
            completion_tokens += int(response_data.get("eval_count") or 0)
            parsed = None
            if json_schema is not None:
                try:
                    decoded = json.loads(text)
                    parsed = model.model_validate(decoded) if model else decoded
                except Exception as exc:
                    validation_error = exc
                    if attempt < 2:
                        repair_messages = [
                            *repair_messages,
                            {"role": "assistant", "content": text},
                            {"role": "user", "content": "Repair the previous response. Return only valid JSON matching the requested schema. Do not add explanation."},
                        ]
                        continue
                    raise LLMStructuredError("Ollama returned JSON that does not match the requested schema.") from validation_error
            return LLMResult(
                text=text, parsed=parsed,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=round((time.perf_counter() - start) * 1000, 3),
                model=str(response_data.get("model") or self.config.OLLAMA_MODEL),
                llm_calls=attempt + 1,
            )
        raise LLMStructuredError("Ollama returned JSON that does not match the requested schema.")
