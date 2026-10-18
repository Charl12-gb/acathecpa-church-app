"""
Small cache-based counters against brute force and spam.

Uses Django's cache (local memory by default: counters are per process; set a
shared cache such as Redis in production to count across workers).
"""
from __future__ import annotations

from django.core.cache import cache

LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_MAX_PER_ACCOUNT_AND_IP = 5
# Higher: a school or a cybercafé often shares one public address.
LOGIN_MAX_PER_IP = 30

CONTACT_WINDOW_SECONDS = 60 * 60
CONTACT_MAX_PER_IP = 5


def client_ip(request) -> str:
    return request.META.get("REMOTE_ADDR", "") or "unknown"


def _count(key: str) -> int:
    return cache.get(key, 0)


def _hit(key: str, window: int) -> None:
    if cache.add(key, 1, window):
        return
    try:
        cache.incr(key)
    except ValueError:  # expired between add() and incr()
        cache.set(key, 1, window)


def _login_keys(request, username: str):
    ip = client_ip(request)
    return f"login-fail:{ip}:{username.strip().lower()}", f"login-fail-ip:{ip}"


def login_blocked(request, username: str) -> bool:
    pair, ip = _login_keys(request, username)
    return _count(pair) >= LOGIN_MAX_PER_ACCOUNT_AND_IP or _count(ip) >= LOGIN_MAX_PER_IP


def login_failed(request, username: str) -> None:
    for key in _login_keys(request, username):
        _hit(key, LOGIN_WINDOW_SECONDS)


def login_succeeded(request, username: str) -> None:
    cache.delete(_login_keys(request, username)[0])


def contact_allowed(request) -> bool:
    key = f"contact:{client_ip(request)}"
    if _count(key) >= CONTACT_MAX_PER_IP:
        return False
    _hit(key, CONTACT_WINDOW_SECONDS)
    return True
