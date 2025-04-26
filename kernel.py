from colorama import init, Fore, Style
from scripts.filesystem.filesystem import init_filesystem, load_filesystem, save_filesystem, get_node
from scripts.users.users import init_users, load_users, save_users, authenticate
from scripts.commands.commands import ls, cd, mkdir, touch, cat, write, rm, pwd, adduser, deluser, switchuser
import time

init()

current_user = None

# Основной цикл ОС
def main():
    init_filesystem()
    init_users()
    
    users = load_users()
    if not users:
        print("Нет зарегистрированных пользователей. Создайте первого пользователя.")
        username = input("Имя пользователя: ")
        password = input("Пароль: ")
        users.append({
            "username": username,
            "password": password,
            "created_at": time.time()
        })
        save_users(users)
        print(Fore.GREEN + f"Пользователь {username} создан" + Style.RESET_ALL)
    
    # Аутентификация
    global current_user
    while not current_user:
        username = input("Имя пользователя: ")
        password = input("Пароль: ")
        user = authenticate(username, password)
        if user:
            current_user = user
            print(f"Добро пожаловать, {username}!")
        else:
            print(Fore.RED + "Неверное имя пользователя или пароль" + Style.RESET_ALL)

    print("Введите 'help' для списка команд.")
    
    commands = {
        "ls": lambda args: ls(args, load_filesystem, get_node),
        "cd": lambda args: cd(args, load_filesystem, get_node),
        "mkdir": lambda args: mkdir(args, load_filesystem, save_filesystem, get_node),
        "touch": lambda args: touch(args, load_filesystem, save_filesystem, get_node),
        "cat": lambda args: cat(args, load_filesystem, get_node),
        "write": lambda args: write(args, load_filesystem, save_filesystem, get_node),
        "rm": lambda args: rm(args, load_filesystem, save_filesystem, get_node),
        "pwd": pwd,
        "adduser": lambda args: adduser(args, load_users, save_users),
        "deluser": lambda args: deluser(args, load_users, save_users, current_user),
        "switchuser": lambda args: globals().update({"current_user": switchuser(args, authenticate, current_user)})
    }
    
    while True:
        try:
            command = input(f"pyOS[{current_user['username']}]:{pwd('')} $ ")
            parts = command.split(maxsplit=1)
            cmd = parts[0].lower() if parts else ""
            args = parts[1] if len(parts) > 1 else ""

            if cmd == "help":
                print("Доступные команды:")
                print("  ls - показать содержимое текущей директории")
                print("  cd <путь> - сменить директорию")
                print("  mkdir <имя> - создать директорию")
                print("  touch <имя> - создать файл")
                print("  cat <имя> - прочитать файл")
                print("  write <имя> <содержимое> - записать в файл")
                print("  rm <имя> - удалить файл или директорию")
                print("  pwd - показать текущую директорию")
                print("  adduser <имя> <пароль> - создать пользователя")
                print("  deluser <имя> - удалить пользователя")
                print("  switchuser <имя> - сменить пользователя")
                print("  exit - выйти из ОС")
            elif cmd == "exit":
                print(Fore.GREEN + "Выход из pyOS" + Style.RESET_ALL)
                break
            elif cmd in commands:
                commands[cmd](args)
            elif cmd:
                print(Fore.RED + f"Неизвестная команда: {cmd}" + Style.RESET_ALL)
        except KeyboardInterrupt:
            print(Fore.RED + "\nПрервано. Введите 'exit' для выхода." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Ошибка: {str(e)}" + Style.RESET_ALL)

if __name__ == "__main__":
    main()