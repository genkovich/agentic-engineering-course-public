"""common.py - спільний мінімум для грейдерів сьюту: живий HTTP-сервіс."""
import socket
import time
import urllib.error
import urllib.request


def http_status(url, headers=None):
    """Фактичний HTTP-код відповіді (0, якщо сервіс не відповів)."""
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except OSError:
        return 0


def wait_for_port(host, port, timeout=10):
    """Чекає, поки сервіс відкриє порт. True = дочекались."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.2):
                return True
        except OSError:
            time.sleep(0.1)
    return False
