"""custom object decoder to convert a JSON into a python object"""
class ObjectDecoder:
    """
    Allow to convert JSON like datastructure in Python object.
    """
    def child2object(self, name, node):
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

        if isinstance(node, int):
            pyobj = node
            return pyobj
        if isinstance(node, list):
            setattr(pyobj, name, [])
            for item in node:
                getattr(pyobj, name).append(self.child2object(name, item))
            return pyobj
        if isinstance(node, dict):
            for child_name, child in node.items():
                self.add_node(child_name, pyobj, child)
        else:
            setattr(pyobj, name, node)
        return pyobj

    def add_node(self, name, pyobj, child):
        """
        Add node in generic Python object
        """
        if isinstance(child, list):
            setattr(pyobj, name, [])
            for item in child:
                getattr(pyobj, name).append(self.child2object(name, item))
        elif isinstance(child, dict):
            setattr(pyobj, name, self.child2object(name, child))
        else:
            setattr(pyobj, name, child)

    def dict2object(self, node):
        pytype = type('response', (object, ), {})
        pyobj = pytype()
        for child_key, child_node in node.items():
            self.add_node(child_key, pyobj, child_node)
        return pyobj