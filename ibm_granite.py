"""Production-oriented IBM watsonx.ai Granite adapter; disabled unless configured."""
from __future__ import annotations

import json
import os
from typing import Any

import requests

from ai_engine import AIEngine


class IBMGraniteAgent(AIEngine):
    """IBM Granite integration using environment variables, with safe failures.

    Set IBM_WATSONX_URL, IBM_WATSONX_APIKEY and IBM_WATSONX_PROJECT_ID to enable.
    IBM_WATSONX_DEPLOYMENT_ID is optional for deployment-based inference.
    """

    def __init__(self) -> None:
        self.endpoint = os.getenv("IBM_WATSONX_URL", "").rstrip("/")
        self.api_key = os.getenv("IBM_WATSONX_APIKEY", "")
        self.project_id = os.getenv("IBM_WATSONX_PROJECT_ID", "")
        self.deployment_id = os.getenv("IBM_WATSONX_DEPLOYMENT_ID", "")

    def _validate_configuration(self) -> None:
        if not all([self.endpoint, self.api_key, self.project_id]):
            raise RuntimeError(
                "IBM Granite is not configured. Add IBM_WATSONX_URL, IBM_WATSONX_APIKEY, "
                "and IBM_WATSONX_PROJECT_ID to your deployment environment."
            )

    def _token(self) -> str:
        response = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": self.api_key},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def _request(self, prompt: str) -> str:
        self._validate_configuration()
        url = f"{self.endpoint}/ml/v1/text/generation?version=2024-05-31"
        payload = {
            "input": prompt,
            "parameters": {"decoding_method": "greedy", "max_new_tokens": 800},
            "project_id": self.project_id,
            "model_id": "ibm/granite-3-8b-instruct",
        }
        if self.deployment_id:
            url = f"{self.endpoint}/ml/v4/deployments/{self.deployment_id}/predictions?version=2024-05-31"
            payload = {"input": prompt}
        try:
            response = requests.post(url, json=payload, headers={
                "Authorization": f"Bearer {self._token()}", "Content-Type": "application/json"
            }, timeout=45)
            response.raise_for_status()
            body = response.json()
            return body.get("results", [{}])[0].get("generated_text", body.get("predictions", [{}])[0].get("generated_text", ""))
        except (requests.RequestException, KeyError, IndexError, ValueError) as error:
            raise RuntimeError(f"IBM Granite request failed: {error}") from error

    def _json_response(self, prompt: str) -> Any:
        text = self._request(prompt)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return [{"result": text}]

    def generate_study_plan(self, profile: dict[str, Any]) -> list[dict[str, str]]:
        return self._json_response(f"Create JSON study plan for: {profile}")

    def generate_revision_plan(self, profile: dict[str, Any]) -> list[dict[str, str]]:
        return self._json_response(f"Create JSON revision plan for: {profile}")

    def generate_daily_tasks(self, profile: dict[str, Any]) -> list[dict[str, str]]:
        return self._json_response(f"Create JSON daily tasks for: {profile}")

    def generate_motivation(self, profile: dict[str, Any]) -> dict[str, str]:
        result = self._json_response(f"Create JSON motivation for: {profile}")
        return result if isinstance(result, dict) else {"quote": str(result), "tip": "Stay consistent."}

    def generate_subject_priority(self, profile: dict[str, Any]) -> list[dict[str, int | str]]:
        return self._json_response(f"Create JSON subject priorities for: {profile}")

