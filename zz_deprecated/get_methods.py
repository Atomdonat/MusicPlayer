def get_methods():
    # get modules
    modules = []
    for file in os.listdir(absolute_path('code_backend')):
        if file.endswith('.py') and file != '__init__.py':
            modules.append(file[:-3])

    # get methods
    methods = {}
    for module in modules:
        i = importlib.import_module(f"code_backend.{module}")
        module_name = i.__name__
        methods[module_name] = [name for name, obj in inspect.getmembers(i, inspect.isfunction) if inspect.getmodule(obj) == i]

    return methods

if __name__ == '__main__':
    """"""