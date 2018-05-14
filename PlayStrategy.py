import GoClass as GC
import UserFunction as UF
import numpy as np
import MonteCarloClass as MCC
import copy as cp
import random

# Board object is from GoClass.py, and num_plays indicate how many plays would be executed. 
def Random_Play(board,num_plays):
    
    def Find_Empty(Board):
        empty = []
        size = Board._size
        for i in range(size):
            for j in range(size):
                if Board.stones[i,j].condition == 0 :
                    empty.append((i+1,j+1))
        return empty
    
        
    for i in range(num_plays):
        empty = Find_Empty(board)
        integer = np.random.randint(len(empty))
        if i % 2 == 0:
            board.Play(1,pos=empty[integer])
        else :
            board.Play(-1,pos=empty[integer])
    
    board.Compute_Scores()
    print(board)
    

def MonteCarlo_Play(board,num_trees,num_moves,num_simulations):
    nodes = []
    trees = []
    def Run_Tree(num_moves,num_simulations):
        nodes_move = []
        tree = MCC.MCTree(board)
        color = 1
        node = tree._root
        for i in range(num_moves+1) :
            if node._action == None :
                print("Turn:",i,", ","Move:", node._action,", ","Color: None\n")
            else :
                if node._color == 1 :
                    print("Turn:",i,", ","Move:", (node._action[0]+1,node._action[1]+1),", ","Color: Black\n")
                else :
                    print("Turn:",i,", ","Move:", (node._action[0]+1,node._action[1]+1),", ","Color: White\n")
            UF.Print_Board(node.board)
            nodes_move.append(node)
            for j in range(num_simulations):
                tree.Execute(node)
            node = tree.Move(node)
            color *= -1
        return tree, nodes_move
    
    for i in range(num_trees) :
        print("Game:",i+1,"\n")
        tree, nodes_move = Run_Tree(num_moves,num_simulations)
        nodes += nodes_move
        trees.append(tree)
    
    return trees, nodes

# This function will continue to play untill the number of move attains num_plays or 
# the player can't score more.

def Score_Play(board,num_plays):
    
    
    def Decision(board,color,black_score=0,white_score=0):
        if color == 1 : score = black_score
        else :  score = white_score
        scores = []
        actions = []
        for action in board.legal_actions :
            board_test = cp.deepcopy(board)
            board_test.Play(color=color,pos=(action[0]+1,action[1]+1))
            board_test.Compute_Scores()
            if color == 1 : 
                if board_test.black_score <= score :
                    pass
                else :
                    scores.append(board_test.black_score)
                    actions.append(action)
                
            else :
                if board_test.white_score <= score :
                    pass
                else :
                    scores.append(board_test.white_score)
                    actions.append(action)
            del board_test
        
        if len(scores) == 0 : return 
        else : 
            candidate = np.argwhere(scores == np.amax(scores))
            candidate = candidate.flatten().tolist()
            if len(candidate) == 1 :
                return actions[candidate[0]]
            else :
                return actions[random.choice(candidate)]
    
    num_pass = 0
    # Black starts
    color = 1
    for i in range(num_plays):
        if i == 0 : action = Decision(board,color)
        else : action = Decision(board,color,board.black_score,board.white_score)
        if action == None :
            num_pass += 1
            color *= -1
            if num_pass == 2 :
                board.Compute_Scores()
                print("Two passes, the Game is over!\n")
                print(board)
                break
            continue
        board.Play(color=color,pos=(action[0]+1,action[1]+1))
        if color == 1 :
            print("Turn:",i+1,", ","Move:", (action[0]+1,action[1]+1),", ","Color: Black\n")
        else :
            print("Turn:",i+1,", ","Move:", (action[0]+1,action[1]+1),", ","Color: White\n")
        board.Compute_Scores()
        print(board,"\n")
        color *= -1
        
        
def MonteCarlo_Play_Atari(board,num_trees,num_moves,num_simulations):
    nodes = []
    trees = []
    def Run_Tree(num_moves,num_simulations):
        nodes_move = []
        tree = MCC.MCTree(board)
        color = 1
        node = tree._root
        for i in range(num_moves) :
            if node._action == None :
                print("Turn:",i+1,", ","Move:", node._action,", ","Color: None\n")
            else :
                if node._color == 1 :
                    print("Turn:",i+1,", ","Move:", (node._action[0]+1,node._action[1]+1),", ","Color: Black\n")
                else :
                    print("Turn:",i+1,", ","Move:", (node._action[0]+1,node._action[1]+1),", ","Color: White\n")
            UF.Print_Board(node.board)
            nodes_move.append(node)
            for j in range(num_simulations):
                tree.Execute(node)
            node = tree.Move(node)
            color *= -1
        return tree, nodes_move
    
    for i in range(num_trees) :
        print("Game:",i+1,"\n")
        tree, nodes_move = Run_Tree(num_moves,num_simulations)
        nodes.append(nodes_move)
        trees.append(tree)
    
    return trees, nodes