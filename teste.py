from pathlib import Path

SECRET_KEY = Path('./secret_key.txt')

a = ''
with SECRET_KEY.open() as secret:
    a = secret.readline()

print(a)
