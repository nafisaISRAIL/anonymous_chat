directories = {}

def check_command(main_func):
    def wrapper(command, parameter):
        if command not in ["CREATE", "DELETE", "LIST", "MOVE"]:
            raise Exception("Command does not valid.")
        return main_func(command, parameter)
    return wrapper


def run_command(command, parameter=None):
    commands = {
        "DELETE": delete_path,
        "CREATE": create_path,
        "LIST": list_path,
        "MOVE": move_path
    }

def delete_path(parameter):
    pass

def create_path(parameter):
    pass

def list_path(parameter):
    pass

def move_path(parameter):
    pass


if __name__ == "__main__":
    command = ""
    while True:
        command, parameter = input().split(" ")
        if not all(command, parameter):
            break