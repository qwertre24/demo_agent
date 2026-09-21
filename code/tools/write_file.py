def write_file(file_name,content):
    print("===已调用write_file===")
    with open(f"{file_name}", "w", encoding="utf-8") as f:
        f.write(f"{content}")
        f.close()
