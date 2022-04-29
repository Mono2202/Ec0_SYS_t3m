# Imports:
import neat, os, socket, json
from agent import Agent
from food import Food
from constants import *

# Constants:
IP = '127.0.0.1'
PORT = 2222
CLIENT_INFORMATION = (IP, PORT)
SIZE = 2048

# Initial information:
INIT_SIM = {"agentCount": 10, "foodCount": FOOD_COUNT, "agentKinds": None, "foodKinds": None}
DEAD_ANGLE_VALUE = 99999


def init_socket():
    """
    Initializing the socket with the simulation

    Returns
    -------
    sock : socket.socket
        Server socket
    conn : socket.socket
        Client socket
    """

    # Creating the socket:
    sock = socket.socket()

    # Binding:
    sock.bind(CLIENT_INFORMATION)

    # Listening:
    sock.listen(1)
    print("Socket is listening...")
    
    # Connecting to the simulation:
    conn, addr = sock.accept()
    print("Connected to", addr)

    print(type(sock))
    print(type(conn))
    return sock, conn


def init_genomes(genomes, config):
    """
    Initializing the genomes

    Parameters
    ----------
    genomes : list
        Genomes list
    config : neat.config.Config
        NEAT config
    """

    # Inits:
    counter = 0
    kind = 'Rabbit'
    food_types = 'Apple'
    INIT_SIM["agentKinds"] = []

    # Initializing the agents:
    for genome_id, genome in genomes:
        
        # Switching to fox agents:
        if counter > 5:
            kind = 'Fox'
            food_types = 'Rabbit'

        # Adding a new agent to the agents list:
        agent_list.append(Agent(kind, food_types))
        INIT_SIM["agentKinds"].append(kind)

        # Adding the agent's genome:
        ge.append(genome)

        # Creating the agent's neural network:
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        # Adding the new neural network to the nets list:
        nets.append(net)

        # Setting the genome's fitness to 0:
        genome.fitness = 0

        # Raising the counter:
        counter += 1


def check_in_los(current_agent, los_list, category):
    """
    Checking whether something is in the line of sight
    of the current agent

    Parameters
    ----------
    current_agent : Agent
        Current agent
    los_list : list
        List to check
    category : string
        Which type category to search
    
    Returns
    -------
    bool
        True  - object in LOS
        False - otherwise
    """

    # Checking for object in LOS:
    for curr_los_subject in los_list:
        if curr_los_subject.kind in eval("current_agent." + category + "_types") and curr_los_subject.alive and \
            current_agent.is_in_fov(current_agent.calculate_angle_to_object(curr_los_subject), curr_los_subject):
            return True
    
    # Condition: no object in LOS
    return False


def calculate_movement(eaten_food, are_alive):
    """
    Calculating the agent's movement
    
    Parameters
    ----------
    eaten_food : list
        Eaten food list
    are_alive : bool
        True if atleast one agent is alive
    
    Returns
    -------
    data : dict
        Dictionary with data to update the simulation
    """
    
    # Inits:
    data = {"angles": [], "eaten": eaten_food, "dead": not are_alive}

    # Moving the agents:
    for i in range(len(agent_list)):

        # Setting the current agent:
        current_agent = agent_list[i]

        # Condition: the current agent isn't alive
        if not current_agent.alive:
            data["angles"].append(DEAD_ANGLE_VALUE)
            continue
        
        # Checking for objects in agent's LOS:
        food_in_los = int(check_in_los(current_agent, food_list, "food") or check_in_los(current_agent, agent_list, "food"))

        # Feeding the agent's neural network:
        output = nets[i].activate((food_in_los,))

        # Resetting angle:
        if output[0] == 0:
            output[0] = 0.5

        # Adding the current angle to the angles list:
        data["angles"].append(output[0])

    return data


def calculate_fitness():
    """
    Calculating the agents fitness

    Returns
    -------
    eaten_food : list
        Eaten food list
    """

    # Inits:
    ate = False
    eaten_food = []
    
    # Checking for collisions between agents and food:
    for i in range(len(agent_list)):

        # Condition: current agent isn't alive
        if not agent_list[i].alive:
            continue
        
        # Checking for collisions between the current agent and food:
        for food in food_list:
            
            # Condition: the current agent eats the current food
            if food.kind in agent_list[i].food_types:

                # Condition: collision occured
                if (abs(agent_list[i].x - food.x) < 0.7) and (abs(agent_list[i].y - food.y) < 0.7):  
                    
                    # Adding the food to the eaten food:
                    eaten_food.append(food_list.index(food))

                    # Raising the current agent's energy:
                    agent_list[i].energy += food.food_energy

                    # Raising the agent's fitness:
                    ge[i].fitness += FOOD_FITNESS

                    # Setting the flag to True:
                    ate = True
        
        # Checking for collisions between the current agent and food:
        for food in agent_list:

            # Condition: the current agent eats the current food
            if food.kind in agent_list[i].food_types and food.alive == True:

                # Condition: collision occured
                if (abs(agent_list[i].x - food.x) < 0.7) and (abs(agent_list[i].y - food.y) < 0.7):  
                    food.alive = False

                    # Raising the current agent's energy:
                    agent_list[i].energy += 100 # TODO: ADD TO ANIMALS FOOD ENERGY

                    # Raising the agent's fitness:
                    ge[i].fitness += FOOD_FITNESS

                    # Setting the flag to True:
                    ate = True

        # Condition: current agent didn't eat this frame
        if not ate:

            # Reducing the current agent's hunger status:
            agent_list[i].energy -= 0.1
        
        # Setting the flag:
        ate = False

        # Condition: the current agent's energy is 0 or lower
        if agent_list[i].energy < 0:

            # Eliminating the current agent:
            agent_list[i].alive = False

    return eaten_food


def get_locations(locations_list):
    """
    Getting locations from locations_list

    Parameters
    ----------
    locations_list : list
        The locations list
    """

    # Setting the food list:
    for i in range(len(locations_list["foodList"]) // 2):
        food_list[i].x = locations_list["foodList"][i * 2]
        food_list[i].y = locations_list["foodList"][i * 2 + 1]
    
    # Settings the agent list:
    for i in range(len(locations_list["agentList"]) // 3):
        agent_list[i].x = locations_list["agentList"][i * 3]
        agent_list[i].y = locations_list["agentList"][i * 3 + 1]
        agent_list[i].angle = locations_list["agentList"][i * 3 + 2]


def eval_genomes(genomes, config):
    """
    Evaluating the genomes

    Parameters
    ----------
    genomes : list
        Genomes list
    config : neat.config.Config
        NEAT config
    """

    # Inits:
    global ge, nets, agent_list, food_list
    ge, nets, agent_list, eaten_food = [], [], [], []
    food_list = [Food('Apple') for i in range(FOOD_COUNT)]
    INIT_SIM["foodKinds"] = ['Apple' for i in range(FOOD_COUNT)]
    
    # Initializing the genomes:
    init_genomes(genomes, config)

    # Sending the initial data:
    conn.sendall(json.dumps(INIT_SIM).encode())

    # Getting the initial locations:
    initial_locations = json.loads(conn.recv(SIZE).decode())
    get_locations(initial_locations)
    
    # Training loop:
    while True:
        
        # Inits:
        are_alive = False

        # Counting the amount of agents alive:
        for i in range(len(agent_list)):

            # Condition: current agent is alive
            if agent_list[i].alive:
                are_alive = True
                break
        
        # Calculating the agents moves:
        angles = calculate_movement(eaten_food, are_alive)
        
        # Sending the data to the simulation:
        conn.sendall(json.dumps(angles).encode())

        # Getting "OK" message:
        conn.recv(SIZE)
        
        # Condition: no agents left alive
        if not are_alive:
            break
        
        # Getting the updated locations from the simulation:
        updated_locations = json.loads(conn.recv(SIZE).decode())
        get_locations(updated_locations)

        # Calculating the agents fitness:
        eaten_food = calculate_fitness()


def run(config_path):
    """
    Runs the NEAT algorithm

    Parameters
    ----------
    config_path : str
        NEAT config file path
    """
    
    # Setting the training config:
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # Starting the training:
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.run(eval_genomes, 10)


if __name__ == '__main__':
    # Finding the config file path:
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    # Creating the socket:
    global sock, conn
    sock, conn = init_socket()

    # Running the NEAT algorithm:
    run(config_path)