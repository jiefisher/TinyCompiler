# TinyInterpreter
A simple Compiler in python
Using Antlr4 to parse, and using llvmlite to generate bytecode.
## You can write rule like this (test.gl):
```
def func(x){
    x = x+1;
    return x;
}
out = 0;
for(i=0;i<5;i=i+1){
    out = out + 10;
}
out = out +1;
c = func(out);
d = 0;
if(c<0){
    d = 1;
}
```
## Following is llvm ir code:
```
; ModuleID = ""
target triple = "unknown-unknown-unknown"
target datalayout = ""

define double @"main"() 
{
entry:
  %"out" = alloca double
  store double              0x0, double* %"out"
  %"i" = alloca double
  store double              0x0, double* %"i"
  br label %"loop.header"
loop.header:
  %".5" = load double, double* %"i"
  %"smalltmp" = fcmp ult double %".5", 0x4014000000000000
  br i1 %"smalltmp", label %"loop.body", label %"loop.end"
loop.body:
  %".7" = load double, double* %"out"
  %"addtmp" = fadd double %".7", 0x4024000000000000
  store double %"addtmp", double* %"out"
  %".9" = load double, double* %"i"
  %"addtmp.1" = fadd double %".9", 0x3ff0000000000000
  store double %"addtmp.1", double* %"i"
  br label %"loop.header"
loop.end:
  %".12" = load double, double* %"out"
  %"addtmp.2" = fadd double %".12", 0x3ff0000000000000
  store double %"addtmp.2", double* %"out"
  %".14" = load double, double* %"out"
  %"calltmp" = call double @"func"(double %".14")
  %"c" = alloca double
  store double %"calltmp", double* %"c"
  %"d" = alloca double
  store double              0x0, double* %"d"
  %".17" = load double, double* %"c"
  %"smalltmp.1" = fcmp ult double %".17",              0x0
  br i1 %"smalltmp.1", label %"loop.end.if", label %"loop.end.else"
loop.end.if:
  store double 0x3ff0000000000000, double* %"d"
  br label %"loop.end.endif"
loop.end.else:
  br label %"loop.end.endif"
loop.end.endif:
  %"d.1" = load double, double* %"d"
  ret double %"d.1"
}

define double @"func"(double %".1") 
{
entry:
  %"addtmp" = fadd double %".1", 0x3ff0000000000000
  %"x" = alloca double
  store double %"addtmp", double* %"x"
  %".4" = load double, double* %"x"
  ret double %".4"
}
```
## Run `python3 main.py ` to use.
## Implement 
### Todo List
- [x] Basic OP: +, -, *, /, Parentheses
- [x] ASSIGN OP: =
- [x] Control Flow
  - [x] function
  - [x] if
- [] Array
