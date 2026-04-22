from __future__ import annotations

import httpx

from shared.config import get_status_config


class StatusClient:
    def __init__(self) -> None:
        cfg = get_status_config()
        self.base_url = cfg.status_api_base.rstrip("/")
        self.token = cfg.status_api_token

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_workflow_status(self, workflow_id: str) -> dict:
        url = f"{self.base_url}/n8n"
        payload = {
            "art": "status",
            "vorgangsnummer": workflow_id,
        }

        with httpx.Client(timeout=20.0) as client:
            response = client.post(url, json=payload, headers=self._headers())
            response.raise_for_status()

            data_list = response.json()
            data = data_list[0] if isinstance(data_list, list) and data_list else {}

        return {
            "workflow_id": data.get("vorgangsnummer", workflow_id),
            "status": self._normalize_workflow_status(data),
            "current_step": self._derive_current_step(data),
            "updated_at": data.get("updated_at"),
        }

    def get_processing_summary(self, case_id: str) -> dict:
        url = f"{self.base_url}/n8n"
        payload = {
            "art": "status",
            "vorgangsnummer": case_id,
        }

        with httpx.Client(timeout=20.0) as client:
            response = client.post(url, json=payload, headers=self._headers())
            response.raise_for_status()

            data_list = response.json()
            data = data_list[0] if isinstance(data_list, list) and data_list else {}

        # 👉 业务状态映射（重点）
        status_map = {
            "widerspruch": "🔴 Rejected (Objection)",
            "in_bearbeitung": "🟡 In Progress",
            "erfolgreich": "🟢 Approved",
        }

        business_status_raw = data.get("bearbeitungsstatus", "unknown")
        business_status = status_map.get(business_status_raw, business_status_raw)

        return {
            "case_id": data.get("vorgangsnummer", case_id),

            # 👉 技术状态（统一）
            "workflow_status": self._normalize_workflow_status(data),

            # 👉 业务状态（用户看这个）
            "case_status": business_status,
            "display_status": business_status.replace("_", " ").title(),  # ← 这里加逗号

            # 👉 原始状态（调试用，可选）
            "raw_status": business_status_raw,

            "next_action": self._derive_next_action(data),
        }

    # ------------------------
    # normalization helpers
    # ------------------------

    def _normalize_workflow_status(self, data: dict) -> str:
        raw = (
            data.get("status")
            or data.get("workflow_status")
            or data.get("bearbeitungsstatus")
            or ""
        ).strip().lower()

        mapping = {
            "pending": "pending",
            "completed": "completed",
            "error": "error",

            # KVBB domain mapping
            "widerspruch": "pending",
            "in_bearbeitung": "pending",
            "bearbeitung": "pending",

            "approved": "completed",
            "genehmigt": "completed",

            "rejected": "completed",
            "abgelehnt": "completed",
        }

        return mapping.get(raw, "pending")

    def _derive_current_step(self, data: dict) -> str:
        if data.get("human_review"):
            return "human_review"
        if data.get("ki_ergebnis"):
            return "ai_evaluated"
        return "received"

    def _derive_next_action(self, data: dict) -> str | None:
        if data.get("human_review"):
            return "wait_for_review"
        if data.get("pdf_url") or data.get("pdfUrl"):
            return "download_pdf"
        return "processing"