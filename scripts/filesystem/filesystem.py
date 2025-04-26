import os
import struct
import time

FS_PATH = "pyOS/filesystem.pyos"

TYPE_FILE = 0x01
TYPE_DIR = 0x02

def init_filesystem():
    if not os.path.exists("pyOS"):
        os.makedirs("pyOS")
    if not os.path.exists(FS_PATH):
        root = encode_node({
            "name": "/",
            "type": "directory",
            "children": [],
            "created_at": time.time()
        })
        with open(FS_PATH, "wb") as f:
            f.write(root)

def encode_node(node):
    data = bytearray()
    data.append(TYPE_FILE if node["type"] == "file" else TYPE_DIR)
    name_bytes = node["name"].encode("utf-8")
    data.append(len(name_bytes))
    data.extend(name_bytes)
    data.extend(struct.pack("d", node["created_at"]))
    
    if node["type"] == "file":
        content_bytes = node["content"].encode("utf-8")
        data.extend(struct.pack("I", len(content_bytes)))
        data.extend(content_bytes)
    else:
        data.extend(struct.pack("I", len(node["children"])))
        for child in node["children"]:
            data.extend(encode_node(child))
    
    return data

def decode_node(data, offset=0):
    if offset >= len(data):
        return None, offset
    
    node_type = data[offset]
    offset += 1
    name_len = data[offset]
    offset += 1
    name = data[offset:offset + name_len].decode("utf-8")
    offset += name_len
    created_at = struct.unpack_from("d", data, offset)[0]
    offset += 8
    
    node = {"name": name, "created_at": created_at}
    
    if node_type == TYPE_FILE:
        node["type"] = "file"
        content_len = struct.unpack_from("I", data, offset)[0]
        offset += 4
        node["content"] = data[offset:offset + content_len].decode("utf-8")
        offset += content_len
    else:
        node["type"] = "directory"
        children_count = struct.unpack_from("I", data, offset)[0]
        offset += 4
        node["children"] = []
        for _ in range(children_count):
            child, new_offset = decode_node(data, offset)
            if child:
                node["children"].append(child)
                offset = new_offset
    
    return node, offset

def load_filesystem():
    with open(FS_PATH, "rb") as f:
        data = f.read()
    fs, _ = decode_node(data)
    return fs

def save_filesystem(fs):
    data = encode_node(fs)
    with open(FS_PATH, "wb") as f:
        f.write(data)

def get_node(fs, path):
    node = fs
    for part in path[1:]:
        if node["type"] != "directory":
            return None
        for child in node["children"]:
            if child["name"] == part:
                node = child
                break
        else:
            return None
    return node
