#---------
# IMPORTS
#---------
import blessed
term = blessed.Terminal()

from game_functions import *
from  AI_orders import *
from module_remote_play import create_connection, get_remote_orders, notify_remote_orders, close_connection
from game_graphic import graphic_data

#---------------
# MAIN FUNCTION
#---------------
def play_game(map_path, group_1, type_1, group_2, type_2):
    """Play a game.
    
    Parameters
    ----------
    map_path: path of map file (str)
    group_1: group of player 1 (int)
    type_1: type of player 1 (str)
    group_2: group of player 2 (int)
    type_2: type of player 2 (str)
    
    Notes
    -----
    Player type is either 'human', 'AI' or 'remote'.
    
    If there is an external referee, set group id to 0 for remote player.
    
    """
    #--------------
    # initializing
    #--------------

    game_data = get_info_from_file(map_path)
    initialize_game_data_dict(game_data,graphic_data) 
    print_screen(game_data["board"])
    del game_data["board"]
    print_turn(game_data,graphic_data) 
    print_score_1(game_data,graphic_data,group_1)
    print_score_2(game_data,graphic_data,group_2)
    
    
    #--------------------------------
    # create connection, if necessary
    #---------------------------------
    if type_1 == 'remote':
        connection = create_connection(group_2, group_1)
    elif type_2 == 'remote':
        connection = create_connection(group_1, group_2,"138.48.160.148")
    
    #--------
    # BOUCLE 
    #--------
    while is_game_finished(game_data) == False: 

        #print("iamove: ",get_AI_orders(game_data,1))
        #print("iamove: ",get_AI_orders(game_data,2))
       

        if type_1 == 'remote':
            p1_orders = get_remote_orders(connection)
        if type_1 == 'AI':
            p1_orders = get_AI_orders(game_data, 1)
            if type_2 == 'remote':
                notify_remote_orders(connection, p1_orders)
        elif type_1 == 'human':
            p1_orders = input_order(graphic_data)
            if type_2 == 'remote':
                notify_remote_orders(connection,p1_orders)
                
        if type_2 == 'remote':
            p2_orders = get_remote_orders(connection)
        if type_2 == 'AI':
            p2_orders= get_AI_orders(game_data, 2)
            if type_1 == 'remote':
                notify_remote_orders(connection, p2_orders)
        elif type_2 == 'human':
            p2_orders = input_order(graphic_data)
            if type_2 == 'remote':
                notify_remote_orders(connection, p2_orders)

        
        
        #----------------
        # CREATE ORDERS
        #----------------
        p1_orders = read_input_orders(p1_orders,game_data,"player1")
        p2_orders = read_input_orders(p2_orders,game_data,"player2")

        #----------------
        # EXECUTE ORDERS
        #----------------
        game_data = execute_orders(game_data, p1_orders, p2_orders, graphic_data)

        #---------------------------
        # UPDATE TURN/SCORES/RESETS
        #---------------------------
        update_turn(game_data,graphic_data)
        print_score_1(game_data,graphic_data,group_1)
        print_score_2(game_data,graphic_data,group_2)
        game_data["player1"]["check_orders"] = []
        game_data["player2"]["check_orders"] = []
        game_data["before_position"] = []

    #--------------
    # END THE GAME
    #--------------
    
    print("FIN DU JEU ->",get_win_player(game_data)," wins !")
      
    #--------------------------------
    # close connection, if necessary
    #--------------------------------
                
    if type_1 == 'remote' or type_2 == 'remote':
        close_connection(connection)
        
    print(term.move_y(term.height-2))

#---------------
# PLAY THE GAME
#---------------
print(term.home + term.clear + term.hide_cursor)
path = "map_list/camping.bsh"
#---------------

play_game(path, 15, 'AI', 16, 'AI')