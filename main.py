from fastapi import FastAPI, HTTPException, Form
from database import SessionLocal, User, Message
from crypto import encrypt, decrypt
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Разрешаем доступ с любых устройств
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = SessionLocal()

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...), sex: str = Form(...)):
    if db.query(User).filter_by(username=username).first():
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(username=username, password=password, sex=sex, is_admin=(username=="EXOLITH"))
    db.add(user)
    db.commit()
    return {"status": "ok"}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user = db.query(User).filter_by(username=username, password=password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user.last_seen = datetime.utcnow()
    db.commit()
    return {"status": "ok", "is_admin": user.is_admin}

@app.post("/send")
def send(sender: str = Form(...), receiver: str = Form(...), message: str = Form(...)):
    encrypted = encrypt(message)
    msg = Message(sender=sender, receiver=receiver, content=encrypted)
    db.add(msg)
    db.commit()
    return {"status": "sent"}

@app.get("/messages")
def get_messages(user1: str, user2: str):
    msgs = db.query(Message).filter(
        ((Message.sender == user1) & (Message.receiver == user2)) |
        ((Message.sender == user2) & (Message.receiver == user1))
    ).order_by(Message.timestamp.asc()).all()
    return [{"from": m.sender, "to": m.receiver, "text": decrypt(m.content), "time": m.timestamp} for m in msgs]

@app.get("/users")
def get_users(admin: str):
    if admin != "EXOLITH":
        raise HTTPException(status_code=403, detail="Not authorized")
    users = db.query(User).all()
    return [{"username": u.username, "password": u.password, "online": u.last_seen} for u in users]

