from __future__ import annotations

import pickle


class Node:
    """A node in a Tree connecting to multiple branch nodes by letter-labeled edges.

    Attributes
    ----------
    branch_nodes : dict[str, Node]
        Mapping of edge letter to node connecting to edge.
    terminal : bool
        Whether the edges of the node from the root node makes up a valid word.
    """

    def __init__(self) -> None:
        """Initialises an new node with no branches."""
        self.branch_nodes: dict[str, Node] = {}
        self.terminal = False  # if a node is a terminal node, the word formed by the letter edges is a valid word

    def add_branch(self, edge: str, node: Node):
        """Add a branch node and the edge that it connects to.

        Parameters
        ----------
        edge : str
            Single-character string to represent the edge that when followed leads to the branch node.
        node : Node
            Branch node connected by the edge.

        Raises
        ------
        ValueError
            If the edge going out of the node already exists.
        """
        edge = edge.upper()
        if self.branch_nodes.get(edge) is not None:
            raise ValueError(f"Edge '{edge}' already exists.")
        self.branch_nodes[edge] = node

    def get_branch(self, edge: str) -> Node | None:
        """Get a branch node by following the edge it connects to.

        Parameters
        ----------
        edge : str
            Single-character string.

        Returns
        -------
        Node | None
            Branch node found, or None if no such branch exists.
        """
        return self.branch_nodes.get(edge.upper())


class Tree:
    """A tree with nodes and connecting edges that represent an entire dictionary."""

    def __init__(self, root_node: Node) -> None:
        """Initialise a tree with the given root node.

        Parameters
        ----------
        root_node : Node
            Root node.
        """
        self.root_node = root_node

    @staticmethod
    def build_from_list(word_list: list[str]) -> Tree:
        """Build the tree from list of all valid words.

        Parameters
        ----------
        word_list : list[str]
            All valid words.

        Returns
        -------
        Tree
            Tree created.
        """
        # build dictionary tree
        root_node = Node()
        for word in word_list:
            current_node = root_node

            for letter in word:
                next_node = current_node.get_branch(letter)
                if not next_node:
                    next_node = Node()
                    current_node.add_branch(letter, next_node)
                current_node = next_node

            current_node.terminal = True

        return Tree(root_node)

    @staticmethod
    def build_from_save(filepath: str) -> Tree:
        """Build the tree from a .pickle file.

        Parameters
        ----------
        filepath : str
            Filepath to .pickle file.

        Returns
        -------
        Tree
            Tree created.
        """
        with open(filepath, "rb") as f:
            root_node = pickle.load(f)
        return Tree(root_node)

    def save(self, filepath: str):
        """Save the tree as a .pickle file.

        Parameters
        ----------
        filepath : str
            Filepath of .pickle file.
        """
        with open(filepath, "wb") as f:
            pickle.dump(self.root_node, f)

    def get_node(self, path: str) -> Node:
        """Get a node given the edges to the node, starting from the root node.

        Parameters
        ----------
        path : str
            All edge letters combined.

        Returns
        -------
        Node | None
            Branch node found, or None if no such branch exists.

        Raises
        ------
        KeyError
            If path to node cannot be found.
        """
        current_node = self.root_node
        for letter in path.upper():
            next_node = current_node.get_branch(letter)
            if not next_node:
                raise KeyError(f"Path '{path}' to node does not exist")
            current_node = next_node
        return current_node

    def lookup(self, word: str) -> Node | None:
        """Check if a word exists in the tree.

        Checks if the letters in the word form a valid edge path and the branch node found is a terminal node.

        Parameters
        ----------
        word : str
            Word to lookup.

        Returns
        -------
        Node | None
            Branch node found by following the edges of the word, or None if no such branch exists.
        """
        try:
            found_node = self.get_node(word.upper())
            if found_node.terminal:
                return found_node
        except KeyError:
            pass


if __name__ == "__main__":
    with open("assets/CSW21.txt", "r") as f:
        word_list = f.read().split()
    d = Tree.build_from_list(word_list)
    d.save("assets/CSW21.pickle")
