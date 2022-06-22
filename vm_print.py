import llvmlite.ir as ir
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE
import os

llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()  # yes, even this one
def create_execution_engine():
    """
    Create an ExecutionEngine suitable for JIT code generation on
    the host CPU.  The engine is reusable for an arbitrary number of
    modules.
    """
    # Create a target machine representing the host
    target =  llvm.Target.from_triple("i386-pc-linux-gnu")
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

def main():
    
    
    m = ir.Module(name="demo")
    func_ty = ir.FunctionType(ir.VoidType(), [])
    i32_ty = ir.DoubleType()
    func = ir.Function(m, func_ty, name="main")

    voidptr_ty = ir.IntType(8).as_pointer()

    fmt = "%s %f\n\0"
    c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                        bytearray(fmt.encode("utf8")))
    global_fmt = ir.GlobalVariable(m, c_fmt.type, name="fstr")
    global_fmt.linkage = 'internal'
    global_fmt.global_constant = True
    global_fmt.initializer = c_fmt

    arg = ">>\0"
    c_str_val = ir.Constant(ir.ArrayType(ir.IntType(8), len(arg)),
                            bytearray(arg.encode("utf8")))

    printf_ty = ir.FunctionType(ir.DoubleType(), [voidptr_ty], var_arg=True)
    printf = ir.Function(m, printf_ty, name="printf")

    builder = ir.IRBuilder(func.append_basic_block('entry'))

    c_str = builder.alloca(c_str_val.type)
    builder.store(c_str_val, c_str)

    # this val can come from anywhere
    int_val = builder.fadd(i32_ty(1.0), i32_ty(3.0))

    fmt_arg = builder.bitcast(global_fmt, voidptr_ty)
    builder.call(printf, [fmt_arg, c_str, int_val])

    builder.ret_void()

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    # print(str(m))
    # module_ref = llvm.parse_assembly(str(module))

    llvm_module = llvm.parse_assembly(str(m))
    tm = llvm.Target.from_default_triple().create_target_machine()

    with llvm.create_mcjit_compiler(llvm_module, tm) as ee:
        ee.finalize_object()
        fptr = ee.get_function_address("main")
        py_func = CFUNCTYPE(None)(fptr)
        py_func()
        
    llvm_ir = str(m)
    engine = create_execution_engine()
    mod = compile_ir(engine, llvm_ir)

    module_ref = llvm.parse_assembly(str(m))
    module_ref.verify()

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine(codemodel="small")

    m.triple = llvm.get_default_triple()
    m.data_layout = target_machine.target_data

    obj = target_machine.emit_object(module_ref)
    open('demo.o', 'wb').write(obj)
    os.system("clang demo.o -o demo")
    os.system("./demo")

if __name__ == "__main__":
    main()
    
        # %1 = getelementptr [4 x i8],[4 x i8]* @.fstr, i64 0, i64 0