from __future__ import annotations

from shared.config import get_business_data_config
from servers.business_data.repository import BusinessRepository
from servers.business_data.schemas import (
    CaseStatusOutput,
    GetCaseStatusInput,
    SearchCasesInput,
    SearchCasesOutput,
)

cfg = get_business_data_config()
repo = BusinessRepository(db_url=cfg.db_url, db_schema=cfg.db_schema)


def get_case_status(payload: dict) -> dict:
    data = GetCaseStatusInput.model_validate(payload)
    result = repo.get_case_status(data.case_id)
    return CaseStatusOutput.model_validate(result).model_dump()


def search_cases(payload: dict) -> dict:
    data = SearchCasesInput.model_validate(payload)
    result = repo.search_cases(
        filters=data.filters.model_dump(exclude_none=True),
        limit=data.limit,
    )
    return SearchCasesOutput.model_validate(result).model_dump()