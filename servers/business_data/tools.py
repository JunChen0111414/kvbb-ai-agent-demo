from __future__ import annotations

from shared.config import get_business_data_config
from servers.analytics.tools import _fetch_cases
from servers.business_data.schemas import (
    CaseStatusOutput,
    GetCaseStatusInput,
    SearchCasesInput,
    SearchCasesOutput,
)




def get_case_status(payload: dict) -> dict:
    data = GetCaseStatusInput.model_validate(payload)
    case_id = data.case_id

    all_cases = _fetch_cases()

    for item in all_cases:
        if item.get("case_id") == case_id:
            return item

    # 👉 不要 raise，直接返回 None（避免 Streamlit 崩）
    return None


def search_cases(payload: dict) -> dict:
    data = SearchCasesInput.model_validate(payload)

    all_cases = _fetch_cases()

    results = []

    for item in all_cases:
        match = True

        # 简单 filter（你可以扩展）
        for key, value in data.filters.model_dump(exclude_none=True).items():
            if str(item.get(key)) != str(value):
                match = False
                break

        if match:
            results.append(item)

    # limit 控制
    results = results[: data.limit or 10]

    return {
        "cases": results,
        "total": len(results)
    }