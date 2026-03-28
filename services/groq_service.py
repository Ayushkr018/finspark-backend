from groq import Groq
from config import settings
import json, re

client = Groq(api_key=settings.GROQ_API_KEY)

def _clean_json(text: str) -> str:
    """Strip markdown code fences and return raw JSON."""
    text = re.sub(r"```(?:json)?", "", text).strip()
    text = text.rstrip("`").strip()
    return text

def parse_document_with_ai(document_text: str) -> dict:
    prompt = f"""You are an expert enterprise integration architect. Analyze the following BRD/SOW document and extract structured integration requirements.

DOCUMENT:
{document_text[:6000]}

Return ONLY valid JSON (no markdown, no explanation) with this exact schema:
{{
  "project_name": "string",
  "summary": "string (2-3 sentences)",
  "detected_services": [
    {{
      "service_name": "string",
      "category": "Credit Bureau | KYC | GST | Payment Gateway | Fraud Detection | Open Banking",
      "is_mandatory": true,
      "confidence": 0.95,
      "mentioned_fields": ["field1", "field2"],
      "notes": "string"
    }}
  ],
  "recommended_adapters": ["adapter-id-1", "adapter-id-2"],
  "integration_flow": "string describing the overall flow",
  "estimated_complexity": "Low | Medium | High",
  "warnings": ["any compliance or version concerns"]
}}"""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2048,
    )
    raw = _clean_json(response.choices[0].message.content)
    return json.loads(raw)


def generate_config_with_ai(adapter: dict, requirements: dict, tenant_id: str) -> dict:
    prompt = f"""You are an enterprise integration engineer. Generate a complete production-ready configuration for this adapter based on the requirements.

ADAPTER: {json.dumps(adapter, indent=2)}
REQUIREMENTS: {json.dumps(requirements, indent=2)}
TENANT_ID: {tenant_id}

Return ONLY valid JSON (no markdown) with this schema:
{{
  "field_mappings": [
    {{
      "source_field": "string (from requirement doc)",
      "target_field": "string (adapter expected field)",
      "transformation": "direct | uppercase | date_format | mask_last4 | hash",
      "is_required": true,
      "default_value": null,
      "notes": "string"
    }}
  ],
  "auth_config": {{
    "type": "API_KEY | OAUTH2 | BASIC_AUTH",
    "key_placeholder": "VAULT:{{tenant_id}}/{{adapter_id}}/api_key",
    "token_url": "string or null",
    "scopes": []
  }},
  "retry_config": {{
    "max_retries": 3,
    "backoff_ms": 500,
    "timeout_ms": 5000
  }},
  "webhook_config": {{
    "enabled": false,
    "url": "/webhooks/{{tenant_id}}/{{adapter_id}}",
    "events": []
  }},
  "environment_overrides": {{
    "sandbox": {{"base_url": "https://sandbox.example.com"}},
    "production": {{"base_url": "https://api.example.com"}}
  }},
  "compliance_flags": {{
    "pii_masking_enabled": true,
    "consent_required": true,
    "data_retention_days": 90
  }},
  "config_version": "1.0.0",
  "ai_confidence_score": 0.92
}}"""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2048,
    )
    raw = _clean_json(response.choices[0].message.content)
    return json.loads(raw)


def generate_mock_response(adapter: dict, endpoint: dict) -> dict:
    prompt = f"""Generate a realistic mock API response for this enterprise integration endpoint.

ADAPTER: {adapter['name']} ({adapter['category']})
ENDPOINT: {endpoint['method']} {endpoint['path']} — {endpoint['description']}

Return ONLY valid JSON (no markdown) with:
{{
  "status": "success",
  "http_status_code": 200,
  "response_time_ms": 342,
  "response_body": {{ ... realistic response data ... }},
  "headers": {{"Content-Type": "application/json", "X-Request-ID": "abc123"}},
  "notes": "string describing what this response means"
}}"""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024,
    )
    raw = _clean_json(response.choices[0].message.content)
    return json.loads(raw)
