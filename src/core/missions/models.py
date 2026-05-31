from dataclasses import dataclass
from typing import Optional

@dataclass
class Mission:
    id: str
    title: str
    description: str
    category: str
    tier: str
    status: str
    progress: int
    target: int
    reward_xp: int
    trigger_event: Optional[str] = None
    actor: str = "any"
    
    @classmethod
    def from_row(cls, row):
        return cls(
            id=row[0],
            title=row[1],
            description=row[2],
            category=row[3],
            tier=row[4],
            status=row[5],
            progress=row[6],
            target=row[7],
            reward_xp=row[8],
            trigger_event=row[9] if len(row) > 9 else None,
            actor=row[10] if len(row) > 10 else "any"
        )
