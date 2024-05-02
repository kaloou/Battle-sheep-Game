#----------------------
# INITIALIZE FUNCTIONS
#----------------------
def get_info_from_file(path):
    """ Extracts game information from a file.

    Parameters:
        path (str): The path to the file.

    Returns:
        game_data (dict): The dictionary containing game information.
        
    Raises: FileNotFoundError if the file is not found.

    Version:
        specification: Leandro Bessa Lourenço (v2 26/02/24)
        implementation: Leandro Bessa Lourenço (v3 3/03/24)
    """
    
    # Check if the provided path exists
    if(os.path.exists(path)):
        print('Found the path:', path)
        file = open(path, 'r') # Open file
        info_lines_list = file.readlines() # Creates a list with all the info in the file
        file.close()
        
        # Initialize variables
        current_info_type = ''
        nb_rows = 0
        nb_cols = 0
        spawn1 = 0
        spawn2 = 0
        seeds = []
        rocks = []
        
        #Iterate trough each line
        for line in info_lines_list:
            
            # If current line ends with ':' e.g. 'map:', 'spawn:', etc.
            if(line.endswith(':\n')):
                # Saves current type (e.g. 'map' or 'spawn' etc.)
                current_info_type = line.strip(':\n')
                
            else :
                #line = '11 9' --> line.split()[1] == '9'
                if(current_info_type == 'map'): # Map size
                    nb_rows = int(line.split()[0])
                    nb_cols = int(line.split()[1])
                    
                    # Min size is 20 rows and 20 lines
                    if(nb_rows < 20):
                        nb_rows = 20
                    
                    if(nb_cols < 20):
                        nb_cols = 20
                    
                    # Max size is 40 rows and 60 lines
                    if(nb_rows > 40):
                        nb_rows = 40
                    
                    if(nb_cols > 60):
                        nb_cols = 60
                    
                elif(current_info_type == 'spawn'): # Spawn cords
                    if(line.split()[0] == '1'): # spawn1
                        spawn1 = (int(line.split()[1]), int(line.split()[2])) # tuple (row, col)
                        
                    elif(line.split()[0] == '2'): # spawn2
                        spawn2 = (int(line.split()[1]), int(line.split()[2])) # tuple (row, col)

                elif(current_info_type == 'seeds'):
                    # Add current line cords to 'seeds' list
                    seeds.append((int(line.split()[0]), int(line.split()[1])))
                    
                elif(current_info_type == 'rocks'):
                    # Add current line cords to 'rocks' list
                    rocks.append((int((line.split()[0])), int(line.split()[1])))
         
         
        game_dict = {'turn' : 1,
                     'dim_board' : [],
                     'board' : [[]],    
                     'board_size' : (nb_rows, nb_cols),
                     'player1': {'sheep' : [],  
                                 'grass' : [],  
                                 'spawn' : spawn1}, 
                     'player2': {'sheep' : [],  
                                 'grass' : [],  
                                 'spawn' : spawn2}, 
                     'seeds' : seeds, 
                     'rocks' : rocks}
        
        return game_dict
    else :
        raise FileNotFoundError('The given path was not found or does not exist!')

def initialize_game_data_dict(game_data,graphic_data):
    """ Initializes the game data dictionary with base information for starting the game.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        game_data (dict): The updated game data dictionary.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto, Leandro Bessa Lourenço (v2 23/03/24)
    """
    game_data["dim_board"] = create_dim_board(game_data)
    game_data["board"] = create_board(game_data,graphic_data)
    game_data = add_sheep(game_data, "player1")
    game_data = add_sheep(game_data, "player2")
    game_data["turn"] = 1
    game_data["player1"]["check_orders"] = []
    game_data["player2"]["check_orders"] = []
    game_data["before_position"] = []


    return game_data                       

def create_dim_board(game_data):
    """ Creates a list of all the coordinates representing the dimensions of the game board.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        dim_board (list): A list of coordinate tuples representing each square on the game board.

    Version:
        specification: Lucas Paludetto (v2 17/03/24)
        implementation: Lucas Paludetto (V2 11/03/24)
    """
    dim_board = []
    for row in range(game_data["board_size"][0]): 
        for col in range(game_data["board_size"][1]):
            dim_board.append((row +1, col +1))

    return dim_board

def create_board(game_data,graphic_data):
    """ Creates a list of rows representing the graphical elements of all the board.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        board (list): A list of lists representing the game board with graphical elements.

    Version:
        specification: Lucas Paludetto (v2 21/03/24)
        implementation: Lucas Paludetto (v3 13/03/24)
    """

    height = term.height -1 #terminal height
    width = term.width // 2 #terminal width

    center_row = height // 2  # center of terminal height
    center_col = width // 2  # center of terminal width

    start_row = center_row - (game_data["board_size"][0] // 2) # first board row coord 
    start_col = center_col - (game_data["board_size"][1] // 2) # first board col coord

    board = []  
    for row_id  in range(height): #using terminal height
        row = []
        for col_id in range(width): #using terminal width

            real_row = row_id - start_row # calcul to get real row
            real_col = col_id - start_col # # calcul to get real col

            if (real_row + 1, real_col +1) == game_data["player1"]["spawn"]: #spawn1 
                row.append(graphic_data["player1"]["spawn"]+graphic_data["player1"]["sheep"] + term.normal)

            elif (real_row + 1, real_col +1) == game_data["player2"]["spawn"]:#spawn2
                row.append(graphic_data["player2"]["spawn"]+graphic_data["player2"]["sheep"] + term.normal)

            elif (real_row +1, real_col +1) in game_data["rocks"]: #rocks
                if (row_id + col_id) % 2 == 0: 
                    row.append(graphic_data["ground"][0] + graphic_data["rocks"] + term.normal)
                else:
                    row.append(graphic_data["ground"][1] + graphic_data["rocks"] + term.normal)
                
            elif (real_row +1, real_col +1) in game_data["seeds"]: #seeds
                if (row_id + col_id) % 2 == 0: 
                    row.append(graphic_data["ground"][0] + graphic_data["seeds"] + term.normal)
                else:
                    row.append(graphic_data["ground"][1] + graphic_data["seeds"] + term.normal)
          
            elif (real_row +1, real_col +1) in game_data["dim_board"]: # ground
                if (row_id + col_id) % 2 == 0: # altered ground color to make a "damier"
                    row.append(graphic_data["ground"][0] + '  ' + term.normal)
                else:
                    row.append(graphic_data["ground"][1] + '  ' + term.normal)
           
            else: # the rest of coord is the background
                option = [graphic_data["background"]["symbol"],'  ', '  ', '  ', '  ', '  ', '  ','  ','  ','  ','  ','  ']
                option = random.choice(option)
                #if (row_id + col_id) % 2 == 0: 
                    #row.append(term.on_red + "  " + term.normal)
                #else:
                    #row.append(term.on_yellow + "  " + term.normal)

                row.append(graphic_data["background"]["color"][0] + option  + term.normal)
                 
        board.append(row) #add row list in board list
        
     
    return board

def print_screen(board):
    """ Prints the game board row by row.

    Parameters:
        board (list): A list of lists representing the game board.

    Version:
        specification: Lucas Paludetto (v1 21/02/24)
        implementation: Lucas Paludetto (v2 28/02/24)
    """
    for row in board:
        row_string = ""
        #time.sleep(0.1)
        for cell in row:
            row_string += cell
        print(row_string)

#----------------------
# SPAWN SHEEP FUNCTIONS
#----------------------
def add_sheep(game_data, player_nb):

    """ Adds a new sheep to the game with the player's spawnpoint as coords and 3 default health points.

    Parameters:
        game_data (dict): The dictionary containing game information.
        player_nb (str) : In the game dict the player key. 

    Returns:
        game_data (dict): The dictionary containing game information.
        
    Version:
        specification: Leandro Bessa Lourenço (v2 02/03/24)
        implementation: Leandro Bessa Lourenço (v1 02/03/24)
    """
    spawn = game_data[player_nb]["spawn"]
    sheep_list = []
    for sheep in game_data[player_nb]["sheep"]:
        sheep_list.append(sheep[0])
    

    if player_nb in ['player1', 'player2'] and spawn not in sheep_list:
        game_data[player_nb]['sheep'].append([spawn, 3])
    
    return game_data
#-----
def spawn_new_sheep(game_data, player_nb):
    """ Spawns a new sheep for the given player.

    Parameters:
        game_data (dict): The dictionary containing game information.
        player_nb (str): The player number to spawn a new sheep.

    Returns:
        game_data (dict): The dictionary containing game information.

    Version:
        specification: Leandro Bessa Lourenço (v1 14/03/24)
        implementation: Leandro Bessa Lourenço (v2 15/03/24)
    """
    if(not is_a_sheep(game_data, game_data[player_nb]['spawn']) #check if a sheep is not in the spawn
       and enough_grass_to_spawn_sheep(game_data, player_nb)):
        game_data = add_sheep(game_data, player_nb)
    return game_data

#----------------------
# MOVE SHEEP FUNCTIONS
#----------------------
            
def is_move_valid(game_data,coord,new_coord):
    """ Checks if a move from coord to new_coord is valid according to game rules.

    Parameters:
        game_data (dict): The dictionary containing game information.
        coord (tuple): The current coordinates of the sheep in the format (row, col).
        new_coord (tuple): The new coordinates for the sheep in the format (row, col).

    Returns:
        bool: True if the move is valid, False otherwise.

    Version:
        specification: Lucas Paludetto, Ismail Hafid Benchougra (v1 21/03/24)
        implementation: Lucas Paludetto, Ismail Hafid Benchougra (v1 18/03/24)
    """
    if check_range_move(coord,new_coord) == True\
        and is_in_board(game_data,coord) == True\
        and is_in_board(game_data,new_coord) == True\
        and is_a_rock(game_data,new_coord) == False\
        and is_a_spawn(game_data,new_coord) == False\
        and is_a_sheep(game_data,coord) == True\
        and is_a_sheep(game_data,new_coord) == False:
        return True    
    
    else :
        return False
#-----     
def move_sheep(game_data,coord,new_coord,player): 
    """ Moves a sheep on the game board .

    Parameters:
        game_data (dict): The dictionary containing game information.
        coord (tuple): The current coordinates of the sheep in the format (row, col).
        new_coord (tuple): The new coordinates for the sheep in the format (row, col).

    Version:
        specification: Lucas Paludetto (v1 29/03/24)
        implementation: Lucas Paludetto (v1 29/03/24)
    """
    already_attacked = False
    for attack_log in game_data["before_position"]:
        if attack_log[1] == coord:
            already_attacked = True

    if is_move_valid(game_data,coord,new_coord) == True\
    and already_attacked == False\
    and is_right_player(player,coord,game_data):

        for player in ["player1","player2"]: # iterate in the right player
            for sheep in game_data[player]["sheep"]: # iterate in the right player sheep
                if coord == sheep[0]: # find sheep
                    sheep[0] = new_coord # update dict (new coord of the sheep)
 
    return game_data
    
#---------------------
# EAT GRASS FUNCTIONS
#---------------------
def is_grass_edible(game_data,coord):
    """ Checks if the grass at the specified coordinates is edible for a sheep.

    Parameters:
        game_data (dict): The dictionary containing game information.
        coord (tuple): The coordinates of the grass in the format (row, col).

    Returns:
        bool: True if the grass is edible for a sheep, False otherwise.

    Version:
        specification: Leandro Bessa Lourenço, Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (v1 21/03/24)
    """
    grass_player = get_player_grass(game_data,coord) # check what grass player own the  grass
    player = get_player_sheep(game_data,coord) # check the player of the ship

    if player != "player1" and player != "player2": 
        return False
    elif grass_player != "player1" and grass_player != "player2":
        return False
    
    if (player == "player1" or player == "player2")\
        and (grass_player == "player1" or grass_player == "player2"):
        for sheep in game_data[player]["sheep"]: # iterate in right player sheep
            for grass in game_data[grass_player]["grass"]: # iterate in  the owner of the grass
                if sheep[0] == grass[0]\
                    and sheep[0] == coord\
                    and grass[0] == coord: #if the coord = sheep_coord = grass_cord
                    return True
    return False




    # do the same as the previous one but sheep cannot eat their grass
    player = get_player_sheep(coord)
    if player == "player1":
        other_player = "player2"
    elif player == "player2":
        other_player ="player1"
    else:
        return False
    
    for grass in game_data[other_player]["grass"]:# check if grass is owwn by the other player
            if grass[0] == coord:
                 for sheep in game_data[player]["sheep"]:# check if coord grass is in sheep of player
                     if sheep[0] == grass[0] and sheep[0] == coord:
                         return True
    return False
#-----
def eat_grass(game_data,coord,player):
    """ Eat a grass by a sheep at the specified coordinates if possible.

    Parameters:
        game_data (dict): The dictionary containing game information.
        coord (tuple): The coordinates of the grass in the format (row, col).

    Returns:
        game_data (dict): The dictionary containing game information.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (v1 21/03/24)
    """
    already_attacked = False
    for attack_log in game_data["before_position"]:
        if attack_log[1] == coord:
            already_attacked = True

    if is_grass_edible(game_data,coord) == True\
    and already_attacked == False\
    and is_right_player(player,coord,game_data):
        
        index = 0
        for grass in game_data[get_player_grass(game_data,coord)]["grass"]:# iterate in grass of the right player
            if grass[0] == coord: # finded the grass equal the coord
                del (game_data[get_player_grass(game_data,coord)])["grass"][index] # update the dict (delete the grass)
            index += 1
    return game_data

#------------------------
# ATTACK SHEEP FUNCTIONS
#------------------------     
def is_attack_valid(game_data, attacker_coord, attacked_coord):
    """ Checks if a attack order is valid/acceptable.

    Parameters:
        game_data (dict): The dictionary containing game information.
        attacking_sheep_coord (tuple): Coords from the attacking sheep.
        attacked_sheep_coord  (tuple): Coords from the attacked sheep.

    Returns:
        True if the given sheep can attack the other given sheep, false otherwise.
        
    Version:
        specification: Leandro Bessa Lourenço (v2 1/03/24)
        implementation: Ismail Hafid Benchougra (v2 14/03/24)
    """

    if check_range_move(attacker_coord,attacked_coord) == True\
        and is_in_board(game_data,attacker_coord) == True\
        and is_in_board(game_data,attacked_coord) == True\
        and is_a_sheep(game_data,attacker_coord) == True\
        and is_a_sheep(game_data,attacked_coord) == True:
        return True
    
    return False
    
def eject_sheep(game_data, attacker_coord, attacked_coord):
    """ Ejects given sheep to given coords. If it lands on e.g. a rock, the sheep dies.
    
    Parameters:
        game_data (dict): The game dictionary containing game information.
        attacker_coord (tuple): The attacker sheep coords.
        attacked_coord (tuple): The attacked sheep coords.
    
    Returns:
        game_data (dict) : The game dictionary containing game information.
        
    Version:
        specification: Leandro Bessa Lourenço (v2 1/03/24)
        implementation: Lucas Paludetto, Ismail Hafid Benchougra (v2 20/03/24)
    """
   
    landed_coord = get_landed_coord(game_data,attacker_coord, attacked_coord)
    game_data["before_position"].append([attacked_coord,landed_coord]) #before he was, where he has landed
    
    for player in ["player1","player2"]: 
        for sheep in game_data[player]["sheep"]:
            if attacked_coord == sheep[0]: #find the sheep attacked

                if (landed_coord) in game_data["rocks"] or (landed_coord) not in game_data["dim_board"] and len(game_data[player]["sheep"]) == 1 :

                    remove_sheep(game_data,attacked_coord)
                    add_sheep(game_data,player)
                
                elif (landed_coord) in game_data["rocks"] or (landed_coord) not in game_data["dim_board"] and len(game_data[player]["sheep"]) > 1 :

                    remove_sheep(game_data,attacked_coord)
        
                
                elif sheep[1] == 0 and len(game_data[player]["sheep"]) == 1:# if last sheep

                    remove_sheep(game_data,attacked_coord)
                    add_sheep(game_data,player)
                
                elif sheep[1] == 0 and len(game_data[player]["sheep"]) > 1: #if more than 1 sheep

                    remove_sheep(game_data,attacked_coord)

                else:

                    for player in ["player1","player2"]: 
                        for sheep in game_data[player]["sheep"]: 
                            if attacked_coord == sheep[0]: 
                                sheep[0] = (landed_coord)

    return game_data

def reduce_sheep_hp(game_data, sheep_coord):
    """ Reduces the given sheep health points by minus one. If sheep's health points is zero, then the sheep dies.
    
    Parameters:
        game_data (dict): The game dictionary containing game information.
        sheep_coord (tuple): The coords from the sheep.
    
    Returns:
        game_data (dict) : The game dictionary containing game information.
        
    Version:
        specification: Leandro Bessa Lourenço (v1 24/02/24)
        implementation: Ismail Hafid Benchougra (v1 20/03/24)
    """

    for player in [get_player_sheep(game_data,sheep_coord)]: 
        for sheep in game_data[player]["sheep"]:
            if sheep_coord == sheep[0]: 
                sheep[1] -= 1
    return game_data
#------
def attack_sheep(game_data, attacker_coord, attacked_coord,player):
    """ Executes an attack on a sheep cell and make all the associated things.

    Parameters:
        game_data (dict): The dictionary containing game information.
        attacker_coord (tuple): The coordinates of the attacker, in the format (row, col).
        attacked_coord (tuple): The coordinates of the attacked sheep, in the format (row, col).

    Version:
        specification: Lucas Paludetto, Ismail Hafid Benchougra  (v2 18/03/24)
        implementation: Lucas Paludetto, Ismail Hafid Benchougra (v2 19/03/24)
    """
    #code suggested but not working
    
    
    #--------------------------
    #before the new rule
    if is_attack_valid(game_data, attacker_coord, attacked_coord) == True and is_right_player(player,attacker_coord,game_data):
        game_data = reduce_sheep_hp(game_data,attacked_coord)
        game_data = eject_sheep(game_data,attacker_coord,attacked_coord)
    
    
    for attack_log in game_data["before_position"]:
        if attack_log[0] == attacker_coord:
            game_data = reduce_sheep_hp(game_data,attacked_coord)
            game_data = eject_sheep(game_data,attacker_coord,attacked_coord)
                
    return game_data
             
#-----------------------
# GROW GRASS FUNCTIONS
#-----------------------
def remove_seed(game_data, seed_coord):
    """
    Removes a given seed from the game.

    Parameters:
        game_data (dict): The dictionary containing game information.
        seed_coords (tuple): Seed's coords to remove from the game.

    Returns:
        game_data (dict): The dictionary containing game information.
        
    Version:
        specification: Leandro Bessa Lourenço (v2 02/03/24)
        implementation: Carina Filipa Nóbrega Magalhães (v1 02/03/24)
    """
    if seed_coord in game_data["seeds"]:
        game_data["seeds"].remove(seed_coord)
    return game_data

def print_grow_grass(game_data,graphic_data):
    """
    Prints the visual representation of the grass growth on the game board.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Version:
        specification: Lucas Paludetto (v1 10/03/24)
        implementation: Lucas Paludetto (v1 10/03/24)
    """
    sheep_list = []
    for player in ["player1","player2"]:
        for sheep in game_data[player]["sheep"]:
            sheep_list.append(sheep[0])

    for player in ["player1","player2"]:
        for grass in game_data[player]["grass"]:

            if grass[0] not in sheep_list:

                if grass[1] <= 2:

                    y,x = get_real_coord(game_data,grass[0]) #vrai coord de sheep 
                    board_y,board_x = get_real_board_coord(game_data,grass[0]) #coord de sheep sur le plateau
                    
                    print(term.move_yx(y,x)+ graphic_data[player]["grass"][0] + '  ' + term.normal)
                    game_data["board"][board_y][board_x] = graphic_data[player]["grass"][0] + '  ' + term.normal
                
                elif grass[1] <= 4 :
                    
                    y,x = get_real_coord(game_data,grass[0]) #vrai coord de sheep 
                    board_y,board_x = get_real_board_coord(game_data,grass[0]) #coord de sheep sur le plateau
                    
                    print(term.move_yx(y,x)+ graphic_data[player]["grass"][1] + '  ' + term.normal)
                    game_data["board"][board_y][board_x] = graphic_data[player]["grass"][1] + '  ' + term.normal
                
                elif grass[1] <= 6 :
                    
                    y,x = get_real_coord(game_data,grass[0]) #vrai coord de sheep 
                    board_y,board_x = get_real_board_coord(game_data,grass[0]) #coord de sheep sur le plateau
                    
                    print(term.move_yx(y,x)+ graphic_data[player]["grass"][2] + '  ' + term.normal)
                    game_data["board"][board_y][board_x] = graphic_data[player]["grass"][2] + '  ' + term.normal
                
                elif grass[1] <= 8:
                    
                    y,x = get_real_coord(game_data,grass[0]) #vrai coord de sheep 
                    board_y,board_x = get_real_board_coord(game_data,grass[0]) #coord de sheep sur le plateau
                    
                    print(term.move_yx(y,x)+ graphic_data[player]["grass"][3] + '  ' + term.normal)
                    game_data["board"][board_y][board_x] = graphic_data[player]["grass"][3] + '  ' + term.normal
                
                elif grass[1] <= 10 :
                    
                    y,x = get_real_coord(game_data,grass[0]) #vrai coord de sheep 
                    board_y,board_x = get_real_board_coord(game_data,grass[0]) #coord de sheep sur le plateau
                    
                    print(term.move_yx(y,x)+ graphic_data[player]["grass"][4] + '  ' + term.normal)
                    game_data["board"][board_y][board_x] = graphic_data[player]["grass"][4] + '  ' + term.normal
    
            elif grass[0] in sheep_list:
                player_sheep = get_player_sheep(game_data,grass[0])

                if grass[1] <= 2:

                    y,x = get_real_coord(game_data,grass[0]) #vrai coord de sheep 
                    board_y,board_x = get_real_board_coord(game_data,grass[0]) #coord de sheep sur le plateau
                    
                    print(term.move_yx(y,x)+ graphic_data[player]["grass"][0] + graphic_data[player_sheep]["sheep"] + term.normal)
                    game_data["board"][board_y][board_x] = graphic_data[player]["grass"][0] + graphic_data[player_sheep]["sheep"] + term.normal
                
                elif grass[1] <= 4 :
                    
                    y,x = get_real_coord(game_data,grass[0]) #vrai coord de sheep 
                    board_y,board_x = get_real_board_coord(game_data,grass[0]) #coord de sheep sur le plateau
                    
                    print(term.move_yx(y,x)+ graphic_data[player]["grass"][1] + graphic_data[player_sheep]["sheep"] + term.normal)
                    game_data["board"][board_y][board_x] = graphic_data[player]["grass"][1] + graphic_data[player_sheep]["sheep"] + term.normal
                
                elif grass[1] <= 6 :
                    
                    y,x = get_real_coord(game_data,grass[0]) #vrai coord de sheep 
                    board_y,board_x = get_real_board_coord(game_data,grass[0]) #coord de sheep sur le plateau
                    
                    print(term.move_yx(y,x)+ graphic_data[player]["grass"][2] + graphic_data[player_sheep]["sheep"] + term.normal)
                    game_data["board"][board_y][board_x] = graphic_data[player]["grass"][2] + graphic_data[player_sheep]["sheep"] + term.normal
                
                elif grass[1] <= 8 :
                    
                    y,x = get_real_coord(game_data,grass[0]) #vrai coord de sheep 
                    board_y,board_x = get_real_board_coord(game_data,grass[0]) #coord de sheep sur le plateau
                    
                    print(term.move_yx(y,x)+ graphic_data[player]["grass"][3] + graphic_data[player_sheep]["sheep"] + term.normal)
                    game_data["board"][board_y][board_x] = graphic_data[player]["grass"][3] + graphic_data[player_sheep]["sheep"] + term.normal
                
                elif grass[1] <= 10:
                    
                    y,x = get_real_coord(game_data,grass[0]) #vrai coord de sheep 
                    board_y,board_x = get_real_board_coord(game_data,grass[0]) #coord de sheep sur le plateau
                    
                    print(term.move_yx(y,x)+ graphic_data[player]["grass"][4] + graphic_data[player_sheep]["sheep"] + term.normal)
                    game_data["board"][board_y][board_x] = graphic_data[player]["grass"][4] + graphic_data[player_sheep]["sheep"] + term.normal
#-------
def grow_grass(game_data):
    """
    Makes every grass grow. (auto def, no order needed)

    Parameters:
        game_data (dict): The game dictionary containing game information.
    
    Returns:
        game_data (dict) : The game dictionary containing game information.
        
    Version:
        specification: Leandro Bessa Lourenço, Carina Filipa Nóbrega Magalhães (v1 24/02/24)
        implementation: Carina Filipa Nóbrega Magalhães (v1 06/03/24)
    """

    for player in ("player1","player2"):

        for grass in game_data[player]["grass"]:

            grass_to_appear = []
            #Increases grass life by 1
            if grass[1] <= 10 :
                grass[1]=grass[1]+1
    
            #Spreads grass if needed
            if grass[1] == 10:

                #Get new grass coords
                x_grass = grass[0][0]
                y_grass = grass[0][1]

                directions =[        (-1, 0),
                             (0, -1),        (0 , 1),
                                     ( 1, 0)        ]

                for dr, dc in directions:
                    x_coord, y_coord = x_grass + dr, y_grass + dc

                    if is_a_seed(game_data,(x_coord,y_coord)) == True:
                        remove_seed(game_data,(x_coord,y_coord))
                    #checks
                    if is_in_board(game_data,(x_coord, y_coord)) == True\
                        and is_a_rock(game_data,(x_coord,y_coord)) == False\
                        and is_a_spawn(game_data,(x_coord,y_coord)) == False\
                        and is_a_grass(game_data,(x_coord,y_coord)) == False\
                        and (x_coord,y_coord) not in grass_to_appear:

                        grass_to_appear.append((x_coord,y_coord))
                        game_data[player]["grass"].append([(x_coord,y_coord),0])       

    return game_data

#---------------------------
# TRANSFORM SEED INTO GRASS
#---------------------------
def transform_seeds_into_grass(game_data):
    """ Transforms seeds into grass if a sheep is standing on a seed.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        game_data (dict): The dictionary containing game information.
    
    Version:
        specification: Leandro Bessa Lourenço (v1 18/03/24)
        implementation: Leandro Bessa Lourenço (v2 19/03/24)
    """

    for player in ['player1', 'player2']:
        for sheep in game_data[player]['sheep']:
            # Make a copy of seeds list before iterating
            seeds_copy = game_data["seeds"][:]
            for seed_coord in seeds_copy:
                if seed_coord == sheep[0]:
                    game_data = remove_seed(game_data, seed_coord)
                    game_data[player]['grass'].append([seed_coord, 0])

    return game_data

#------------
# ALL CHECKS
#------------
def is_in_board(game_data, coords):
    """ Checks if given coordinates are within the limits of the game board.

    Parameters:
        game_dict (dict): The dictionary containing game information.
        coords (tuple): Coords to check if within the game board.

    Returns:
        bool: True if the given coordinates in the game board, False otherwise.
        
    Version:
        specification: Leandro Bessa Lourenço (v1 18/03/24)
        implementation: Leandro Bessa Lourenço (v2 20/03/24)
    """
    row, col = coords
    if (    0 < row <= game_data['board_size'][0]\
        and 0 < col <= game_data['board_size'][1]):
        return True
    
    else:
        return False

def is_a_sheep(game_data,coord):
    """ Checks if there is a sheep at the given coordinates.

    Parameters:
        game_data (dict): The dictionary containing game information.
        coord (tuple): The coordinates to check in the format (row, col).

    Returns:
        bool: True if there is a sheep at the given coordinates, False otherwise.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (v1 21/03/24)
    """
    for player in ["player1", "player2"]:
        for sheep in game_data[player]["sheep"]:
            if coord == sheep[0]:
                return True
    return False

def is_a_seed(game_data,coord):
    """ Checks if the given coordinates is a seed.

    Parameters:
        game_data (dict): The dictionary containing game information.
        coord (tuple): The coordinates to check in the format (row, col).

    Returns:
        bool: True if the given coordinates correspond to a seed, False otherwise.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (v1 21/03/24)
    """
    if coord in game_data["seeds"]:
        return True
    
    return False

def is_a_rock(game_data,coord):
    """ Checks if a rock is at given location.

    Parameters:
        game_data (dict): The dictionary containing game information.
        coord (tuple): The coordinates to check in the format (row, col).

    Returns:
        True if a rock is at a given location, false otherwise.
        
    Version:
        specification: Leandro Bessa Lourenço (v1 24/02/24)
        implementation: Leandro Bessa Lourenço (v1 24/02/24)
    """
    
    if (coord in game_data["rocks"]):
        return True
    
    return False

def is_a_spawn(game_data,coord):
    """ Checks if the given coordinates is a spawnpoint.

    Parameters:
        game_data (dict): The dictionary containing game information.
        coord (tuple): The coordinates to check in the format (row, col).

    Returns:
        bool: True if the coordinates correspond to a spawn coord, False otherwise.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (v1 21/03/24)
    """
    for player in ["player1", "player2"]:
            if coord == game_data[player]["spawn"]:
                return True
    return False

def is_a_grass(game_data,coord):
    """ Checks if there is grass at the given coordinates.

    Parameters:
        game_data (dict): The dictionary containing game information.
        coord (tuple): The coordinates to check in the format (row, col).

    Returns:
        bool: True if there is grass at the given coordinates, False otherwise.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (v1 21/03/24)
    """
    for player in ["player1", "player2"]:
        for grass in game_data[player]["grass"]:
            if coord == grass[0]:
                return True
    return False

def check_range_move(coord,new_coord):
    """ Checks if the move range is respected in the 8 directions.

    Parameters:
        coord (tuple): The coordinates of the starting position in the format (row, col).
        new_coord (tuple): The coordinates of the new position in the format (row, col).

    Returns:
        bool: True if the move range is respected, False otherwise.

    Version:
        specification: Lucas Paludetto, Ismail Hafid Benchougra (v1 21/03/24)
        implementation: Lucas Paludetto, Ismail Hafid Benchougra (v1 21/03/24)
    """
    row, col = coord
    new_row, new_col = new_coord
    # Check if the values are not empty
    if(    row is not None 
       and col is not None 
       and new_row is not None
       and new_col is not None):
        if new_row == row and new_col == col + 1:  # droite
            return True
        elif new_row == row + 1:  
            if new_col == col - 1 or new_col == col + 1 or new_col == col:  # en bas gauche, en bas à droite, en bas milieu
                return True
        elif new_row == row and new_col == col - 1:  # gauche
            return True
        elif new_row == row - 1: 
            if new_col == col + 1 or new_col == col - 1 or new_col == col:  # en haut droite, en haut gauche, en haut milieu
                return True
    
    return False

def is_game_finished(game_data):
    """
        Checks if the game is finished.

        Parameters:
            game_data (dict): The dictionary containing game information.

        Returns:
            bool: True if game is finished, false otherwise.
            
        Version:
            specification: Ismail Hafid Benchougra (v1 24/03/24)
            implementation: Ismail Hafid Benchougra (v1 24/03/24) 
        """
        
    for player in ["player1","player2"]:
        
        if len(game_data[player]["grass"]) > 100:
            return True
            
        elif len(game_data[player]["grass"]) == 0 and game_data["turn"] >= 20:
            return True
        
    return False

def is_right_player(right_player,sheep_coord,game_data):

    for player in ["player1","player2"]:
        for sheep in game_data[player]["sheep"]:
            if sheep_coord == sheep[0]:#finded
                if player ==  right_player:
                    return True
    
    return False
#----------
# GET SMTH
#----------
def get_real_coord(game_data,object_coord):
    """ Gets the real coordinates of an object to use the cursor pointer.

    Parameters:
        game_data (dict): The dictionary containing game information.
        object_coord (tuple): The virtual coordinates of the object in the format (row, col).

    Returns:
        real_row, real_col (tuple): The real coordinates of the object in the terminal.

    Version:
        specification: Lucas Paludetto (v1 17/02/24)
        implementation: Lucas Paludetto (v1 17/02/24)
    """
    height = term.height -1 #terminal height
    width = term.width // 2 #terminal width

    center_row = height // 2  # center of terminal height
    center_col = width // 2  # center of terminal width

    start_row = center_row - (game_data["board_size"][0] // 2) # first board row coord 
    start_col = center_col - (game_data["board_size"][1] // 2) # first board col coord

    row, col = object_coord # ex : 1,1 = (1,1)
    real_row = row + start_row -1 # 1 + (first board row coord) - 1 because virtual coord started with (1,1)
    real_col = (col *2) + (start_col * 2) -2 # same thing but all X 2 because a col is 2 character not 1
    return real_row, real_col

def get_real_board_coord(game_data,object_coord):
    """ Gets the real board coordinates of an object to know the position in the board list.

    Parameters:
        game_data (dict): The dictionary containing game information.
        object_coord (tuple): The virtual coordinates of the object in the format (row, col).

    Returns:
        real_row, real_col (tuple): The real board coordinates of the object.

    Version:
        specification: Lucas Paludetto (v1 17/02/24)
        implementation: Lucas Paludetto (v1 17/02/24)
    """
    height = term.height -1 #terminal height
    width = term.width // 2 #terminal width

    center_row = height // 2  # center of terminal height
    center_col = width // 2  # center of terminal width

    start_row = center_row - (game_data["board_size"][0] // 2) # first board row coord 
    start_col = center_col - (game_data["board_size"][1] // 2) # first board col coord


    row, col = object_coord
    real_row = row + start_row -1
    real_col = (col) + (start_col) -1
    return real_row, real_col

def get_ground_color(game_data,coord): 
    """ Gets the ground color of a square on the board because we using a "damier".

    Parameters:
        game_data (dict): The dictionary containing game information.
        coord (tuple): The coordinates of the cell in the format (row, col).

    Returns:
        int: An index representing the alternating ground color (0 or 1).

    Version:
        specification: Lucas Paludetto (v1 2/03/24)
        implementation: Lucas Paludetto (v1 2/03/24)
    """
    height = term.height -1 #terminal height
    width = term.width // 2 #terminal width

    center_row = height // 2  # center of terminal height
    center_col = width // 2  # center of terminal width


    real_row = coord[0] - (center_row - (game_data["board_size"][0] // 2))
    real_col = coord[1] - (center_col - (game_data["board_size"][1] // 2))

    if (real_row + real_col) % 2 == 0:
        return 0 # -> 0 is the first element of the list of ground color
    else:
        return 1 # -> is the second ... "                 "

def get_player_sheep(game_data,coord):
    """ Gets the player owning the sheep at the given coordinates.

    Parameters:
        game_data (dict): The dictionary containing game information.
        coord (tuple): The coordinates of the sheep in the format (row, col).

    Returns:
        str: The player owning the sheep ("player1" or "player2"), or None if there is no sheep at the given coordinates.

    Version:
        specification: Lucas Paludetto (v2 14/03/24)
        implementation: Lucas Paludetto (v2 14/03/24)
    """
    nb_sheep_1 = len(game_data["player1"]["sheep"]) # number of sheep in player 1
    nb_sheep_2 = len(game_data["player2"]["sheep"]) # number of sheep in player 2

    for sheep in range (nb_sheep_1): # iterate n(nb_sheep_1)
        if coord == game_data["player1"]["sheep"][sheep][0]: # if coord in player1 sheep
            return "player1"
    
    for sheep in range (nb_sheep_2): # iterate n(nb_sheep_2)
        if coord == game_data["player2"]["sheep"][sheep][0]: # if coord in player2 sheep
            return "player2"
           
def get_player_grass(game_data,coord):
    """ Gets the player owner of the grass at the given coordinates.

    Parameters:
        game_data (dict): The dictionary containing game information.
        coord (tuple): The coordinates of the grass in the format (row, col).

    Returns:
        str: The player owning the grass ("player1" or "player2"), or None if there is no grass at the given coordinates.

    Version:
        specification: Lucas Paludetto (v1 27/02/24)
        implementation: Lucas Paludetto (v1 27/02/24
    """
    nb_grass_1 = len(game_data["player1"]["grass"]) # number of grass in player 1
    nb_grass_2 = len(game_data["player2"]["grass"]) # number of grass in player 2

    for grass in range (nb_grass_1): # iterate n(nb_grass_1)
        if coord == game_data["player1"]["grass"][grass][0]: # if coord in player1 grass
            return "player1"
    
    for grass in range (nb_grass_2): # iterate n(nb_grass_2)
        if coord == game_data["player2"]["grass"][grass][0]: #if coord in player2 grass
            return "player2"

#---------------
# SUB FONCTIONS
#---------------
def remove_sheep(game_data, sheep_coord):
    """ Removes a sheep from the game.

    Parameters:
        game_data (dict): The dictionary containing game information.
        sheep_coords (tuple): Coords from the sheep to remove from the game.
    Returns:
        game_data (dict): The dictionary containing game information.
        
    Version:
        specification: Leandro Bessa Lourenço (v2 02/03/24)
        implementation: Carina Filipa Nóbrega Magalhães, Lucas Paludetto (v2 07/03/24)
    """
    
    for player in ["player1","player2"]:
            index = 0
            for sheep in game_data[player]["sheep"]: 
                if sheep_coord == sheep[0]:
                    del(game_data[player]["sheep"][index])
                index += 1
    return game_data
    
    # Leandro's Version
    # # Iterate over the two players
    # for player_nb in ['player1', 'player2']:
    #     # Check if the current key == 'sheep')
    #     if('sheep') in game_data[player_nb]:
    #         # Iterate in the current player's sheep list backwards -> (to safely remove items without causing problems to the iteration)
    #         for current_sheep_i in range(len(game_data[player_nb]['sheep'])-1, -1, -1):
    #             # Save current sheep in a temp variable
    #             current_sheep = game_data[player_nb]['sheep'][current_sheep_i]
    #             # Check if the current sheep coords are the same as given coords
    #             if(current_sheep[0] == sheep_coords):
    #                 game_data[player_nb]['sheep'].remove(current_sheep)

def get_direction(attacker_coord, attacked_coord):
    """ Determines the direction of an attack based on the coordinates of the attacker and the target.

    Parameters:
        attacker_coord (tuple): The coordinates of the attacker in the format (row, col).
        attacked_coord (tuple): The coordinates of the target in the format (row, col).

    Returns:
        str: The direction of the attack.
        
    Version:
        specification: Ismail Hafid Benchougra, Lucas Paludetto (v1 21/03/24)
        implementation: Ismail Hafid Benchougra, Lucas Paludetto (v1 21/03/24)
    """
    row, col = attacker_coord
    new_row, new_col = attacked_coord

    if new_row == row and new_col == col + 1:  # droite
        return "right"
    elif new_row == row and new_col == col - 1:  # gauche
        return "left"
    
    elif new_row == row + 1:  
        if new_col == col - 1 : # bas gauche
            return "down_left"
        elif new_col == col + 1: # bas droite
            return "down_right"
        elif new_col == col:  # bas milieu
            return "down"
    
    elif new_row == row - 1: 
        if new_col == col + 1 : # haut droite
            return "top_right"
        elif new_col == col - 1: # haut gauche
            return "top_left"
        elif new_col == col:  # haut milieu
            return "top"

def get_landed_coord(game_data,attacker_coord, attacked_coord):
    """ Determines the coordinates where the sheep attacked land.

    Parameters:
        game_data (dict): The game data containing information about the board and player entities.
        attacker_coord (tuple): The coordinates of the attacker in the format (row, col).
        attacked_coord (tuple): The coordinates of the target in the format (row, col).

    Returns:
        tuple: The coordinates where the attack lands, in the format (row, col).

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (v1 21/03/24)
    """
    sheep_y,sheep_x = attacked_coord
    
    direction = get_direction(attacker_coord,attacked_coord)

    if direction == "right" :
        sheep_x += 5
    elif direction == "left" :
        sheep_x -= 5
    elif direction == "down" :
        sheep_y += 5
    elif direction == "top" :
        sheep_y -= 5

    elif direction == "top_right" :
        sheep_y -= 5
        sheep_x += 5
    elif direction == "down_right" :
        sheep_y += 5
        sheep_x += 5
    elif direction == "top_left" :
        sheep_y -= 5
        sheep_x -= 5
    elif direction == "down_left" :
        sheep_y += 5
        sheep_x -= 5
    
    while is_a_sheep(game_data,(sheep_y,sheep_x)) == True\
        or is_a_spawn(game_data,(sheep_y,sheep_x)) == True:

        if direction == "right" :
            sheep_x += 1
        elif direction == "left" :
            sheep_x -= 1
        elif direction == "down" :
            sheep_y += 1
        elif direction == "top" :
            sheep_y -= 1

        elif direction == "top_right" :
            sheep_y -= 1
            sheep_x += 1
        elif direction == "down_right" :
            sheep_y += 1
            sheep_x += 1
        elif direction == "top_left" :
            sheep_y -= 1
            sheep_x -= 1
        elif direction == "down_left" :
            sheep_y += 1
            sheep_x -= 1
    
    return sheep_y,sheep_x

def enough_grass_to_spawn_sheep(game_data, player_nb):
    """ Checks if there is enough grass to spawn sheep for the given player.

    Parameters:
        game_data (dict): Dictionary containing game data.
        player_nb (str): The player's number.

    Returns:
        bool: True if there is enough grass to spawn sheep, False otherwise.
    
    Version:
        specification: Leandro Bessa Lourenço (v1 21/03/24)
        implementation: Leandro Bessa Lourenço, Ismail Hafid Benchougra (v1 21/03/24)
    """
    nb_sheep = len(game_data[player_nb]["sheep"])
    nb_grass = len(game_data[player_nb]["grass"])

    if nb_grass >= (nb_sheep) * 30 :
        return True
    else :
        return False

def get_phase_nb(coord,game_data):
    for player in ["player1","player2"]:
        for grass in game_data[player]["grass"]:
            if coord == grass[0]:
                phase = grass[1]
    if phase <= 2 :
        phase_nb = 0
    elif phase <= 4 :
        phase_nb = 1
    elif phase <= 6 :
        phase_nb = 2
    elif phase <= 8 :
        phase_nb = 3
    elif phase <= 11 :
        phase_nb = 4

    return phase_nb

def get_win_player(game_data):

    grass_player1_list = []
    grass_player2_list = []

    for grass in game_data["player1"]["grass"]:
        grass_player1_list.append(grass)
    
    for grass in game_data["player2"]["grass"]:
        grass_player2_list.append(grass)
    

    if len(grass_player1_list) > len(grass_player2_list):
            win_player = "player 1"

    elif len(grass_player1_list) < len(grass_player2_list):
            win_player = "player 2"

    elif len(grass_player1_list) == len(grass_player2_list):

        phase_aditional_player1 = 0
        for grass in grass_player1_list:
            phase_aditional_player1 += grass[1]

        phase_aditional_player2 = 0
        for grass in grass_player1_list:
            phase_aditional_player2 += grass[1]
        
        if phase_aditional_player1 > phase_aditional_player2:
            win_player = "player 1"
        elif phase_aditional_player1 < phase_aditional_player2:
            win_player = "player 2"
        else:
            win_player = "both players"
    
    return win_player

#-----------------
# ORDERS FUNCTIONS
#-----------------
def input_order(graphic_data):
    """ Takes user input for orders and returns it.

    Parameters:
        graphic_data (dict): Graphic data containing visual representations.

    Returns:
        str: The command entered by the user.

    Version:
        specification: Lucas Paludetto (v1 12/03/24)
        implementation: Lucas Paludetto (v1 14/03/21)
    """
    
    print(term.move_y(term.height-3) + graphic_data["background"]["color"][0]) # position de l'input
    order = input("order : ") # placer l'input
    print(term.move_y(term.height-3)) # replacer le curseur à la meme position y pour ne pas passer la ligne
    if term.width % 2 == 0 :
        print(term.clear_eol)
    else:
        print(term.clear_eol+term.normal+(term.move_yx(term.height-2,term.width-1)+' '))
    return order

def is_input_syntax_respected(current_order):
    """ Checks if the input syntax is respected.

    Parameters:
        current_order (str): The input string (a order).

    Returns:
        bool: True if the input syntax is respected, False otherwise.
    
    Version:
        specification: Leandro Bessa Lourenço (v1 16/03/24)
        implementation: Leandro Bessa Lourenço (v5 20/03/24)
    """
    # Check if the current_order is 'sheep'
    if current_order == "sheep" :
            return True
        
    order = current_order.split(':') # Cleanse the current order, order = list
    if len(order) == 2: # Check if the split worked, if order has two parts (not e.g. '10')     
        order_left  = order[0] # Left  side of the ':'
        order_right = order[1] # Right side of the ':'
        
        # Check if order_right starts with "@" or "x" or "*"
        if order_right.startswith("@") or order_right.startswith("x") or order_right == "*":
                # Check if ':' in the current_order and if the order is made up by 2 tuples
                if ":" in current_order: 
                    return True
    return False

def read_input_orders(input_orders,game_data,player):
    """ Decodes and reads the players' input orders. If syntax is not respected, then it will be ignored.

    Parameters:
        input_orders (str):  The input string with the players' orders.

    Returns:
        orders_dict (dict): The dictionary containing the players' orders.
        
    Version:
        specification: Leandro Bessa Lourenço (v2 05/03/24)
        implementation: Leandro Bessa Lourenço (v2 05/03/24)
    """
    # Structure of return dict
    # orders_dict = {
    #     'sheep' : 0 
    #     '*' : [(20, 20), (row, col), (row, col)] # Eat grass
    #     'x' : [([19, 20], [20, 20]), ([],[])] # Attack
    #     '@' : [([12, 10], [12, 11]), ([],[])] # Move (old cords -> new cords)
    #     }
    
    

    # Split the input in sub orders
    orders = input_orders.split(' ') # Cleanse the input
    orders_dict = {'sheep': 0, # Sheep to spawn (int, either 1 to spawn or 0)
                    '*': [], # Eat grass
                    'x': [], # Attack
                    '@': []  # Move
                    }
    
    #print(orders) # To see how the split works
    
    # Iterate over every order and add them to each list
    for current_order in orders:
        
        if(is_input_syntax_respected(current_order)):

            if(current_order == 'sheep'):
                orders_dict['sheep'] = 1
                game_data[player]["check_orders"].append(1)
                
            elif(current_order) : # If str not empty
                # Example :
                # current_order = '19-20:x20-20'
                # order         = ['19-20', 'x20-20']
                # order_left    = '19-20'
                # order_right   = 'x20-20'
                # order_symbol  = 'x'
                game_data[player]["check_orders"].append(1)

                order = current_order.split(':') # Cleanse the current order
                order_left  = order[0] # Left  side of the ':'
                order_right = order[1] # Right side of the ':'
                order_symbol = order_right[0] # Get the order symbol (*, x, @)
                
                if(order_symbol == '*'):
                    # For example : current_order = '20-20:*', order_left = '20-20'
                    row = int(order_left.split('-')[0])
                    col = int(order_left.split('-')[1])
                    orders_dict['*'].append((row,col))
                    
                elif(order_symbol == 'x'):
                    # For example : current_order = '19-20:x20-20'
                    attacking_sheep_cords_str = order_left.split('-')
                    attacked_square_cords_str = order_right[1:].split('-') # [1:] removes the 'x' an keeps the rest
                    
                    # Casting str to int values
                    attacking_sheep_cords = [int(coord) for coord in attacking_sheep_cords_str]
                    attacked_square_cords = [int(coord) for coord in attacked_square_cords_str]
                    
                    orders_dict['x'].append((attacking_sheep_cords, attacked_square_cords))
                    
                elif(order_symbol == '@'):
                    # For example : current_order = '12-10:@12-11'
                    old_cords_str = order_left.split('-')
                    new_cords_str = order_right[1:].split('-') # [1:] removes the '@' and keeps the rest
                    
                    # Casting str to int values
                    old_cords = [int(coord) for coord in old_cords_str]
                    new_cords = [int(coord) for coord in new_cords_str]
                    
                    orders_dict['@'].append((old_cords, new_cords))
            else:
                game_data[player]["check_orders"].append(0)

        elif is_input_syntax_respected(current_order) == False:
            game_data[player]["check_orders"].append(0)


    return orders_dict

def execute_orders(game_data, p1_orders_dict, p2_orders_dict,graphic_data):
    """ Executes the given orders by both players, respecting the game rules.

    Parameters:
        game_data (dict): 
        p1_orders_dict (dict): The orders dictionary for player 1.
        p2_orders_dict (dict): The orders dictionary for player 2.

    Returns:
        game_data (dict): Dictionary containing game data.

    Notes: 6 Phases:
            - Phase 1: Spawn new sheep if specified in the orders.
            - Phase 2: Grow grass automatically.
            - Phase 3: Sheep attacks if specified in the orders. 
            - Phase 4: Move sheep according to specified orders.
            - Phase 5: Eat grass at specified coordinates.
            - Phase 6: Colonize seeds automatically.
    Version:
        specification: Leandro Bessa Lourenço (v3 18/03/24)
        implementation: Leandro Bessa Lourenço (v6 20/03/24)
    """
    # Structure of orders_dict
    # orders_dict = {
    #     'sheep' : 1 # 1 = spawn new sheep, 0 = do not spawn new sheep
    #     '*' : [(20, 20), (row, col), (row, col)] # Eat grass
    #     'x' : [([19, 20], [20, 20]), ([],[])] # Attack
    #     '@' : [([12, 10], [12, 11]), ([],[])] # Move (old cords -> new cords)
    #     }
    
    
    #---------Phase 1: SPAWN sheep---------- 
    if(p1_orders_dict['sheep'] == 1): 
        game_data = spawn_new_sheep(game_data, 'player1')
    
    if(p2_orders_dict['sheep'] == 1): 
        game_data = spawn_new_sheep(game_data, 'player2')

    
    #-------Phase 2: GROW GRASS (auto)------- 
    
    game_data = grow_grass(game_data)
    
    #--------Phase 3: Sheep ATTACKS----------
    
    # Check if player1 has given attack orders
    if len(p1_orders_dict['x'])>0: 
        # Iterate trought each attack order
        for current_attack in p1_orders_dict['x']:
            attacker_coord = tuple(current_attack[0]) 
            attacked_coord = tuple(current_attack[1])
            
            game_data = attack_sheep(game_data, attacker_coord, attacked_coord,"player1")
           
    
    # Check if player2 has given attack orders
    if len(p2_orders_dict['x'])>0: 
        # Iterate trought each attack order
        for current_attack in p2_orders_dict['x']:
            attacker_coord = tuple(current_attack[0]) 
            attacked_coord = tuple(current_attack[1])
            
            game_data = attack_sheep(game_data, attacker_coord, attacked_coord,"player2")
            #!here should be print_attack_sheep, and not in the attack_sheep def
        
    

    #---------Phase 4: Sheep MOVES----------
    
    # Check if player1 has given move orders
    if len(p1_orders_dict['@'])>0: 
        # Iterate trough each move order
        for current_move in p1_orders_dict['@']:
            coord     = tuple(current_move[0]) 
            new_coord = tuple(current_move[1])
            
            game_data = move_sheep(game_data, coord, new_coord,"player1")
            
    
    if len(p2_orders_dict['@'])>0: # Check if player2 has given move orders
        # Iterate trough each move order
        for current_move in p2_orders_dict['@']:
            coord     = tuple(current_move[0]) 
            new_coord = tuple(current_move[1])
             
            game_data = move_sheep(game_data, coord, new_coord,"player2")
    
    
    #---------Phase 5: Eat grass---------
    
    for current_eat_coords in p1_orders_dict['*']:
        game_data = eat_grass(game_data, current_eat_coords,"player1")

    for current_eat_coords in p2_orders_dict['*']:
        game_data = eat_grass(game_data, current_eat_coords,"player2")
    
    
    #---------Phase 6: Colonize seeds (auto)---------
    game_data = transform_seeds_into_grass(game_data)
    
    #-----Print all changes--------
    print_board(game_data,graphic_data)

    return game_data

#-----------------
# PRINTS FUNCTION
#-----------------
def print_board(game_data,graphic_data):

    sheep_list_coord = []
    for player in ["player1","player2"]:
        for sheep in game_data[player]["sheep"]:
            sheep_list_coord.append(sheep[0])

    grass_list_coord = []
    for player in ["player1","player2"]:
        for grass in game_data[player]["grass"]:
            grass_list_coord.append(grass[0])

    seed_list_coord = game_data["seeds"]
    rock_list_coord = game_data["rocks"]
    spawn_coord = [game_data["player1"]["spawn"],game_data["player2"]["spawn"]]
    
    coord_printed = []

    for cell_coord in game_data["dim_board"]:# iterate in all cell of the game board
        y,x = get_real_coord(game_data,cell_coord) #coord du curseur
        ground_number = get_ground_color(game_data,cell_coord) # color of the ground

        #GROUND
        if cell_coord not in sheep_list_coord\
        and cell_coord not in grass_list_coord\
        and cell_coord not in spawn_coord:
            
            #just ground
            if cell_coord not in seed_list_coord\
            and cell_coord not in rock_list_coord\
            and cell_coord not in coord_printed:
                print(term.move_yx(y,x)+ graphic_data["ground"][ground_number] + "  " + term.normal)
                coord_printed.append(cell_coord)
            #ground with seed
            elif cell_coord in seed_list_coord\
            and cell_coord not in rock_list_coord\
            and cell_coord not in coord_printed:
                print(term.move_yx(y,x)+ graphic_data["ground"][ground_number] + graphic_data["seeds"] + term.normal)
                coord_printed.append(cell_coord)
            #ground with rock
            elif cell_coord not in seed_list_coord\
            and cell_coord in rock_list_coord\
            and cell_coord not in coord_printed:
                print(term.move_yx(y,x)+ graphic_data["ground"][ground_number] + graphic_data["rocks"] + term.normal)
                coord_printed.append(cell_coord)
    
        #SHEEP
        elif cell_coord in sheep_list_coord\
        and cell_coord not in rock_list_coord:
            sheep_player = get_player_sheep(game_data,cell_coord)

            #sheep on grass
            if cell_coord in grass_list_coord\
            and cell_coord not in spawn_coord\
            and cell_coord not in coord_printed:
                grass_player = get_player_grass(game_data,cell_coord)
                phase_nb = get_phase_nb(cell_coord,game_data)
                print(term.move_yx(y,x)+ graphic_data[grass_player]["grass"][phase_nb] + graphic_data[sheep_player]["sheep"] + term.normal)
                coord_printed.append(cell_coord)
           
            #sheep on ground
            elif cell_coord not in grass_list_coord\
            and cell_coord not in spawn_coord\
            and cell_coord not in coord_printed:
                print(term.move_yx(y,x)+ graphic_data["ground"][ground_number] + graphic_data[sheep_player]["sheep"] + term.normal)
                coord_printed.append(cell_coord)
            #sheep on spawn
            elif cell_coord not in grass_list_coord\
            and cell_coord in spawn_coord\
            and cell_coord not in coord_printed:
                print(term.move_yx(y,x)+ graphic_data[sheep_player]["spawn"] + graphic_data[sheep_player]["sheep"] + term.normal)
                coord_printed.append(cell_coord)
        #GRASS
        elif cell_coord in grass_list_coord\
        and cell_coord not in rock_list_coord\
        and cell_coord not in seed_list_coord\
        and cell_coord not in spawn_coord:
            grass_player = get_player_grass(game_data,cell_coord)
            phase_nb = get_phase_nb(cell_coord,game_data)

            #just grass
            if cell_coord not in sheep_list_coord\
            and cell_coord not in coord_printed:
                print(term.move_yx(y,x)+ graphic_data[grass_player]["grass"][phase_nb] + "  " + term.normal)
                coord_printed.append(cell_coord)
        #SPAWN
        elif cell_coord in spawn_coord\
        and cell_coord not in sheep_list_coord\
        and cell_coord not in coord_printed:
            if cell_coord == game_data["player1"]["spawn"]:
                player = "player1"
            elif cell_coord == game_data["player2"]["spawn"]:
                player = "player2"
            
            print(term.move_yx(y,x)+ graphic_data[player]["spawn"] + "  " + term.normal)
            coord_printed.append(cell_coord)

def print_number(game_data):
    
    for cell_coord in game_data["dim_board"]:
        if cell_coord[0] == 1 and cell_coord[1] != 1:
            
            if cell_coord[1] < 11 :
                y,x = get_real_coord(game_data,(cell_coord[0]-1,cell_coord[1]))
                print(term.move_yx(y,x)+term.bold + term.on_cyan + str(cell_coord[1]) + term.normal)
            else:
                if cell_coord[1] % 2 == 0:
                    y,x = get_real_coord(game_data,(cell_coord[0]-1,cell_coord[1]))
                    print(term.move_yx(y,x)+term.bold + term.on_cyan + str(cell_coord[1]) + term.normal)
                else:
                    y,x = get_real_coord(game_data,(cell_coord[0]-2,cell_coord[1]))
                    print(term.move_yx(y,x)+term.bold + term.on_cyan + str(cell_coord[1]) + term.normal)


        elif cell_coord[1] == 1 and cell_coord[0] != 1:

            if cell_coord[1] < 10 :
                y,x = get_real_coord(game_data,(cell_coord[0],cell_coord[1]-1))
                print(term.move_yx(y,x)+term.bold + term.on_cyan + str(cell_coord[0]) + term.normal)

            else :
                y,x = get_real_coord(game_data,(cell_coord[0],cell_coord[1]-2))
                print(term.move_yx(y,x)+term.bold + term.on_cyan + str(cell_coord[0]) + term.normal)
        

        elif cell_coord[0] == 1 and cell_coord[1] == 1:

            y,x = get_real_coord(game_data,(cell_coord[0],cell_coord[1]-1))
            print(term.move_yx(y,x)+term.bold + term.on_cyan + str(cell_coord[1]) + term.normal)

            y,x = get_real_coord(game_data,(cell_coord[0]-1,cell_coord[1]))
            print(term.move_yx(y,x)+term.bold + term.on_cyan + str(cell_coord[0]) + term.normal)

#----------------
# TURN FUNCTIONS
#----------------

def turn_enough_space(game_data):
    """ Checks if there is enough vertical space in the terminal to print the turn.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        bool: True if there is enough space, False otherwise.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    height = term.height -1 #terminal heigh

    if height - 2 >= game_data["board_size"][0]:
        return True
    
def turn_first_coord(game_data):
    """ Calculates the  first coordinates used to centered the turn in the terminal.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        tuple: Coordinates (row, column) of the top-left corner of the game board.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    height = term.height - 1
    width = term.width
    
    top_space = (height - game_data["board_size"][0]) //2
    
    first_row_coord = top_space //2
    first_col_coord = (width //2) - 5

    return first_row_coord,first_col_coord

#------   
def print_turn(game_data,graphic_data):
    """ Prints the current turn number on the game interface.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    
    y,x = turn_first_coord(game_data)
    if turn_enough_space(game_data) == True:
        print(term.move_yx(y,x)+ graphic_data["menu"]["background"]+ " TURN : " + str(game_data["turn"])+" " + term.normal)

def update_turn(game_data,graphic_data):
    """ Updates the current turn number and prints it on the game interface.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    game_data["turn"] += 1
    print_turn(game_data,graphic_data)

#------------------
# SCORES FUNCTIONS
#------------------
#score player 1
def get_rest_1(game_data):
    """ Calculates a rest value to help the centering og the score menu of the player 1.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        int: The rest factor, either 0 or 1.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    rest = 0
    if game_data["board_size"][1] % 2 == 1:
        width = term.width
        left_space = (width//2) - (game_data["board_size"][1])
        
        if term.width %2 == 1 and left_space % 2 == 1 :
            rest = 1
        if term.width %2 == 0 and left_space % 2 == 0 :#
            rest = 0
        if term.width %2 == 0 and left_space % 2 == 1 :#
            rest = 1
        if term.width %2 == 1 and left_space % 2 == 0 :
            rest = 0
        
    return rest    

def get_size_of_menu(game_data):
    """ Calculates the size of the menu based on the number of sheep owned by player 1.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        tuple: A tuple containing the height and width of the menu.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    extra_sheep = len(game_data["player1"]["sheep"]) -1

    height = 16 + (3*extra_sheep) +1
    width = 48

    return height,width

def score_enough_space_1(game_data):  
    """ Checks if there is enough space in the terminal to print the score menu.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        bool: True if there is enough space, False otherwise.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    width = term.width // 2 
    height = term.height - 1
    menu_height,menu_width = get_size_of_menu(game_data)

    if width - (game_data["board_size"][1]) - menu_width - 2 >= 0 and height - menu_height >= 0 :
        return True
    elif (term.height-1) - game_data["board_size"][0] >= 4:
        return False
    
def score_first_coord_player_1(game_data):
    """ Calculates the first coordinates of the menu for player 1.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        tuple: Coordinates (row, column) of the top-left corner.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    height = term.height - 1
    width = term.width
    menu_height,menu_width = get_size_of_menu(game_data)
    rest = get_rest_1(game_data)

    left_space = (width//2) - (game_data["board_size"][1]) 

    first_row_coord = (height // 2 )  - menu_height //2 
    first_col_coord = (left_space //2) - menu_width //2 + rest

    return first_row_coord,first_col_coord
#-----
def print_score_1(game_data,graphic_data,group_number):
    """ Prints the score of player 1.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    #graphic data
    blank = " "
    vline = "│"
    hline = "─"
    dlcorner = "└"
    tlcorner = "┌"
    drcorner = "┘"
    trcorner = "┐"
    correct = graphic_data["menu"]["marker"][0]
    incorrect = graphic_data["menu"]["marker"][1]
    bg = graphic_data["menu"]["background"]
    color = graphic_data["menu"]["color"]
    y,x = score_first_coord_player_1(game_data)
    height,width = get_size_of_menu(game_data)
    #----
    sheep_list_coord = []
    for player in ["player1","player2"]:
        for sheep in game_data[player]["sheep"]:
            sheep_list_coord.append(sheep[0])
    grass_list_coord = []
    for player in ["player1","player2"]:
        for grass in game_data[player]["grass"]:
            grass_list_coord.append(grass[0])
    spawn_coord = [game_data["player1"]["spawn"],game_data["player2"]["spawn"]]
    #orders
    orders = ""
    for order in game_data["player1"]["check_orders"]:
        if order == 1:
            orders += correct
        elif order == 0:
            orders += incorrect
    #grass
    nb_grass = len(game_data["player1"]["grass"])
    len_nb_grass = len(str(nb_grass))
    rest = 0
    if len_nb_grass % 2 == 1:
        rest += 1

    groupe = " (groupe " + str(group_number) + ")"
    groupe_width = len(groupe)
    if groupe_width % 2 == 0:
        rest_number = 0
    else:
        rest_number =1

    if score_enough_space_1(game_data) == True:   
        #Player1
        print(term.move_yx(y,x)+bg + color + (blank*width) +term.normal)
        print(term.move_yx(y+1,x)+bg + color + blank*(width//2-7- (groupe_width//2)) +(term.white+ "P L A Y E R  1")+groupe+ blank*(width//2-7-(groupe_width//2)-rest_number) +term.normal)
        print(term.move_yx(y+2,x)+bg + color + (blank*width) +term.normal)
        #check orders
        print(term.move_yx(y+3,x)+bg + color + (blank*2) +("• CHECK ORDERS")+ (blank*(width-16)) +term.normal)
        print(term.move_yx(y+4,x)+bg + color + (blank*2) +tlcorner+(hline*(width-6))+trcorner + (blank*2))
        print(term.move_yx(y+5,x)+bg + color+ (blank*2) + vline+ (orders) + (blank*(width-(len(orders)*2)-6)) + vline + (blank*2) + term.normal)
        print(term.move_yx(y+6,x)+bg + color + (blank*2) + dlcorner + (hline*(width-6)) + drcorner + (blank*2) + term.normal)
        #GRASS ACQUIRED
        print(term.move_yx(y+7,x)+bg + color + (blank*2) +("• GRASS ACQUIRED")+ (blank*(width-18)) +term.normal)
        print(term.move_yx(y+8,x)+bg + color + (blank*2) +tlcorner+(hline*(width-6))+trcorner + (blank*2))
        print(term.move_yx(y+9,x)+bg + color+ (blank*2) + vline+ (blank*((width//2)-(len_nb_grass//2) - 3 )) +(str(nb_grass))+ (blank*((width//2)-(len_nb_grass//2) - 3 - rest))+ vline + (blank*2)+ term.normal)
        print(term.move_yx(y+10,x)+bg + color+ (blank*2) + dlcorner + (hline*(width-6)) + drcorner + (blank*2) + term.normal)
        #SHEEP STATUS
        print(term.move_yx(y+11,x)+bg + color + blank*2 +(term.white+ "• SHEEP STATUS")+ (blank*(width-16)) +term.normal)
        row = 12

        i = 0
        for sheep in game_data["player1"]["sheep"]:
            sheep_coord = sheep[0]
            sheep_life = sheep[1]
            len_coord = len(str(sheep_coord))
            number_life = sheep_life
            sheep_player = get_player_sheep(game_data,sheep_coord)
            ground_number = get_ground_color(game_data,sheep_coord)

            #sheep on grass
            if sheep_coord in grass_list_coord\
            and sheep_coord not in spawn_coord:
                grass_player = get_player_grass(game_data,sheep_coord)
                phase_nb = get_phase_nb(sheep_coord,game_data)
                cell = graphic_data[grass_player]["grass"][phase_nb] + graphic_data[sheep_player]["sheep"] + term.normal
            #sheep on ground
            elif sheep_coord not in grass_list_coord\
            and sheep_coord not in spawn_coord:
                cell = graphic_data["ground"][ground_number] + graphic_data[sheep_player]["sheep"] + term.normal
            
            #sheep on spawn
            elif sheep_coord not in grass_list_coord\
            and sheep_coord in spawn_coord:
                cell = graphic_data[sheep_player]["spawn"] + graphic_data[sheep_player]["sheep"] + term.normal
            #-------
            print(term.move_yx(y+row,x)+ bg + color + (blank*2) +tlcorner+(hline*(width-6))+trcorner + (blank*2))
            print(term.move_yx((y+(row+1)), x) + bg + color + (blank * 2) + vline + (" Sheep " + str(i + 1) + " : " + cell\
            + bg + " Coord :(" + str(sheep_coord[0]) + "," + str(sheep_coord[1]) + ") Life : " + term.red + (number_life *"♥ ")+ term.normal)\
            + bg + blank* (width - (34) - (len_coord)- (2 * number_life)) + bg + vline + (blank * 2) + term.normal)
            print(term.move_yx(y+(row+2), x) + bg + color + (blank * 2) + dlcorner + (hline * (width - 6)) + drcorner + (blank * 2) + term.normal)

            i += 1
            row += 3
        
        print(term.move_yx(y+row,x)+bg + color + (blank*width) +term.normal)

    elif score_enough_space_1(game_data) == False:
        width = 12
        print(term.move_yx(0,0)+bg + color + (blank*2) +"PLAYER 1" + (blank*2)+ "\n"+\
             (blank*(width//2-(len_nb_grass//2))+ (str(nb_grass))+ blank*(width//2-(len_nb_grass//2)- rest)  +term.normal))

#-----
#score player 2
def get_rest_2(game_data):
    """ Calculates a rest value to help the centering og the score menu of the player 1.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        int: The remainder needed for vertical alignment.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    width = term.width
    left_space = (width//2) - (game_data["board_size"][1])
    board_space = game_data["board_size"][1]
    rest = 0

    if term.width %2 == 1 and left_space % 2 == 0 and (board_space) % 2 == 0 :
        rest = 1
    if term.width %2 == 0 and left_space % 2 == 0 and (board_space) % 2 == 0 :
        rest = 0
    if term.width %2 == 1 and left_space % 2 == 1 and (board_space) % 2 == 0 :
        rest = 2
    if term.width %2 == 0 and left_space % 2 == 1 and (board_space) % 2 == 0 :
        rest = 1
    if term.width %2 == 1 and left_space % 2 == 0 and (board_space) % 2 == 1 :
        rest = 1
    if term.width %2 == 0 and left_space % 2 == 0 and (board_space) % 2 == 1 :
        rest = 0
    if term.width %2 == 1 and left_space % 2 == 1 and (board_space) % 2 == 1 :
        rest = 1
    if term.width %2 == 0 and left_space % 2 == 1 and (board_space) % 2 == 1 :
        rest = 0
      
    return rest

def get_size_of_menu_2(game_data):
    """ Calculates the size of the menu based on the number of sheep owned by player 2.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        tuple: A tuple containing the height and width of the menu.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    extra_sheep = len(game_data["player2"]["sheep"]) -1

    height = 16 + (3*extra_sheep) +1
    width = 48

    return height,width

def score_enough_space_2(game_data):  
    """ Checks if there is enough space in the terminal to print the score menu.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        bool: True if there is enough space, False otherwise.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    width = term.width // 2 
    height = term.height - 1
    menu_height,menu_width = get_size_of_menu_2(game_data)

    if width - (game_data["board_size"][1]) - menu_width - 2 >= 0 and height - menu_height >= 0 :
        return True
    elif (term.height-1) - game_data["board_size"][0] >= 4:
        return False
    
def score_first_coord_player_2(game_data):
    """ Calculates the first coordinates of the menu for player 2.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Returns:
        tuple: Coordinates (row, column) of the top-left corner.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    height = term.height - 1
    width = term.width 
    menu_height,menu_width = get_size_of_menu_2(game_data)
    rest = get_rest_2(game_data)
   
    right_space = (width//2) - (game_data["board_size"][1]) 

    first_row_coord = (height // 2 )  - menu_height //2 
    first_col_coord = width - right_space//2 - menu_width//2 -rest

    return first_row_coord,first_col_coord
#------
def print_score_2(game_data,graphic_data,group_number):
    """ Prints the score of player 1.

    Parameters:
        game_data (dict): The dictionary containing game information.

    Version:
        specification: Lucas Paludetto (v1 21/03/24)
        implementation: Lucas Paludetto (24/03/21)
    """
    y,x = score_first_coord_player_2(game_data)
    height,width = get_size_of_menu_2(game_data)
    #graphic
    blank = " "
    vline = "│"
    hline = "─"
    dlcorner = "└"
    tlcorner = "┌"
    drcorner = "┘"
    trcorner = "┐"
    correct = graphic_data["menu"]["marker"][0]
    incorrect = graphic_data["menu"]["marker"][1]
    bg = graphic_data["menu"]["background"]
    color = graphic_data["menu"]["color"]
    #------
    sheep_list_coord = []
    for player in ["player1","player2"]:
        for sheep in game_data[player]["sheep"]:
            sheep_list_coord.append(sheep[0])
    grass_list_coord = []
    for player in ["player1","player2"]:
        for grass in game_data[player]["grass"]:
            grass_list_coord.append(grass[0])
    spawn_coord = [game_data["player1"]["spawn"],game_data["player2"]["spawn"]]
    
    #orders
    orders = ""
    for order in game_data["player2"]["check_orders"]:
        if order == 1:
            orders += correct
        elif order == 0:
            orders += incorrect
    #grass
    nb_grass = len(game_data["player2"]["grass"])
    len_nb_grass = len(str(nb_grass))
    rest = 0
    terminal_rest = 0
    if len_nb_grass % 2 == 1:
        rest += 1
    if term.width % 2 == 1:
        terminal_rest += 1
    #group
    groupe = " (groupe " + str(group_number) + ")"
    groupe_width = len(groupe)
    if groupe_width % 2 == 0:
        rest_number = 0
    else:
        rest_number =1


    if score_enough_space_2(game_data) == True:      
        #Player1
        print(term.move_yx(y,x)+bg + color + (blank*width) +term.normal)
        print(term.move_yx(y+1,x)+bg + color + blank*(width//2-7-(groupe_width//2)) +(term.white+ "P L A Y E R  2")+groupe+ blank*(width//2-7-(groupe_width//2+rest_number)) +term.normal)
        print(term.move_yx(y+2,x)+bg + color + (blank*width) +term.normal)
        #check orders
        print(term.move_yx(y+3,x)+bg + color + (blank*2) +("• CHECK ORDERS")+ (blank*(width-16)) +term.normal)
        print(term.move_yx(y+4,x)+bg + color + (blank*2) +tlcorner+(hline*(width-6))+trcorner + (blank*2))
        print(term.move_yx(y+5,x)+bg + color+ (blank*2) + vline+ (orders) + (blank*(width-(len(orders)*2)-6)) + vline + (blank*2) + term.normal)
        print(term.move_yx(y+6,x)+bg + color + (blank*2) + dlcorner + (hline*(width-6)) + drcorner + (blank*2) + term.normal)
        #GRASS ACQUIRED
        print(term.move_yx(y+7,x)+bg + color + (blank*2) +("• GRASS ACQUIRED")+ (blank*(width-18)) +term.normal)
        print(term.move_yx(y+8,x)+bg + color + (blank*2) +tlcorner+(hline*(width-6))+trcorner + (blank*2))
        print(term.move_yx(y+9,x)+bg + color+ (blank*2) + vline+ (blank*((width//2)-(len_nb_grass//2) - 3 )) +(str(nb_grass))+ (blank*((width//2)-(len_nb_grass//2) - 3 - rest))+ vline + (blank*2)+ term.normal)
        print(term.move_yx(y+10,x)+bg + color+ (blank*2) + dlcorner + (hline*(width-6)) + drcorner + (blank*2) + term.normal)
        #SHEEP STATUS
        print(term.move_yx(y+11,x)+bg + color + blank*2 +(term.white+ "• SHEEP STATUS")+ (blank*(width-16)) +term.normal)
        row = 12

        i = 0
        for sheep in game_data["player2"]["sheep"]:
            sheep_coord = sheep[0]
            sheep_life = sheep[1]
            len_coord = len(str(sheep_coord))
            number_life = sheep_life
            sheep_player = get_player_sheep(game_data,sheep_coord)
            ground_number = get_ground_color(game_data,sheep_coord)

            #sheep on grass
            if sheep_coord in grass_list_coord\
            and sheep_coord not in spawn_coord:
                grass_player = get_player_grass(game_data,sheep_coord)
                phase_nb = get_phase_nb(sheep_coord,game_data)
                cell = graphic_data[grass_player]["grass"][phase_nb] + graphic_data[sheep_player]["sheep"] + term.normal
            #sheep on ground
            elif sheep_coord not in grass_list_coord\
            and sheep_coord not in spawn_coord:
                cell = graphic_data["ground"][ground_number] + graphic_data[sheep_player]["sheep"] + term.normal
            
            #sheep on spawn
            elif sheep_coord not in grass_list_coord\
            and sheep_coord in spawn_coord:
                cell = graphic_data[sheep_player]["spawn"] + graphic_data[sheep_player]["sheep"] + term.normal
            #-------
            print(term.move_yx(y+row,x)+ bg + color + (blank*2) +tlcorner+(hline*(width-6))+trcorner + (blank*2))
            print(term.move_yx((y+(row+1)), x) + bg + color + (blank * 2) + vline + (" Sheep " + str(i + 1) + " : " + cell\
            + bg + " Coord :(" + str(sheep_coord[0]) + "," + str(sheep_coord[1]) + ") Life : " + term.red + (number_life *"♥ ")+ term.normal)\
            + bg + blank* (width - (34) - (len_coord)- (2 * number_life)) + bg + vline + (blank * 2) + term.normal)
            print(term.move_yx(y+(row+2), x) + bg + color + (blank * 2) + dlcorner + (hline * (width - 6)) + drcorner + (blank * 2) + term.normal)

            i += 1
            row += 3

        print(term.move_yx(y+row,x)+bg + color + (blank*width) +term.normal)

    elif score_enough_space_2(game_data) == False:
        width = 12
        print(term.move_yx(0,term.width-width-terminal_rest)+bg + color + (blank*2) +"PLAYER 2" + (blank*2)+ term.normal)
        print(term.move_yx(1,term.width-width -terminal_rest)+bg + color +blank*(width//2-(len_nb_grass//2))+ (str(nb_grass))+ (blank*(width//2-(len_nb_grass//2) - rest))+ term.normal)

#---------
# IMPORTS
#---------
if __name__ != "__main__":
    import os,blessed,random
    term = blessed.Terminal()

