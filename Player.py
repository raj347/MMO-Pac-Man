

class Player:

    #Attribute
    

    #Method

    def __init__(self, game_engine, x = -1, y = -1, id):
        self.id = id
        self.x = x
        self.y = y
        self.ori = 0
        self.score = 0
        self.power_up = False
        self.game_engine = game_engine

    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y
    
    def get_score(self):
        return self.score

    def is_powered_up(self):
        return self.powerUp

    def has_pressed_arrow(self):
        return False

    def change_orientation(self, ori):
        self.ori = ori

    def can_move_forward(self):
        new_x = x
        new_y = y
        if(self.ori == 0):
            new_y -= 1
        elif(self.ori ==1):
            new_x -= 1
        elif(self.ori ==2):
            new_y += 1
        elif(self.ori ==3):
            new_x += 1

        if(self.game_engine.get_arena().get_grid_typ(new_x, new_y) == 4):
            return False
        else:
            return True

    def move_forward(self):
        return False