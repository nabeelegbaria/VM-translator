import os
import sys
import pathlib

Ram = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}
push_D_to_stack = '@SP\nA=M\nM=D\n@SP\nM=M+1\n'
pop_to_D = '@SP\nM=M-1\nA=M\nD=M\n'
use_R13='\nD=A\n@R13\nM=D\n'
get_R13='@R13\nA=M\nM=D\n'
increment='\n@SP\nM=M+1\n'
set_SP_to_LCL = '@LCL\nD=M\n@SP\nM=D\n'
set_i_to_zero = '@i\nM=0\n'
increment_i = '@i\nM=M+1\n'
binary = {'add': '+', 'sub': '-', 'and': '&', 'or': '|'}
boolean = {'eq': 'JEQ', 'lt': 'JLT', 'gt': 'JGT'}
unary = {'not': '!', 'neg': '-'}


counter=0
def parser(FilePath,path,fileName):
    """ This function receives a file and opens a new one for writing the assembly code """
    path = pathlib.PurePath(path)
    new_path = str(path) + '/' + path.name + '.asm'
    f = open(FilePath,"r")
    f_out = open(new_path, "a+")
    line = f.readline()
    counter = -1
    while line:
        comment = line.find('//')
        if (comment >= 0):
            line = line[:comment]
        line = line.replace('\n', '')
        if (line != ''):
            f_out.write('// ' + line + '\n')
            res, counter = codewriter(line, counter,fileName)
            f_out.write(res)
        line = f.readline()
    f.close()
    f_out.close()

def codewriter(line, counter,fileName):
    """ This function translates from a vm code to an assembly one """
    words = line.split(' ')
    res = ''
    temp = words
    cou = -1
    for i in range (len(temp)) :
        if temp[i] =='':
            cou=i
            break
    if cou != -1:
        words=temp[:cou]
    if (len(words) == 1 and words[0] != 'return'):
        res, counter = arthmetic(words, counter)
    elif (len(words) == 1 and words[0] == 'return'):
        res = return_value()
    elif (len(words) == 3 and words[0] == 'push'):
        res = push(words,fileName)
    elif (len(words) == 3 and words[0] == 'pop'):
        res = pop(words,fileName)
    elif (len(words) == 3 and words[0] == 'function' and words[1] != 'Sys.init'):
        res = function(words)
    elif (len(words) == 3 and words[0] == 'function' and words[1] == 'Sys.init'):
        res = write_init()
    elif (len(words) == 3 and words[0] == 'call'):
        res = call_function(words)
    elif (len(words)==2):
        res = branching(words)
    return res, counter


def arthmetic(word, counter):
    """ This function translates the arthmetic vm code to assembly code """
    if (word[0] in binary.keys()):
        return (pop_to_D + '@SP\nM=M-1\n@SP\nA=M\nM=M' + binary[word[0]] + 'D' + increment , counter)
    elif (word[0] in boolean.keys()):
        counter += 1
        return (pop_to_D + '@SP\nM=M-1\n@SP\nA=M\nD=M-D\n@BOOL.' + str(counter) + '\nD;' + boolean[
            word[0]] + '\n@SP\nA=M\nM=0\n@END' + str(counter) +
                '\n0;JMP\n' + '(BOOL.' + str(counter) + ')\n@SP\nA=M\nM=-1\n(END' + str(counter) + ')\n@SP\nM=M+1\n',
                counter)
    elif (word[0] in unary.keys()):
        return ('@SP\nM=M-1\n@SP\nA=M\nM=' + unary[word[0]] + 'M'+increment, counter)

def pop(words,fileName):
    """ A pop function which pops the last element in the stack"""
    if (words[1] in Ram.keys()):
        return '@' + Ram[words[1]] + '\nD=M\n@' + words[2] + '\nA=D+A' + use_R13 + pop_to_D + get_R13
    elif (words[1] == 'temp'):
        temp = 5 + int(words[2])
        return '@R' + str(temp) + use_R13 + pop_to_D + get_R13
    elif (words[1] == 'static'):
        return '@foo.' +fileName+ words[2] + use_R13 + pop_to_D + get_R13
    elif (words[1] == 'pointer'):
        if (words[2] == '1'):
            return '@R4' + use_R13 + pop_to_D + get_R13
        else:
            return '@R3' + use_R13 + pop_to_D + get_R13


def push(words,fileName):
    """ A push function which pushs the given element into the stack"""
    if (words[1] == 'constant'):
        return '@' + words[2] + '\n' + 'D=A' + '\n' + push_D_to_stack
    elif (words[1] == 'local' or words[1] == 'this' or words[1] == 'that' or words[1] == 'argument'):
        return '@' + str(Ram[words[1]]) + '\nD=M\n@' + words[2] + '\nA=D+A\n' + 'D=M' + '\n' + push_D_to_stack
    elif (words[1] == 'temp'):
        temp = 5 + int(words[2])
        return '@R' + str(temp) + '\nD=M\n' + push_D_to_stack
    elif (words[1] == 'static'):
        return '@foo.' + fileName+words[2] + '\nD=M\n' + push_D_to_stack
    elif (words[1] == 'pointer'):
        if (words[2] == '1'):
            return '@R4' + '\nD=M' + '\n' + push_D_to_stack
        else:
            return '@R3' + '\nD=M' + '\n' + push_D_to_stack

def branching(words):
    """ This function converts the branching code from vm to assembly code """
    if words[0]=="label":
        return '(' + words[1] + ')\n'
    if words[0]=="goto":
        return '@' + words[1] + '\n' + '0;JMP' + '\n'
    if words[0] == "if-goto":
        return pop_to_D + '@' + words[1] + '\n' + 'D;JNE' + '\n'

def function(words):
    global counter
    counter+=1
    return '(' + words[1] + ')\n' + set_i_to_zero + '(LOOP_' + str(counter) + ')\n@' + words[2] + '\nD=A\n' \
           + '@i\n' + 'D=D-M\n' +'@END'+str(counter)+ '\nD;JEQ\n' + '@SP\n' + 'A=M\nM=0' + increment + increment_i \
           + '@LOOP_' + str(counter) + '\n0;JMP\n' + '(END'+str(counter) + ')\n'


def call_function(words):
    """ This function converts the call of a function to the assembly code """
    global counter
    push_return_address = '@return_' + words[1] + str(counter) + '\n'
    get_SP = 'D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    push_LCL = '@LCL\nD=M\n' + push_D_to_stack
    push_ARG = '@ARG\nD=M\n' + push_D_to_stack
    push_THIS = '@THIS\nD=M\n' + push_D_to_stack
    push_THAT = '@THAT\nD=M\n' + push_D_to_stack
    reposition_ARG = '@' + words[2] + '\nD=A\n@SP\nD=M-D\n@5\nD=D-A\n@ARG\nM=D\n'
    reposition_LCL = '@SP\nD=M\n@LCL\nM=D\n'
    goto_f = '@' + words[1] + '\n0;JMP\n'
    return_label = '(return_' + words[1] + str(counter) + ')\n'
    counter+=1
    return push_return_address + get_SP + push_LCL + push_ARG + push_THIS + push_THAT + reposition_ARG \
           + reposition_LCL + goto_f + return_label

def return_value():
    """ This function converts the return to the assembly code """
    FRAME = '@LCL\nD=M\n@FRAME\nM=D\n' #FRAME=LCL
    RET = '@5\nD=A\n@FRAME\nA=M-D\nD=M\n@RET\nM=D\n' #RET=*FRAME-5
    save_into_ARG='\n@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n'
    update_SP = '@ARG\nD=M\n@SP\nM=D+1\n' #SP=ARG+1
    update_THAT = '@FRAME\nA=M-1\nD=M\n@THAT\nM=D\n' #THAT=*FRAME-1
    update_THIS = '@2\nD=A\n@FRAME\nA=M-D\nD=M\n@THIS\nM=D\n' #THIS=*FRAME-2
    update_ARG = '@3\nD=A\n@FRAME\nA=M-D\nD=M\n@ARG\nM=D\n' #ARG=*FRAME-3
    update_LCL = '@4\nD=A\n@FRAME\nA=M-D\nD=M\n@LCL\nM=D\n' #LCL=*FRAME-4
    goto_RET = '@RET\nA=M\n0;JMP\n' #go to RET = return_address
    return FRAME + RET + save_into_ARG + update_SP + update_THAT + update_THIS + update_ARG + update_LCL + goto_RET

def write_init():
    """ This function is responsible for the initialization for the Sys.init function """
    sp = '@256\nD=A\n@SP\nM=D\n'
    call = '@return_Sys.init\nD=A\n'+push_D_to_stack
    LCL = '@LCL\nD=M\n' + push_D_to_stack
    ARG = '@ARG\nD=M\n' + push_D_to_stack
    THIS = '@THIS\nD=M\n' + push_D_to_stack
    THAT = '@THAT\nD=M\n' + push_D_to_stack + 'D=0\n@SP\nD=M-D\n@5\nD=D-A\n@ARG\nM=D\n'
    LCL1 = '@SP\nD=M\n@LCL\nM=D\n'
    goback = '@Sys.init\n0;JMP\n'
    ret = '(return_Sys.init)\n'
    return sp + call + LCL + ARG + THIS + THAT + LCL1 + goback + ret+('(Sys.init)\n')

def main():
    """ The main function which runs the code """
    file_path = sys.argv[1]
    output = ''
    # if the argument is a folder
    path = pathlib.PurePath(file_path)
    new_path = str(path) + '/' + path.name + '.asm'
    f_out = open(new_path, "w")
    if (os.path.isdir(sys.argv[1])):
        for filename in os.listdir(file_path):
            if filename.startswith("Sys") and filename.endswith(".vm"):
                FilePath = file_path + "/" + filename
                parser(FilePath,file_path,filename)
                break
        for filename in os.listdir(file_path):
            if filename.endswith(".vm") and not filename.startswith("Sys"):
                FilePath = file_path+"/"+filename
                parser(FilePath,file_path,filename)
    # if the argument is a file
    else:
        parser(file_path,path,path.name)


if __name__ == "__main__":
    main()

