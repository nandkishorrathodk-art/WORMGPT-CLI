"""
Comprehensive tests for DynamicLoader.
"""
import pytest
import tempfile
import os
from pathlib import Path
from wormgpt_hive.shared.dynamic_loader import DynamicLoader
from wormgpt_hive.tools.base_tool import BaseTool
from wormgpt_hive.drones.base_drone import BaseDrone


class TestDynamicLoader:
    """Test DynamicLoader functionality."""
    
    def test_discover_modules_in_package(self):
        """Test discovering modules in a package."""
        package_path = "wormgpt_hive/tools"
        modules = DynamicLoader.discover_modules(package_path, BaseTool)
        
        assert len(modules) > 0
        assert "FileSystemTool" in modules or "ShellExecutorTool" in modules
    
    def test_discover_modules_invalid_package(self):
        """Test discovering modules in non-existent package."""
        modules = DynamicLoader.discover_modules("nonexistent/package", BaseTool)
        
        assert len(modules) == 0
    
    def test_load_tool_from_file(self):
        """Test loading a tool class from a file."""
        file_path = "wormgpt_hive/tools/file_system.py"
        cls = DynamicLoader.load_tool_from_file(file_path, "FileSystemTool")
        
        assert cls is not None
        assert cls.__name__ == "FileSystemTool"
    
    def test_load_tool_invalid_file(self):
        """Test loading tool from invalid file."""
        with pytest.raises(ImportError):
            DynamicLoader.load_tool_from_file("nonexistent/file.py", "SomeClass")
    
    def test_load_tool_invalid_class_name(self):
        """Test loading non-existent class from valid file."""
        file_path = "wormgpt_hive/tools/file_system.py"
        
        with pytest.raises(AttributeError):
            DynamicLoader.load_tool_from_file(file_path, "NonExistentClass")
    
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
        with pytest.raises(ImportError):
            DynamicLoader.reload_module("nonexistent.module")
    
    def test_discover_and_load_tools(self):
        """Test discovering and loading all tools."""
        package_path = "wormgpt_hive/tools"
        modules = DynamicLoader.discover_modules(package_path, BaseTool)
        
        assert len(modules) > 0
        assert any("FileSystemTool" in str(cls) for cls in modules.values())
    
    def test_discover_and_load_drones(self):
        """Test discovering and loading all drones."""
        package_path = "wormgpt_hive/drones"
        modules = DynamicLoader.discover_modules(package_path, BaseDrone)
        
        assert len(modules) > 0
        assert any("CoderDrone" in str(cls) for cls in modules.values())
    
    def test_get_capabilities_with_docstring(self):
        """Test that capabilities include information from class docstring."""
        from wormgpt_hive.drones.shell_drone import ShellDrone
        
        capabilities = DynamicLoader.get_class_capabilities(ShellDrone)
        
        assert "methods" in capabilities
        assert len(capabilities["methods"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
