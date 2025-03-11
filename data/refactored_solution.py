import sys
from collections import defaultdict, deque

class ChessSolver:
    def __init__(self):
        self.MOD = 998244353
        self.MAX_N = 2 * 10**5 + 5
        # Pre-compute factorials and inverse factorials up to MAX_N for combinatorial calculations
        self.fact, self.invfact = self._precompute_factorials()
        
    def _precompute_factorials(self):
        """Pre-compute factorials and inverse factorials for efficient nCr calculations"""
        fact = [1] * self.MAX_N
        invfact = [1] * self.MAX_N
        
        # Calculate factorials
        for i in range(2, self.MAX_N):
            fact[i] = (fact[i - 1] * i) % self.MOD
            
        # Calculate inverse factorials using Fermat's little theorem
        invfact[self.MAX_N - 1] = pow(fact[self.MAX_N - 1], self.MOD - 2, self.MOD)
        for i in range(self.MAX_N - 2, -1, -1):
            invfact[i] = (invfact[i + 1] * (i + 1)) % self.MOD
            
        return fact, invfact
    
    def nCr(self, n, r):
        """Calculate nCr with modular arithmetic"""
        if r < 0 or r > n:
            return 0
        return (self.fact[n] * self.invfact[r] % self.MOD) * self.invfact[n - r] % self.MOD

    def solve_rook_placement(self, n, k):
        """
        Problem 1: Calculate the number of ways to place n rooks on an n×n chessboard
        so that every empty cell is under attack and exactly k pairs of rooks attack each other.
        """
        # When k = 0, it's a permutation placement (one rook per row/column)
        if k == 0:
            return self.fact[n] % self.MOD
        
        # If k > n-1, it's impossible (maximum attacking pairs is n-1)
        if k > n - 1:
            return 0
        
        m = n - k  # Number of rows with rooks when all columns have rooks
        F = 0
        
        # Compute F(n, m) = Σ_{j=0}^{m} [(-1)^(m-j) * C(m, j) * j^n]
        for j in range(m + 1):
            sign = self.MOD - 1 if (m - j) & 1 else 1
            comb = (self.fact[m] * self.invfact[j] % self.MOD) * self.invfact[m - j] % self.MOD
            term = (sign * comb) % self.MOD
            term = (term * pow(j, n, self.MOD)) % self.MOD
            F = (F + term) % self.MOD
            
        # Multiply by 2 * C(n, k) for the final answer
        return (2 * self.nCr(n, k) % self.MOD * F) % self.MOD

    def solve_gregor_pawns(self, n, enemy, gregor):
        """
        Problem 2: Find the maximum number of Gregor's pawns that can reach row 1.
        """
        # Convert strings to lists for easier processing
        enemy = list(enemy)
        gregor = list(gregor)
        
        # Track which enemy cells are used (captured or occupied)
        used = [False] * n
        count = 0
        
        # For each of Gregor's pawns, try to find a path to the first row
        # using greedy approach prioritizing diagonal captures
        for i in range(n):
            if gregor[i] == '1':
                # Try left diagonal capture
                if i > 0 and enemy[i - 1] == '1' and not used[i - 1]:
                    count += 1
                    used[i - 1] = True
                # Try vertical move
                elif enemy[i] == '0' and not used[i]:
                    count += 1
                    used[i] = True
                # Try right diagonal capture
                elif i < n - 1 and enemy[i + 1] == '1' and not used[i + 1]:
                    count += 1
                    used[i + 1] = True
                    
        return count

    def solve_king_path(self, start, end):
        """
        Problem 3: Find the shortest path for the king from start to end on a chessboard.
        """
        # Convert chess coordinates to numerical coordinates
        def to_coords(pos):
            col = ord(pos[0]) - ord('a') + 1
            row = int(pos[1])
            return col, row
        
        sc, sr = to_coords(start)
        ec, er = to_coords(end)
        
        # If already at destination, return 0 moves
        if (sc, sr) == (ec, er):
            return 0, []
        
        moves = []
        # Find minimum moves (max of horizontal and vertical distance)
        while (sc, sr) != (ec, er):
            step = ""
            # Handle horizontal movement
            if sc < ec:
                step += "R"
                sc += 1
            elif sc > ec:
                step += "L"
                sc -= 1
                
            # Handle vertical movement
            if sr < er:
                step += "U"
                sr += 1
            elif sr > er:
                step += "D"
                sr -= 1
                
            moves.append(step)
            
        return len(moves), moves

    def solve_rooks_to_diagonal(self, n, m, rook_positions):
        """
        Problem 4: Find minimum moves to place all rooks on the main diagonal.
        """
        # Create mapping from row to column for rooks not on main diagonal
        mapping = {}
        off_diag = 0
        
        for x, y in rook_positions:
            if x == y:  # Already on main diagonal
                continue
            mapping[x] = y
            off_diag += 1
        
        # Find cycles in the mapping
        visited = set()
        cycles = 0
        
        for start in mapping:
            if start in visited:
                continue
                
            current = start
            chain_set = set()
            
            while True:
                visited.add(current)
                chain_set.add(current)
                
                if current in mapping:
                    next_pos = mapping[current]
                    
                    # If next position is in current chain, we found a cycle
                    if next_pos in chain_set:
                        cycles += 1
                        break
                        
                    # If next position already visited, this joins a processed chain
                    if next_pos in visited:
                        break
                        
                    current = next_pos
                else:
                    break
        
        # Answer is (off-diagonal rooks) + (number of cycles)
        return off_diag + cycles

    def solve_pawn_states(self, board):
        """
        Problem 5: Count possible states after a sequence of pawn moves.
        """
        n = len(board)
        ones = board.count("1")
        
        # Count maximum number of disjoint adjacent "11" pairs (greedy scan)
        r = 0
        i = 0
        while i < n - 1:
            if board[i] == "1" and board[i + 1] == "1":
                r += 1
                i += 2
            else:
                i += 1
                
        # The answer equals C((n - ones) + r, r)
        return self.nCr((n - ones) + r, r)
        
    def detect_problem_and_solve(self, lines):
        """Detect which problem we're dealing with based on input pattern and solve it."""
        if not lines:
            return ""
        
        # Try to parse first line to check problem type
        first_line = lines[0].strip()
        
        # Problem 1: Two integers n and k on a single line
        if len(first_line.split()) == 2 and len(lines) == 1:
            n, k = map(int, first_line.split())
            return str(self.solve_rook_placement(n, k))
        
        # Problem 3: Two lines with chess coordinates
        if len(lines) == 2 and len(first_line) == 2 and 'a' <= first_line[0] <= 'h' and '1' <= first_line[1] <= '8':
            start = lines[0].strip()
            end = lines[1].strip()
            moves_count, move_list = self.solve_king_path(start, end)
            return str(moves_count) + "\n" + "\n".join(move_list) if moves_count else "0"
        
        # Problem 5: Multiple test cases with board states
        if first_line.isdigit() and int(first_line) > 0:
            t = int(first_line)
            results = []
            line_idx = 1
            
            for _ in range(t):
                if line_idx >= len(lines):
                    break
                    
                # Skip the length line (potentially unreliable)
                line_idx += 1
                if line_idx >= len(lines):
                    break
                    
                board = lines[line_idx].strip()
                line_idx += 1
                
                results.append(str(self.solve_pawn_states(board)))
                
            return "\n".join(results)
        
        # Problem 2: Multiple test cases with enemy and Gregor pawns
        if first_line.isdigit() and int(first_line) > 0 and len(lines) >= 2:
            t = int(first_line)
            results = []
            line_idx = 1
            
            for _ in range(t):
                if line_idx >= len(lines):
                    break
                    
                n = int(lines[line_idx].strip())
                line_idx += 1
                
                if line_idx + 1 >= len(lines):
                    break
                    
                enemy = lines[line_idx].strip()
                line_idx += 1
                gregor = lines[line_idx].strip()
                line_idx += 1
                
                # If strings are only 0s and 1s, it's likely problem 2
                if all(c in '01' for c in enemy) and all(c in '01' for c in gregor):
                    results.append(str(self.solve_gregor_pawns(n, enemy, gregor)))
                    
            # Only return if we actually processed some test cases
            if results:
                return "\n".join(results)
        
        # Problem 4: Multiple test cases with rook positions
        if first_line.isdigit() and int(first_line) > 0:
            t = int(first_line)
            results = []
            line_idx = 1
            
            for _ in range(t):
                if line_idx >= len(lines):
                    break
                    
                n, m = map(int, lines[line_idx].strip().split())
                line_idx += 1
                
                rook_positions = []
                for i in range(m):
                    if line_idx >= len(lines):
                        break
                        
                    x, y = map(int, lines[line_idx].strip().split())
                    rook_positions.append((x, y))
                    line_idx += 1
                    
                results.append(str(self.solve_rooks_to_diagonal(n, m, rook_positions)))
                
            return "\n".join(results)
        
        # If no problem detected
        return "Cannot determine problem type"

def main():
    # Read all input lines
    lines = []
    for line in sys.stdin:
        if line.strip():
            lines.append(line)
    
    solver = ChessSolver()
    result = solver.detect_problem_and_solve(lines)
    print(result)

if __name__ == "__main__":
    main()