import os
from datetime import datetime

# Analyzes and extracts information from the manifest file
def PARSE_MANIFEST_FILE(FILENAME):
    GRID = {}
    CONTAINER_COUNT = 0
    
    with open(FILENAME, 'r') as FHANDLE:
        LINES = FHANDLE.readlines()
    
    for LINE in LINES:
        LINE = LINE.strip()
        if not LINE or not LINE.startswith('['):
            continue
        
        PARTS_OF_FILE = LINE.split(',', 1)
        if len(PARTS_OF_FILE) < 2:
            continue
        
        ROW_PART = PARTS_OF_FILE[0].strip('[')
        REST = PARTS_OF_FILE[1]
        
        COL_PART = REST.split(']')[0]
        REMAINDER = REST.split(']', 1)[1].strip().lstrip(',').strip()
        
        try:
            ROW = int(ROW_PART)
            COL = int(COL_PART)
        except ValueError:
            continue
        
        if REMAINDER.startswith('{') and '}' in REMAINDER:
            WEIGHT_STR = REMAINDER.split('{')[1].split('}')[0]
            DESC_PART = REMAINDER.split('}', 1)[1].strip()
            
            if DESC_PART.startswith(','):
                DESC_PART = DESC_PART[1:].strip()
            
            try:
                WEIGHT = int(WEIGHT_STR)
            except ValueError:
                WEIGHT = 0
            
            if DESC_PART == 'NAN':
                GRID[(ROW, COL)] = {'weight': 0, 'type': 'NAN', 'description': 'NAN'}
            elif DESC_PART == 'UNUSED':
                GRID[(ROW, COL)] = {'weight': 0, 'type': 'UNUSED', 'description': 'UNUSED'}
            else:
                GRID[(ROW, COL)] = {'weight': WEIGHT, 'type': 'CONTAINER', 'description': DESC_PART}
                if WEIGHT > 0:
                    CONTAINER_COUNT += 1
    
    for ROW in range(1, 9):
        for COL in range(1, 13):
            if (ROW, COL) not in GRID:
                GRID[(ROW, COL)] = {'weight': 0, 'type': 'UNUSED', 'description': 'UNUSED'}
    
    return GRID, CONTAINER_COUNT

# Writes entries to the manifest file
def WRITE_MANIFEST(FILENAME, GRID):
    DESKTOP = os.path.join(os.path.expanduser('~'), 'Desktop')
    FULL_PATH = os.path.join(DESKTOP, FILENAME)
    
    with open(FULL_PATH, 'w') as FILE:
        for ROW in range(1, 9):
            for COL in range(1, 13):
                CELL = GRID.get((ROW, COL))
                if CELL:
                    WEIGHT = CELL['weight']
                    DESC = CELL['description']
                    FILE.write(f"[{ROW:02d},{COL:02d}], {{{WEIGHT:05d}}}, {DESC}\n")

# Creates the date stamp for each log entry
def CREATE_MANFIEST_LOG_ENTRY(MESSAGE):
    TIMESTAMP = datetime.now().strftime("%m %d %Y: %H:%M")
    return f"{TIMESTAMP} {MESSAGE}"

# Saves the log file in the correct format and naming convention
def SAVE_LOG_FILE(LOG_ENTRIES, START_TIME):
    DESKTOP = os.path.join(os.path.expanduser('~'), 'Desktop')
    TIMESTAMP = START_TIME.strftime("%m_%d_%Y_%H%M")
    FILENAME = f"KeoghsPort{TIMESTAMP}.txt"
    FULL_PATH = os.path.join(DESKTOP, FILENAME)
    
    with open(FULL_PATH, 'w') as FILE:
        for ENTRY in LOG_ENTRIES:
            FILE.write(ENTRY + '\n')
    
    return FILENAME

# Calculates the time for each step of a container move:
def CALCULATE_MOVE_TIME(FROM_POS, TO_POS, PREV_POS):
    PARK_POSITION = (1, 8)
    
    TIME_TO_SOURCE = abs(PREV_POS[0] - FROM_POS[0]) + abs(PREV_POS[1] - FROM_POS[1])
    
    TIME_SOURCE_TO_DEST = abs(FROM_POS[0] - TO_POS[0]) + abs(FROM_POS[1] - TO_POS[1])
    
    TIME_DEST_TO_PARK = abs(TO_POS[0] - PARK_POSITION[0]) + abs(TO_POS[1] - PARK_POSITION[1])
    
    return (TIME_TO_SOURCE, TIME_SOURCE_TO_DEST, TIME_DEST_TO_PARK)