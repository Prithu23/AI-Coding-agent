class Node:
    def __init__(self, data):
        """
        Initialize a new Node object with given data, a previous pointer, and a next pointer.
        """
        self.data = data
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        """
        Initialize a new DoublyLinkedList object with a head and a tail set to None.
        """
        self.head = None
        self.tail = None

    def insert(self, data):
        """
        Insert a new node with the given data into the DoublyLinkedList.
        If the list is empty, the new node becomes both the head and the tail.
        Otherwise, the new node is inserted at the end of the list.
        """
        new_node = Node(data)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node

    def delete(self, data):
        """
        Delete the first occurrence of the given data from the DoublyLinkedList.
        If the data is not found, return False.
        If the node to be deleted is the head or tail, update the head or tail accordingly.
        """
        current = self.head
        while current:
            if current.data == data:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                return True
            current = current.next
        return False

    def search(self, data):
        """
        Search for the given data in the DoublyLinkedList.
        Return True if the data is found, False otherwise.
        """
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False