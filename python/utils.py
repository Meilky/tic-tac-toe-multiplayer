import re

PROT_RE = r"(\w+)\:(.*)"

def parseCmd(payload: str) -> tuple[str, str] | None:
    result = re.search(PROT_RE, payload)

    if not result:
        return None

    (cmd, arg) = ("", "")
    (cmd, arg) = result.groups()

    return (cmd, arg)

