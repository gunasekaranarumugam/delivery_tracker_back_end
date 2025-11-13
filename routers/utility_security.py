from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
hash_from_db = "$argon2id$v=19$m=65536,t=3,p=4$YGyNMYZQqlVqrZUyBmCM8Q$Rgk8YrU3nAgYaw7rE4pDwBxmOAutzHjYqXacQ2K+mxw"
print(pwd_context.verify("1234", hash_from_db))


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
password = "1234"

hashed_password = pwd_context.hash(password)
print(hashed_password)
