# generate_hash.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
print(pwd_context.hash("secret"))   # replace "secret" with whatever password you want
