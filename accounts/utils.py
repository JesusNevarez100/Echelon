import secrets
import string

def create_temp_username(prefix="user", length=8) -> str:
	alphabet = string.ascii_lowercase + string.digits
	return f"{prefix}_{''.join(secrets.choice(alphabet) for _ in range(length))}"

def create_temp_password(length=14) -> str:
	alphabet = string.ascii_lowercase + string.digits + "!@#$%^&*"
	return "".join(secrets.choice(alphabet) for _ in range(length))


