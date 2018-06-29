import numpy as np
import ExceptionClass as EC
import UserFunction as UF
import copy as cp
from collections import deque
##  ---------------------------------------------------------------------   ##
##  This file builds the fundamental classes for the Go game.               ##
##  ------------------------------------------------------------------------##

# This is an abstract class containing some functions for updating the board condition. 
class Go():
    # Initialize the position of the stones
    def Initialize(self):
        #Initialize the stones
        for i in range(self._size):
            for j in range(self._size):
                self.stones[i,j] = Stone()
    
        #Initialize the position and neighbor stones
        for i in range(self._size):
            pass
            for j in range(self._size):
                self.legal_actions.append((i,j))
                self.stones[i,j]._position = (i,j)
                self.Append_Neighbor_Stones((i,j))  
    
    def Append_Neighbor_Stones(self,pos):
        size = self._size
        row = pos[0]
        col = pos[1]
        stone = self.stones[row,col]
        if(row-1==-1):
            pass
        else:
            stone._neighbor_stones.append((row-1,col))
            stone.neighbor_stones_empty.append((row-1,col))
        if(row+1==size):
            pass
        else:
            stone._neighbor_stones.append((row+1,col))
            stone.neighbor_stones_empty.append((row+1,col))
        if(col-1==-1):
            pass
        else:
            stone._neighbor_stones.append((row,col-1))
            stone.neighbor_stones_empty.append((row,col-1))
        if(col+1==size):
            pass
        else:
            stone._neighbor_stones.append((row,col+1))
            stone.neighbor_stones_empty.append((row,col+1))

    def Check_Chain_Neighbor_And_Update_Scores(self,chain):
        stones = self.stones
        record = [0,0]
        both_color = False
        for pos in chain:
            for pos_tmp in stones[pos[0],pos[1]]._neighbor_stones:
                if stones[pos_tmp[0],pos_tmp[1]].condition == 1 :
                    record[0] = 1
                elif stones[pos_tmp[0],pos_tmp[1]].condition == -1 :
                    record[1] = 1
                if record == [1,1] :
                    both_color = True
                    break
            if both_color : break

        if not both_color :
            if record[0] == 1 : self.black_score += len(chain)
            elif record[1] == 1 : self.white_score += len(chain)
        
    def Compute_Scores_Recursive(self,history,pos):
        history_cp = cp.copy(history)
        stone = self.stones[pos[0],pos[1]]
        empty = cp.copy(stone.neighbor_stones_empty)
        return_history = [pos]
        for pos_tmp in empty :
            if pos_tmp not in history_cp:
                new_history = self.Compute_Scores_Recursive(history=history_cp + return_history,pos=pos_tmp)
                return_history = return_history + new_history
                history_cp = history_cp + return_history
        return return_history
    
    def Update_Neighbor_Before_Remove(self,pos):
        stones = self.stones
        stone = stones[pos[0],pos[1]]
        different = cp.copy(stone.neighbor_stones_different)
        for pos_tmp in different:
            stones[pos_tmp[0],pos_tmp[1]].neighbor_stones_different.remove(pos) 
            stones[pos_tmp[0],pos_tmp[1]].neighbor_stones_empty.append(pos)
    
    
    # Remove from board
    def Remove(self,history,pos):
        history.append(pos)
        stone = self.stones[pos[0],pos[1]]
        same = cp.copy(stone.neighbor_stones_same)
        for pos_tmp in same:
            if(pos_tmp not in history):
                self.Remove(history,pos_tmp)
        self.Update_Neighbor_Before_Remove(pos)
        stone.Clean()
        self.legal_actions.append(pos)
        self.Update_Neighbor_After_Remove(pos)
    # Update empty neighbor
    def Update_Neighbor_After_Remove(self,pos):
        stones = self.stones
        stone = stones[pos[0],pos[1]]
        _neighbor = stone._neighbor_stones
        for pos_tmp in _neighbor:
            if stones[pos_tmp[0],pos_tmp[1]].condition == 0 :
                stone.neighbor_stones_empty.append(pos_tmp)
                stones[pos_tmp[0],pos_tmp[1]].neighbor_stones_empty.append(pos)
        
    def Check_And_Remove(self,pos):
        stone= self.stones[pos[0],pos[1]]
#        UF.Print_Neighbor(self,pos)
        different = cp.copy(stone.neighbor_stones_different)
        # Check four directions if it could remove the oponent
        for pos_tmp in different:
            if not self.Check_Living(history=[],pos=pos_tmp):
#                print("EAT!!!!!!!!!!!!!!!!!!!\n")
                self.Remove(history=[],pos=pos_tmp)        
        
    # This recursive function check if the chain is living or not 
    def Check_Living(self,history,pos):
        stone = self.stones[pos[0],pos[1]]
        history.append(pos)
        # If there is an empty stone beside this stone, then it's living.
        if(len(stone.neighbor_stones_empty) > 0): return True
        # Recursively determine.
        same = cp.copy(stone.neighbor_stones_same)
        for pos_tmp in same:
            if(pos_tmp not in history):
                if self.Check_Living(history,pos_tmp): return True
        return False
    
    def Check_Suicide(self,pos):
        
        if not self.Check_Living(history=[],pos=pos):
#            print("Suicide!!!!!!!!!!!!!!!!!!!\n")
            self.Remove(history=[],pos=pos)
            
    def Update_Neighbor_Stones(self,pos,color):
        stones = self.stones
        stone = stones[pos[0],pos[1]]
        _neighbor = cp.copy(stone._neighbor_stones)
        for pos_tmp in _neighbor:
            row = pos_tmp[0]
            col = pos_tmp[1]
            if(stones[row,col].condition is color):
                stone.neighbor_stones_same = stone.neighbor_stones_same + stones[row,col].neighbor_stones_same
                stone.neighbor_stones_same.append(pos_tmp)
                self.Update_Neighbor_Stones_Same([pos],pos_tmp,pos)
            elif((stones[row,col].condition != color) and (stones[row,col].condition != 0)):
                stone.neighbor_stones_different.append(pos_tmp)
                stones[row,col].neighbor_stones_different.append(pos)
                stones[row,col].neighbor_stones_empty.remove(pos)
            else:
                if pos_tmp not in stone.neighbor_stones_empty:
                    stone.neighbor_stones_empty.append(pos_tmp)
                stones[pos_tmp[0],pos_tmp[1]].neighbor_stones_empty.remove(pos)
            
            
    def Update_Neighbor_Stones_Same(self,history,pos,new_pos):
        history.append(pos)
        stones = self.stones
        stone = stones[pos[0],pos[1]]
        same = cp.copy(stone.neighbor_stones_same)
        for pos_tmp in same:
            if(pos_tmp not in history):
                self.Update_Neighbor_Stones_Same(history,pos_tmp,new_pos)
        if(new_pos not in stone.neighbor_stones_same):
            stone.neighbor_stones_same.append(new_pos)
        if(new_pos in stone.neighbor_stones_empty):
            stone.neighbor_stones_empty.remove(new_pos)
class Stone():
    
    def __init__(self,cond=0):
        
        # Row and Col is the position of the stone.
        self._position = None
        # A list of poaitions of neighbor stones.
        self._neighbor_stones = []
        # Condition is an integer. It could be 0(empty), 1(black), -1(white).
        self.condition = cond  
        # A list of positions of neighbor stones with same color
        self.neighbor_stones_same = []
        # A list of positions of neighbor stones with different color
        self.neighbor_stones_different = []
        # A list of positions of neighbor with empty
        self.neighbor_stones_empty = []
        
    # Clean data
    def Clean(self):
        self.condition = 0
        self.neighbor_stones_same = []
        self.neighbor_stones_different = []
        self.neighbor_stones_empty = []
                
        
class Board(Go):
    
    def __str__(self):
        if self.black_score > self.white_score : deter = 1
        elif self.black_score == self.white_score : deter = 0
        else : deter = -1    
        out_str = "Black score: {} \nWhite score: {}\n".format(self.black_score,self.white_score)
        if deter == 1 : out_str = out_str + "Black Wins!"
        elif deter ==0 : out_str = out_str + "Tied!"
        else : out_str = out_str + "White Wins!"
        UF.Print_Board(self)
        return out_str
    
    def __init__(self,size,memory=8):        
        super().__init__()
        # _goba_size indicates the size of the GoBan
        self._size = size
        # Create the kis for GoBan
        self.stones = np.empty(shape=(size,size),dtype=object)
        #Initialize the stones
        self.legal_actions = []
        self.Initialize()
        # white_scoring and black_scoring indicate the scores of white and black
        self.white_score = 0
        self.black_score = 0
        # The history stores a list of tuples, the first indicates the color and the second indicates 
        # the position
        self.history = deque([])
        self.memory = memory
     

    # Compute the scores of the black and the white
    def Compute_Scores(self):
        history = []
        for i in range(self._size):
            for j in range(self._size):
                if (i,j) not in history : 
                    if self.stones[i][j].condition == 1 : self.black_score += 1
                    elif self.stones[i][j].condition == -1 : self.white_score += 1
                    else : 
                        sub_history = self.Compute_Scores_Recursive(history=[],pos=(i,j))
                        history += sub_history
                        self.Check_Chain_Neighbor_And_Update_Scores(sub_history)
        if self.black_score > self.white_score : return 1
        else : return -1
            
    # A Play is called
    def Play(self,color,pos):
        
        # change the coordinate
        pos_new = (pos[0]-1,pos[1]-1)
        
        # Initialize the scores
        self.black_score = 0
        self.white_score = 0
        stone = self.stones[pos_new[0],pos_new[1]]
        self.history.append((color,pos_new))
        if len(self.history) > self.memory :
            self.history.popleft()
        try:
            #If the site is already occupied, then it is against the rule.
            if(stone.condition != 0): raise EC.RuleError               
            stone.condition = color
            self.legal_actions.remove(pos_new)
            # Update neighbor stones
            self.Update_Neighbor_Stones(pos_new,color)
            # Check and Remove
            self.Check_And_Remove(pos_new)
            # Check Suicide
            self.Check_Suicide(pos_new)
        
        except EC.RuleError as RE: 
            print(RE)
        except IndexError:
            pass
        finally:
            pass
    
            
if __name__ == "__main__" :
    a = Board(size=5,memory=8)
    a.Play(color=1,pos=(0,1))
    stone = a.stones[0][1]
    print(stone._position, stone._neighbor_stones)