from dataclasses import dataclass, field


@dataclass
class FastApiArgument:
    server_address: str = field(
        default="localhost"
    )

    server_port: int = field(
        default=8000
    )
