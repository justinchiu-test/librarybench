import sys
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict

# Constants
MOD = 998244353

# ------------------- Utility Functions -------------------
class MathUtils:
    @staticmethod
    def precompute_factorials(max_value, mod):
        """Precompute factorials and inverse factorials up to max_value."""
        fact = [1] * (max_value + 1)
        invfact = [1] * (max_value + 1)
        
        for i in range(2, max_value + 1):
            fact[i] = fact[i - 1] * i % mod
            
        invfact[max_value] = pow(fact[max_value], mod - 2, mod)
        for i in range(max_value, 0, -1):
            invfact[i - 1] = invfact[i] * i % mod
            
        return fact, invfact
    
    @staticmethod
    def nCr(n, r, fact, invfact, mod):
        """Calculate n choose r with modular arithmetic."""
        if r < 0 or r > n:
            return 0
        return (fact[n] * invfact[r] % mod) * invfact[n - r] % mod

# ------------------- Chess-Related Classes -------------------
@dataclass
class Position:
    """Represents a position on a chessboard."""
    x: int  # column (1-indexed)
    y: int  # row (1-indexed)
    
    @classmethod
    def from_chess_notation(cls, notation):
        """Convert chess notation (e.g., 'a1') to Position."""
        col = ord(notation[0]) - ord('a') + 1
        row = int(notation[1])
        return cls(col, row)
    
    def to_chess_notation(self):
        """Convert Position to chess notation."""
        col = chr(self.x + ord('a') - 1)
        return f"{col}{self.y}"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))

class Chessboard:
    """Represents a chessboard of variable size."""
    def __init__(self, size, initial_state=None):
        self.size = size
        if initial_state is not None:
            self.board = initial_state
        else:
            self.board = np.zeros((size, size), dtype=int)
    
    @classmethod
    def from_binary_strings(cls, rows, cols):
        """Create a chessboard from binary strings for rows and columns."""
        size = len(rows)
        board = np.zeros((size, size), dtype=int)
        
        for i, row_str in enumerate(rows):
            for j, val in enumerate(row_str):
                if val == '1':
                    board[i][j] = 1
                    
        return cls(size, board)
    
    def is_valid_position(self, pos):
        """Check if a position is within the board boundaries."""
        return 1 <= pos.x <= self.size and 1 <= pos.y <= self.size
    
    def get_piece_at(self, pos):
        """Get the piece at a given position."""
        if self.is_valid_position(pos):
            return self.board[pos.y-1][pos.x-1]
        return None
    
    def set_piece_at(self, pos, value):
        """Set the piece at a given position."""
        if self.is_valid_position(pos):
            self.board[pos.y-1][pos.x-1] = value

# ------------------- Problem Solvers -------------------
class RookPlacementSolver:
    """Solver for Problem 1: Placing rooks on a chessboard."""
    def __init__(self, n, k):
        self.n = n
        self.k = k
        self.mod = MOD
        max_val = n
        self.fact, self.invfact = MathUtils.precompute_factorials(max_val, self.mod)
    
    def nCr(self, a, b):
        return MathUtils.nCr(a, b, self.fact, self.invfact, self.mod)
    
    def solve(self):
        if self.k > self.n - 1:
            return "0"
        
        if self.k == 0:
            return str(self.fact[self.n] % self.mod)
        
        m = self.n - self.k  # number of nonempty rows
        F = 0
        
        for j in range(m + 1):
            sign = self.mod - 1 if (m - j) & 1 else 1
            comb = (self.fact[m] * self.invfact[j] % self.mod) * self.invfact[m - j] % self.mod
            term = sign * comb % self.mod
            term = term * pow(j, self.n, self.mod) % self.mod
            F = (F + term) % self.mod
            
        ans = 2 * self.nCr(self.n, self.k) % self.mod * F % self.mod
        return str(ans % self.mod)

class PawnMovementSolver:
    """Solver for Problem 2: Moving pawns to reach the top row."""
    def __init__(self, n, enemy_row, gregor_row):
        self.n = n
        self.enemy_row = enemy_row
        self.gregor_row = gregor_row
    
    def solve(self):
        used = [False] * self.n
        count = 0
        
        for i in range(self.n):
            if self.gregor_row[i] == '1':
                # Try left capture
                if i > 0 and self.enemy_row[i-1] == '1' and not used[i-1]:
                    count += 1
                    used[i-1] = True
                # Try vertical move
                elif self.enemy_row[i] == '0' and not used[i]:
                    count += 1
                    used[i] = True
                # Try right capture
                elif i < self.n - 1 and self.enemy_row[i+1] == '1' and not used[i+1]:
                    count += 1
                    used[i+1] = True
                    
        return str(count)

class KingMovementSolver:
    """Solver for Problem 3: Finding shortest path for king movement."""
    def __init__(self, start_pos, target_pos):
        self.start = start_pos
        self.target = target_pos
        
    def solve(self):
        if self.start == self.target:
            return "0"
        
        moves = []
        cur_x, cur_y = self.start.x, self.start.y
        target_x, target_y = self.target.x, self.target.y
        
        # Calculate moves until we reach the target
        while (cur_x, cur_y) != (target_x, target_y):
            step = ""
            
            # Process horizontal move
            if cur_x < target_x:
                step += "R"
                cur_x += 1
            elif cur_x > target_x:
                step += "L"
                cur_x -= 1
                
            # Process vertical move
            if cur_y < target_y:
                step += "U"
                cur_y += 1
            elif cur_y > target_y:
                step += "D"
                cur_y -= 1
                
            moves.append(step)
            
        return str(len(moves)) + "\n" + "\n".join(moves)

class RookToMainDiagonalSolver:
    """Solver for Problem 4: Moving rooks to the main diagonal."""
    def __init__(self, n, rook_positions):
        self.n = n
        self.rook_positions = rook_positions
        
    def solve(self):
        # Map from row to column for rooks not on main diagonal
        mapping = {}
        off_diag = 0
        
        for pos in self.rook_positions:
            if pos.x == pos.y:  # already on main diagonal
                continue
            mapping[pos.x] = pos.y
            off_diag += 1
            
        # Find cycles in the mapping
        visited = set()
        cycles = 0
        
        for start in mapping:
            if start in visited:
                continue
            
            cur = start
            chain_set = set()
            
            while True:
                visited.add(cur)
                chain_set.add(cur)
                
                if cur in mapping:
                    nxt = mapping[cur]
                    if nxt in chain_set:
                        cycles += 1
                        break
                    if nxt in visited:
                        break
                    cur = nxt
                else:
                    break
                    
        return str(off_diag + cycles)

class PawnStatesCountSolver:
    """Solver for Problem 5: Counting reachable states from initial pawn positions."""
    def __init__(self, n, initial_state):
        self.n = n
        self.initial_state = initial_state
        self.mod = MOD
        max_n = 10**5 + 5
        self.fact, self.invfact = MathUtils.precompute_factorials(max_n, self.mod)
        
    def nCr(self, n, r):
        return MathUtils.nCr(n, r, self.fact, self.invfact, self.mod)
    
    def solve(self):
        ones = self.initial_state.count("1")
        
        # Count maximum number of disjoint adjacent "11" pairs
        r = 0
        i = 0
        while i < self.n - 1:
            if self.initial_state[i] == "1" and self.initial_state[i+1] == "1":
                r += 1
                i += 2
            else:
                i += 1
                
        # Calculate answer using combination formula
        ans = self.nCr((self.n - ones) + r, r)
        return str(ans)

# ------------------- Main Function -------------------
def main():
    lines = sys.stdin.read().strip().split('\n')
    line_index = 0
    
    # Try to determine which problem we're solving based on the input pattern
    if len(lines) == 1 and ' ' in lines[0]:
        # Problem 1: Rook placement
        n, k = map(int, lines[0].split())
        solver = RookPlacementSolver(n, k)
        print(solver.solve())
        
    elif len(lines) >= 3 and lines[0].isdigit() and len(lines[1]) == len(lines[2]):
        # Problem 2: Pawn movement to top row
        t = int(lines[0])
        results = []
        line_index = 1
        
        for _ in range(t):
            n = int(lines[line_index])
            line_index += 1
            enemy_row = lines[line_index]
            line_index += 1
            gregor_row = lines[line_index]
            line_index += 1
            
            solver = PawnMovementSolver(n, enemy_row, gregor_row)
            results.append(solver.solve())
            
        print('\n'.join(results))
        
    elif len(lines) == 2 and len(lines[0]) == 2 and len(lines[1]) == 2:
        # Problem 3: King movement
        start_pos = Position.from_chess_notation(lines[0])
        target_pos = Position.from_chess_notation(lines[1])
        
        solver = KingMovementSolver(start_pos, target_pos)
        print(solver.solve())
        
    elif lines[0].isdigit() and int(lines[0]) >= 1:
        # Check if it's Problem 4 or 5 based on further patterns
        t = int(lines[0])
        if ' ' in lines[1] and int(lines[1].split()[1]) < int(lines[1].split()[0]):
            # Problem 4: Rooks to main diagonal
            results = []
            line_index = 1
            
            for _ in range(t):
                n, m = map(int, lines[line_index].split())
                line_index += 1
                
                rook_positions = []
                for i in range(m):
                    x, y = map(int, lines[line_index].split())
                    rook_positions.append(Position(x, y))
                    line_index += 1
                    
                solver = RookToMainDiagonalSolver(n, rook_positions)
                results.append(solver.solve())
                
            print('\n'.join(results))
            
        else:
            # Problem 5: Pawn states count
            results = []
            line_index = 1
            
            for _ in range(t):
                n = int(lines[line_index])
                line_index += 1
                initial_state = lines[line_index]
                line_index += 1
                
                solver = PawnStatesCountSolver(n, initial_state)
                results.append(solver.solve())
                
            print('\n'.join(results))

if __name__ == '__main__':
    main()