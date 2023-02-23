import sys

# Written By Chippy
# Program to demangle GCC EE 2.9 C++ symbols

# Now supports Indexed Args and Class Methods

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
    "w": "wchar_t",
    "r": "long double",
    "F": "Unhandled Function Pointer!"
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
'G' is generated for a union parameter
'G' is generated for a UNION or RECORD type
"""

Modifiers = {
    "U": "unsigned",
    "S": "signed",
    "C": "const",
    "V": "volatile",
    "P": "pointer",
    "R": "reference",
    "G": "struct"
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

# need to figure out namespaces and handle them
"""
'Q' = namespace, whether explicit namespace or a struct in a struct
'2' = inheritance(?) depth
'7' = length of namespace name
len("SmoothY") = 7
Update__Q27SmoothY11SmoothYInfoPf - original symbol
namespace SmoothY {
    struct SmoothYInfo {
        float y;
        void Update(float*);
    };
};

struct SmoothY::SmoothYInfo info;
info.Update(0);
"""

"""
add support for 128 bit types
typedef int TItype __attribute__ ((mode (TI)));
void func(TItype*); = func__FPI80
typedef unsigned int UTItype __attribute__ ((mode (TI)));
void func2(UTItype*); = func__FPUI80
"""

"""
function pointer args need to be handled
figure this symbol out:
Set__8EV_EVENTPFP8EV_EVENT_P6EV_JOBUcUsUcUsUs
SetModulateFunc__8DM_FRAMEPFP8DM_FRAMEUsPv_vPv
this is a funciton pointer symbol
"PF" is the start of a function
struct DM_FRAME {
    void SetModulateFunc(void (*func)(DM_FRAME*, u16, void*), void*);
};

void Modulation(DM_FRAME*, u16, void*);
DM_FRAME frame;
frame.SetModulateFunc(Modulation, 0);
SetModulateFunc = SetModulateFunc__8DM_FRAMEPFP8DM_FRAMEUsPv_vPv
"""

"""
anyway to handle ctors?
__7BaggageP10ALG_MATRIXP10ALG_VECTORPiUiUiiii

struct ALG_MATRIX;
struct ALG_VECTOR;

struct Baggage {
    Baggage(ALG_MATRIX*, ALG_VECTOR*, int*, unsigned int, unsigned int, int, int, int);
};
"""

"""
handle dtors
_$_6VRHold
VRHold::~VRHold()
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
    isClassSymbol = False
    if symArgs.startswith('F'):
        pos = sym.index("__F") + 3
    elif symArgs[0].isdecimal() == True:
        classNameLength = ""
        isClassSymbol = True
        pos = sym.index(symArgs)
        while True:
            if sym[pos].isdecimal() == False:
                break
            classNameLength += sym[pos]
            pos += 1
        classNameLength = int(classNameLength, 10)
        className = sym[pos:pos+classNameLength]
        pos += classNameLength
        demangledSym = className + "::" + demangledSym
    sym_args = []
    # this code needs to be rewritten to parse all parameters
    # then expand and generate the demangled symbol
    while pos < len(sym):
        modifiers = [] # list of modifier information
        while True:
            isPointer = False
            isReference = False
            hasModifier = False
            length = "0"
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
        indexed = False
        indexValue = "-1"
        if sym[pos].isdecimal() == True:
            while True:
                if sym[pos].isdecimal() == False:
                    break
                nameLength += sym[pos]
                pos += 1
            iNameLength = int(nameLength, 10)
            argType = sym[pos:pos+iNameLength]
            pos += iNameLength
        elif sym[pos] == 'T':
            indexed = True
            indexValue = ""
            pos += 1
            if sym[pos].isdecimal() == True:
                while True:
                    if pos == len(sym) or sym[pos].isdecimal() == False:
                        break
                    indexValue += sym[pos]
                    pos += 1
            # is this okay?
            if pos != len(sym) and sym[pos] == '_':
                pos += 1
        else:
            #print(pos)
            argType = ParamTypes.get(sym[pos])
            #print(argType)
            pos += 1
            isPrimitive = True
        symArg = {
            "isPrimitive": isPrimitive,
            "symName": argType,
            "indexed": indexed,
            "indexValue": int(indexValue, 10),
            "modifiers": modifiers
        }
        sym_args.append(symArg)
    for i, arg in enumerate(sym_args):
        if arg["indexed"] == True and arg["indexValue"] != -1:
            argIdx = arg["indexValue"]
            if isClassSymbol == True:
                argIdx -= 1
            arg = sym_args[argIdx]
        argType = arg["symName"]
        for modifier in arg["modifiers"]:
            if modifier["isPointer"] == True:
                argType += '*'
            if modifier["isReference"] == True:
                argType += '&'
            if modifier["hasModifier"] == True:
                if modifier["typeModifier"] != "pointer" and modifier["typeModifier"] != "reference":
                    if modifier["typeModifier"] != "struct":
                        argType = modifier["typeModifier"] + ' ' + argType
        if i + 1 != len(sym_args):
            argType += ', '
        demangledSym = demangledSym + argType
    demangledSym += ')'
    print(demangledSym)
         

if __name__ == "__main__":
    main()