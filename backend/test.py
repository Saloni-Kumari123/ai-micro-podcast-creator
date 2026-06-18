from dotenv import load_dotenv
import os

load_dotenv()

print("EMAIL_USER =", os.getenv("EMAIL_USER"))
print("EMAIL_PASS =", os.getenv("EMAIL_PASS"))