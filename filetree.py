import os

current_file = ""
tree = None

class Node:

    def __init__(self, name, path):
        self.__name = name
        self.__children = []
        self._value = 0

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value
        
    def get_children(self):
        return self.__children

    def get_name(self):
        return self.__name

    def add_child(self, child):
        self.__children.append(child)
        self._value += child._value

    def sort_children(self):
        self.__children.sort(key = lambda node: node._value)
        for i in range(len(self.__children) - 2, 0, -2):
            self.__children.append(self.__children.pop(i))

def create_file_tree(start):
    global tree
    tree = file_tree_from(start, start)

def file_tree_from(name, path):
    current = Node(name, path)
    try:
        subfiles = os.listdir(path)
        for file in subfiles:
            current.add_child(file_tree_from(file, path+"/"+file))
            
        current.sort_children()

    except NotADirectoryError:
        global current_file
        current_file = name
        current.set_value(os.path.getsize(path))

    except FileNotFoundError:
        pass

    except PermissionError:
        pass

    return current
