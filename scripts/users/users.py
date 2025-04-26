import os
import struct
import time

USERS_PATH = "pyOS/fs-users.pyos"

def init_users():
    if not os.path.exists("pyOS"):
        os.makedirs("pyOS")
    if not os.path.exists(USERS_PATH):
        users = []
        with open(USERS_PATH, "wb") as f:
            f.write(encode_users(users))

def encode_users(users):
    data = bytearray()
    data.extend(struct.pack("I", len(users)))
    for user in users:
        username_bytes = user["username"].encode("utf-8")
        password_bytes = user["password"].encode("utf-8")
        data.append(len(username_bytes))
        data.extend(username_bytes)
        data.append(len(password_bytes))
        data.extend(password_bytes)
        data.extend(struct.pack("d", user["created_at"]))
    return data

def decode_users(data):
    users = []
    offset = 0
    count = struct.unpack_from("I", data, offset)[0]
    offset += 4
    for _ in range(count):
        username_len = data[offset]
        offset += 1
        username = data[offset:offset + username_len].decode("utf-8")
        offset += username_len
        password_len = data[offset]
        offset += 1
        password = data[offset:offset + password_len].decode("utf-8")
        offset += password_len
        created_at = struct.unpack_from("d", data, offset)[0]
        offset += 8
        users.append({"username": username, "password": password, "created_at": created_at})
    return users

def load_users():
    with open(USERS_PATH, "rb") as f:
        data = f.read()
    return decode_users(data)

def save_users(users):
    data = encode_users(users)
    with open(USERS_PATH, "wb") as f:
        f.write(data)

def authenticate(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user
        
    return None
