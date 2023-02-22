import sys

# Written By Chippy
# Program to demangle GCC EE 2.9 C++ symbols

# primitive types
ParamTypes = {
    "v": "void",
    "b": "bool",
    "i": "int",
    "l": "long",
    "x": "long long",
    "c": "char",
    "s": "short",
    "f": "float",
    "d": "double",
    "e": "...",
    "w": "wchar_t"
}

# Need to figure out template format
"""

Max__H1Zf_X01X01_X01
template <typename T>
T Max(T, T);

"H_" = template type count
"X01X01" = parameter types
"X01" (at the end) = return type
"H1ZZ", Z = "'Z' + type"
"""

# Parameter Modifiers
# "P", pointer (Pt, t*)
# "R", reference (Rt, t&)
# "C", const (Ct, const t) Note: Only mangles for pointers or references
# "G", seems to be a struct that isn't passed through a pointer or a reference (see next)
"""
struct MAX {
    int x;
    int y;
};
void test(Max);
"test__FG3MAX"
"""

Modifiers = {
    "U": "unsigned",
    "S": "signed",
    "C": "const",
    "V": "volatile",
    "P": "pointer",
    "R": "reference"
    #"T": "index"
    #"G": "struct",
    #"G": "name_length" # need to implement handling of this
}

"""
Modifier Dict:
hasModifier,
isPointer,
isReference,
typeModifier
"""

"""
SymParam Dict:
isPrimitive,
nameLength,
symName, # typename
ModifierDict
"""

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print("Need a symbol to demangle")
        return
    sym = args[0]
    splitSymAll = sym.split("__")
    splitSym = splitSymAll[0]
    symArgs = splitSymAll[1]
    demangledSym = splitSym + "("
    if symArgs.startswith('F'):
        types = symArgs.split("F")[1]
        pos = sym.index(types)
        sym_args = []
        # this code needs to be rewritten to parse all parameters
        # then expand and generate the demangled symbol
        while pos < len(sym):
            modifiers = [] # list of modifier information
            modifierPos = pos # not sure how to use this
            while True:
                isPointer = False
                isReference = False
                hasModifier = False
                length = ""
                structName = ""
                if len(sym) == pos:
                    break
                typeModifier = Modifiers.get(sym[pos])
                if typeModifier != None:
                    hasModifier = True
                    pos += 1
                    if typeModifier == "pointer":
                        isPointer = True
                    elif typeModifier == "reference":
                        isReference = True
                    """elif typeModifier == "name_length":
                        # max name length?
                        print("X")
                        for i in range(10000):
                            if sym[pos].isdecimal() == False:
                                break
                            length += sym[pos]
                            pos += 1
                        for i in range(int(length, 10)):
                            structName += sym[pos]
                            pos += 1"""
                    modifierInfo = {
                        "hasModifier": hasModifier,
                        "isPointer": isPointer,
                        "isReference": isReference,
                        "typeModifier": typeModifier,
                        "nameLength": length,
                        "structName": structName
                    }
                    modifiers.append(modifierInfo)
                else:
                    break
            nameLength = ""
            isPrimitive = False
            if sym[pos].isdecimal() == True:
                while True:
                    if sym[pos].isdecimal() == False:
                        break
                    nameLength += sym[pos]
                    pos += 1
                iNameLength = int(nameLength, 10)
                argType = sym[pos:pos+iNameLength]
                pos += iNameLength
            else:
                argType = ParamTypes.get(sym[pos])
                pos += 1
                isPrimitive = True
            symArg = {
                "isPrimitive": isPrimitive,
                "symName": argType,
                "modifiers": modifiers
            }
            sym_args.append(symArg)
            """param_index = -1
            if argType == None:
                if sym[pos] == "T":
                    pos += 1
                    param_index = sym[pos]
                    pos += 1
            for modifier in modifiers:
                if modifier["isPointer"] == True:
                    argType += '*'
                if modifier["isReference"] == True:
                    argType += '&'
                if modifier["hasModifier"] == True:
                    if modifier["typeModifier"] != "pointer" and modifier["typeModifier"] != "reference":
                        argType = modifier["typeModifier"] + ' ' + argType
            print(len(sym), pos)
            if argType == None:
                argType = ""
            elif len(sym) != pos + 1:
                argType += ', '
            pos += 1
            demangledSym = demangledSym + argType"""
    for i, arg in enumerate(sym_args):
        argType = arg["symName"]
        for modifier in arg["modifiers"]:
            if modifier["isPointer"] == True:
                argType += '*'
            if modifier["isReference"] == True:
                argType += '&'
            if modifier["hasModifier"] == True:
                if modifier["typeModifier"] != "pointer" and modifier["typeModifier"] != "reference":
                    argType = modifier["typeModifier"] + ' ' + argType
        if i + 1 != len(sym_args):
            argType += ', '
        demangledSym = demangledSym + argType
    demangledSym += ')'
    print(demangledSym)
         

if __name__ == "__main__":
    main()