import os
from datetime import datetime
from CONTAINER_SOLVER import BALANCE_SHIP, CALCULATE_BALANCE_COST
from HELPER_FUNCTIONS import PARSE_MANIFEST_FILE, WRITE_MANIFEST, CREATE_MANFIEST_LOG_ENTRY, SAVE_LOG_FILE, CALCULATE_MOVE_TIME
from GUI_GRID_VISUALIZATION import SHOW_BALANCE_VISUALIZATION

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
    
    OUTBOUND_FILE = MANIFEST_FILE.replace(".txt", "OUTBOUND.txt")
    SOLUTION = None
    FINAL_GRID = GRID
    
    # Store a deep copy of the original grid for visualization
    ORIGINAL_GRID = {}
    for pos, cell in GRID.items():
        ORIGINAL_GRID[pos] = cell.copy()
    
    if CONTAINER_COUNT == 0:
        print("\nShip is empty - already balanced!")
        WRITE_MANIFEST(OUTBOUND_FILE, GRID)
        LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Finished a Cycle. Manifest {OUTBOUND_FILE} was written to desktop, and a reminder pop-up to operator to send file was displayed."))
    
    elif CONTAINER_COUNT == 1:
        print("\nShip has only one container - already balanced!")
        WRITE_MANIFEST(OUTBOUND_FILE, GRID)
        LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Finished a Cycle. Manifest {OUTBOUND_FILE} was written to desktop, and a reminder pop-up to operator to send file was displayed."))
    
    elif CONTAINER_COUNT == 2:
        CONTAINERS = [(POS, CELL) for POS, CELL in GRID.items() if CELL['weight'] > 0]
        COL1 = CONTAINERS[0][0][1]
        COL2 = CONTAINERS[1][0][1]
        
        if (COL1 <= 6 and COL2 > 6) or (COL1 > 6 and COL2 <= 6):
            print("\nShip has two containers on opposite sides - already balanced!")
            WRITE_MANIFEST(OUTBOUND_FILE, GRID)
            LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Finished a Cycle. Manifest {OUTBOUND_FILE} was written to desktop, and a reminder pop-up to operator to send file was displayed."))
        
        else:
            print("\nShip has two containers on the same side - moving one to achieve legal balance...")
            SOLUTION, FINAL_GRID = BALANCE_SHIP(GRID)

            if SOLUTION:
                # Now steps: 2 per move + 1 final return to park
                TOTAL_TIME = CALCULATE_BALANCE_COST(SOLUTION)
                TOTAL_STEPS = len(SOLUTION) * 2 + 1
                print(f"\n... solution was found, it will take {TOTAL_TIME} minutes and {TOTAL_STEPS} moves")
                LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Balance solution found, it will require {TOTAL_STEPS} moves/{TOTAL_TIME} minutes."))

                STEP_NUM = 1
                for i, MOVE in enumerate(SOLUTION, 1):
                    FROM_POS, TO_POS = MOVE
                    # prev position (for time to source) is park for first move, otherwise previous move destination
                    PREV_POS = (1, 8) if i == 1 else SOLUTION[i-2][1]
                    MOVE_TIME = CALCULATE_MOVE_TIME(FROM_POS, TO_POS, PREV_POS)
                    
                    # Step: move from PARK or previous pos to source
                    print(f"\n{STEP_NUM} of {TOTAL_STEPS}: Move from {'PARK' if PREV_POS == (1,8) else f'[{PREV_POS[0]:02d},{PREV_POS[1]:02d}]'} to [{FROM_POS[0]:02d},{FROM_POS[1]:02d}], {MOVE_TIME[0]} minutes")
                    LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Move from {'PARK' if PREV_POS == (1,8) else f'[{PREV_POS[0]:02d},{PREV_POS[1]:02d}]'} to [{FROM_POS[0]:02d},{FROM_POS[1]:02d}], {MOVE_TIME[0]} minutes"))
                    STEP_NUM += 1
                    
                    # Step: move container from source to destination
                    print(f"{STEP_NUM} of {TOTAL_STEPS}: Move container in [{FROM_POS[0]:02d},{FROM_POS[1]:02d}] to [{TO_POS[0]:02d},{TO_POS[1]:02d}], {MOVE_TIME[1]} minutes")
                    LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"[{FROM_POS[0]:02d},{FROM_POS[1]:02d}] was moved to [{TO_POS[0]:02d},{TO_POS[1]:02d}]"))
                    STEP_NUM += 1
                
                # Final return to PARK (only once)
                LAST_DEST = SOLUTION[-1][1]
                # compute time directly (or reuse last MOVE_TIME[2])
                TIME_TO_PARK = abs(LAST_DEST[0] - 1) + abs(LAST_DEST[1] - 8)
                print(f"\n{STEP_NUM} of {TOTAL_STEPS}: Move from [{LAST_DEST[0]:02d},{LAST_DEST[1]:02d}] to PARK, {TIME_TO_PARK} minutes")
                LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Move from [{LAST_DEST[0]:02d},{LAST_DEST[1]:02d}] to PARK, {TIME_TO_PARK} minutes"))
                
                # Ask for operator comment after all moves are shown
                COMMENT_INPUT = input("\nAdd a comment? (y/n): ").strip().lower()
                if COMMENT_INPUT == 'y':
                    print("Enter your comment (press Enter twice when done):")
                    COMMENT_LINES = []
                    while True:
                        LINE = input()
                        if LINE == "":
                            break
                        COMMENT_LINES.append(LINE)
                    
                    if COMMENT_LINES:
                        FULL_COMMENT = " ".join(COMMENT_LINES)
                        LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(FULL_COMMENT))

                print(f"\nDone! {OUTBOUND_FILE} was written to the desktop")
                WRITE_MANIFEST(OUTBOUND_FILE, FINAL_GRID)
                LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Finished a Cycle. Manifest {OUTBOUND_FILE} was written to desktop."))

            else:
                print("\nNo balance solution found within constraints.")
                WRITE_MANIFEST(OUTBOUND_FILE, GRID)
    
    elif INITIAL_IMBALANCE < BALANCE_THRESHOLD:
        print("\nShip is already balanced!")
        WRITE_MANIFEST(OUTBOUND_FILE, GRID)
        LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Finished a Cycle. Manifest {OUTBOUND_FILE} was written to desktop, and a reminder pop-up to operator to send file was displayed."))
    
    else:
        print("\nShip needs balancing. Calculating solution...")
        SOLUTION, FINAL_GRID = BALANCE_SHIP(GRID)
        
        if SOLUTION:
            TOTAL_TIME = CALCULATE_BALANCE_COST(SOLUTION)
            TOTAL_STEPS = len(SOLUTION) * 2 + 1  # two steps per move + final return to park
            print(f"\n... solution was found, it will take {TOTAL_TIME} minutes and {TOTAL_STEPS} moves")
            LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Balance solution found, it will require {TOTAL_STEPS} moves/{TOTAL_TIME} minutes."))
            
            STEP_NUM = 1
            for i, MOVE in enumerate(SOLUTION, 1):
                FROM_POS, TO_POS = MOVE
                PREV_POS = (1, 8) if i == 1 else SOLUTION[i-2][1]
                MOVE_TIME = CALCULATE_MOVE_TIME(FROM_POS, TO_POS, PREV_POS)
                
                print(f"\n{STEP_NUM} of {TOTAL_STEPS}: Move from {'PARK' if PREV_POS == (1,8) else f'[{PREV_POS[0]:02d},{PREV_POS[1]:02d}]'} to [{FROM_POS[0]:02d},{FROM_POS[1]:02d}], {MOVE_TIME[0]} minutes")
                LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Move from {'PARK' if PREV_POS == (1,8) else f'[{PREV_POS[0]:02d},{PREV_POS[1]:02d}]'} to [{FROM_POS[0]:02d},{FROM_POS[1]:02d}], {MOVE_TIME[0]} minutes"))
                STEP_NUM += 1
                
                print(f"{STEP_NUM} of {TOTAL_STEPS}: Move container in [{FROM_POS[0]:02d},{FROM_POS[1]:02d}] to [{TO_POS[0]:02d},{TO_POS[1]:02d}], {MOVE_TIME[1]} minutes")
                LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"[{FROM_POS[0]:02d},{FROM_POS[1]:02d}] was moved to [{TO_POS[0]:02d},{TO_POS[1]:02d}]"))
                STEP_NUM += 1
            
            # Final single return to PARK
            LAST_DEST = SOLUTION[-1][1]
            TIME_TO_PARK = abs(LAST_DEST[0] - 1) + abs(LAST_DEST[1] - 8)
            print(f"\n{STEP_NUM} of {TOTAL_STEPS}: Move from [{LAST_DEST[0]:02d},{LAST_DEST[1]:02d}] to PARK, {TIME_TO_PARK} minutes")
            LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Move from [{LAST_DEST[0]:02d},{LAST_DEST[1]:02d}] to PARK, {TIME_TO_PARK} minutes"))
            
            # Ask for operator comment after all moves are shown
            COMMENT_INPUT = input("\nAdd a comment? (y/n): ").strip().lower()
            if COMMENT_INPUT == 'y':
                print("Enter your comment (press Enter twice when done):")
                COMMENT_LINES = []
                while True:
                    LINE = input()
                    if LINE == "":
                        break
                    COMMENT_LINES.append(LINE)
                
                if COMMENT_LINES:
                    FULL_COMMENT = " ".join(COMMENT_LINES)
                    LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(FULL_COMMENT))
            
            print(f"\nDone! {OUTBOUND_FILE} was written to the desktop")
            WRITE_MANIFEST(OUTBOUND_FILE, FINAL_GRID)
            LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY(f"Finished a Cycle. Manifest {OUTBOUND_FILE} was written to desktop."))
        
        else:
            print("\nCannot balance ship. SIFT operation required.")
            LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY("SIFT operation required - ship cannot be balanced."))
            WRITE_MANIFEST(OUTBOUND_FILE, GRID)
    
    LOG_ENTRIES.append(CREATE_MANFIEST_LOG_ENTRY("Program was shut down."))
    
    LOG_FILENAME = SAVE_LOG_FILE(LOG_ENTRIES, START_TIME, MANIFEST_FILE=MANIFEST_FILE)
    print(f"\nLog saved to: {LOG_FILENAME}")
    print("\n" + "=" * 60)
    
    if SOLUTION and len(SOLUTION) > 0:
        print("\nOpening visualization window...")
        SHOW_BALANCE_VISUALIZATION(ORIGINAL_GRID, SOLUTION, SHIP_NAME)

if __name__ == "__main__":
    main()