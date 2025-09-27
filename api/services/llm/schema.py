# api/services/llm/schema.py
from api.core.schemas import SummaryIn, SummaryOut  # Assume Pydantic models are defined here

# Original schema (for existing system)
JSON_SCHEMA = {
  "name": "summary", "strict": True,
  "schema": { "type":"object", "properties": {
    "hpi":{"type":"string"},
    "ros":{"type":"object","properties":{
      "cardiovascular":{"type":"object","properties":{
        "positive":{"type":"array","items":{"type":"string"}},
        "negative":{"type":"array","items":{"type":"string"}}},
        "required":["positive","negative"],"additionalProperties":False},
      "respiratory":{"type":"object","properties":{
        "positive":{"type":"array","items":{"type":"string"}},
        "negative":{"type":"array","items":{"type":"string"}}},
        "required":["positive","negative"],"additionalProperties":False},
      "constitutional":{"type":"object","properties":{
        "positive":{"type":"array","items":{"type":"string"}},
        "negative":{"type":"array","items":{"type":"string"}}},
        "required":["positive","negative"],"additionalProperties":False}
    }, "required":["cardiovascular","respiratory","constitutional"], "additionalProperties":False},
    "pmh":{"type":"array","items":{"type":"string"}},
    "meds":{"type":"array","items":{"type":"string"}},
    "flags":{"type":"object","properties":{
      "ischemic_features":{"type":"boolean"},
      "dm_followup":{"type":"boolean"},
      "labs_a1c_needed":{"type":"boolean"}},
      "required":["ischemic_features","dm_followup","labs_a1c_needed"],
      "additionalProperties":False}
  },
  "required":["hpi","ros","pmh","meds","flags"], "additionalProperties":False }
}

# New summary schema (customized for user requirements)
SUMMARY_JSON_SCHEMA = {
    "name": "summary",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "hpi": {"type": "string"},
            "ros": {
                "type": "object",
                "properties": {
                    "cardiovascular": {
                        "type": "object",
                        "properties": {
                            "positive": {"type": "array", "items": {"type": "string"}},
                            "negative": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["positive", "negative"],
                        "additionalProperties": False
                    },
                    "respiratory": {
                        "type": "object",
                        "properties": {
                            "positive": {"type": "array", "items": {"type": "string"}},
                            "negative": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["positive", "negative"],
                        "additionalProperties": False
                    },
                    "constitutional": {
                        "type": "object",
                        "properties": {
                            "positive": {"type": "array", "items": {"type": "string"}},
                            "negative": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["positive", "negative"],
                        "additionalProperties": False
                    }
                },
                "required": ["cardiovascular", "respiratory", "constitutional"],
                "additionalProperties": False
            },
            "pmh": {"type": "array", "items": {"type": "string"}},
            "meds": {"type": "array", "items": {"type": "string"}},
            "flags": {
                "type": "object",
                "properties": {
                    "ischemic_features": {"type": "boolean"},
                    "dm_followup": {"type": "boolean"},
                    "labs_a1c_needed": {"type": "boolean"}
                },
                "required": ["ischemic_features", "dm_followup", "labs_a1c_needed"],
                "additionalProperties": False
            }
        },
        "required": ["hpi", "ros", "pmh", "meds", "flags"],
        "additionalProperties": False
    }
}
