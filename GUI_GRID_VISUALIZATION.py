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
        
        self.MOVE_LABEL = ttk.Label(self.INFO_FRAME, text="", font=('Arial', 10))
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
        
        self.GRID_STATES = [self.GRID.copy()]
        self.APPLY_MOVES()
        
        self.DRAW_GRID()
        self.UPDATE_INFO()
    
    # Apply each move to create grid states for each step
    def APPLY_MOVES(self):
        CURRENT_GRID = self.GRID.copy()
        
        for MOVE in self.SOLUTION:
            FROM_POS, TO_POS = MOVE
            NEW_GRID         = {}
            
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
                if self.CURRENT_STEP > 0 and self.CURRENT_STEP <= len(self.SOLUTION):
                    FROM_POS, TO_POS = self.SOLUTION[self.CURRENT_STEP - 1]
                    if (ROW, COL) == FROM_POS:
                        OUTLINE = 'blue'
                        WIDTH   = 3
                    elif (ROW, COL) == TO_POS:
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
        
        LEGEND_Y = 30 + 8 * self.CELL_SIZE + 20
        self.CANVAS.create_rectangle(25, LEGEND_Y, 45, LEGEND_Y + 15, fill='#4CAF50')
        self.CANVAS.create_text(50, LEGEND_Y + 7, text="Container", anchor=tk.W, font=('Arial', 9))
        
        self.CANVAS.create_rectangle(125, LEGEND_Y, 145, LEGEND_Y + 15, fill='#E0E0E0')
        self.CANVAS.create_text(150, LEGEND_Y + 7, text="Empty", anchor=tk.W, font=('Arial', 9))
        
        self.CANVAS.create_rectangle(200, LEGEND_Y, 220, LEGEND_Y + 15, fill='#808080')
        self.CANVAS.create_text(225, LEGEND_Y + 7, text="Unavailable", anchor=tk.W, font=('Arial', 9))
    
    # Calculate port and starboard weights for current state
    def CALCULATE_BALANCE_INFO(self):
        CURRENT_GRID     = self.GRID_STATES[self.CURRENT_STEP]
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
        
        self.STEP_LABEL.config(text=f"Step {self.CURRENT_STEP} of {len(self.SOLUTION)}")
        self.BALANCE_LABEL.config(
            text=f"Port: {PORT_WEIGHT} kg  |  Starboard: {STARBOARD_WEIGHT} kg  |  Imbalance: {IMBALANCE} kg"
        )
        
        if self.CURRENT_STEP > 0 and self.CURRENT_STEP <= len(self.SOLUTION):
            FROM_POS, TO_POS = self.SOLUTION[self.CURRENT_STEP - 1]
            self.MOVE_LABEL.config(
                text=f"Move: [{FROM_POS[0]:02d},{FROM_POS[1]:02d}] → [{TO_POS[0]:02d},{TO_POS[1]:02d}]"
            )
        else:
            self.MOVE_LABEL.config(text="")
        
        self.PREV_BUTTON.config(state='normal' if self.CURRENT_STEP > 0 else 'disabled')
        self.NEXT_BUTTON.config(state='normal' if self.CURRENT_STEP < len(self.SOLUTION) else 'disabled')
    
    # Move to next step in the visualization
    def NEXT_STEP(self):
        if self.CURRENT_STEP < len(self.SOLUTION):
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


if __name__ == "__main__":
    TEST_GRID = {}
    for ROW in range(1, 9):
        for COL in range(1, 13):
            TEST_GRID[(ROW, COL)] = {'weight': 0, 'type': 'UNUSED', 'description': 'UNUSED'}
    
    TEST_GRID[(1, 2)]  = {'weight': 1000, 'type': 'CONTAINER', 'description': 'Container A'}
    TEST_GRID[(1, 3)]  = {'weight': 1500, 'type': 'CONTAINER', 'description': 'Container B'}
    TEST_GRID[(1, 10)] = {'weight': 0, 'type': 'UNUSED', 'description': 'UNUSED'}
    
    TEST_SOLUTION = [
        ((1, 3), (1, 10))
    ]
    
    SHOW_BALANCE_VISUALIZATION(TEST_GRID, TEST_SOLUTION, "TEST_SHIP")