def calculator(x:float, y:float,op:str) -> float:
    print("===已调用计算器===")
    if op == "add" or op=="+":
        return x+y
    elif op == "sub" or op=="-":
        return x-y
    elif op == "mul" or op=="*":
        return x*y
    elif op == "div" or op=="/":
        return x/y
    elif op == "pow" or op=="^":
        return x**y
    else:
        return 0