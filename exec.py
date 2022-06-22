
from __future__ import print_function

from ctypes import CFUNCTYPE, c_double

import llvmlite.binding as llvm


# All these initializations are required for code generation!
llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()  # yes, even this one

llvm_ir = """
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
  %".16" = load double, double* %"c"
  %"bigtmp" = fcmp ugt double %".16",              0x0
  br i1 %"bigtmp", label %"loop.end.if", label %"loop.end.else"
loop.end.if:
  %"d" = alloca double
  store double 0x3ff0000000000000, double* %"d"
  br label %"loop.end.endif"
loop.end.else:
  store double 0x4000000000000000, double* %"d"
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
   """

def create_execution_engine():
    """
    Create an ExecutionEngine suitable for JIT code generation on
    the host CPU.  The engine is reusable for an arbitrary number of
    modules.
    """
    # Create a target machine representing the host
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    # And an execution engine with an empty backing module
    backing_mod = llvm.parse_assembly("")
    engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
    return engine


def compile_ir(engine, llvm_ir):
    """
    Compile the LLVM IR string with the given engine.
    The compiled module object is returned.
    """
    # Create a LLVM module object from the IR
    mod = llvm.parse_assembly(llvm_ir)
    mod.verify()
    # Now add the module and make sure it is ready for execution
    engine.add_module(mod)
    engine.finalize_object()
    return mod


engine = create_execution_engine()
mod = compile_ir(engine, llvm_ir)

# Look up the function pointer (a Python int)
func_ptr = engine.get_function_address("main")

# Run the function via ctypes
cfunc = CFUNCTYPE(c_double, c_double, c_double)(func_ptr)
res = cfunc(1, 3.5)
print("fpadd(...) =", res)

# target = llvm.Target.from_default_triple()
# tm = target.create_target_machine(jit=False)
# target_machine = tm

# obj_bin = target_machine.emit_object(mod)
# f = open("a.out","wb")
# f.write(obj_bin)