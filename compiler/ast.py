from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ASTNode:
    name: str
    value: Optional[str] = None
    children: List["ASTNode"] = field(default_factory=list)

    def add(self, child: "ASTNode") -> None:
        self.children.append(child)

    def label(self) -> str:
        return f"{self.name}: {self.value}" if self.value is not None else self.name

    def to_lines(self, prefix: str = "", is_last: bool = True, root: bool = True) -> List[str]:
        lines = [self.label()] if root else [
            prefix + ("└── " if is_last else "├── ") + self.label()
        ]
        child_prefix = "" if root else prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            lines.extend(child.to_lines(
                child_prefix,
                i == len(self.children) - 1,
                root=False
            ))
        return lines

    def pretty(self) -> str:
        return "\n".join(self.to_lines())
