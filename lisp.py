from openai import OpenAI

def aicompiler(prompt):
    client = OpenAI(
        api_key = 'your_api'
    )

    command = '''please translate these lisp code to python. and don't give me any Note or explanation if there are print-num or print-bool it means print in python. besides that please don't output anything. you can only output the equivalence code of python. just the thing that equivalence python code. only remember one thing that .don't output like "The code will be like the following:" or "Here is the Python code equivalent to the given Lisp code, without any additional print statements:" or etc additional messages'''

    chat_completion = client.chat.completions.create(
        messages = [
            {
                "role" : "user",
                "content" : command + prompt
            },    
        ],
        model="gpt-3.5-turbo"
    )
    ret = chat_completion.choices[0].message.content
    ret += '\n'
    #print(ret) #Log of Python Code
    try:
        exec(ret, globals(), locals())
    except:
        print(ret)

class Token:
    def __init__(self, id, type):
        self.id = id
        self.type = type

token_stream = []
run_position = 0
input_data = ""
mp_var = {}

def add_token(id, type):
    new_token = Token(id, type)
    token_stream.append(new_token)

def parse(s):
    sz = len(s)
    i = 0
    while i < sz:
        if s[i].isdigit() or (s[i] == '-' and i + 1 < sz and s[i + 1].isdigit()):
            start = i
            i += 1
            while i < sz and s[i].isdigit():
                i += 1
            add_token(s[start:i], "NUM")
            i -= 1
        elif s[i].isalpha():
            start = i
            while i < sz and (s[i].isalnum() or s[i] == '-'):
                i += 1
            word = s[start:i]
            if word == "and":
                add_token("and", "LOGICAL_OP")
            elif word == "or":
                add_token("or", "LOGICAL_OP")
            elif word == "not":
                add_token("not", "LOGICAL_OP")
            elif word == "mod":
                add_token("mod", "NUM_OP")
            elif word == "if":
                add_token("if", "if_EXP")
            elif word == "fun":
                add_token("fun", "func_EXP")
            elif word == "define":
                add_token("define", "define_OP")
            elif word == "#t":
                add_token("#t", "bool_VAL")
            elif word == "#f":
                add_token("#f", "bool_VAL")
            elif word == "print-num":
                add_token("print-num", "print_OP")
            elif word == "print-bool":
                add_token("print-bool", "print_OP")
            else:
                add_token(word, "VAR")
            i -= 1
        elif s[i] == '#' and i + 1 < sz and (s[i + 1] == 't' or s[i + 1] == 'f'):
            if s[i + 1] == 't':
                add_token("#t", "bool_VAL")
            else:
                add_token("#f", "bool_VAL")
            i += 1
        elif s[i] in ['+', '-', '*', '/', '>', '<', '=', '(', ')']:
            if s[i] in ['(', ')']:
                add_token(s[i], "PAR")
            else:
                add_token(s[i], "NUM_OP")
        i += 1

def parsing_exp_token(ind): # for all
    sz = len(token_stream)
    stk = []
    if(ind < sz):
        stk.append(token_stream[ind])
        ind += 1
    else:
        return stk, ind

    while ind < sz:
        if token_stream[ind].id == ')':
            stk.append(token_stream[ind])
            break

        elif token_stream[ind].type == "bool_VAL" or token_stream[ind].type == "NUM" or token_stream[ind].type == "VAR":
            stk.append(token_stream[ind])

        elif token_stream[ind].type == "if_EXP":
            stk.append(token_stream[ind])

        elif token_stream[ind].id == '(':
            result_token, ind = parsing_exp_token(ind)
            result = process_exp(result_token)
            stk.append(result)

        elif token_stream[ind].type == 'func_EXP':
            stk.append(token_stream[ind])

        else:
            stk.append(token_stream[ind])
        ind += 1
    
    #print_Token(stk) # Log

    return stk, ind

#要回傳token
def process_exp(vec):
    if(len(vec) == 0):
        return Token(None, None)
    NewToken = Token(None, None)
    
    vec.pop(0)
    vec.pop(-1)
    operation = vec[0].id 
    operands = vec[1:]
    # print_Token(vec)
    # function 處理 但爛了
    # if(vec[0].type != "NUM_OP" or vec[0].type != "LOGICAL_OP"):
    #    return vec[0]
    # 

    if operation == 'if':
        if operands[0].id == "#t":
            return operands[1]
        else:
            return operands[2]

    if operation == 'define':
        if operands[0].type == "VAR":
            mp_var[operands[0].id] = operands[1].id
            return "OK"

    if operation == '+':
        sumation = 0
        if len(operands) < 2:
            return "Syntax Error"
        for tmp in operands:
            try:
                sumation += int(tmp.id)
            except:
                if(tmp.type == 'VAR'): # 保留處理
                    sumation += int(mp_var[tmp.id])
                    continue

                elif(tmp.type != "NUM"):
                    return "Type Error +"

                return "Syntax Error +"
        NewToken.id = str(sumation)
        NewToken.type = "NUM"
        return NewToken

    if operation == '*':
        if len(operands) < 2:
            return "Syntax Error"
        product = 1
        for token in operands:
            try:
                product *= int(token.id)
            except:
                if(tmp.type == 'VAR'): # 等等修
                    product *= int(mp_var[tmp.id])
                    continue

                if(tmp.type != "NUM"):
                    return "Type Error"

                return "Syntax Error"
        NewToken.id = str(product)
        NewToken.type = "NUM"
        return NewToken

    if operation == '-':
        if len(operands) != 2:
            return "Syntax Error -"
        if(not((operands[0].type == 'NUM' or operands[0].type == 'VAR') or (operands[1].type == 'NUM' or operands[0].type == 'VAR'))):
            return "Type Error"
        if(operands[0].type == "VAR"):
            operands[0].id = mp_var[operands[0].id]
        if(operands[1].type == "VAR"):
            operands[1].id = mp_var[operands[1].id]
        NewToken.id = str(int(operands[0].id) - int(operands[1].id))
        NewToken.type = "NUM"
        return NewToken

    if operation == '/':
        if len(operands) != 2:
            return "Syntax Error -"

        if(not((operands[0].type == 'NUM' or operands[0].type == 'VAR') or (operands[1].type == 'NUM' or operands[0].type == 'VAR'))):
            return "Type Error"
        if(operands[0].type == "VAR"):
            operands[0].id = mp_var[operands[0].id]
        if(operands[1].type == "VAR"):
            operands[1].id = mp_var[operands[1].id]

        if int(operands[1].id) == 0:
            return "Division by Zero Error"
        NewToken.id = str( int(int(operands[0].id) / int(operands[1].id)) )
        NewToken.type = "NUM"
        return NewToken

    if operation == 'mod':
        if len(operands) != 2:
            return "Syntax Error"
        if(not((operands[0].type == 'NUM' or operands[0].type == 'VAR') or (operands[1].type == 'NUM' or operands[0].type == 'VAR'))):
            return "Type Error"
        if(operands[0].type == "VAR"):
            operands[0].id = mp_var[operands[0].id]
        if(operands[1].type == "VAR"):
            operands[1].id = mp_var[operands[1].id]

        NewToken.id = str( int(operands[0].id) % int(operands[1].id) )
        NewToken.type = "NUM"
        return NewToken

    if operation == '=': #處理變數問題
        if len(operands) < 2:
            return "Syntax Error"
        if(all(token.id == operands[0].id for token in operands)):
            NewToken.id = "#t"
        else:
            NewToken.id = "#f"
        NewToken.type = "bool_VAL"
        return NewToken

    if operation == '>':
        
        if len(operands) != 2:
            return "Syntax Error"

        if(not((operands[0].type == 'NUM' or operands[0].type == 'VAR') or (operands[1].type == 'NUM' or operands[0].type == 'VAR'))):
            return "Type Error"
        if(operands[0].type == "VAR"):
            operands[0].id = mp_var[operands[0].id]
        if(operands[1].type == "VAR"):
            operands[1].id = mp_var[operands[1].id]

        if((operands[0].id) > (operands[1].id)):
            NewToken.id = "#t"
        else:
            NewToken.id = "#f"
        NewToken.type = "bool_VAL"
        return NewToken

    if operation == '<':
        
        if len(operands) != 2:
            return "Syntax Error"

        if(not((operands[0].type == 'NUM' or operands[0].type == 'VAR') or (operands[1].type == 'NUM' or operands[0].type == 'VAR'))):
            return "Type Error"
        if(operands[0].type == "VAR"):
            operands[0].id = mp_var[operands[0].id]
        if(operands[1].type == "VAR"):
            operands[1].id = mp_var[operands[1].id]

        if((operands[0].id) < (operands[1].id)):
            NewToken.id = "#t"
        else:
            NewToken.id = "#f"
        NewToken.type = "bool_VAL"
        return NewToken

    ret = True

    if operands[0] == 'Type Error':
        return "Type Error"

    if operation == 'not':
        if(operands[0].type != 'bool_VAL'):
            return "Type Error"
        if operands[0].id == "#t":
            NewToken.id = "#f"
        elif operands[0].id == "#f":
            NewToken.id = "#t"
        NewToken.type = "bool_VAL"
        return NewToken

    if operation == 'and':
        if len(operands) < 2:
            return "Syntax Error"
        for i in operands:
            if i.type != 'bool_VAL':
                return "Type Error"
            if i.id == "#t":
                ret = ret and True
            else:
                ret = ret and False
        if ret: NewToken.id = "#t"
        else: NewToken.id = "#f"
        NewToken.type = "bool_VAL"
        return NewToken
    
    if operation == 'or':
        if len(operands) < 2:
            return "Syntax Error"
        for i in operands:
            if i.type != 'bool_VAL':
                return "Type Error"
            if i.id == "#t":
                ret = ret or True
            else:
                ret = ret or False
        if ret: NewToken.id = "#t"
        else: NewToken.id = "#f"
        NewToken.type = "bool_VAL"
        return NewToken

    if operation == 'print-num':
        lst = []
        for i in operands:
            lst.append(i)
        return lst
    
    if operation == 'print-bool':
        lst = []
        for i in operands:
            lst.append(i)
        return lst


def print_Token(vec):
    for i in vec:
        if(type(i) == type(Token(1,1))):
            print(i.type, i.id)
        else:
            print(i)
    print(end = "END OF THIS STK\n\n")

def run_code():
    #寫判斷 看目前 pattern 決定下一步解析目標 解析完處理
    global run_position
    
    for index, now_token in enumerate(token_stream):
        if index == len(token_stream) - 1:
            break
        if(run_position > index):
            continue

        if now_token.type == "NUM_OP" or now_token.type == "LOGICAL_OP": 
            exp1_index_interval, run_position = parsing_exp_token(run_position)
            # print_Token(exp1_index_interval)  #Log
            result = process_exp(exp1_index_interval)
            if(type(result) == type("Syntax Error")):
                    if(result == "OK"):
                        pass
                    else:
                        print(result)
                        return
            run_position += 1
            
        elif now_token.type == "print_OP":
            if now_token.id == "print-num":
                # 以檢查 PAR 為主 一直往右
                exp1_index_interval, run_position = parsing_exp_token(run_position)
                # print_Token(exp1_index_interval) #LOG
                result = process_exp(exp1_index_interval)
                if(type(result) == type("Syntax Error")):
                    if(result == "OK"):
                        pass
                    else:
                        print(result)
                        return
                else:
                    for tmp_item in result:
                        if(tmp_item.type == "VAR"):
                            print(mp_var[tmp_item.id], end = ' ')
                        else:
                            print(tmp_item.id, end = ' ')
                    print()
                run_position += 1
            elif now_token.id == "print-bool":
                exp1_index_interval, run_position = parsing_exp_token(run_position)
                result = process_exp(exp1_index_interval)
                if(type(result) == type("Syntax Error")):
                    print(result)
                    return
                # print_Token(exp1_index_interval)
                run_position += 1
                for tmp_item in result:
                    print(tmp_item.id, end = ' ')
                print()

        elif now_token.type == "if_EXP":
            exp1_index_interval, run_position = parsing_exp_token(run_position)
            result = process_exp(exp1_index_interval)
            run_position += 1
            print(result.id) # final Output

        elif now_token.type == "define_OP":
            exp1_index_interval, run_position = parsing_exp_token(run_position)
            result = process_exp(exp1_index_interval)
            run_position += 1
            if(result == "OK"):
                continue
        
        elif now_token.type == "func_EXP":
            exp1_index_interval, run_position = parsing_exp_token(run_position)
            # print_Token(exp1_index_interval)
            # result = process_exp(exp1_index_interval) #等待新增
            run_position += 1
            


            

if __name__ == "__main__":
    check_back_flag = False
    while True:
        try:
            tmp = input()
            input_data += tmp
        except EOFError:
            break
    
    parse(input_data)
    
    flag = True

    # 超神解析
    for item in token_stream:
        if item.id == 'fun':
            aicompiler(input_data)
            flag = False
            break
    
    if(flag):
        run_code()
        