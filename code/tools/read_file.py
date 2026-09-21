def read_file(file_name):
    print("===已调用read_file===")
    with open(f"{file_name}", "r", encoding="utf-8") as f:
        content=f.read()
    return content