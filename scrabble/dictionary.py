from __future__ import annotations
from typing import Callable

import pickle


class Node:
    """A node in a DAWG connecting to multiple children by letter-labeled edges"""

    def __init__(self) -> None:
        self.children: dict[str, Node] = {}
        self.terminal = False  # if a node is a terminal node, the word formed by the letter edges is a valid word

    def add_child(self, edge: str, node: Node):
        """
        Add a child node and the edge that it connects to
        :param edge: letter to represent the edge
        :param node: child node
        :return:
        """
        assert self.children.get(edge.upper()) is None
        self.children[edge.upper()] = node

    def get_child(self, edge: str) -> Node | None:
        """
        Get a child node by following the edge it connects to
        :param edge: letter to represent the edge
        :return: child node
        """
        return self.children.get(edge.upper())


class Tree:
    def __init__(self) -> None:
        self.root_node: Node = Node()

    def build_from_txt(self, filepath: str) -> None:
        """
        Build the dictionary tree from a txt file of all valid words
        :param filepath: filepath to txt file with all valid words
        :return:
        """
        with open(filepath, "r") as f:
            word_list = f.read().split()

        # build dictionary tree
        self.root_node = Node()
        for word in word_list:
            current_node = self.root_node

            for letter in word:
                next_node = current_node.get_child(letter)
                if not next_node:
                    next_node = Node()
                    current_node.add_child(letter, next_node)
                current_node = next_node

            current_node.terminal = True

    def build_from_save(self, filepath: str) -> None:
        """
        Build the dictionary tree from a pickle file
        :param filepath: filepath to the pickle file
        :return:
        """
        with open(filepath, "rb") as f:
            self.root_node = pickle.load(f)

    def save(self, filepath: str):
        """
        Save the dictionary tree as a pickle file
        :param filepath: filepath of the pickle file
        :return:
        """
        with open(filepath, "wb") as f:
            pickle.dump(self.root_node, f)

    def get_node(self, path: str) -> Node:
        """
        Get a node given the path to the node
        :param path: all edges combined as a string (partial word)
        :return: node at path
        :raises KeyError: if path does not exist
        """
        current_node = self.root_node
        for letter in path.upper():
            next_node = current_node.get_child(letter)
            if not next_node:
                raise KeyError(f"Could not find node at path '{path}'")
            current_node = next_node
        return current_node

    def lookup(self, word: str) -> Node | None:
        """
        Check if a word exists in the tree
        :param word: word to check in upercase
        :return: terminal node if word exists, else None
        """
        found_node = self.get_node(word)
        if found_node is not None and found_node.terminal:
            return found_node
        return None


if __name__ == "__main__":
    d = Tree()

    d.build_from_txt("assets/CSW21.txt")
    d.save("assets/CSW21.pickle")
