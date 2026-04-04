import vllm, pkgutil, importlib

for m in pkgutil.walk_packages(vllm.__path__, prefix='vllm.'):
    try:
        mod = importlib.import_module(m.name)
        if hasattr(mod, 'ReasoningConfig'):
            print(m.name)
    except:
        pass