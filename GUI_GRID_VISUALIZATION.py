import tkinter as tk
from tkinter import ttk

# GUI class for visualizing ship balancing operations
class ShipBalanceGUI:
    # Initialize the GUI with grid data and solution moves
    def __init__(self, ROOT, GRID, SOLUTION, SHIP_NAME):
        self.ROOT          = ROOT
        self.ROOT.title(f"Ship Balancing Visualization - {SHIP_NAME}")
        self.GRID          = GRID
        self.SOLUTION      = SOLUTION
        self.CURRENT_STEP  = 0
        self.CELL_SIZE     = 60
        self.PARK_POS      = (1, 8)
        
        self.EXPANDED_STEPS = self.CREATE_EXPANDED_STEPS()
        
        self.MAIN_FRAME    = ttk.Frame(ROOT, padding="10")
        self.MAIN_FRAME.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        TITLE = ttk.Label(self.MAIN_FRAME, text=f"Ship: {SHIP_NAME}", font=('Arial', 16, 'bold'))
        TITLE.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.CANVAS = tk.Canvas(self.MAIN_FRAME, width=self.CELL_SIZE*12+50, 
                                height=self.CELL_SIZE*8+50, bg='white')
        self.CANVAS.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        self.INFO_FRAME = ttk.LabelFrame(self.MAIN_FRAME, text="Information", padding="10")
        self.INFO_FRAME.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.STEP_LABEL = ttk.Label(self.INFO_FRAME, text="", font=('Arial', 10))
        self.STEP_LABEL.grid(row=0, column=0, sticky=tk.W)
        
        self.BALANCE_LABEL = ttk.Label(self.INFO_FRAME, text="", font=('Arial', 10))
        self.BALANCE_LABEL.grid(row=1, column=0, sticky=tk.W)
        
        self.MOVE_LABEL = ttk.Label(self.INFO_FRAME, text="", font=('Arial', 10, 'bold'))
        self.MOVE_LABEL.grid(row=2, column=0, sticky=tk.W)
        
        self.BUTTON_FRAME = ttk.Frame(self.MAIN_FRAME)
        self.BUTTON_FRAME.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.PREV_BUTTON = ttk.Button(self.BUTTON_FRAME, text="← Previous", 
                                      command=self.PREV_STEP, state='disabled')
        self.PREV_BUTTON.grid(row=0, column=0, padx=5)
        
        self.NEXT_BUTTON = ttk.Button(self.BUTTON_FRAME, text="Next →", 
                                      command=self.NEXT_STEP)
        self.NEXT_BUTTON.grid(row=0, column=1, padx=5)
        
        self.RESET_BUTTON = ttk.Button(self.BUTTON_FRAME, text="Reset", 
                                       command=self.RESET_VIEW)
        self.RESET_BUTTON.grid(row=0, column=2, padx=5)
        
        self.INITIAL_GRID = {}
        for pos, cell in self.GRID.items():
            self.INITIAL_GRID[pos] = cell.copy()
        
        self.GRID_STATES = []
        self.APPLY_MOVES()
        
        self.DRAW_GRID()
        self.UPDATE_INFO()
    
    # Create expanded step list that includes PARK movements
    def CREATE_EXPANDED_STEPS(self):
        EXPANDED = []
        
        for i, MOVE in enumerate(self.SOLUTION, 1):
            FROM_POS, TO_POS = MOVE
            
            if i == 1:
                TIME_TO_SOURCE = abs(self.PARK_POS[0] - FROM_POS[0]) + abs(self.PARK_POS[1] - FROM_POS[1])
                EXPANDED.append({
                    'type': 'to_source',
                    'move_num': i,
                    'from': self.PARK_POS,
                    'to': FROM_POS,
                    'time': TIME_TO_SOURCE,
                    'description': f"{i} of {len(self.SOLUTION)}: Move from PARK to [{FROM_POS[0]:02d},{FROM_POS[1]:02d}], {TIME_TO_SOURCE} minutes"
                })
            else:
                PREV_POS = self.SOLUTION[i-2][1]
                TIME_TO_SOURCE = abs(PREV_POS[0] - FROM_POS[0]) + abs(PREV_POS[1] - FROM_POS[1])
                EXPANDED.append({
                    'type': 'to_source',
                    'move_num': i,
                    'from': PREV_POS,
                    'to': FROM_POS,
                    'time': TIME_TO_SOURCE,
                    'description': f"{i} of {len(self.SOLUTION)}: Move from [{PREV_POS[0]:02d},{PREV_POS[1]:02d}] to [{FROM_POS[0]:02d},{FROM_POS[1]:02d}], {TIME_TO_SOURCE} minutes"
                })
            
            TIME_SOURCE_TO_DEST = abs(FROM_POS[0] - TO_POS[0]) + abs(FROM_POS[1] - TO_POS[1])
            EXPANDED.append({
                'type': 'move_container',
                'move_num': i,
                'from': FROM_POS,
                'to': TO_POS,
                'time': TIME_SOURCE_TO_DEST,
                'description': f"{i} of {len(self.SOLUTION)}: Move container in [{FROM_POS[0]:02d},{FROM_POS[1]:02d}] to [{TO_POS[0]:02d},{TO_POS[1]:02d}], {TIME_SOURCE_TO_DEST} minutes"
            })
        
        # Final step: return to PARK from last destination
        LAST_POS = self.SOLUTION[-1][1]
        TIME_DEST_TO_PARK = abs(LAST_POS[0] - self.PARK_POS[0]) + abs(LAST_POS[1] - self.PARK_POS[1])
        EXPANDED.append({
            'type': 'to_park',
            'move_num': len(self.SOLUTION),
            'from': LAST_POS,
            'to': self.PARK_POS,
            'time': TIME_DEST_TO_PARK,
            'description': f"{len(self.SOLUTION)} of {len(self.SOLUTION)}: Move from [{LAST_POS[0]:02d},{LAST_POS[1]:02d}] to PARK, {TIME_DEST_TO_PARK} minutes"
        })
        
        return EXPANDED
    
    # Apply each move to create grid states for each step
    def APPLY_MOVES(self):
        CURRENT_GRID = {}
        for pos, cell in self.INITIAL_GRID.items():
            CURRENT_GRID[pos] = cell.copy()
        
        self.GRID_STATES.append(CURRENT_GRID.copy())
        
        for STEP in self.EXPANDED_STEPS:
            if STEP['type'] == 'to_source':
                self.GRID_STATES.append(CURRENT_GRID.copy())
            elif STEP['type'] == 'move_container':
                FROM_POS = STEP['from']
                TO_POS = STEP['to']
                NEW_GRID = {}
                
                for POSITION in CURRENT_GRID:
                    if POSITION == FROM_POS:
                        NEW_GRID[POSITION] = {'weight': 0, 'type': 'UNUSED', 'description': 'UNUSED'}
                    elif POSITION == TO_POS:
                        NEW_GRID[POSITION] = {
                            'weight': CURRENT_GRID[FROM_POS]['weight'],
                            'type': CURRENT_GRID[TO_POS]['type'],
                            'description': CURRENT_GRID[FROM_POS]['description']
                        }
                    else:
                        NEW_GRID[POSITION] = CURRENT_GRID[POSITION].copy()
                
                self.GRID_STATES.append(NEW_GRID)
                CURRENT_GRID = NEW_GRID
            elif STEP['type'] == 'to_park':
                self.GRID_STATES.append(CURRENT_GRID.copy())
    
    # Draw the ship grid on the canvas
    def DRAW_GRID(self):
        self.CANVAS.delete("all")
        
        CURRENT_GRID = self.GRID_STATES[self.CURRENT_STEP]
        
        for COL in range(1, 13):
            X = 25 + (COL - 1) * self.CELL_SIZE + self.CELL_SIZE // 2
            self.CANVAS.create_text(X, 15, text=str(COL), font=('Arial', 10, 'bold'))
        
        DIVIDER_X = 25 + 6 * self.CELL_SIZE
        self.CANVAS.create_line(DIVIDER_X, 30, DIVIDER_X, 30 + 8 * self.CELL_SIZE, 
                                width=3, fill='red', dash=(5, 5))
        
        HIGHLIGHT_FROM = None
        HIGHLIGHT_TO = None
        
        if self.CURRENT_STEP > 0 and self.CURRENT_STEP <= len(self.EXPANDED_STEPS):
            STEP_INFO = self.EXPANDED_STEPS[self.CURRENT_STEP - 1]
            
            if STEP_INFO['from'] != self.PARK_POS:
                HIGHLIGHT_FROM = STEP_INFO['from']
            if STEP_INFO['to'] != self.PARK_POS:
                HIGHLIGHT_TO = STEP_INFO['to']
        
        for ROW in range(8, 0, -1):
            for COL in range(1, 13):
                X    = 25 + (COL - 1) * self.CELL_SIZE
                Y    = 30 + (8 - ROW) * self.CELL_SIZE
                CELL = CURRENT_GRID.get((ROW, COL))
                
                if not CELL:
                    continue
                
                if CELL['type'] == 'NAN':
                    COLOR   = '#808080'
                    OUTLINE = 'black'
                elif CELL['weight'] > 0:
                    COLOR   = '#4CAF50'
                    OUTLINE = 'black'
                else:
                    COLOR   = '#E0E0E0'
                    OUTLINE = 'gray'
                
                WIDTH = 1
                
                if (ROW, COL) == HIGHLIGHT_FROM:
                    OUTLINE = 'blue'
                    WIDTH   = 3
                elif (ROW, COL) == HIGHLIGHT_TO:
                    OUTLINE = 'orange'
                    WIDTH   = 3
                
                self.CANVAS.create_rectangle(X, Y, X + self.CELL_SIZE, Y + self.CELL_SIZE,
                                            fill=COLOR, outline=OUTLINE, width=WIDTH)
                
                self.CANVAS.create_text(X + 5, Y + 5, 
                                       text=f"[{ROW},{COL}]", 
                                       anchor=tk.NW, font=('Arial', 7))
                
                if CELL['weight'] > 0:
                    self.CANVAS.create_text(X + self.CELL_SIZE // 2, Y + self.CELL_SIZE // 2 - 5,
                                           text=f"{CELL['weight']} kg", 
                                           font=('Arial', 8, 'bold'))
                    DESC = CELL['description']
                    if len(DESC) > 10:
                        DESC = DESC[:8] + "..."
                    self.CANVAS.create_text(X + self.CELL_SIZE // 2, Y + self.CELL_SIZE // 2 + 8,
                                           text=DESC, font=('Arial', 7))
                elif CELL['type'] == 'NAN':
                    self.CANVAS.create_text(X + self.CELL_SIZE // 2, Y + self.CELL_SIZE // 2,
                                           text="NAN", font=('Arial', 8, 'bold'))
        
        if HIGHLIGHT_FROM and HIGHLIGHT_TO and HIGHLIGHT_FROM != HIGHLIGHT_TO:
            STEP_INFO = self.EXPANDED_STEPS[self.CURRENT_STEP - 1] if self.CURRENT_STEP > 0 else None
            
            if STEP_INFO and STEP_INFO['type'] == 'move_container':
                X1 = 25 + (HIGHLIGHT_FROM[1] - 1) * self.CELL_SIZE + self.CELL_SIZE // 2
                Y1 = 30 + (8 - HIGHLIGHT_FROM[0]) * self.CELL_SIZE + self.CELL_SIZE // 2
                X2 = 25 + (HIGHLIGHT_TO[1] - 1) * self.CELL_SIZE + self.CELL_SIZE // 2
                Y2 = 30 + (8 - HIGHLIGHT_TO[0]) * self.CELL_SIZE + self.CELL_SIZE // 2
                
                self.CANVAS.create_line(X1, Y1, X2, Y2, arrow=tk.LAST, width=3, 
                                       fill='red', dash=(5, 3))
        
        LEGEND_Y = 30 + 8 * self.CELL_SIZE + 20
        self.CANVAS.create_rectangle(25, LEGEND_Y, 45, LEGEND_Y + 15, fill='#4CAF50')
        self.CANVAS.create_text(50, LEGEND_Y + 7, text="Container", anchor=tk.W, font=('Arial', 9))
        
        self.CANVAS.create_rectangle(125, LEGEND_Y, 145, LEGEND_Y + 15, fill='#E0E0E0')
        self.CANVAS.create_text(150, LEGEND_Y + 7, text="Empty", anchor=tk.W, font=('Arial', 9))
        
        self.CANVAS.create_rectangle(200, LEGEND_Y, 220, LEGEND_Y + 15, fill='#808080')
        self.CANVAS.create_text(225, LEGEND_Y + 7, text="Unavailable", anchor=tk.W, font=('Arial', 9))
    
    # Calculate port and starboard weights for current state
    def CALCULATE_BALANCE_INFO(self):
        CURRENT_GRID = self.GRID_STATES[self.CURRENT_STEP]
        PORT_WEIGHT      = 0
        STARBOARD_WEIGHT = 0
        
        for ROW in range(1, 9):
            for COL in range(1, 13):
                CELL = CURRENT_GRID.get((ROW, COL))
                if CELL and CELL['weight'] > 0:
                    if COL <= 6:
                        PORT_WEIGHT += CELL['weight']
                    else:
                        STARBOARD_WEIGHT += CELL['weight']
        
        IMBALANCE = abs(PORT_WEIGHT - STARBOARD_WEIGHT)
        return PORT_WEIGHT, STARBOARD_WEIGHT, IMBALANCE
    
    # Update the information panel with current step details
    def UPDATE_INFO(self):
        PORT_WEIGHT, STARBOARD_WEIGHT, IMBALANCE = self.CALCULATE_BALANCE_INFO()
        
        TOTAL_STEPS = len(self.EXPANDED_STEPS)
        self.STEP_LABEL.config(text=f"Step {self.CURRENT_STEP} of {TOTAL_STEPS}")
        self.BALANCE_LABEL.config(
            text=f"Port: {PORT_WEIGHT} kg  |  Starboard: {STARBOARD_WEIGHT} kg  |  Imbalance: {IMBALANCE} kg"
        )
        
        if self.CURRENT_STEP > 0 and self.CURRENT_STEP <= len(self.EXPANDED_STEPS):
            STEP_INFO = self.EXPANDED_STEPS[self.CURRENT_STEP - 1]
            self.MOVE_LABEL.config(text=STEP_INFO['description'])
        else:
            self.MOVE_LABEL.config(text="Initial state")
        
        self.PREV_BUTTON.config(state='normal' if self.CURRENT_STEP > 0 else 'disabled')
        self.NEXT_BUTTON.config(state='normal' if self.CURRENT_STEP < len(self.EXPANDED_STEPS) else 'disabled')
    
    # Move to next step in the visualization
    def NEXT_STEP(self):
        if self.CURRENT_STEP < len(self.EXPANDED_STEPS):
            self.CURRENT_STEP += 1
            self.DRAW_GRID()
            self.UPDATE_INFO()
    
    # Move to previous step in the visualization
    def PREV_STEP(self):
        if self.CURRENT_STEP > 0:
            self.CURRENT_STEP -= 1
            self.DRAW_GRID()
            self.UPDATE_INFO()
    
    # Reset to initial state
    def RESET_VIEW(self):
        self.CURRENT_STEP = 0
        self.DRAW_GRID()
        self.UPDATE_INFO()


# Create and show the GUI visualization window
def SHOW_BALANCE_VISUALIZATION(GRID, SOLUTION, SHIP_NAME):
    if not SOLUTION:
        print("No moves to visualize - ship is already balanced or requires SIFT.")
        return
    
    ROOT = tk.Tk()
    APP  = ShipBalanceGUI(ROOT, GRID, SOLUTION, SHIP_NAME)
    ROOT.mainloop()