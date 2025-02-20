import importlib
import logging

def get_class_from_string(class_path):
    """Import a class from a string path."""
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)
