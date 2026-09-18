from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def bfs_traversal(root):
    """
    Perform a breadth-first traversal of a binary tree and return a list of lists,
    where each inner list represents a level of the tree.

    Parameters:
    root (TreeNode): The root node of the binary tree.

    Returns:
    list of list of int: A list of lists, where each sublist contains the values of nodes
                          at the corresponding level of the tree.
    """
    if not root:
        return []

    queue = deque([root])
    result = []

    while queue:
        level_size = len(queue)
        current_level = []

        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(current_level)

    return result