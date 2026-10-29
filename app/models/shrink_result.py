from dataclasses import dataclass

@dataclass
class ShrinkResult:
    logical_name: str
    before_mb: float
    after_mb: float

    @property
    def recovered_mb(self) -> float:
        return self.before_mb - self.after_mb