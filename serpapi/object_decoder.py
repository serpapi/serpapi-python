"""custom object decoder"""
class ObjectDecoder:
    """
    Allow to convert JSON like datastructure in Python object.
    """
    def dict2object(self, name, node):
        """Make python object from dict
        Parameters
        ---
        name: str
            parent field name to start walk the node
        node: dict
            source dict structure to convert into object
        """
        pytype = type(name, (object, ), {})
        pyobj = pytype()

        if isinstance(node, list):
            setattr(pyobj, name, [])
            for item in node:
                getattr(pyobj, name).append(self.dict2object(name, item))
            return pyobj
        if isinstance(node, dict):
            for child_name, child in node.items():
                self.add_node(child_name, pyobj, child)
        else:
            setattr(pyobj, name, node)

        return pyobj

    def add_node(self, name, pyobj, child):
        """
        add node in object
        """
        if isinstance(child, list):
            setattr(pyobj, name, [])
            for item in child:
                getattr(pyobj, name).append(self.dict2object(name, item))
        elif isinstance(child, dict):
            setattr(pyobj, name, self.dict2object(name, child))
        else:
            setattr(pyobj, name, child)
