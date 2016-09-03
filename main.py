import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json
from GameEngine import GameEngine
from Arena import Arena
from Player import Player
from Ghost import Ghost
from random import randint
from tornado.ioloop import PeriodicCallback

list_of_clients = []
players = []
ghosts = []
counter = 0
GE = None
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index1.html")

class SocketHandler(tornado.websocket.WebSocketHandler):
    """
        Type:
            0 - connection established, provides player's id and initial position
            1 - update map
            2 - connection closed
    """
    def check_origin(self, origin):
        return True
    def open(self):
        global counter
        global list_of_clients
        if(self not in list_of_clients):
            counter += 1
            list_of_clients.append([self, counter])
            player_x = 1000
            player_y = 1000
            GE.add_player(counter, "dummy_name", player_x, player_y)
            msg = {"type": 0, "player_id": counter, "x": player_x, "y": player_y}
            self.callback = PeriodicCallback(self.update_client, 500)
            self.callback.start()
            self.write_message(msg)

    def update_client(self):
        global list_of_clients
        global GE
        print(list_of_clients)
        for d in list_of_clients:
            player_id = d[1]
            p = None
            for x in GE.get_players():
                if x.get_id() == player_id:
                    p = x
                    break
            
            row = p.get_x()
            col = p.get_y()
            player_name = p.name

            left_boundary = col - 16
            right_boundary = col + 16
            top_boundary = row - 9
            bottom_boundary = row + 9
            local_grids = GE.get_arena().grids[top_boundary:bottom_boundary+1]
            
            grids = []
            food_pos = []
            for i in local_grids:
                current_row = i[left_boundary:right_boundary]
                r = []
                for j in current_row:
                    if(j.get_type() == 4):
                        r.append(1)
                    else:
                        r.append(0)
                    if(j.get_type() == 1):
                        food_pos.append({"x": j.get_x(), "y": j.get_y()})
                grids.append(r)
            

            pac_pos = dict()
            ghost_pos = dict()
            for i in GE.get_players():
                player_row = i.get_y()
                player_col = i.get_x()
                if(left_boundary <= player_col <= right_boundary and top_boundary <= player_row <= bottom_boundary):
                    pac_pos[str(i.get_id())] = {"x": i.get_x(), "y": i.get_y(), "orientation": i.orientation, "player_name": i.name}

            for i in GE.get_ghosts():
                ghost_row = i.get_y()
                ghost_col = i.get_x()
                if(left_boundary <= ghost_col <= right_boundary and top_boundary <= ghost_row <= bottom_boundary):
                    ghost_pos[str(i.get_id())] = {"x": i.get_x(), "y": i.get_y(), "orientation": i.orientation, "ghost_type": i.ghost_type}

            if(p.is_dead):
                data = {"type": 2}
            else:
                data = {"type": 1, "grids": grids, "pac_pos": pac_pos, "ghost_pos": ghost_pos, "food_pos": food_pos, "score": p.get_score()}
            self.write_message(data)

    def on_message(self, msg):
        global counter
        incoming_data = json.loads(msg)
        msg_type = incoming_data["type"]
        print(msg_type)
        if(msg_type == 0):
            row = incoming_data["row"]
            col = incoming_data["col"]
            player_id = incoming_data["player_id"]
            player_name = incoming_data["player_name"]
            arrow = incoming_data["arrow"]
            
            p = None
            for x in GE.get_players():
                if x.get_id() == player_id:
                    x.name = player_name
                    p = x
                    break
                    
            left_boundary = col - 16
            right_boundary = col + 16
            top_boundary = row - 9
            bottom_boundary = row + 9
            local_grids = GE.get_arena().grids[top_boundary:bottom_boundary+1]
            
            if(arrow != 4):
                p.pressed_arrow_key(arrow)

            grids = []
            food_pos = []
            for i in local_grids:
                current_row = i[left_boundary:right_boundary]
                r = []
                for j in current_row:
                    if(j.get_type() == 4):
                        r.append(1)
                    else:
                        r.append(0)
                    if(j.get_type() == 1):
                        food_pos.append({"x": j.get_x(), "y": j.get_y()})
                grids.append(r)
                
            print(grids)
            pac_pos = dict()
            ghost_pos = dict()
            for i in GE.get_players():
                player_row = i.get_y()
                player_col = i.get_x()
                if(left_boundary <= player_col <= right_boundary and top_boundary <= player_row <= bottom_boundary):
                    pac_pos[str(i.get_id())] = {"x": i.get_x(), "y": i.get_y(), "orientation": i.orientation, "player_name": i.name}
            #print(left_boundary, right_boundary, top_boundary, bottom_boundary)
            for i in GE.get_ghosts():
                ghost_row = i.get_y()
                ghost_col = i.get_x()
                if(left_boundary <= ghost_col <= right_boundary and top_boundary <= ghost_row <= bottom_boundary):
                    print(i.get_x(), i.get_y())
                    ghost_pos[str(i.get_id())] = {"x": i.get_x(), "y": i.get_y(), "orientation": i.orientation, "ghost_type": i.ghost_type}
            
            if(p.is_dead):
                data = {"type": 2}
            else:
                data = {"type": 1, "grids": grids, "pac_pos": pac_pos, "ghost_pos": ghost_pos, "food_pos": food_pos, "score": p.get_score()}
            self.write_message(data)
        else:
            # closed
            print("in")
            player_id = incoming_data["player_id"]
            print("delete", player_id)
            p = None
            for x in GE.get_players():
                if x.get_id() == player_id:
                    p = x
                    break
            GE.delete_player(p.get_id())
            global list_of_clients
            for i in list_of_clients:
                if(i[0] == self):
                    self.callback.stop()
                    list_of_clients.remove(i)
                    print("removed!")
                    break

    def on_close(self):
        global list_of_clients
        for i in list_of_clients:
            if(i[0] == self):
                list_of_clients.remove(i)
                break
            

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", SocketHandler),
    ])

if __name__ == "__main__":
    global counter
    global GE
    GE = GameEngine()
    
    ghost_counter = 1
    print("in")
    for i in range(0, 2000, 20):
        for j in range(0, 2000, 30):
            for k in range(3):
                while(True):
                    ghost_row = randint(i, min(i+18, 1999))
                    ghost_col = randint(j, min(j+32, 1999))
                    if(GE.get_arena().grids[ghost_row][ghost_col].get_type() != 4):
                        break
                GE.add_ghost(ghost_counter, ghost_counter % 4, ghost_col, ghost_row)
                ghost_counter += 1
    GE.start()
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()