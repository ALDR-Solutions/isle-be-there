import re

from app.core.security import get_password_hash, verify_password

BCRYPT_RE = re.compile(r"^\$2b\$\d{2}\$[./A-Za-z0-9]{53}$")

def test_hash_password():
    hashed = get_password_hash("password")

    assert hashed != "password"
    assert BCRYPT_RE.match(hashed)

def test_verify_password():
    hashed = get_password_hash("password")

    assert verify_password("password", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = get_password_hash("password")

    assert verify_password("wrong-password", hashed) is False
