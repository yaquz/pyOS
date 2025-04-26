import struct
import datetime
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os

TYPE_FILE = 0x01
TYPE_DIR = 0x02

def decode_node(data, offset=0, indent=0):
    if offset >= len(data):
        return None, offset, []
    
    node_type = data[offset]
    offset += 1
    name_len = data[offset]
    offset += 1
    name = data[offset:offset + name_len].decode("utf-8")
    offset += name_len
    created_at = struct.unpack_from("d", data, offset)[0]
    offset += 8
    
    created_at_str = datetime.datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S")
    node = {"name": name, "created_at": created_at}
    output = []
    
    if node_type == TYPE_FILE:
        node["type"] = "file"
        content_len = struct.unpack_from("I", data, offset)[0]
        offset += 4
        node["content"] = data[offset:offset + content_len].decode("utf-8")
        offset += content_len
        output.append("  " * indent + f"Файл: {name}")
        output.append("  " * indent + f"  Создан: {created_at_str}")
        output.append("  " * indent + f"  Содержимое: {node['content']}")
    else:
        node["type"] = "directory"
        children_count = struct.unpack_from("I", data, offset)[0]
        offset += 4
        node["children"] = []
        output.append("  " * indent + f"Папка: {name}")
        output.append("  " * indent + f"  Создана: {created_at_str}")
        for _ in range(children_count):
            child, new_offset, child_output = decode_node(data, offset, indent + 1)
            if child:
                node["children"].append(child)
                offset = new_offset
                output.extend(child_output)
    
    return node, offset, output
  
def decode_users(data):
    users = []
    offset = 0
    output = []
    count = struct.unpack_from("I", data, offset)[0]
    offset += 4
    output.append(f"Всего пользователей: {count}")
    for i in range(count):
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
        created_at_str = datetime.datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S")
        output.append(f"Пользователь {i + 1}:")
        output.append(f"  Имя: {username}")
        output.append(f"  Пароль: {password}")
        output.append(f"  Создан: {created_at_str}")
        users.append({"username": username, "password": password, "created_at": created_at})
    return users, output
  
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

def find_node(node, path_parts):
    if not path_parts:
        return node
    for child in node["children"]:
        if child["name"] == path_parts[0]:
            return find_node(child, path_parts[1:])
    return None

class PyOSReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Чтение файлов PyOS")
        self.root.geometry("600x500")

        # Переменные
        self.file_path = None
        self.fs_data = None
        self.users_data = None

        self.status_label = tk.Label(self.root, text="Выберите файл .pyos для чтения", font=("Arial", 12))
        self.status_label.pack(pady=5, fill="x")

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=5)

        self.browse_button = tk.Button(self.button_frame, text="Выбрать файл", command=self.browse_file, font=("Arial", 12))
        self.browse_button.pack(side=tk.LEFT, padx=5)

        self.add_button = tk.Button(self.button_frame, text="Добавить", command=self.show_add_form, font=("Arial", 12))
        self.add_button.pack(side=tk.LEFT, padx=5)
        self.add_button.configure(state="disabled")

        self.delete_button = tk.Button(self.button_frame, text="Удалить", command=self.show_delete_form, font=("Arial", 12))
        self.delete_button.pack(side=tk.LEFT, padx=5)
        self.delete_button.configure(state="disabled")

        self.output_text = scrolledtext.ScrolledText(self.root, font=("Arial", 12), wrap=tk.WORD, height=15)
        self.output_text.pack(padx=10, pady=10, fill="both", expand=True)
        self.output_text.configure(state="disabled")
      
        self.form_frame = tk.Frame(self.root)
        self.form_frame.pack(pady=5, fill="x")
        self.form_inputs = {}

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл .pyos",
            filetypes=[("Файлы PyOS", "*.pyos")],
            initialdir="pyOS/"
        )
        if not file_path:
            self.status_label.configure(text="Файл не выбран")
            return
        
        if not file_path.endswith(".pyos"):
            self.status_label.configure(text="Файл должен иметь расширение .pyos")
            return

        try:
            with open(file_path, "rb") as f:
                data = f.read()
        except FileNotFoundError:
            self.status_label.configure(text=f"Файл {file_path} не найден")
            return
        except Exception as e:
            self.status_label.configure(text=f"Ошибка при чтении файла: {str(e)}")
            return

        self.file_path = file_path
        self.fs_data = None
        self.users_data = None

        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)

        if "filesystem" in file_path.lower():
            self.fs_data, _, output = decode_node(data)
            self.output_text.insert(tk.END, "Чтение файловой системы:\n")
            for line in output:
                self.output_text.insert(tk.END, line + "\n")
        elif "fs-users" in file_path.lower():
            self.users_data, output = decode_users(data)
            self.output_text.insert(tk.END, "Чтение пользователей:\n")
            for line in output:
                self.output_text.insert(tk.END, line + "\n")
        else:
            self.status_label.configure(text="Неизвестный тип файла. Поддерживаются filesystem.pyos и fs-users.pyos")
            return

        self.output_text.configure(state="disabled")
        self.status_label.configure(text=f"Загружен: {file_path}")
        self.add_button.configure(state="normal")
        self.delete_button.configure(state="normal")
        self.clear_form()

    def clear_form(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        self.form_inputs.clear()

    def show_add_form(self):
        self.clear_form()
        if not self.file_path:
            messagebox.showerror("Ошибка", "Сначала выберите файл")
            return

        if "filesystem" in self.file_path.lower():
            tk.Label(self.form_frame, text="Путь (например, /mydir/myfile.txt):", font=("Arial", 12)).pack(anchor="w")
            path_entry = tk.Entry(self.form_frame, font=("Arial", 12))
            path_entry.pack(fill="x")
            self.form_inputs["path"] = path_entry

            tk.Label(self.form_frame, text="Содержимое (для файла, оставьте пустым для папки):", font=("Arial", 12)).pack(anchor="w")
            content_entry = tk.Entry(self.form_frame, font=("Arial", 12))
            content_entry.pack(fill="x")
            self.form_inputs["content"] = content_entry

        elif "fs-users" in self.file_path.lower():
            tk.Label(self.form_frame, text="Имя пользователя:", font=("Arial", 12)).pack(anchor="w")
            username_entry = tk.Entry(self.form_frame, font=("Arial", 12))
            username_entry.pack(fill="x")
            self.form_inputs["username"] = username_entry

            tk.Label(self.form_frame, text="Пароль:", font=("Arial", 12)).pack(anchor="w")
            password_entry = tk.Entry(self.form_frame, font=("Arial", 12))
            password_entry.pack(fill="x")
            self.form_inputs["password"] = password_entry

        tk.Button(self.form_frame, text="Выполнить", command=self.perform_add, font=("Arial", 12)).pack(pady=5)

    def show_delete_form(self):
        self.clear_form()
        if not self.file_path:
            messagebox.showerror("Ошибка", "Сначала выберите файл")
            return

        if "filesystem" in self.file_path.lower():
            tk.Label(self.form_frame, text="Путь для удаления (например, /mydir/myfile.txt):", font=("Arial", 12)).pack(anchor="w")
            path_entry = tk.Entry(self.form_frame, font=("Arial", 12))
            path_entry.pack(fill="x")
            self.form_inputs["path"] = path_entry

        elif "fs-users" in self.file_path.lower():
            tk.Label(self.form_frame, text="Имя пользователя для удаления:", font=("Arial", 12)).pack(anchor="w")
            username_entry = tk.Entry(self.form_frame, font=("Arial", 12))
            username_entry.pack(fill="x")
            self.form_inputs["username"] = username_entry

        tk.Button(self.form_frame, text="Выполнить", command=self.perform_delete, font=("Arial", 12)).pack(pady=5)

    def perform_add(self):
        if "filesystem" in self.file_path.lower():
            path = self.form_inputs["path"].get().strip()
            content = self.form_inputs["content"].get()
            if not path:
                messagebox.showerror("Ошибка", "Укажите путь")
                return

            path_parts = path.strip("/").split("/")
            if not path_parts or path_parts == [""]:
                messagebox.showerror("Ошибка", "Некорректный путь")
                return

            new_node = {
                "name": path_parts[-1],
                "created_at": datetime.datetime.now().timestamp()
            }
            if content:
                new_node["type"] = "file"
                new_node["content"] = content
            else:
                new_node["type"] = "directory"
                new_node["children"] = []

            parent_path = path_parts[:-1]
            parent = find_node(self.fs_data, parent_path)
            if not parent or parent["type"] != "directory":
                messagebox.showerror("Ошибка", f"Родительская папка {'/' + '/'.join(parent_path)} не найдена или не является папкой")
                return

            for child in parent["children"]:
                if child["name"] == new_node["name"]:
                    messagebox.showerror("Ошибка", f"Элемент {new_node['name']} уже существует")
                    return

            parent["children"].append(new_node)
            with open(self.file_path, "wb") as f:
                f.write(encode_node(self.fs_data))
            messagebox.showinfo("Успех", f"Добавлен элемент: {path}")

        elif "fs-users" in self.file_path.lower():
            username = self.form_inputs["username"].get().strip()
            password = self.form_inputs["password"].get().strip()
            if not username or not password:
                messagebox.showerror("Ошибка", "Укажите имя пользователя и пароль")
                return

            for user in self.users_data:
                if user["username"] == username:
                    messagebox.showerror("Ошибка", f"Пользователь {username} уже существует")
                    return

            self.users_data.append({
                "username": username,
                "password": password,
                "created_at": datetime.datetime.now().timestamp()
            })
            with open(self.file_path, "wb") as f:
                f.write(encode_users(self.users_data))
            messagebox.showinfo("Успех", f"Добавлен пользователь: {username}")

        self.browse_file() 

    def perform_delete(self):
        if "filesystem" in self.file_path.lower():
            path = self.form_inputs["path"].get().strip()
            if not path:
                messagebox.showerror("Ошибка", "Укажите путь")
                return

            path_parts = path.strip("/").split("/")
            if not path_parts or path_parts == [""]:
                messagebox.showerror("Ошибка", "Некорректный путь")
                return

            parent_path = path_parts[:-1]
            parent = find_node(self.fs_data, parent_path)
            if not parent or parent["type"] != "directory":
                messagebox.showerror("Ошибка", f"Родительская папка {'/' + '/'.join(parent_path)} не найдена или не является папкой")
                return

            target_name = path_parts[-1]
            for i, child in enumerate(parent["children"]):
                if child["name"] == target_name:
                    parent["children"].pop(i)
                    with open(self.file_path, "wb") as f:
                        f.write(encode_node(self.fs_data))
                    messagebox.showinfo("Успех", f"Удален элемент: {path}")
                    self.browse_file() 
                    return
            messagebox.showerror("Ошибка", f"Элемент {target_name} не найден")

        elif "fs-users" in self.file_path.lower():
            username = self.form_inputs["username"].get().strip()
            if not username:
                messagebox.showerror("Ошибка", "Укажите имя пользователя")
                return

            for i, user in enumerate(self.users_data):
                if user["username"] == username:
                    self.users_data.pop(i)
                    with open(self.file_path, "wb") as f:
                        f.write(encode_users(self.users_data))
                    messagebox.showinfo("Успех", f"Удален пользователь: {username}")
                    self.browse_file() 
                    return
            messagebox.showerror("Ошибка", f"Пользователь {username} не найден")

if __name__ == "__main__":
    root = tk.Tk()
    app = PyOSReaderApp(root)
    root.mainloop()
