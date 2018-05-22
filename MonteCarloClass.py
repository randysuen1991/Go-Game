import math as mt
import numpy as np
import UserFunction as UF
import copy as cp


##  ---------------------------------------------------------------------   ##
##  This file builds the fundamental classes for Monte Carlo Tree Search.   ##
##  ------------------------------------------------------------------------##


class MonteCarlo(object):
    # These are some parameters needed in the Monte Carlo Tree Search
    temperature = 1
    exploration = 5
    # This function is to be used for updating the uct of children of a node.
    def Update_Children_UCT(self):
        children = self.children
        for child in children : 
            try :
                child.uct = child.win_value / child.n + 5 * child.prior_pb * np.sqrt(child._parent.n) / (1 + child.n)
            except ZeroDivisionError :
                child.uct = 5 * child.prior_pb * np.sqrt(child._parent.n) / (1 + child.n)
    
    # This function is to be used for computing the posterior probability of a node.
    def Compute_Children_Post_Pb(self):
        children_n_sum = 0
        for child in self.children :
            children_n_sum += child.n ** (1/self.temperature)
        try :
            return [child.n ** (1/self.temperature)/children_n_sum for child in self.children]
        except ZeroDivisionError :
            print("This node ",self," hasn't been visited.")
    # This function is to be used for creating new children for a node.
    def Initialize_Children(self):
        actions = cp.copy(self.board.legal_actions)
        for action in actions :
            new_board = cp.deepcopy(self.board)
            new_board.Play(color=-self._color,pos=(action[0]+1,action[1]+1))
            child = MCNode(board = new_board,_parent=self,_action=action,_color=-self._color)
            # The probability is pre-determined
            child.prior_pb = (1 + np.random.uniform(0,0.1)) / len(self.board.legal_actions)
            self.children.append(child)
            
    # This function would return all the offspring of a node(includin itself).
    def Nodes_To_List(self):
        nodes = []
        return self._Traverse_Children(nodes)
    
    def _Traverse_Children(self,nodes):
        nodes.append(self)
        if self.children == [] : return []
        for child in self.children :
            childs = child._Traverse_Children(nodes)
        return nodes + childs
    @classmethod
    def Create_More_Info(cls):
        raise NotImplementedError
        
class MCNode(MonteCarlo):
    def __init__(self,board,**kwags):
        self.n = kwags.get("n",0)
        # The _color means the last player of the current board situation.
        self._color = kwags.get("_color",-1)
        self._parent = kwags.get("_parent")
        self.board = board
        self.uct = 0
        self._win_value = 0
        self._prior_pb = 0
        self._post_pb = 0
        self.children = []
        self._action = kwags.get("_action")
        # The r value indicates whether the current color wins or not
        self.r = 0
        
    # This method returns the AtariGo object to a MCNode.
    @classmethod
    def From_AtariGo(cls,board):
        return cls(board = board,_color = board._color)
        
    @property
    def prior_pb(self):
        return self._prior_pb
    @prior_pb.setter
    def prior_pb(self,value):
        self._prior_pb = value
        self.uct =  5 * self.prior_pb * mt.sqrt(self._parent.n) / (1 + self.n)       
    @property 
    def win_value(self):
        return self._win_value
    @win_value.setter
    def win_value(self,value):
        self._win_value = value
        self.uct = self._win_value / self.n + self.exploration * self.prior_pb * mt.sqrt(self._parent.n) / (1 + self.n)
    
    @classmethod
    def Create_More_Infor(cls):
        pass

class MCTree(MonteCarlo):
    def __init__(self,board):
        self._root = MCNode(board,n=1)
        self._root.Initialize_Children()
        self.path = []
        
    def Traversal(self,node):
        if node.children == [] : return
        uct = [child.uct for child in node.children]
        UF.Print_Board(node.board)
        self.Traversal(node.children[np.argmax(uct)])       
    
    def Execute(self,node):
        new_node = self.Search(node)
        color = self.Repeat(node = new_node)
        self.Backup(node = new_node._parent ,color=color)
    def Search(self,node):
        if node.children ==[] : return node
        node.n += 1
        node.Update_Children_UCT()
        uct = [child.uct for child in node.children]
        return self.Search(node.children[np.argmax(uct)])
    def Repeat(self,node):
        node.n = node.n + 1
        node.Initialize_Children()
        color = node.board.Compute_Scores()
        # The set value should be the visiting number of parent
        # There should be a function to generate p, v = f(s)
        if node._color == color: 
            node.win_value += 1
            node.r = 1
        else : 
            node.win_value -= 1
            node.r = -1
        return color
    def Backup(self,node,color):
        if node == self._root : return
        if node._color == color : node.win_value += 1
        else : node.win_value -= 1
        self.Backup(node._parent,color)
        
    # This function moves one step to the node with the largest visit time.
    def Move(self,node):
        children = node.children
        n_list = [child.n for child in children]
        return children[np.argmax(n_list)]

class AtariTree(MCTree):
    def __init__(self,board):
        super().__init__(board)

if __name__ == "__main__":
    pass
