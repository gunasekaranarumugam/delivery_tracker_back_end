import os
from dotenv import load_dotenv

load_dotenv()


print("Host:", os.environ.get("DB_HOST"))
print("User:", os.environ.get("DB_USER"))
