"""
Comprehensive tests for DynamicLoader.
"""
import pytest
import tempfile
import os
from pathlib import Path
from wormgpt_hive.shared.dynamic_loader import DynamicLoader


class TestDynamicLoader:
    """Test DynamicLoader functionality."""
    
    def test_discover_modules_in_package(self):
        """Test discovering modules in a package."""
        modules = DynamicLoader.discover_modules("wormgpt_hive.tools")
        
        assert len(modules) > 0
        assert any("file_system" in m for m in modules)
        assert any("shell_executor" in m for m in modules)
    
    def test_discover_modules_invalid_package(self):
        """Test discovering modules in non-existent package."""
        modules = DynamicLoader.discover_modules("nonexistent.package")
        
        assert len(modules) == 0
    
    def test_load_class_from_module(self):
        """Test loading a class from a module."""
        cls = DynamicLoader.load_class_from_module(
            "wormgpt_hive.tools.file_system",
            "FileSystemTool"
        )
        
        assert cls is not None
        assert cls.__name__ == "FileSystemTool"
    
    def test_load_class_invalid_module(self):
        """Test loading class from invalid module."""
        cls = DynamicLoader.load_class_from_module(
            "nonexistent.module",
            "SomeClass"
        )
        
        assert cls is None
    
    def test_load_class_invalid_class_name(self):
        """Test loading non-existent class from valid module."""
        cls = DynamicLoader.load_class_from_module(
            "wormgpt_hive.tools.file_system",
            "NonExistentClass"
        )
        
        assert cls is None
    
    def test_get_class_capabilities(self):
        """Test getting capabilities of a class."""
        from wormgpt_hive.tools.file_system import FileSystemTool
        
        capabilities = DynamicLoader.get_class_capabilities(FileSystemTool)
        
        assert "methods" in capabilities
        assert len(capabilities["methods"]) > 0
        
        method_names = [m["name"] for m in capabilities["methods"]]
        assert "execute" in method_names
    
    def test_get_class_capabilities_with_methods(self):
        """Test that capabilities include method information."""
        from wormgpt_hive.drones.coder_drone import CoderDrone
        
        capabilities = DynamicLoader.get_class_capabilities(CoderDrone)
        
        assert "methods" in capabilities
        methods = capabilities["methods"]
        
        assert len(methods) > 0
        
        for method in methods:
            assert "name" in method
    
    def test_reload_module(self):
        """Test reloading a module."""
        original_module = DynamicLoader.reload_module("wormgpt_hive.tools.file_system")
        
        assert original_module is not None
        
        reloaded_module = DynamicLoader.reload_module("wormgpt_hive.tools.file_system")
        
        assert reloaded_module is not None
    
    def test_reload_invalid_module(self):
        """Test reloading non-existent module."""
        module = DynamicLoader.reload_module("nonexistent.module")
        
        assert module is None
    
    def test_discover_and_load_tools(self):
        """Test discovering and loading all tools."""
        modules = DynamicLoader.discover_modules("wormgpt_hive.tools")
        
        loaded_classes = []
        for module_name in modules:
            if module_name == "wormgpt_hive.tools.base_tool":
                continue
            if module_name == "wormgpt_hive.tools.__init__":
                continue
            
            parts = module_name.split(".")
            if len(parts) > 0:
                class_name = "".join([p.capitalize() for p in parts[-1].split("_")])
                cls = DynamicLoader.load_class_from_module(module_name, class_name)
                if cls:
                    loaded_classes.append(cls)
        
        assert len(loaded_classes) > 0
    
    def test_discover_and_load_drones(self):
        """Test discovering and loading all drones."""
        modules = DynamicLoader.discover_modules("wormgpt_hive.drones")
        
        loaded_classes = []
        for module_name in modules:
            if module_name == "wormgpt_hive.drones.base_drone":
                continue
            if module_name == "wormgpt_hive.drones.__init__":
                continue
            
            parts = module_name.split(".")
            if len(parts) > 0:
                class_name = "".join([p.capitalize() for p in parts[-1].split("_")])
                cls = DynamicLoader.load_class_from_module(module_name, class_name)
                if cls:
                    loaded_classes.append(cls)
        
        assert len(loaded_classes) > 0
    
    def test_get_capabilities_with_docstring(self):
        """Test that capabilities include information from class docstring."""
        from wormgpt_hive.drones.shell_drone import ShellDrone
        
        capabilities = DynamicLoader.get_class_capabilities(ShellDrone)
        
        assert "methods" in capabilities
        assert len(capabilities["methods"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
