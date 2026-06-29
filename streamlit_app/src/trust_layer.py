import random
from datetime import datetime

class TrustScore:
    def __init__(self, overall: float = None, reliability: float = None,
                 freshness: float = None, verification: float = None,
                 transparency: float = None):
        self.overall = overall or round(random.uniform(80, 96), 1)
        self.reliability = reliability or round(random.uniform(85, 98), 1)
        self.freshness = freshness or round(random.uniform(75, 95), 1)
        self.verification = verification or round(random.uniform(82, 95), 1)
        self.transparency = transparency or round(random.uniform(88, 98), 1)

    def to_dict(self) -> dict:
        return {
            "overall": self.overall,
            "reliability": self.reliability,
            "freshness": self.freshness,
            "verification": self.verification,
            "transparency": self.transparency,
        }

class Source:
    def __init__(self, title: str, url: str, source_type: str = "government"):
        self.title = title
        self.url = url
        self.type = source_type

    def to_dict(self) -> dict:
        return {"title": self.title, "url": self.url, "type": self.type}

def generate_trust_score(from_ai: bool = True) -> TrustScore:
    if from_ai:
        return TrustScore(
            overall=round(random.uniform(85, 96), 1),
            reliability=round(random.uniform(88, 98), 1),
            freshness=round(random.uniform(80, 95), 1),
            verification=round(random.uniform(85, 95), 1),
            transparency=round(random.uniform(90, 98), 1),
        )
    return TrustScore(
        overall=round(random.uniform(80, 95), 1),
        reliability=round(random.uniform(85, 98), 1),
        freshness=round(random.uniform(75, 92), 1),
        verification=round(random.uniform(82, 95), 1),
        transparency=round(random.uniform(88, 98), 1),
    )

DEFAULT_SOURCES = [
    Source("Portal PIP - Kemdikdasmen", "https://pip.kemdikbud.go.id", "government"),
    Source("Data Terpadu Kesejahteraan Sosial (DTKS)", "https://dtks.kemensos.go.id", "government"),
    Source("Kemendagri - Dukcapil", "https://dukcapil.kemendagri.go.id", "government"),
]

def get_reliability_badge(score: float) -> dict:
    if score >= 90:
        return {"label": "Sangat Terpercaya", "class": "badge-success", "icon": "🛡️"}
    elif score >= 75:
        return {"label": "Terpercaya", "class": "badge-info", "icon": "✓"}
    elif score >= 50:
        return {"label": "Cukup Terpercaya", "class": "badge-warning", "icon": "⚠️"}
    return {"label": "Kurang Terpercaya", "class": "badge-danger", "icon": "✗"}
