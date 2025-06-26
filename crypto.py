from Crypto.Cipher import AES
import base64
import hashlib

SECRET_KEY = "exolith-secret-key"  # ключ можно поменять

def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

def unpad(s):
    return s[:-ord(s[len(s)-1:])]

def encrypt(message):
    key = hashlib.sha256(SECRET_KEY.encode()).digest()
    raw = pad(message)
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted = cipher.encrypt(raw.encode())
    return base64.b64encode(encrypted).decode()

def decrypt(enc_message):
    key = hashlib.sha256(SECRET_KEY.encode()).digest()
    encrypted = base64.b64decode(enc_message)
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(encrypted).decode()
    return unpad(decrypted)

