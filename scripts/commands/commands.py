from colorama import Fore, Style
import time

current_path = ["/"]

def ls(args, load_filesystem, get_node):
    fs = load_filesystem()
    current = get_node(fs, current_path)
    if not current or current["type"] != "directory":
        print(Fore.RED + "Ошибка: текущая директория не найдена" + Style.RESET_ALL)
        return
    for child in current["children"]:
        color = Fore.BLUE if child["type"] == "directory" else ""
        print(color + f"{child['type'][0]} {child['name']}" + Style.RESET_ALL)

def cd(args, load_filesystem, get_node):
    global current_path
    fs = load_filesystem()
    
    if not args or args == "/":
        current_path = ["/"]
        return
    elif args == "..":
        if len(current_path) > 1:
            current_path.pop()
        return
    
    parts = args.strip("/").split("/")
    temp_path = current_path.copy()
    
    for part in parts:
        if not part:
            continue
        current = get_node(fs, temp_path)
        if not current or current["type"] != "directory":
            print(Fore.RED + f"Ошибка: директория {part} не найдена" + Style.RESET_ALL)
            return
        for child in current["children"]:
            if child["name"] == part:
                if child["type"] != "directory":
                    print(Fore.RED + f"Ошибка: {part} не является директорией" + Style.RESET_ALL)
                    return
                temp_path.append(part)
                break
        else:
            print(Fore.RED + f"Ошибка: директория {part} не найдена" + Style.RESET_ALL)
            return
    
    current_path = temp_path
    print(Fore.GREEN + f"Перешли в {args}" + Style.RESET_ALL)

def mkdir(args, load_filesystem, save_filesystem, get_node):
    if not args:
        print(Fore.RED + "Ошибка: укажите имя директории" + Style.RESET_ALL)
        return
    fs = load_filesystem()
    current = get_node(fs, current_path)
    if not current or current["type"] != "directory":
        print(Fore.RED + "Ошибка: текущая директория не найдена" + Style.RESET_ALL)
        return
    for child in current["children"]:
        if child["name"] == args:
            print(Fore.RED + f"Ошибка: {args} уже существует" + Style.RESET_ALL)
            return
    current["children"].append({
        "name": args,
        "type": "directory",
        "children": [],
        "created_at": time.time()
    })
    save_filesystem(fs)
    print(Fore.GREEN + f"Директория {args} создана" + Style.RESET_ALL)

def touch(args, load_filesystem, save_filesystem, get_node):
    if not args:
        print(Fore.RED + "Ошибка: укажите имя файла" + Style.RESET_ALL)
        return
    fs = load_filesystem()
    current = get_node(fs, current_path)
    if not current or current["type"] != "directory":
        print(Fore.RED + "Ошибка: текущая директория не найдена" + Style.RESET_ALL)
        return
    for child in current["children"]:
        if child["name"] == args:
            print(Fore.RED + f"Ошибка: {args} уже существует" + Style.RESET_ALL)
            return
    current["children"].append({
        "name": args,
        "type": "file",
        "content": "",
        "created_at": time.time()
    })
    save_filesystem(fs)
    print(Fore.GREEN + f"Файл {args} создан" + Style.RESET_ALL)

def cat(args, load_filesystem, get_node):
    if not args:
        print(Fore.RED + "Ошибка: укажите имя файла" + Style.RESET_ALL)
        return
    fs = load_filesystem()
    current = get_node(fs, current_path)
    if not current or current["type"] != "directory":
        print(Fore.RED + "Ошибка: текущая директория не найдена" + Style.RESET_ALL)
        return
    for child in current["children"]:
        if child["name"] == args:
            if child["type"] != "file":
                print(Fore.RED + f"Ошибка: {args} не является файлом" + Style.RESET_ALL)
                return
            print(child["content"])
            return
    print(Fore.RED + f"Ошибка: файл {args} не найден" + Style.RESET_ALL)

def write(args, load_filesystem, save_filesystem, get_node):
    if not args:
        print(Fore.RED + "Ошибка: укажите имя файла и содержимое" + Style.RESET_ALL)
        return
    parts = args.split(maxsplit=1)
    name = parts[0]
    content = parts[1] if len(parts) > 1 else ""
    fs = load_filesystem()
    current = get_node(fs, current_path)
    if not current or current["type"] != "directory":
        print(Fore.RED + "Ошибка: текущая директория не найдена" + Style.RESET_ALL)
        return
    for child in current["children"]:
        if child["name"] == name:
            if child["type"] != "file":
                print(Fore.RED + f"Ошибка: {name} не является файлом" + Style.RESET_ALL)
                return
            child["content"] = content
            save_filesystem(fs)
            print(Fore.GREEN + f"Содержимое записано в {name}" + Style.RESET_ALL)
            return
    print(Fore.RED + f"Ошибка: файл {name} не найден" + Style.RESET_ALL)

def rm(args, load_filesystem, save_filesystem, get_node):
    if not args:
        print(Fore.RED + "Ошибка: укажите имя файла или директории" + Style.RESET_ALL)
        return
    fs = load_filesystem()
    current = get_node(fs, current_path)
    if not current or current["type"] != "directory":
        print(Fore.RED + "Ошибка: текущая директория не найдена" + Style.RESET_ALL)
        return
    for i, child in enumerate(current["children"]):
        if child["name"] == args:
            current["children"].pop(i)
            save_filesystem(fs)
            print(Fore.GREEN + f"{args} удален" + Style.RESET_ALL)
            return
    print(Fore.RED + f"Ошибка: {args} не найден" + Style.RESET_ALL)

def pwd(args):
    return Fore.BLUE + "/" + "/".join(current_path[1:]) + Style.RESET_ALL

def adduser(args, load_users, save_users):
    if not args:
        print(Fore.RED + "Ошибка: укажите имя пользователя и пароль" + Style.RESET_ALL)
        return
    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        print(Fore.RED + "Ошибка: укажите имя пользователя и пароль" + Style.RESET_ALL)
        return
    username, password = parts
    users = load_users()
    for user in users:
        if user["username"] == username:
            print(Fore.RED + f"Ошибка: пользователь {username} уже существует" + Style.RESET_ALL)
            return
    users.append({
        "username": username,
        "password": password,
        "created_at": time.time()
    })
    save_users(users)
    print(Fore.GREEN + f"Пользователь {username} создан" + Style.RESET_ALL)

def deluser(args, load_users, save_users, current_user):
    if not args:
        print(Fore.RED + "Ошибка: укажите имя пользователя" + Style.RESET_ALL)
        return
    if args == current_user["username"]:
        print(Fore.RED + "Ошибка: нельзя удалить текущего пользователя" + Style.RESET_ALL)
        return
    users = load_users()
    for i, user in enumerate(users):
        if user["username"] == args:
            users.pop(i)
            save_users(users)
            print(Fore.GREEN + f"Пользователь {args} удален" + Style.RESET_ALL)
            return
    print(Fore.RED + f"Ошибка: пользователь {args} не найден" + Style.RESET_ALL)

def switchuser(args, authenticate, current_user):
    if not args:
        print(Fore.RED + "Ошибка: укажите имя пользователя" + Style.RESET_ALL)
        return
    password = input(f"Введите пароль для {args}: ")
    user = authenticate(args, password)
    if user:
        print(Fore.GREEN + f"Переключено на пользователя {args}" + Style.RESET_ALL)
        return user
    else:
        print(Fore.RED + "Ошибка: неверное имя пользователя или пароль" + Style.RESET_ALL)
        return current_user  
