from app.v1.utils import hash_password, verify_password

def test_hash_password_returns_hashed_password():
    password_hash = hash_password('password')
    assert password_hash is not None
    assert len(password_hash) == 87


def test_hash_password_returns_different_hash_for_same_password():
    password_hash_1 = hash_password('password')
    password_hash_2 = hash_password('password')
    assert password_hash_1 != password_hash_2


def test_verify_password_returns_true_for_correct_password():
    password = 'password'
    password_hash = hash_password(password)
    assert verify_password(password, password_hash) is True


def test_verify_password_returns_false_for_incorrect_password():
    password = 'password'
    password_hash = hash_password(password)
    assert verify_password('incorrect_password', password_hash) is False
