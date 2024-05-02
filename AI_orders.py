#---------------
# MAIN FUNCTION
#---------------
def get_AI_orders(game_data, player_id):
    """ Return orders of AI.
    
    Parameters:
        game_data (dict): The dictionary containing game information.
        player_id (int) : The player ID of AI.

    Returns:
        The AI oders (str).
        
    Version:
        specification: Ismail Hafid Benchougra (v1 18/03/24)
        implementation: Ismail Hafid Benchougra, Lucas Paludetto (v1 24/03/24)
    """ 

    #--INITIALIZE--
    ia_player = "player" + str(player_id)

    if player_id == 1:
        other_player = "player2"
    elif player_id == 2 :
        other_player = "player1"
    
    #create a copy of the game_data dict
    game_data = deepcopy(game_data)

    #grow grass 
    game_data = grow_grass(game_data)
    
    
    move_historic = []

    #----------------------------------
    orders = ''

    if is_sheep_spawnable(game_data,ia_player) == True : #look if he can spawn a sheep then do it
        orders += "sheep"
        game_data = add_sheep(game_data,ia_player)

    
    for sheep in game_data[ia_player]["sheep"]:
        max_gain = 0
        optimal_move = None

        for move in get_all_moves(sheep, ia_player, other_player, move_historic, game_data):

            gain = get_move_gain(sheep, move, ia_player, other_player, game_data)
            if gain > max_gain:
                max_gain = gain
                optimal_move = move
        
        #print(term.move_y(term.height-7),"optimal move: ", optimal_move)
        #print(term.move_y(term.height-5)+ "gain : ",max_gain)

        move_historic.append(optimal_move) # add the move selected in historic move
        orders += decoder_move(optimal_move[0],orders) # decode the move in the correct syntax

    return orders

#-------------------------
# ALL FUNCTION FOR THE IA
#-------------------------

#----A STAR ALGORITHM----

def get_neighbors(coord, game_data):
    """
    This function gives a list of the neighbors coordinates around a given coordinate.

    Parameters:
        coord (tuple): The coordinate (row, col)
        game_data (dict): The dictionary containing game information.

    Returns:
        list: The list of neighboring coordinates that are valids.

     Version:
        specification: Lucas Paludetto (v1 16/03/24)
        implementation: Lucas Paludetto (v2 21/03/24)
    """
    neighbors = []
    row, col = coord
    
    sheep_list = []
    for player in ["player1", "player2"]:
        for sheep in game_data[player]["sheep"]:
            sheep_list.append(sheep[0])

    directions = [(-1,-1),(-1, 0),(-1, 1),
                  (0, -1),        (0 , 1),
                  (1, -1),( 1, 0),(1 , 1)]

    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc

        if is_in_board(game_data,(new_row,new_col)) == True\
            and is_a_rock(game_data,(new_row,new_col)) == False\
            and is_a_spawn(game_data,(new_row,new_col)) == False\
            and (new_row, new_col) not in sheep_list:
            neighbors.append((new_row, new_col))      
            
    return neighbors

def get_neighbors_without_filtring(coord,game_data):
    """
    This function gives a list of the neighbors coordinates around a given coordinate.

    Parameters:
        coord (tuple): The coordinate (row, col)
        game_data (dict): The dictionary containing game information.

    Returns:
        list: The list of neighboring coordinates that are valids.

     Version:
        specification: Lucas Paludetto (v1 16/03/24)
        implementation: Lucas Paludetto (v2 21/03/24)
    """
    neighbors = []
    row, col = coord

    directions = [(-1,-1),(-1, 0),(-1, 1),
                  (0, -1),        (0 , 1),
                  (1, -1),( 1, 0),(1 , 1)]

    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc

        if is_in_board(game_data,(new_row,new_col)) == True\
            and is_a_rock(game_data,(new_row,new_col)) == False:
            neighbors.append((new_row, new_col))      
            
    return neighbors

def reconstruct_path(came_from, current):
    """
    Reconstructs a path from a dictionary of predecessors and a final node.

    Parameters:
        came_from (dict): A dictionary containing the predecessors of each node in the path.
        current: The final node of the path.

    Returns:
        list: A list representing the reconstructed path from the start node to the current node.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (v1 21/03/24)
    """
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)

    return path[::-1]  

def heuristic(coord, coord_goal):
    """ This function gives the euclidian distance from a coord to a coord.
    (basically we use this to guide the a* algorithm to the goal coord)

    Parameters:
        coord (tuple): the start coord 
        coord_goal (tuple): the coord that we want to reach

    Returns: 
        distance (float): the euclidian distance 
        
    Version:
        specification: Leandro Bessa Lourenço (v1 16/03/24)
        implementation: Lucas Paludetto (v2 21/03/24)
    """
    x1, y1 = coord
    x2, y2 = coord_goal

    distance = ((x2-x1)**2 + (y2-y1)**2)**0.5
    return distance

def a_star(start_coord, goal_coord, game_data):
    """ This function is an implementation of an algorithm of pathfinding, the function gives the shortest path from 2 coords 

    Parameters:
        start_coord (tuple): the start coord
        goal_coord (tuple): the goal coord
        game_data (dict): The dictionary containing game information.

    Returns: 
        path (list): The path in a list given by recronstuct function.
        
    Version:
        specification: Leandro Bessa Lourenço (v1 16/03/24)
        implementation: Lucas Paludetto (v2 21/03/24)
    """
    closed_set = [] # nodes already evaluated
    open_set = [] # nodes discovered but not yet evaluated
    came_from = {} # most efficient path to reach from
    g_score = {} # cost to get to that node from start
    f_score = {} # cost to get to goal from start node via that node

    for coord in game_data["dim_board"]:
        g_score[coord] = float("inf") # intialize cost for every node to inf
    
    for coord in game_data["dim_board"]:
        f_score[coord] = float("inf")

    g_score[start_coord] = 0
    f_score[start_coord] = heuristic(start_coord, goal_coord) # cost for start is only h(x)

    open_set.append(start_coord)

    while len(open_set) > 0 :

        min_val = float("inf")
        for coord in open_set:
            if f_score[coord] < min_val:
                min_val = f_score[coord]
                min_node = coord

        current = min_node # set that node to current

        if current == goal_coord:
            return reconstruct_path(came_from, current)
        
        open_set.remove(current)  # remove node from set to be evaluated and
        closed_set.append(current) # add it to set of evaluated nodes

        neighbors = get_neighbors(current, game_data)
        for neighbor in neighbors: # check neighbors of current node

            if neighbor not in closed_set: # consider neighbor node only if it's not already evaluated

                if neighbor not in open_set: # add neighbor to set of nodes to be evaluated
                    open_set.append(neighbor)

                # dist from start to neighbor through current 
                tentative_g_score = g_score[current] + 1  
                
                # found a better path to reach neighbor
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current  
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal_coord)

    return False

#---GET MOVES---
        
def get_all_moves_in_1_direction(sheep,game_data):
    """ Gets all the moves in one direction from a sheep's position.
    
    Parameters:
        sheep (list) Info of the given sheep.
        game_data (dict): The dictionary containing game information.

    Returns:
        Returns all possible moves for the given sheep.
        
    Version:
        specification: Leandro Bessa Lourenço (v2 25/03/24)
        implementation: Ismail Hafid Benchougra (v2 26/03/24)
    """ 
    sheep_position = sheep[0]
    sheep_y = sheep_position[0]
    sheep_x = sheep_position[1]
    neighbors = get_neighbors(sheep[0],game_data)
    neighbors_2 = get_neighbors_without_filtring(sheep[0],game_data)

    all_possible_moves = []
    # eat
    all_possible_moves.append([sheep_y,sheep_x,"eat"])
    #move
    for neighbor in neighbors:
        all_possible_moves.append([sheep_y , sheep_x , neighbor[0] , neighbor[1] , "move"]) 

    #attack   
    for neighbor in neighbors_2:
        all_possible_moves.append([sheep_y ,sheep_x ,neighbor[0] , neighbor[1], "attack"]) 

    return all_possible_moves

def get_all_moves(sheep,player,other_player,move_historic,game_data):
    """ Gets all the moves suggested by us from a sheep's position, it also combines the all moves in 1 direction.
    
    Parameters:
        sheep (list) Info of the given sheep.
        player (str): The player number.
        other_player (str): The enemy player number.
        game_data (dict): The dictionary containing game information.

    Returns:
        Returns a series of moves.
        
    Version:
        specification: Leandro Bessa Lourenço (v2 29/03/24)
        implementation: Ismail Hafid Benchougra, Lucas Paludetto (v3 17/04/24)
    """ 
    series_of_moves = []

    sheep_position = sheep[0]

    #-----set all moves in 1 direction-----
    for move in get_all_moves_in_1_direction(sheep, game_data):
        
        series_of_moves.append([move])

    #-----set series of moves to go on seed----- 
    seed_coord_list = game_data["seeds"]

    for seed in seed_coord_list:
        if check_range_move(sheep_position,seed) == False:
            path = a_star(sheep_position, seed, game_data)
            moves = []

            if(path):
                for index in range(len(path)-1):
                    move = [path[index][0], path[index][1], path[index+1][0], path[index+1][1] ,"move"]
                    moves.append(move)
            
            series_of_moves.append(moves)

    #-----series of moves to go on grass of the other player and eat it-----
    other_player_grass_coord_list = get_player_herb_coords(other_player,game_data)
    for grass in other_player_grass_coord_list:
        #if check_range_move(sheep_position,grass) == False:
            if grass != sheep_position :
                path = a_star(sheep_position, grass, game_data)
                moves = []

                if(path):
                    for index in range(len(path)-1):
                        move = [path[index][0], path[index][1], path[index+1][0], path[index+1][1] ,"move"]
                        moves.append(move)
                    moves.append([path[index+1][0], path[index+1][1] ,"eat"])

                series_of_moves.append(moves)

    #---------series of move to go attack a sheep---------------
    game_data_copy = deepcopy(game_data)

    #actual sheeps list
    other_player_sheep_list = []
    for sheep in game_data_copy[other_player]["sheep"]:
        other_player_sheep_list.append(sheep[0])

    # game_data copy without the other sheep 
    other_player_sheep_copy = deepcopy(game_data_copy[other_player]["sheep"])
    for sheep in other_player_sheep_copy:
        if sheep[0] in other_player_sheep_list:
            game_data_copy[other_player]["sheep"].remove(sheep)
    
    for sheep_coord in other_player_sheep_list:

        # game_data copy without the enemy spawn if he is on spawn so a* can go on it
        if sheep_coord == game_data_copy[other_player]["spawn"]:
            game_data_copy[other_player]["spawn"] = (0, 0)
        else:
            game_data_copy[other_player]["spawn"] = game_data[other_player]["spawn"]
        
        if check_range_move(sheep_position, sheep_coord) == False:
            path = a_star(sheep_position, sheep_coord, game_data_copy)
            moves = []

            if path:
                for index in range(len(path) - 2):
                    move = [path[index][0], path[index][1], path[index + 1][0], path[index + 1][1], "move"]
                    moves.append(move)
                moves.append([path[index + 1][0], path[index + 1][1], path[index + 2][0], path[index + 2][1], "attack"])

            series_of_moves.append(moves)

    #----series of move to go on our grass to protect them---
    our_grass_coord_list = get_player_herb_coords(player,game_data)

    for grass_coord in our_grass_coord_list:
        if check_range_move(sheep_position,grass_coord) == False:
            path = a_star(sheep_position, grass_coord, game_data)
            moves = []

            if(path):
                for index in range(len(path)-1):
                    move = [path[index][0], path[index][1], path[index+1][0], path[index+1][1] ,"move"]
                    moves.append(move)
            
            series_of_moves.append(moves)
    

    #delete move already in move historic
    all_moves = delete_duplicate_move(series_of_moves,move_historic)

    #-----éù^$"'@'(^ù§)"------
    if True :
        if len(game_data[other_player]["grass"]) < 100 and len(game_data[other_player]["grass"]) > 90:
            if len(game_data[other_player]["grass"]) > len(game_data[player]["grass"]) *2 :
                sheep_pos = game_data[other_player]["sheep"][0][0]
                series_of_moves = [[sheep_pos[0],sheep_pos[1],sheep_pos[0]+1,sheep_pos[1],"move"]]
    
    
    return all_moves

#---GAIN FUNCTION---

def get_move_gain(sheep,moves,ia_player,other_player,game_data):
    """ Gets the order gain value.
    
    Parameters:
        moves (list): The given moves.
        ia_player (str): The ia player.
        other_player (str): The enemy player's number.
        move_historic (list): The history of recent moves.
        game_data (dict): The dictionary containing game information.

    Returns:
        gain (float):  the gain of move.
        
    Version:
        specification: Lucas Paludetto (v2 14/04/24)
        implementation: Lucas Paludetto (v4 16/04/24)
    """ 
    
    #moves is a list contain 1 or multiple moves list
    # moves = [ ["move(1,1)to(2,2)",] ] or can be moves = [ ["move(1,1)to(2,2)"],["eat(2,2)"] ]

    gain = 0
    turn_index = 0

    for move in moves :
        
        gain_value = 0
        type_move = move[-1]

        #-----------------
        # eat gain analize 
        if type_move == "eat" :
            #-----
            sheep_coord = (move[0],move[1])
            eat_coord = (move[0],move[1]) 
        
            #-----
            for grass in game_data[ia_player]["grass"]:
                if grass[0] == eat_coord:
                    gain_value -= float("inf")
            
            for grass in game_data[other_player]["grass"]:
                if grass[0] == eat_coord:
                    gain_value += get_value_of_a_grass(other_player,ia_player,sheep,grass,turn_index,game_data)
            #-----
            
            #set gain value
            gain += gain_value

        #-----------------
        # move gain analize
        elif type_move == "move" :

            sheep_coord = (move[0],move[1])
            new_sheep_coord = (move[2],move[3])

            position_value= (get_position_value_for_a_sheep(sheep_coord,ia_player,other_player,game_data) + get_position_value_for_a_sheep(new_sheep_coord,ia_player,other_player,game_data)) / 2
            
            if new_sheep_coord in game_data["seeds"]:
                gain_value += get_value_of_a_seed(ia_player,other_player,sheep,new_sheep_coord,game_data)

            gain_value += position_value

            gain += gain_value

        # attack gain analize
        elif type_move == "attack" :
            
            sheep_coord = (move[0],move[1])
            attack_sheep_coord = (move[2],move[3])

            for sheep in game_data[other_player]["sheep"]:
                if (move[2],move[3]) == sheep[0]:
            
                    attack_gain = get_attack_value(sheep,attack_sheep_coord,ia_player,other_player,game_data)

                    if check_range_move(sheep_coord,attack_sheep_coord) == True:
                        attack_gain *= 2

                    for _ in range(len(moves)-1):
                        attack_gain -= (0.2 * attack_gain) #minus 2% so more the sheep is away the more the gain is less
                        

                    gain_value += attack_gain 

            gain += gain_value
    

        turn_index += 1

    gain  = gain / len(moves) # divide the gain by the numebr of moves 
    return gain

#---GET VALUE OF SMTH---

def get_player_game_phase_value(game_data, player_nb, order):
    """ Get the current game phase VALUE for the given player.

    Parameters:
        game_data (dict): The game dictionnary containg the game information.
        player_nb (str): The player's number.
        order (str): The given order the get the value of it.

    Returns:
        Returns the game phase VALUE depending on the game phase.
    
    Version:
        specification: Leandro Bessa Lourenço (v2 18/04/24)
        implementation: Carina Filipa Nóbrega Magalhães, Leandro Bessa Lourenço (v3 20/04/24)
    """
    # 1. Early game:
    #     go to seed value : +6
    #     eat value : +3
    #     attack value : +1
        
    # 2. Mid game:
    #     go to seed value : +4
    #     eat value : +3
    #     attack value : +3
    
    # 3. End game:
    #     go to seed value : +1
    #     eat value : +2
    #     attack value : +4
    
    current_game_phase = get_player_game_phase(game_data, player_nb)
    
    if(current_game_phase == 1):
        if(order == 'seed'):
            return 6
        elif(order == 'eat'):
            return 3
        elif(order == 'attack'):
            return 1
        
    elif(current_game_phase == 2):
        if(order == 'seed'):
            return 4
        elif(order == 'eat'):
            return 3
        elif(order == 'attack'):
            return 3
    
    elif (current_game_phase == 3):
        if(order == 'seed'):
            return 1
        elif(order == 'eat'):
            return 3
        elif(order == 'attack'):
            return 4
    
    else : # If a misspell/error of the order or phase
        return 0   

def get_value_of_a_grass(other_player,player,sheep,grass,turn_index,game_data):
    """ Get the value to go to a grass.

    Parameters:
        other_player (str): The other player's number.
        player (str): The player's number.
        sheep (list): The list of sheep.
        grass (list): The list of grass.
        turn_index (int): The turn in which the action of the move will take place.
        game_data (dict): The game dictionnary containg the game information.

    Returns:
        Returns the value to go to a grass.
    
    Version:
        specification: Leandro Bessa Lourenço(v1 18/04/24)
        implementation: Leandro Bessa Lourenço, Lucas Paludetto (v3 20/04/24)
    """
    value = 0

    if check_time_to_extend(grass, turn_index, game_data) == True or grass[1] == 11: 
        value -= 2
    else:
        value += 2

    value +=  get_player_game_phase_value(game_data, player, 'eat')

    if grass[1] == 10 or grass[1] == 11:
        value /= 2

    sheep_distance = get_distance(sheep[0], grass[0], game_data) 
    for other_sheep in game_data[other_player]["sheep"]:
        other_sheep_distance = get_distance(other_sheep[0], grass[0], game_data)

        if other_sheep_distance < sheep_distance:
            value -= -3

        elif other_sheep_distance == sheep_distance:
            if player == "player1":
                value += 3
            elif player == "player2":
                value -= 1

        elif other_sheep_distance > sheep_distance:
            value += 3
        
        value += get_position_value_for_a_grass(grass[0],game_data)

    
    return value 

def get_value_of_a_seed(player,other_player,sheep,seed,game_data):
    """ Get the value to go to a seed to make it transform into a grass.

    Parameters:
        player (str): The player's number.
        sheep (list): The list of sheep. 
        seed (list): The list of seeds. 
        game_data (dict): The game dictionnary containg the game information.

    Returns:
        Returns the value to go to a seed.
    
    Version:
        specification: Leandro Bessa Lourenço(v1 18/04/24)
        implementation: Leandro Bessa Lourenço, Lucas Paludetto (v3 19/04/24)
    """
    value = 5

    value += get_player_game_phase_value(game_data, player, 'seed')  #phase
    value += get_position_value_for_a_seed(seed, game_data) #posiiton

    sheep_distance_to_seed = get_distance(sheep[0], seed, game_data)

    for other_sheep in game_data[other_player]["sheep"]:
        other_sheep_distance_to_seed = get_distance(other_sheep[0], seed, game_data)
        
        if other_sheep_distance_to_seed < sheep_distance_to_seed:
            value -= 3

        elif other_sheep_distance_to_seed == sheep_distance_to_seed:
            if player == "player1":
                value += 3
            elif player == "player2":
                value -= 3

        elif other_sheep_distance_to_seed > sheep_distance_to_seed:
            value += 3
    
    if get_expand_potential(game_data,seed) == 0:
        value /= 4
    
    elif get_expand_potential(game_data,seed) == 1:
        value /= 2

    


    
    return value 

def get_attack_value(our_sheep,attacked_sheep_coord,ia_player,other_player, game_data):
    """ Get the value to attack other sheep.

    Parameters:
        attacker_sheep (tuple): The attacker's sheep.
        attacked_sheep (tuple): The attacked sheep.
        ia_player (str): The ia player.
        other_player (str): The other player in the game.
        game_data (dict): The game dictionnary containg the game information.

    Returns:
        Returns the value to go to a seed.
    
    Version:
        specification: Leandro Bessa Lourenço(v1 18/04/24)
        implementation: Leandro Bessa Lourenço, Lucas Paludetto (v3 19/04/24)
    """
    factor = 4
    
    for player in ["player1", "player2"]:
        for sheep in game_data[player]["sheep"]:
            if attacked_sheep_coord == sheep[0]:
                attacked_sheep = sheep
    
    nb_sheep_other_player = len(game_data[other_player]["sheep"])
    our_nb_sheep = len(game_data[ia_player]["sheep"])

    #--
    if our_nb_sheep == 1 and nb_sheep_other_player == 1:

        value = 1.5
    
    elif our_nb_sheep == 2 and nb_sheep_other_player == 1:

        if our_sheep[1] == 3 and  attacked_sheep[1] == 3:
            value = 1
        elif our_sheep[1] == 2 and attacked_sheep[1] == 3 :
            value = 0.5
        elif  our_sheep[1] == 1 and attacked_sheep[1] == 3:
            value = 0.3

        elif our_sheep[1] == 3 and attacked_sheep[1] == 2 :
            value = 3
        elif our_sheep[1] == 2 and attacked_sheep[1] == 2 :
            value = 0.5
        elif our_sheep[1] == 1 and attacked_sheep[1] == 2 :
            value = 0.3

        elif  our_sheep[1] == 3 and attacked_sheep[1] == 1 :
            value = 4
        elif our_sheep[1] == 2 and attacked_sheep[1] == 1 :
            value = 3
        elif our_sheep[1] == 1 and attacked_sheep[1] == 1 :
            value = 0.3
    
    elif our_nb_sheep == 1 and nb_sheep_other_player == 2:

        if our_sheep[1] == 3 and  attacked_sheep[1] == 3:
            value = 4
        elif our_sheep[1] == 2 and attacked_sheep[1] == 3 :
            value = 1.5
        elif  our_sheep[1] == 1 and attacked_sheep[1] == 3:
            value = 0.7

        elif our_sheep[1] == 3 and attacked_sheep[1] == 2 :
            value = 5
        elif our_sheep[1] == 2 and attacked_sheep[1] == 2 :
            value = 3.5
        elif our_sheep[1] == 1 and attacked_sheep[1] == 2 :
            value = 1

        elif our_sheep[1] == 3 and attacked_sheep[1] == 1 :
            value = 6
        elif our_sheep[1] == 2 and attacked_sheep[1] == 1 :
            value = 5
        elif our_sheep[1] == 1 and attacked_sheep[1] == 1 :
            value = 3

    elif our_nb_sheep == nb_sheep_other_player:
        
        if our_sheep[1] == 3 and  attacked_sheep[1] == 3:
            value = 2
        elif our_sheep[1] == 2 and attacked_sheep[1] == 3 :
            value = 1
        elif  our_sheep[1] == 1 and attacked_sheep[1] == 3:
            value = 0.5

        elif our_sheep[1] == 3 and attacked_sheep[1] == 2 :
            value = 4
        elif our_sheep[1] == 2 and attacked_sheep[1] == 2 :
            value = 2
        elif our_sheep[1] == 1 and attacked_sheep[1] == 2 :
            value = 0.5

        elif our_sheep[1] == 3 and attacked_sheep[1] == 1 :
            value = 5
        elif our_sheep[1] == 2 and attacked_sheep[1] == 1 :
            value = 3
        elif our_sheep[1] == 1 and attacked_sheep[1] == 1 :
            value = 1
    
    elif our_nb_sheep > nb_sheep_other_player:

        if our_sheep[1] == 3 and  attacked_sheep[1] == 3:
            value = 2
        elif our_sheep[1] == 2 and attacked_sheep[1] == 3 :
            value = 1
        elif  our_sheep[1] == 1 and attacked_sheep[1] == 3:
            value = 0.7

        elif our_sheep[1] == 3 and attacked_sheep[1] == 2 :
            value = 3
        elif our_sheep[1] == 2 and attacked_sheep[1] == 2 :
            value = 2
        elif our_sheep[1] == 1 and attacked_sheep[1] == 2 :
            value = 1

        elif  our_sheep[1] == 3 and attacked_sheep[1] == 1 :
            value = 3
        elif our_sheep[1] == 2 and attacked_sheep[1] == 1 :
            value = 2
        elif our_sheep[1] == 1 and attacked_sheep[1] == 1 :
            value = 1
    
    elif our_nb_sheep < nb_sheep_other_player:

        if our_sheep[1] == 3 and  attacked_sheep[1] == 3:
            value = 3
        elif our_sheep[1] == 2 and attacked_sheep[1] == 3 :
            value = 1.5
        elif  our_sheep[1] == 1 and attacked_sheep[1] == 3:
            value = 0.5

        elif our_sheep[1] == 3 and attacked_sheep[1] == 2 :
            value = 4
        elif our_sheep[1] == 2 and attacked_sheep[1] == 2 :
            value = 2.5
        elif our_sheep[1] == 1 and attacked_sheep[1] == 2 :
            value = 1

        elif  our_sheep[1] == 3 and attacked_sheep[1] == 1 :
            value = 5.5
        elif our_sheep[1] == 2 and attacked_sheep[1] == 1 :
            value = 4
        elif our_sheep[1] == 1 and attacked_sheep[1] == 1 :
            value = 2


    #value *= our_nb_sheep
    value /= (nb_sheep_other_player/2)

    value *= factor

    return value

def get_position_value_for_a_seed(coord,game_data):
    """ Get the value of a seed placed on the board.

    Parameters:
        coord (tuple): The coord of the given seed.
        game_data (dict): The game dictionnary containg the game information.

    Returns:
        position_value (float):  the position value of the seed.
    
    Version:
        specification: Leandro Bessa Lourenço(v1 18/04/24)
        implementation: Lucas Paludetto (v3 21/04/24)
    """
    position_value = 0
    
    sheep_row, sheep_col = coord

    # virtual square
    square_size = 5  # carré de 11 cases de côté->(-5 à 5)
    square_coords = []
    for row in range(-square_size, square_size + 1):
        for col in range(-square_size, square_size + 1):
            cell_row = sheep_row + row
            cell_col = sheep_col + col
            square_coords.append((cell_row, cell_col))

   #add position value
    for cell in square_coords:
        if cell in game_data["dim_board"] and cell not in game_data["rocks"]:
            position_value += 1.5 / len(square_coords)
    
    return position_value

def get_position_value_for_a_grass(coord,game_data):
    """ Get the value of a grass placed on the board.

    Parameters:
        coord (tuple): The coord of the given seed.
        game_data (dict): The game dictionnary containg the game information.

    Returns:
        position_value (float):  the position value of the grass.
    
    Version:
        specification: Leandro Bessa Lourenço(v1 18/04/24)
        implementation: Lucas Paludetto (v3 21/04/24)
    """
    position_value = 0
    
    sheep_row, sheep_col = coord

    # virtual square
    square_size = 5  # carré de 11 cases de côté->(-5 à 5)
    square_coords = []
    for row in range(-square_size, square_size + 1):
        for col in range(-square_size, square_size + 1):
            cell_row = sheep_row + row
            cell_col = sheep_col + col
            square_coords.append((cell_row, cell_col))

    #add position value
    for cell in square_coords:
        if cell in game_data["dim_board"] and cell not in game_data["rocks"]:
            position_value += 1.5 / len(square_coords)

    return position_value

def get_position_value_for_a_sheep(coord,ia_player,other_player,game_data):
    """ Get the value of a sheep placed on the board.

    Parameters:
        coord (tuple): The coord of the given sheep.
        game_data (dict): The game dictionnary containg the game information.

    Returns:
        position_value (float):  the position value of the sheep.
    
    Version:
        specification: Leandro Bessa Lourenço(v1 18/04/24)
        implementation: Lucas Paludetto (v3 21/04/24)
    """
    position_value = 0
    
    sheep_row, sheep_col = coord

    # virtual square
    square_size = 5  # carré de 11 cases de côté->(-5 à 5)
    square_coords = []
    for row in range(-square_size, square_size + 1):
        for col in range(-square_size, square_size + 1):
            cell_row = sheep_row + row
            cell_col = sheep_col + col
            square_coords.append((cell_row, cell_col))

    #add position value
    for cell in square_coords:

        if cell in game_data["dim_board"]:
            position_value += 1.5 / len(square_coords)

        if cell in game_data["seeds"]:
                position_value += 0.5 / len(square_coords)

        if cell in game_data[other_player]["grass"]:
                    position_value += 0.4 / len(square_coords)

        if cell in game_data[ia_player]["grass"]:
                    position_value += 0.2 / len(square_coords)

        if cell in game_data["rocks"]:
                    position_value -= 0.2 / len(square_coords)

    
    return position_value

#---GET TOOLS FUNCTIONS---

def get_player_game_phase(game_data, player_nb):
    """ Get the current game phase for the given player. (To adapt his strategy)

    Parameters:
        game_data (dict): The game dictionnary containg the game information.
        player_nb (str): The player's number.

    Returns:
        Returns the game phase (1, 2 or 3) for the given player.
    
    Version:
        specification: Leandro Bessa Lourenço (v1 18/04/24)
        implementation: Carina Filipa Nóbrega Magalhães, Leandro Bessa Lourenço (v2 21/04/24)
    """
    
    turn = game_data['turn']
    player_grass = len(game_data[player_nb]['grass'])
    
    if(turn<= 10 or player_grass<=20 or len(game_data["seeds"])>0):
        return 1
    
    elif(turn > 10 and turn <25) or (player_grass >20 and player_grass <40):
        return 2
    
    else: 
        return 3
    
def get_distance(coord_1, coord_2, game_data):
    """ Gets the distance between two coordinates.
    
    Parameters:
        coords_1 (tuple): The coords of the first object.
        coords_2 (tuple): The coords of the second object.
        game_data (dict): The game dictionary containing the game information.

    Returns:
        Returns the distance between two coordinates.
        
    Version:
        specification: Leandro Bessa Lourenço (v1 18/04/24)
        implementation: Lucas Paludetto (v1 15/04/24)
    """ 
    path = a_star(coord_1,coord_2,game_data)
    if path == False:  # Si aucun chemin trouvé -> renvoyer -1 pour indiquer une distance invalide
        return float("inf")
    else :
        return len(path[1:])

def get_player_herb_coords(player, game_data):
    """ Gets the given player's grass coords.
    
    Parameters:
        player (str): The player's number.
        game_data (dict): The game dictionary containing the game information.

    Returns:
        Returns the player's grass coords.
        
    Version:
        specification: Leandro Bessa Lourenço (v1 00/00/24)
        implementation: Ismail Hafid Benchougra (v1 10/03/24)
    """ 
    herb_list = []

    for grass in game_data[player]["grass"]:
        herb_list.append(grass[0])
    
    return herb_list

def get_deadly_coords(sheep,player,gamedata):
    """ Returns a list of coordonates that are deadly for a specific given sheep.

    Parameters:
        gamedata: game data structure (dict)
        player: player id of AI (player1 or player2) (str)
        sheep: sheep from data structure (list)

    Returns:
        deadly_coords: every coord that is deadly for this specific sheep (list)

    Version:
        specification: Carina Filipa Nóbrega Magalhães (v1 10/04/24)
        implementation: Carina Filipa Nóbrega Magalhães (v2 18/04/24)
    """
    #initialize list
    deadly_coords = []

    #coords from outside board
    for x in range(gamedata["board_size"][0]+2):
        deadly_coords.append((x,0))
        deadly_coords.append((x,gamedata["board_size"][1]+1))
    for y in range(1,gamedata["board_size"][1]+1):
        deadly_coords.append((0,y))
        deadly_coords.append((gamedata["board_size"][0]+1,y))

    #coords of rocks
    for rock in gamedata["rocks"]:
        deadly_coords.append(rock)

    #run from attack if 1 life left
    if(sheep[1]==1):

        if player == "player1":
            other_player = "player2"
        else:
            other_player = "player1"

        for other_sheep in gamedata[other_player]["sheep"]:
            x_coord = other_sheep[0][0]
            y_coord = other_sheep[0][1]

            deadly_coords.append((x_coord +1 , y_coord))
            deadly_coords.append((x_coord -1 , y_coord))
            deadly_coords.append((x_coord +1 , y_coord +1))
            deadly_coords.append((x_coord -1 , y_coord +1))
            deadly_coords.append((x_coord +1 , y_coord -1))
            deadly_coords.append((x_coord -1 , y_coord -1))
            deadly_coords.append((x_coord, y_coord +1))
            deadly_coords.append((x_coord, y_coord -1))

    return deadly_coords

def get_grass_phase(game_data, grass_coord):
    """ Get the given grass grow phase.

    Parameters:
        player_nb (str): The player's number.
        grass_coord (tuple): The given grass coords to get its phase.
        
    Returns:
        Returns the given grass grow phase or 0 if grass not found.
    
    Version:
        specification: Leandro Bessa Lourenço (v1 18/03/24)
        implementation: Carina Filipa Nóbrega Magalhães, Leandro Bessa Lourenço (v2 21/04/24)
    """
    # Iterate trough each player
    for player_nb in ['player1', 'player2']:
        # Iterate trough each grass from each player
        for current_grass in game_data[player_nb]['grass']:
            # Example of the grass list:[[(4,9), 3], [(2,6), 2]]
            # Example of current_grass = [(4,9), 3]
            # Example of current_grass_corods = (4,9)
            # Example of current_grass_phase  = 3
            current_grass_coords = current_grass[0]
            
            # Return the phase of the given grass if found
            if(grass_coord == current_grass_coords):
                current_grass_phase = current_grass[1]
                return current_grass_phase
    return 0 

def get_expand_potential(game_data,seed_coord):
    expand_potential = 0

    for seed in game_data["seeds"]:
        if seed == seed_coord:
            
            row, col = seed_coord

            directions =    [      (-1, 0),
                            (0, -1),      (0 , 1),
                                   ( 1, 0),       ]

            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc

                if is_in_board(game_data,(new_row,new_col)) == True\
                    and is_a_rock(game_data,(new_row,new_col)) == False:
                    expand_potential += 1
                    
    return expand_potential

#----OTHER----

def is_sheep_spawnable(game_data,ia_player):
    """
    Checks if a sheep is spawnable.

    Parameters:
        game_data (dict): The dictionary containing game information.
        ia_player (str): The player we are targeting.

    Returns:
        True if a sheep is spawnable , false otherwise.
        
    Version:
        specification: Ismail Hafid Benchougra (v1 24/03/24)
        implementation: Ismail Hafid Benchougra (v1 24/03/24)
    """
    nb_sheep = len(game_data[ia_player]["sheep"])
    nb_grass = len(game_data[ia_player]["grass"])

    if nb_grass >= (nb_sheep) * 30 :
        return True
    else :
        False

def check_time_to_extend(grass_coord,turn_index,game_data):
    """ Checks the needed grow time of a given grass.

    Parameters:
        grass_coord (tuple): The given grass coords.
        turn_index (int): The turn in which the action of the move will take place.
        game_data (dict): The game dictionnary containg the game information.

    Returns:
        Returns True if the turn_index and the given_grass phase equal 10, False otherwise.
    
    Version:
        specification: Leandro Bessa Lourenço (v1 19/04/24)
        implementation: Carina Filipa Nóbrega Magalhães (v1 18/04/24)
    """
    #add turn index to the phase, if phase of grass + turn_index = 10 so return TRUE
    
    grass_phase = get_grass_phase(game_data, grass_coord)
    
    if turn_index + grass_phase == 10:
        return True
    elif turn_index + grass_phase == 11:
        return True
    
    else :
        return False

def decoder_move(move,orders_value):
    """
    This function decode a move(in a special syntax that we use for facility)
    and gives the correct syntax for an order

    Parameters:
        move (list): the move to decode

    Returns:
        decode_move(str): move in the correct syntax
        
    Version:
        specification: Lucas Paludetto (v1 10/04/24)
        implementation: Lucas Paludetto (v2 18/04/24)
    """
    
    if orders_value == "":
        blank = ""
    else:
        blank = " "

    type_move = move[-1]
    decode_move = ""

    if type_move == "eat":

        decode_move += blank + str(move[0]) + "-" + str(move[1]) + ":*"
    
    elif type_move == "move":

        decode_move += blank + str(move[0]) + "-" + str(move[1]) + ":@" +  str(move[2]) + "-" + str(move[3]) 

    elif type_move == "attack":

        decode_move += blank + str(move[0]) + "-" + str(move[1]) + ":x" + str(move[2]) + "-" + str(move[3])

    return decode_move

def delete_duplicate_move(all_moves,move_historic):
    """ Deletes the duplicated moves.

    Parameters:
        all_moves (list): all moves suggested to a sheep
        move_historic (list) : the log move choosen for sheeps

    Returns:
        Returns the cleaned filtered moves.
        
    Version:
        specification: Leandro Bessa Lourenço (v1 18/04/24)
        implementation: Lucas Paludetto (v3 21/04/24)
    """
    filtered_moves = []

    historic_last_moves = []
    for series in move_historic:
        if series:
            historic_last_moves.append([series[-1][-3],series[-1][-2],series[-1][-1]])


    for series_of_moves in all_moves:
        if series_of_moves:
            last_move = [series_of_moves[-1][-3],series_of_moves[-1][-2],series_of_moves[-1][-1]]

            if last_move not in historic_last_moves :
                filtered_moves.append(series_of_moves)
  
    return filtered_moves

def deepcopy(data):
    """ Makes a deepcopy of the given data. (Here: the game_data)

    Parameters:
        data: The given data to make a deepcopy.

    Returns:
        Returns the deepcopy of the given data.
        
    Version:
        specification: Leandro Bessa Lourenço (18/04/24)
        implementation: Lucas Paludetto (v1 20/04/24)
    """
    if type(data) == dict:
        new_data = {}
        for key in data:
            new_data[key] = deepcopy(data[key])
        return new_data
    
    elif type(data) == list:
        new_data = []
        for item in data:
            new_data.append(deepcopy(item))
        return new_data
    
    elif type(data) == tuple:
        new_data = []
        for item in data:
            new_data.append(deepcopy(item))
        return tuple(new_data)
        
    else:
        return data

#-----------------------
# FUNCTIONS FROM ENGINE
#-----------------------
from game_functions import grow_grass, is_in_board, is_a_rock, is_a_spawn,add_sheep,\
    check_range_move


#-----------
# TEST FILE
#-----------
if __name__ == "__main__" :
    
    import blessed,time
    term = blessed.Terminal()
    from game_graphic import graphic_data
    from game_functions import grow_grass, is_in_board, is_a_rock, is_a_spawn,add_sheep,\
    check_range_move, get_info_from_file,initialize_game_data_dict, print_board,execute_orders,\
    read_input_orders,update_turn,print_score_1,print_score_2,print_turn
    
    #---INITIALIZE A GAME DATA---
    path = "map_list/boxes.bsh"
    game_data = get_info_from_file(path)
    initialize_game_data_dict(game_data,graphic_data) 
    print(term.home +term.on_blue+ term.clear + term.hide_cursor)
    print_board(game_data,graphic_data)
    print_turn(game_data,graphic_data)

    #--------------------
    # TEST GET AI ORDERS
    #--------------------
    
    if True :

        #simulate a game
        nb_turn = 18
        for _ in range(nb_turn):
            #--AI Vs AI--
            p1_orders = get_AI_orders(game_data,1)
            p2_orders = get_AI_orders(game_data,2)
            p1_orders = read_input_orders(p1_orders,game_data,"player1")
            p2_orders = read_input_orders(p2_orders,game_data,"player2")
            game_data = execute_orders(game_data,p1_orders,p2_orders,graphic_data)
            print_board(game_data,graphic_data)
            print_score_1(game_data,graphic_data,1)
            print_score_2(game_data,graphic_data,2)
            update_turn(game_data,graphic_data)
            game_data["player1"]["check_orders"] = []
            game_data["player2"]["check_orders"] = []
            game_data["before_position"] = []

            time.sleep(0.2)

    #--print all move and the gain of each move
    
        print(term.move_y(term.height-2))
        print("\nTest all moves")
        move_historic = []
        for sheep in game_data["player1"]["sheep"]:
            max_gain = 0
            optimal_move = None
            print("\n SHEEP")
            for move in get_all_moves(sheep,"player1","player2",move_historic,game_data):
                gain = get_move_gain(sheep,move,"player1","player2",game_data)
                print("move ",move)
                print("gain ",gain)

                if gain > max_gain:
                    max_gain = gain
                    optimal_move = move
                
            move_historic.append(optimal_move) # add the move selected in historic move
            print("move choosen Gain :",max_gain," -> FIRST ",optimal_move[0],"LAST ",optimal_move[-1])

    
    print(term.move_y(term.height-2))  