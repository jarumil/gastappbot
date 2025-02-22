import importlib
import logging

def get_class_from_string(class_path):
    """
    Import a class from a string path.

    Parameters
    ----------
    class_path : str
        The dot-separated path to the class.

    Returns
    -------
    type
        The class type.
    """
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)
