import logging
from enum import Enum

from app.ai.prompts import (
    CRISIS_RESPONSE_CRITICAL,
    CRISIS_RESPONSE_HIGH,
    CRISIS_RESPONSE_MEDIUM,
)

logger = logging.getLogger(__name__)


class CrisisSeverity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


_KEYWORD_TIERS: list[tuple[CrisisSeverity, set[str]]] = [
    (CrisisSeverity.CRITICAL, {
        "kill myself", "end my life", "suicide", "want to die",
        "going to hurt myself", "take my own life", "overdose on",
        "hang myself", "shoot myself",
    }),
    (CrisisSeverity.HIGH, {
        "self-harm", "hurt myself", "cutting myself", "no reason to live",
        "better off dead", "can't go on", "life is not worth living",
        "wish i was dead",
    }),
    (CrisisSeverity.MEDIUM, {
        "hopeless", "worthless", "nobody cares", "give up",
        "can't take it anymore", "disappear forever", "nothing matters",
        "no point in living",
    }),
    (CrisisSeverity.LOW, {
        "very sad", "really sad", "really depressed", "severely anxious",
        "extremely stressed", "completely overwhelmed", "breaking down",
    }),
]


class CrisisDetector:
    _SEVERITY_ORDER = {
        CrisisSeverity.NONE: 0,
        CrisisSeverity.LOW: 1,
        CrisisSeverity.MEDIUM: 2,
        CrisisSeverity.HIGH: 3,
        CrisisSeverity.CRITICAL: 4,
    }

    def detect_keywords(self, text: str) -> CrisisSeverity:
        lowered = text.lower()
        for severity, keywords in _KEYWORD_TIERS:
            for phrase in keywords:
                if phrase in lowered:
                    logger.warning("Crisis keyword detected: '%s' → %s", phrase, severity)
                    return severity
        return CrisisSeverity.NONE

    async def detect_semantic(
        self, text: str, keyword_severity: CrisisSeverity
    ) -> tuple[CrisisSeverity, float]:
        from openai import AsyncOpenAI
        import numpy as np
        from app.config import get_settings

        settings = get_settings()
        key = (settings.OPENAI_API_KEY or "").strip().lower()
        if not key or "placeholder" in key or key == "sk-...":
            return keyword_severity, 0.0

        _CRISIS_REFERENCES = {
            CrisisSeverity.CRITICAL: [
                "I want to kill myself",
                "I am going to end my life tonight",
                "I am planning to commit suicide",
            ],
            CrisisSeverity.HIGH: [
                "I have been hurting myself",
                "I want to harm myself",
                "There is no reason for me to live",
            ],
            CrisisSeverity.MEDIUM: [
                "I feel completely hopeless about everything",
                "Nobody cares whether I exist",
                "I just want to disappear",
            ],
                CrisisSeverity.LOW: [
                    "I feel overwhelmed and cannot cope",
                    "I feel deeply depressed",
                    "I am struggling and need help",
                ],
        }

        try:
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

            msg_response = await client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL, input=[text]
            )
            msg_vec = np.array(msg_response.data[0].embedding)

            best_severity = keyword_severity
            highest_sim = 0.0

            for severity, refs in _CRISIS_REFERENCES.items():
                ref_response = await client.embeddings.create(
                    model=settings.OPENAI_EMBEDDING_MODEL, input=refs
                )
                for ref_data in ref_response.data:
                    ref_vec = np.array(ref_data.embedding)
                    cos_sim = float(
                        np.dot(msg_vec, ref_vec)
                        / (np.linalg.norm(msg_vec) * np.linalg.norm(ref_vec))
                    )
                    if cos_sim > highest_sim:
                        highest_sim = cos_sim
                        best_severity = severity

            logger.info("Semantic crisis score: %.3f → %s", highest_sim, best_severity)
            return best_severity, highest_sim

        except Exception:
            logger.exception("Semantic crisis detection failed; falling back to keyword result")
            return keyword_severity, 0.0

    async def detect(self, text: str) -> tuple[CrisisSeverity, list[str]]:
        from app.config import get_settings

        settings = get_settings()
        keyword_severity = self.detect_keywords(text)
        matched = [kw for _, kws in _KEYWORD_TIERS for kw in kws if kw in text.lower()]
        semantic_severity, semantic_score = await self.detect_semantic(text, keyword_severity)

        # For non-keyword matches, only trust semantic signals above a configured confidence threshold.
        if keyword_severity == CrisisSeverity.NONE and semantic_score < settings.CRISIS_SIMILARITY_THRESHOLD:
            return CrisisSeverity.NONE, []

        final_severity = (
            semantic_severity
            if self._SEVERITY_ORDER[semantic_severity] >= self._SEVERITY_ORDER[keyword_severity]
            else keyword_severity
        )
        return final_severity, matched

    def get_safety_response(self, severity: CrisisSeverity) -> str | None:
        mapping = {
            CrisisSeverity.CRITICAL: CRISIS_RESPONSE_CRITICAL,
            CrisisSeverity.HIGH: CRISIS_RESPONSE_HIGH,
            CrisisSeverity.MEDIUM: CRISIS_RESPONSE_MEDIUM,
        }
        return mapping.get(severity)
