from collections import deque

# Calculates the overall balance of the ship at a particular state
def CALCULATE_BALANCE(GRID):
    PORT_WEIGHT = 0
    STARBOARD_WEIGHT = 0
    
    for ROW in range(1, 9):
        for COL in range(1, 13):
            CELL = GRID.get((ROW, COL))
            if CELL and CELL['weight'] > 0:
                if COL <= 6:
                    PORT_WEIGHT += CELL['weight']
                else:
                    STARBOARD_WEIGHT += CELL['weight']
    
    return abs(PORT_WEIGHT - STARBOARD_WEIGHT)

# Checks whether or not a particular position is valid or not
def VALID_POSITION(GRID, ROW, COL):
    if (ROW, COL) not in GRID:
        return False
    
    GRID_CELL = GRID[(ROW, COL)]
    if GRID_CELL['type'] == 'NAN':
        return False
    
    if GRID_CELL['weight'] > 0:
        return False
    
    if ROW > 1:
        BELOW_CELL = GRID.get((ROW - 1, COL))
        if not BELOW_CELL or BELOW_CELL['type'] == 'NAN' or BELOW_CELL['weight'] == 0:
            return False
    
    return True

# Identifies all containers that are free or accessible
def GET_CONTAINERS(GRID):
    ACCESSIBLE_CONTAINERS = []
    
    for ROW in range(1, 9):
        for COL in range(1, 13):
            GRID_CELL = GRID.get((ROW, COL))
            if not GRID_CELL or GRID_CELL['weight'] == 0:
                continue
            
            IS_ACCESSIBLE = True
            
            for CHECK_ROW in range(ROW + 1, 9):
                ABOVE_CELL = GRID.get((CHECK_ROW, COL))
                if ABOVE_CELL and ABOVE_CELL['weight'] > 0:
                    IS_ACCESSIBLE = False
                    break
            
            if IS_ACCESSIBLE:
                ACCESSIBLE_CONTAINERS.append((ROW, COL))
    
    return ACCESSIBLE_CONTAINERS

# Identifies all valid end positions or destinations for containers
def GET_VALID_DESTINATIONS(GRID):
    VALID_DESTINATIONS = []
    
    for ROW in range(1, 9):
        for COL in range(1, 13):
            if VALID_POSITION(GRID, ROW, COL):
                VALID_DESTINATIONS.append((ROW, COL))
    
    return VALID_DESTINATIONS

# Moves a container from one position to another
def MOVE_CONTAINER(GRID, START_POSITION, END_POSITION):
    NEW_GRID = {}
    
    for POSITION in GRID:
        if POSITION == START_POSITION:
            NEW_GRID[POSITION] = {'weight': 0, 'type': 'UNUSED', 'description': 'UNUSED'}
        elif POSITION == END_POSITION:
            NEW_GRID[POSITION] = {
                'weight': GRID[START_POSITION]['weight'],
                'type': GRID[END_POSITION]['type'],
                'description': GRID[START_POSITION]['description']
            }
        else:
            NEW_GRID[POSITION] = {
                'weight': GRID[POSITION]['weight'],
                'type': GRID[POSITION]['type'],
                'description': GRID[POSITION]['description']
            }
    
    return NEW_GRID

# Calculates the manhattan distance between positions
def CALCULATE_MANHATTAN_DISTANCE(POSITION_1, POSITION_2):
    return abs(POSITION_1[0] - POSITION_2[0]) + abs(POSITION_1[1] - POSITION_2[1])

# Calculates the cost of moving a particular container from a position to another
def CALCULATE_COST_OF_MOVE(START_POSITION, END_POSITION):
    PARK_POSITION = (1, 8)
    
    COST_FROM_PARK_TO_SOURCE = CALCULATE_MANHATTAN_DISTANCE(PARK_POSITION, START_POSITION)
    COST_FROM_SOURCE_TO_DESTINATION = CALCULATE_MANHATTAN_DISTANCE(START_POSITION, END_POSITION)
    COST_FROM_DEST_TO_PARK_POSITION = CALCULATE_MANHATTAN_DISTANCE(END_POSITION, PARK_POSITION)
    
    return COST_FROM_PARK_TO_SOURCE + COST_FROM_SOURCE_TO_DESTINATION + COST_FROM_DEST_TO_PARK_POSITION

# Calculates the cost of balancing the ship based on the number of container moves 
def CALCULATE_BALANCE_COST(CONTAINER_MOVES):
    if not CONTAINER_MOVES:
        return 0
    
    TOTAL_COST = 0
    CURRENT_POSITION = (1, 8)
    
    for MOVE in CONTAINER_MOVES:
        START_POSITION, END_POSITION = MOVE
        
        COST_TO_SOURCE = CALCULATE_MANHATTAN_DISTANCE(CURRENT_POSITION, START_POSITION)
        COST_TO_DESTINATION = CALCULATE_MANHATTAN_DISTANCE(START_POSITION, END_POSITION)
        
        TOTAL_COST += COST_TO_SOURCE + COST_TO_DESTINATION
        CURRENT_POSITION = END_POSITION
    
    COST_TO_PARK_POSITION = CALCULATE_MANHATTAN_DISTANCE(CURRENT_POSITION, (1, 8))
    TOTAL_COST += COST_TO_PARK_POSITION
    
    return TOTAL_COST

# Balances the ship by moving containers accordingly (if necessary)
def BALANCE_SHIP(GRID):
    TOTAL_WEIGHT = sum(CELL['weight'] for CELL in GRID.values())
    BALANCE_THRESHOLD = TOTAL_WEIGHT * 0.10
    
    INITIAL_IMBALANCE = CALCULATE_BALANCE(GRID)
    
    if INITIAL_IMBALANCE < BALANCE_THRESHOLD:
        return [], INITIAL_IMBALANCE
    
    CONTAINER_SOLVER_QUEUE = deque()
    CONTAINER_SOLVER_QUEUE.append((GRID, [], INITIAL_IMBALANCE))
    VISITED = set()
    
    BEST_SOLUTION = None
    BEST_IMBALANCE = INITIAL_IMBALANCE
    BEST_COST = float('inf')
    
    MAX_ITERATIONS = 10000
    ITERATION_COUNT = 0
    
    while CONTAINER_SOLVER_QUEUE and ITERATION_COUNT < MAX_ITERATIONS:
        ITERATION_COUNT += 1
        CURRENT_GRID, CURRENT_MOVES, CURRENT_IMBALANCE = CONTAINER_SOLVER_QUEUE.popleft()
        
        GRID_STATE = tuple(sorted((POSITION, CELL['weight']) for POSITION, CELL in CURRENT_GRID.items()))
        if GRID_STATE in VISITED:
            continue
        
        VISITED.add(GRID_STATE)
        
        if CURRENT_IMBALANCE == 0 or CURRENT_IMBALANCE < BALANCE_THRESHOLD:
            CURRENT_COST = CALCULATE_BALANCE_COST(CURRENT_MOVES)
            
            if CURRENT_COST < BEST_COST:
                BEST_SOLUTION = CURRENT_MOVES
                BEST_IMBALANCE = CURRENT_IMBALANCE
                BEST_COST = CURRENT_COST
            
            if CURRENT_IMBALANCE < BALANCE_THRESHOLD:
                break
        
        if len(CURRENT_MOVES) >= 8:
            continue
        
        ACCESSIBLE_CONTAINERS = GET_CONTAINERS(CURRENT_GRID)
        DESTINATIONS = GET_VALID_DESTINATIONS(CURRENT_GRID)
        
        for START_POSITION in ACCESSIBLE_CONTAINERS:
            FROM_COL = START_POSITION[1]
            
            for END_POSITION in DESTINATIONS:
                TO_COL = END_POSITION[1]
                
                if (FROM_COL <= 6 and TO_COL > 6) or (FROM_COL > 6 and TO_COL <= 6):
                    NEW_GRID = MOVE_CONTAINER(CURRENT_GRID, START_POSITION, END_POSITION)
                    NEW_IMBALANCE = CALCULATE_BALANCE(NEW_GRID)
                    NEW_MOVES = CURRENT_MOVES + [(START_POSITION, END_POSITION)]
                    
                    if NEW_IMBALANCE < CURRENT_IMBALANCE:
                        CONTAINER_SOLVER_QUEUE.append((NEW_GRID, NEW_MOVES, NEW_IMBALANCE))
    
    return BEST_SOLUTION, BEST_IMBALANCE