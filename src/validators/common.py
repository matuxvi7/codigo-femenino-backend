import re
from typing import Any, Dict, List, Optional, Tuple

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    email = email.strip()
    if len(email) > 254:
        return False
    return bool(EMAIL_REGEX.match(email))


def parse_pagination(args: Dict[str, Any], default_limit: int = 10, max_limit: int = 50) -> Tuple[int, int]:
    try:
        page = int(args.get("page", 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1

    try:
        per_page = int(args.get("per_page") or args.get("limit") or default_limit)
        if per_page < 1:
            per_page = default_limit
        elif per_page > max_limit:
            per_page = max_limit
    except (ValueError, TypeError):
        per_page = default_limit

    return page, per_page
