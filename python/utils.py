import re

PROT_RE = r"(\w+)\:(.*)"

def parseCmd(payload):
    result = re.search(PROT_RE, payload)

    if not result:
        raise Exception()

    return result.groups()

