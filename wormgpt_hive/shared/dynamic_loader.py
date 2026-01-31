import importlib
import importlib.util
import inspect
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Type


class DynamicLoader:
    
    @staticmethod
    def discover_modules(package_path: str, base_class: Type) -> Dict[str, Type]:
        modules = {}
        package_dir = Path(package_path)
        
        if not package_dir.exists():
            return modules
        
        for file_path in package_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            
            module_name = file_path.stem
            try:
                spec = importlib.util.spec_from_file_location(
                    f"dynamic.{module_name}", file_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[spec.name] = module
                    spec.loader.exec_module(module)
                    
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, base_class) and 
                            obj is not base_class and
                            obj.__module__ == module.__name__):
                            modules[name] = obj
            except Exception as e:
                print(f"Failed to load {file_path}: {e}")
        
        return modules
    
    @staticmethod
    def reload_module(module_path: str) -> Any:
        try:
            if module_path in sys.modules:
                module = sys.modules[module_path]
                importlib.reload(module)
                return module
            else:
                return importlib.import_module(module_path)
        except Exception as e:
            raise ImportError(f"Failed to reload module {module_path}: {e}")
    
    @staticmethod
    def load_tool_from_file(file_path: str, tool_class_name: str) -> Type:
        spec = importlib.util.spec_from_file_location("dynamic_tool", file_path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not load spec from {file_path}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        
        if not hasattr(module, tool_class_name):
            raise AttributeError(f"Tool class {tool_class_name} not found in {file_path}")
        
        return getattr(module, tool_class_name)
    
    @staticmethod
    def get_class_capabilities(cls: Type) -> Dict[str, Any]:
        capabilities = {
            "name": cls.__name__,
            "description": inspect.getdoc(cls) or "No description",
            "methods": []
        }
        
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if not name.startswith("_"):
                sig = inspect.signature(method)
                method_info = {
                    "name": name,
                    "description": inspect.getdoc(method) or "No description",
                    "parameters": [
                        {
                            "name": param_name,
                            "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any"
                        }
                        for param_name, param in sig.parameters.items()
                        if param_name != "self"
                    ]
                }
                capabilities["methods"].append(method_info)
        
        return capabilities
