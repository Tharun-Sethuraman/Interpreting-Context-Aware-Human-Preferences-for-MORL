import json
from pydantic import ValidationError

def _safe_parse(self, raw_output: str):
    """Try to safely parse raw VLM output into JSON for Pydantic validation."""

    print("Here ----------------------------")
    try:
        # First try normal parsing
        return self._output_parser.parse(raw_output)
    except ValidationError as ve:
        print("⚠️ ValidationError: Trying to clean JSON...")
        return self._try_clean_json(raw_output, ve)

def _try_clean_json(self, raw_output: str, original_error: Exception):
    """Clean common JSON issues and retry parsing."""
    cleaned = raw_output.strip()

    # Remove trailing commas
    cleaned = cleaned.replace(",]", "]").replace(",}", "}")

    # Extract only the JSON substring if extra text is around
    if "{" in cleaned and "}" in cleaned:
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        cleaned = cleaned[start:end]

    try:
        json_obj = json.loads(cleaned)
        # Pass dict directly to model_validate instead of model_validate_json
        return self._output_parser._output_cls.model_validate(json_obj)
    except Exception as e:
        print("❌ Still failed to parse JSON.")
        print("Raw VLM output:\n", raw_output)
        raise original_error  # re-raise original Pydantic error
