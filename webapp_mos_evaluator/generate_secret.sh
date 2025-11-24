# cookie signing/encryption key (64 bytes, base64)
echo "SESSION_KEY $(openssl rand -base64 64 | tr -d '\n')"

echo "================================"

echo "ADMIN_PWHASH:"
# make an Argon2id hash for your admin password (copy output to ADMIN_PWHASH)
python - <<'PY'
from argon2 import PasswordHasher
print(PasswordHasher().hash("83j4b4h_2g#$_x@"))  # replace with your real pass
PY
