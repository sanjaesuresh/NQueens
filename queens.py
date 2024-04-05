from queue import PriorityQueue
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class NQueensApp:
    def __init__(self, master):
        self.master = master
        self.master.title("N-Queens Solver")
        self.master.geometry("800x600")  # Adjusted for better layout
        self.solution_found = False  # Add this attribute
        self.n = None
        self.queen_positions = set()
        self.create_widgets()
        self.board_buttons = []

    def create_widgets(self):
        # It's crucial to use either pack or grid but not both for the widgets inside the same parent
        self.entry_frame = tk.Frame(self.master)
        self.entry_frame.pack()
        self.board_frame = tk.Frame(self.master)  # Frame to contain the board, allows using grid inside
        
        self.entry_size = tk.Entry(self.entry_frame)
        self.entry_size.pack(side='left')
        self.generate_button = tk.Button(self.entry_frame, text="Generate Board", command=self.generate_board)
        self.generate_button.pack(side='left')
        self.solve_button = tk.Button(self.entry_frame, text="Solve", command=self.solve, state=tk.DISABLED)
        self.solve_button.pack(side='left')
        self.cost_label = tk.Label(self.entry_frame, text="Cost: ")
        self.cost_label.pack(side='left')
        
        self.message_area = ScrolledText(self.master, height=10, state='disabled')
        self.message_area.pack()

    def generate_board(self):
        self.message_area['state'] = 'normal'  # Enable the message area to insert text
        self.message_area.delete('1.0', tk.END)  # Clear the message area before inserting new text
        try:
            n = int(self.entry_size.get())
            if n < 1 or n > 8:
                self.message_area.insert(tk.END, f"Error: Board size must be between 1 and 8.\n")
                return
            self.n = n
            self.queen_positions.clear()

            # Destroy the old board frame and create a new one
            self.board_frame.destroy()
            self.board_frame = tk.Frame(self.master)
            self.board_frame.pack()

            self.board_buttons = [[None for _ in range(n)] for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    button = tk.Button(self.board_frame, text=' ', width=4, height=2,
                                       command=lambda x=i, y=j: self.place_or_remove_queen(x, y))
                    button.grid(row=i, column=j)
                    self.board_buttons[i][j] = button
            self.solve_button['state'] = tk.NORMAL
            self.cost_label['text'] = "Cost: "  # Reset the cost label
        except ValueError:
            self.message_area.insert(tk.END, f"Error: Please enter a valid number.\n")

    def place_or_remove_queen(self, x, y):
        if self.solution_found:  # Check if a solution has been found
            return  # If so, ignore clicks
        if (y, x) not in self.queen_positions:  # Use (y, x) to match the chessboard coordinates
            self.queen_positions.add((y, x))
            self.board_buttons[x][y]['text'] = 'Q'

    def solve(self):
        
        self.message_area['state'] = 'normal'  # Enable the message area to insert text
        self.message_area.delete('1.0', tk.END)  # Clear the message area before inserting new text
        
        if not self.board_buttons:  # Ensures there's a generated board before solving
            self.message_area.insert(tk.END, f"Please generate a board first.\n")
            return
        
        if not self.queen_positions:
            self.message_area.insert(tk.END, f"No initial queens provided.\n")
            return
        
        # Check if the number of queens is appropriate for the board size.
        if len(self.queen_positions) > self.n:
            self.message_area.insert(tk.END, f"Error: Queens must be >0 and <=N\n")
            return
        
        if self.n == 2 and len(self.queen_positions) >= 2:
            self.message_area.insert(tk.END, f"No Solutions for N = 2, M >= 2\n")
            return
       
        initial_queens = [(x + 1, y + 1) for x, y in self.queen_positions]
        print(initial_queens)
        if not initial_queens:
            self.message_area.insert(tk.END, f"No queens on the board.\n")
            return
        
        # Handle the case where there's only one queen
        if len(initial_queens) == 1:
            all_solutions = [((col, row),) for row in range(1, self.n + 1) for col in range(1, self.n + 1)]
        else:
            # Generate all possible solutions for the board size and number of queens
            all_solutions = generate_solutions_for_m_queens(self.n, len(initial_queens))
           
        if tuple(initial_queens) in all_solutions: 
            self.message_area.insert(tk.END, f"Initial configuration is already a solution.\n")
            self.display_solution(initial_queens, 0)
            return

        result = integrated_n_queens_solution(initial_queens, self.n, all_solutions)
               
        if result:
            solution, cost, solution_path = result
            if isinstance(solution, tuple):  # Change this line to check for a tuple
                self.display_solution(list(solution), cost)  # Convert tuple to list
                final_state = solution_path[-1]
                self.message_area.insert(tk.END, f"Number of solutions: {len(all_solutions)}\n")
                self.message_area.insert(tk.END, f"Initial State: {(sorted(initial_queens))}\n")
                self.message_area.insert(tk.END, "Solution found!\n")
                self.message_area.insert(tk.END, f"Cost to solution: {cost}\n")
                self.message_area.insert(tk.END, f"Solution Path: {solution_path}\n")
                self.message_area.insert(tk.END, f"Final State: {final_state}\n")
                self.display_solution(list(final_state), cost)

            else:
                self.message_area.insert(tk.END, "No solution found.\n")
        else:
            self.message_area.insert(tk.END, "No solution found.\n")

        self.solve_button['state'] = tk.DISABLED  # Disable the solve button regardless of the outcome
        self.disable_board()  # Disable the board regardless of the outcome
        self.message_area['state'] = 'disabled'  # Disable editing after text is added


    def display_solution(self, solution, cost):
        # Clear the current board first
        for x in range(self.n):
            for y in range(self.n):
                self.board_buttons[x][y]['text'] = ' '
        # Now display the solution on the board
        for col, row in solution:
            # Adjusting because the board_buttons is 0-indexed, while solutions are 1-indexed
            self.board_buttons[row-1][col-1]['text'] = 'Q'
        self.cost_label['text'] = f"Cost: {cost}"
        self.solve_button['state'] = tk.DISABLED  # Disable the solve button
        self.disable_board()  # Call a method to disable the board
        
    def disable_board(self):
        for row in self.board_buttons:
            for button in row:
                button['state'] = tk.DISABLED  # Disable the button

def generate_solutions_for_m_queens(n, m):
    solutions = []

    # Adjusted is_safe to match the dynamic version's parameters but work with 0-index internally
    def is_safe(queen, queens):
        for q in queens:
            if q[0] == queen[0] or q[1] == queen[1] or abs(q[0] - queen[0]) == abs(q[1] - queen[1]):
                return False
        return True

    # For M = N, use the standard backtracking method
    def backtrack_standard(queens, row=0):
        if len(queens) == m:
            solutions.append(sorted([(r+1, c+1) for r, c in queens]))
            return
        for col in range(n):
            # Adjusted to pass parameters in a manner consistent with the dynamic approach
            if is_safe((row+1, col+1), [(q_row+1, q_col+1) for q_row, q_col in queens]):
                queens.append((row, col))
                backtrack_standard(queens, row + 1)
                queens.pop()

    # For M != N, explore more dynamically
    def backtrack_dynamic(queens=[], start=0):
        if len(queens) == m:
            solutions.append(sorted([(r+1, c+1) for r, c in queens]))
            return
        for i in range(start, n * n):
            row, col = divmod(i, n)
            if is_safe((row+1, col+1), [(q_row+1, q_col+1) for q_row, q_col in queens]):
                queens.append((row, col))
                backtrack_dynamic(queens, i + 1)
                queens.pop()

    # Decide which method to use based on M and N
    if m == n:
        backtrack_standard([])
    else:
        backtrack_dynamic([])

    return solutions

def heuristic_cost_estimate(current_state, goals_tuple, use_conflicts):
    
    # Calculate the number of pairs of queens attacking each other
    def conflicts(state):
        count = 0
        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                if (state[i][0] == state[j][0] or
                    state[i][1] == state[j][1] or
                    abs(state[i][0] - state[j][0]) == abs(state[i][1] - state[j][1])):  # same diagonal
                    count += 1
        return count

    # Calculate the distance to the closest goal state as a tie-breaker
    def distance_to_closest_goal(state, goals):
        return min(sum(abs(s[0] - g[0]) + abs(s[1] - g[1]) for s, g in zip(state, goal)) for goal in goals)

    # If use_conflicts is True, consider both conflicts and distance to closest solution
    if use_conflicts:
        return conflicts(current_state) + distance_to_closest_goal(current_state, goals_tuple)
    else:
        # If use_conflicts is False, only consider the distance to the closest solution
        return distance_to_closest_goal(current_state, goals_tuple)


def generate_successors(state, size):
    successors = []
    board = [[0 for _ in range(size)] for _ in range(size)]
    for x, y in state:
        board[y - 1][x - 1] = 1

    for queen in state:
        qx, qy = queen
        qx -= 1  # Adjust because the board is 0-indexed
        qy -= 1

        # Directions in which the queen can move: up, down, left, right, and diagonals
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for dx, dy in directions:
            # Check each step in a direction
            step_x, step_y = qx, qy
            while True:
                step_x += dx
                step_y += dy
                # Stop if the move is out of bounds
                if not (0 <= step_x < size and 0 <= step_y < size):
                    break
                # Stop and don't create a successor if there's another queen in the way
                if board[step_y][step_x] == 1:
                    break
                # Otherwise, it's a valid move
                new_state = list(state)
                new_state.remove(queen)  # Remove the old position of the queen
                new_state.append((step_x + 1, step_y + 1))  # Add the new position, adjusted to 1-indexed
                successors.append(tuple(sorted(new_state)))  # Ensure the state is sorted for consistency

    # Remove duplicates
    return list(set(successors))

def a_star_search(initial_state, goals, size):
    initial_state = tuple(sorted(initial_state))
    goals_tuple = tuple(map(tuple, goals))  # Make sure goals are a tuple of tuples

    # Run A* search to find the closest solution
    closest_solution_path, closest_cost = a_star_search_internal(initial_state, goals_tuple, size, use_conflicts=False)

    # Run A* search again to consider both conflicts and distance to closest solution
    combined_solution_path, combined_cost = a_star_search_internal(initial_state, goals_tuple, size, use_conflicts=True)

    # Choose the better solution based on total cost
    if closest_cost < combined_cost:
        return closest_solution_path, closest_cost
    else:
        return combined_solution_path, combined_cost

def a_star_search_internal(initial_state, goals_tuple, size, use_conflicts):
    open_set = PriorityQueue()
    open_set.put((0, initial_state))
    came_from = {initial_state: None}
    g_score = {initial_state: 0}
    f_score = {initial_state: heuristic_cost_estimate(initial_state, goals_tuple, use_conflicts)}

    while not open_set.empty():
        _, current = open_set.get()
       
        if heuristic_cost_estimate(current, goals_tuple, use_conflicts) == 0:
            return reconstruct_path(came_from, current), g_score[current]
        
        for next_state in generate_successors(current, size):
                       
            tentative_g_score = g_score[current] + 1

            if next_state not in g_score or tentative_g_score < g_score[next_state]:
                came_from[next_state] = current
                g_score[next_state] = tentative_g_score
                f_score[next_state] = tentative_g_score + heuristic_cost_estimate(next_state, goals_tuple, use_conflicts)

                if not any(item[1] == next_state for item in open_set.queue):
                    open_set.put((f_score[next_state], next_state))

    return [], float('inf')  # If no solution is found


def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from and came_from[current] is not None:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


# Function to print the board
def print_board(queens, size):
    board = [["." for _ in range(size)] for _ in range(size)]
    for col, row in queens:
        board[row-1][col-1] = "Q"
    for row in board:
        print(" ".join(row))
    print()
    

def print_all_single_queen_positions(size):
    all_positions = []
    for row in range(1, size + 1):
        for col in range(1, size + 1):
            all_positions.append((col, row))
    return all_positions

def integrated_n_queens_solution(initial_queens, size, all_solutions):
      
    print("Initial State:", initial_queens)
    print("Initial Board:")
    print_board(initial_queens, size)


    # Use A* search to find a solution
    solution_path, cost = a_star_search(initial_queens, all_solutions, size)

    if solution_path:
        if solution_path:
            final_state = solution_path[-1]
            print("Solution found!")
            print("Cost to solution:", cost)
            print("Solution Path:", solution_path)
            print("Solution Board:")
            print_board(final_state, size)
            print("Final State:", final_state)
        return final_state, cost, solution_path
    else:
        print("No solution found.")
        return None, "No solution found."

# #Example usage
# if __name__ == "__main__":

#     size = 8  # Define the size of the board
#     initial_queens = [(1, 1), (1, 2), (2, 3), (2, 4), (3, 5), (3, 6), (4, 7), (4, 8)]


#     integrated_n_queens_solution(initial_queens, size, len(initial_queens))

# To run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = NQueensApp(root)
    root.mainloop()