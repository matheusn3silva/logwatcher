from dataclasses import dataclass

@dataclass
class DataFile:
    logical_name: str
    size_mb: float
    used_mb: float

    @property
    def free_mb(self) -> float:
        return self.size_mb - self.used_mb