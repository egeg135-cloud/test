import hashlib


def make_duplicate_hash(platform: str, pc_url: str, content_excerpt: str) -> str:
    key = f"{platform}|{pc_url}|{content_excerpt[:120]}".encode("utf-8", errors="ignore")
    return hashlib.sha256(key).hexdigest()
