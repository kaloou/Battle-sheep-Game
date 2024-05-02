import blessed 
term = blessed.Terminal()
#-------------------------

graphic_data = {
        "player1": {"sheep": '🐑', "grass": [term.on_lawngreen, term.on_green2, term.on_green3, term.on_green4, term.on_darkgreen], "spawn": term.on_blue},
        "player2": {"sheep": '🐏', "grass": [term.on_darkolivegreen1, term.on_darkolivegreen2, term.on_darkolivegreen3, term.on_darkolivegreen4, term.on_darkolivegreen], "spawn": term.on_red},
        "rocks": '🪨 ',
        "seeds": term.orange4 + '⛬ ',
        "ground": [term.on_chocolate4, term.on_sienna],
        "background": {"color": [term.on_cyan], "symbol": term.white + '🌨 '},
        "menu": {"background": term.on_tan, "color": term.white, "life": '♥', "marker": ['✅', '❌'], "blank": " "},
        "dead": '💀'
    }
