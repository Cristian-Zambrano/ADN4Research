from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class SubmitDraftForReviewCommand:
    researcher_id: int
    research_question_id: int
    framework_id: int
    filled_fields: Dict[str, str]
    reformulated_text: str
    status: str