def calculator(x:float, y:float,op:str) -> int|float|complex :
    """
    负责两个数的基础运算
    参数:
        x:左操作数
        y:右操作数
        op:运算符,支持add,sub,mul,div,pow及其符号形式的运算
    返回:
        运算结果
    异常处理:
        除以0时抛出ZeroDivisionError异常
        op不受支持时抛出ValueError异常

    """
    print("===已调用计算器===\n")
    if op == "add" or op=="+":
        ans=x+y
    elif op == "sub" or op=="-":
        ans=x-y
    elif op == "mul" or op=="*":
        ans=x*y
    elif op == "div" or op=="/":
        ans=x/y
    elif op == "pow" or op=="^":
        ans=pow(x,y)
    else:
        raise ValueError(
            f"不支持的运算符: {op!r}。"
            "支持 add、+、sub、-、mul、*、div、/、pow、^"
        )


    return ans

