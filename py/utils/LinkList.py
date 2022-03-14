"""
utils.LinkList
链表的实现
"""
from typing import Optional


class Node:
    """
    节点类
    """
    def __init__(self, item):
        self.item = item
        self.prev = None
        self.next = None


class DoubleCircleLinkList:
    """
    双向循环链表类
    """
    def __init__(self):
        self.__count = 0
        self.__head = None

    def length(self) -> int:
        """
        获取链表长度
        :return: int
        """
        return self.__count

    def head(self) -> Optional[Node]:
        """
        返回链表头指向的节点，空链表返回None
        :return: Node or None
        """
        return self.__head

    def is_empty(self) -> bool:
        """
        判断是否为空链表
        :return: bool
        """
        return self.__head is None

    def getNode(self, index: int) -> Optional[Node]:
        """
        根据索引获取节点
        正向:表头 --> 表头前驱   反向:表头前驱 --> 表头后继
        例如:index=0获取链表头部节点，index=-1获取链表尾部节点
        超出索引范围则返回None
        :param index: int  索引
        :return: Node or None
        """
        if self.is_empty():
            return None
        if (index >= 0 and self.__count <= index) or (index < 0 and self.__count < abs(index)):
            return None
        targetNode = self.__head

        pos = index
        if index < 0:
            pos = self.__count + index
        if pos < self.__count / 2:
            for i in range(pos):
                targetNode = targetNode.next
        else:
            for i in range(0, (pos - self.__count), -1):
                targetNode = targetNode.prev

        return targetNode

    def node_index(self, node: Node) -> Optional[int]:
        """
        返回节点在链表中的索引，若节点不在链表中则返回None
        :param node: Node 节点
        :return: int or None
        """
        if type(node) is not Node:
            print("not Node")
            return None
        if self.is_empty():
            return None
        nodes = self.__head
        for i in range(self.__count):
            if id(node) == id(nodes):
                return i
            else:
                nodes = nodes.next
        return None

    def index(self, item) -> Optional[int]:
        """
        返回正序查找第一个匹配节点的值的索引，找不到则返回None
        :param item: object
        :return: int or None
        """
        if self.is_empty():
            return None
        targetNode = self.__head
        for i in range(self.__count):
            if targetNode.item == item:
                return i
            else:
                targetNode = targetNode.next
        return None

    def index_reverse(self, item) -> Optional[int]:
        """
        返回逆序查找第一个匹配节点的值的索引，找不到则返回None
        :param item: object
        :return: int or None
        """
        if self.is_empty():
            return None
        targetNode = self.__head.prev
        for i in range(-1, self.__count * -1 - 1, -1):
            if targetNode.item == item:
                return self.__count + i
            else:
                targetNode = targetNode.prev
        return None

    def insert(self, item, index: int) -> int:
        """
        在指定索引位置插入值为item的Node,index超过原来的索引则头部插入或尾部追加
        返回: 插入后Node的索引值
        :param item: object
        :param index: int
        :return: int
        """
        if self.is_empty():
            self.__head = Node(item)
            self.__head.prev = self.__head
            self.__head.next = self.__head
            self.__count += 1
            return 0
        pos = index
        targetNode = self.__head
        if index > self.__count:
            pos = self.__count
        if index < 0:
            pos = self.__count + index
            if pos < 0:
                pos = 0

        if pos < self.__count:
            targetNode = self.getNode(pos)

        Node_insert = Node(item)
        if pos == 0:
            self.__head = Node_insert
        Node_insert.next = targetNode
        Node_insert.prev = targetNode.prev
        Node_insert.prev.next = Node_insert
        targetNode.prev = Node_insert

        self.__count += 1

        return pos

    def add(self, item) -> None:
        """
        往链表头部插入节点
        :param item: object
        :return: None
        """
        self.insert(item, 0)

    def append(self, item) -> None:
        """
        往链表尾部插入节点
        :param item: object
        :return: None
        """
        self.insert(item, self.length())

    def pop(self, index: int = -1) -> Optional[dict]:
        """
        根据索引移除节点(默认最后一个节点)，并返回移除节点的值的字典；若链表为空或超出索引范围，返回None
        :param index: int
        :return: dict or None
        """
        if self.is_empty():
            return None
        if (index >= 0 and self.__count <= index) or (index < 0 and self.__count < abs(index)):
            return None
        pos = index
        if index < 0:
            pos = self.__count + index

        targetNode = self.getNode(pos)

        if self.__count == 1:
            self.__head = None
        else:
            if pos == 0:
                self.__head = self.__head.next
            targetNode.prev.next = targetNode.next
            targetNode.next.prev = targetNode.prev

        result ={"result": targetNode.item}
        targetNode.item = None
        targetNode.prev = None
        targetNode.next = None

        self.__count -= 1

        return result

    def remove(self, item) -> Optional[int]:
        """
        正序查找第一个匹配值节点然后移除，返回被移除节点的原索引；找不到则返回None
        :param item: object
        :return: int or None
        """
        pos = self.index(item)
        if pos is not None:
            self.pop(pos)

        return pos

    def clean(self) -> None:
        """
        清空链表
        :return: None
        """
        while self.__count > 0:
            self.pop()
