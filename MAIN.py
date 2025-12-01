import os
from datetime import datetime
from CONTAINER_SOLVER import BALANCE_SHIP, CALCULATE_BALANCE_COST
from HELPER_FUNCTIONS import PARSE_MANIFEST_FILE, WRITE_MANIFEST, CREATE_MANFIEST_LOG_ENTRY, SAVE_LOG_FILE

# Main program that runs the container solver
def main():
    LOG_ENTRIES = []
    START_TIME = datetime.now()
    
    print("=" * 60)
    print("KEOGH'S PORT - SHIP BALANCING SYSTEM")
    print("=" * 60)
    
    MANIFEST_FILE = input("\nEnter manifest filename: ").strip()
    
    if not os.path.exists(MANIFEST_FILE):
        print(f"ERROR: File {MANIFEST_FILE} not found!")
        return
    
    LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY("Program was started."))
    
    SHIP_NAME = MANIFEST_FILE.replace(".txt", "").replace("OUTBOUND", "")
    GRID, CONTAINER_COUNT = PARSE_MANIFEST_FILE(MANIFEST_FILE)
    
    LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Manifest {MANIFEST_FILE} is opened, there are {CONTAINER_COUNT} containers on the ship."))
    
    INITIAL_PORT_WEIGHT = 0
    INITIAL_STARBOARD_WEIGHT = 0
    
    for ROW in range(1, 9):
        for COL in range(1, 13):
            CELL = GRID.get((ROW, COL))
            if CELL and CELL['weight'] > 0:
                if COL <= 6:
                    INITIAL_PORT_WEIGHT += CELL['weight']
                else:
                    INITIAL_STARBOARD_WEIGHT += CELL['weight']
    
    TOTAL_WEIGHT = INITIAL_PORT_WEIGHT + INITIAL_STARBOARD_WEIGHT
    BALANCE_THRESHOLD = TOTAL_WEIGHT * 0.10
    INITIAL_IMBALANCE = abs(INITIAL_PORT_WEIGHT - INITIAL_STARBOARD_WEIGHT)
    
    print(f"\nShip: {SHIP_NAME}")
    print(f"Containers: {CONTAINER_COUNT}")
    print(f"Port side weight: {INITIAL_PORT_WEIGHT} kg")
    print(f"Starboard side weight: {INITIAL_STARBOARD_WEIGHT} kg")
    print(f"Imbalance: {INITIAL_IMBALANCE} kg")
    print(f"Balance threshold (10%): {BALANCE_THRESHOLD:.2f} kg")
    
    if CONTAINER_COUNT == 0:
        print("\nShip is empty - already balanced!")
        OUTBOUND_FILE = MANIFEST_FILE.replace(".txt", "OUTBOUND.txt")
        WRITE_MANIFEST(OUTBOUND_FILE, GRID)
        LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Finished a Cycle. Manifest {OUTBOUND_FILE} was written to desktop, and a reminder pop-up to operator to send file was displayed."))
    
    elif CONTAINER_COUNT == 1:
        print("\nShip has only one container - already balanced!")
        OUTBOUND_FILE = MANIFEST_FILE.replace(".txt", "OUTBOUND.txt")
        WRITE_MANIFEST(OUTBOUND_FILE, GRID)
        LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Finished a Cycle. Manifest {OUTBOUND_FILE} was written to desktop, and a reminder pop-up to operator to send file was displayed."))
    
    elif CONTAINER_COUNT == 2:
        CONTAINERS = [(POS, CELL) for POS, CELL in GRID.items() if CELL['weight'] > 0]
        COL1 = CONTAINERS[0][0][1]
        COL2 = CONTAINERS[1][0][1]
        
        if (COL1 <= 6 and COL2 > 6) or (COL1 > 6 and COL2 <= 6):
            print("\nShip has two containers on opposite sides - already balanced!")
            OUTBOUND_FILE = MANIFEST_FILE.replace(".txt", "OUTBOUND.txt")
            WRITE_MANIFEST(OUTBOUND_FILE, GRID)
            LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Finished a Cycle. Manifest {OUTBOUND_FILE} was written to desktop, and a reminder pop-up to operator to send file was displayed."))
        
        else:
            print("\nCalculating balance solution...")
            SOLUTION, _ = BALANCE_SHIP(GRID)
            
            if SOLUTION:
                TOTAL_TIME = CALCULATE_BALANCE_COST(SOLUTION)
                print(f"\nBalance solution found, it will require {len(SOLUTION)} moves/{TOTAL_TIME} minutes.")
                LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Balance solution found, it will require {len(SOLUTION)} moves/{TOTAL_TIME} minutes."))
            
            else:
                print("\nNo balance solution found within constraints.")
    
    elif INITIAL_IMBALANCE < BALANCE_THRESHOLD:
        print("\nShip is already balanced!")
        OUTBOUND_FILE = MANIFEST_FILE.replace(".txt", "OUTBOUND.txt")
        WRITE_MANIFEST(OUTBOUND_FILE, GRID)
        LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Finished a Cycle. Manifest {OUTBOUND_FILE} was written to desktop, and a reminder pop-up to operator to send file was displayed."))
    
    else:
        print("\nShip needs balancing. Calculating solution...")
        SOLUTION, _ = BALANCE_SHIP(GRID)
        
        if SOLUTION:
            TOTAL_TIME = CALCULATE_BALANCE_COST(SOLUTION)
            print(f"\nBalance solution found, it will require {len(SOLUTION)} moves/{TOTAL_TIME} minutes.")
            LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Balance solution found, it will require {len(SOLUTION)} moves/{TOTAL_TIME} minutes."))
            
            for MOVE in SOLUTION:
                FROM_POS, TO_POS = MOVE
                LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"[{FROM_POS[0]:02d},{FROM_POS[1]:02d}] was moved to [{TO_POS[0]:02d},{TO_POS[1]:02d}]"))
        
        else:
            print("\nCannot balance ship. SIFT operation required.")
            LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY("SIFT operation required - ship cannot be balanced."))
    
    LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY("Program was shut down."))
    
    LOG_FILENAME = SAVE_LOG_FILE(LOG_ENTRIES, START_TIME)
    print(f"\nLog saved to: {LOG_FILENAME}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()