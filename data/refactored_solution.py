import sys

class ChessSolver:
    MOD = 998244353
    
    def __init__(self):
        # Precompute factorials and inverse factorials for large values
        self.max_val = 10**5 + 5
        self.fact = [1] * self.max_val
        self.invfact = [1] * self.max_val
        
        for i in range(2, self.max_val):
            self.fact[i] = (self.fact[i - 1] * i) % self.MOD
            
        self.invfact[-1] = pow(self.fact[-1], self.MOD - 2, self.MOD)
        for i in range(self.max_val - 2, -1, -1):
            self.invfact[i] = (self.invfact[i + 1] * (i + 1)) % self.MOD
    
    def nCr(self, n, r):
        """Calculate n choose r with modular arithmetic"""
        if r < 0 or r > n:
            return 0
        return (self.fact[n] * self.invfact[r] % self.MOD) * self.invfact[n - r] % self.MOD
    
    def detect_problem(self, data):
        """Detect which problem we're solving based on input pattern"""
        if not data:
            return None
        
        first_line = data[0].strip() if isinstance(data[0], str) else data[0]
        
        # Problem 3: Chess coordinates (e.g., "a8")
        if len(first_line) == 2 and 'a' <= first_line[0] <= 'h' and '1' <= first_line[1] <= '8':
            return 3
        
        try:
            # Check if first line is a single number
            val = int(first_line)
            
            # Problem 1: Just two integers
            if len(data) == 2 and all(len(line.split()) == 1 for line in data):
                return 1
            
            # For problems with test cases, look at second line
            if len(data) > 1:
                second_line = data[1].strip() if isinstance(data[1], str) else data[1]
                
                # Problem 2: t test cases with 3 lines each
                if len(data) >= 3 and len(data[2].strip()) == int(second_line):
                    return 2
                
                # Problem 4: t test cases with m positions
                if len(second_line.split()) == 2:
                    return 4
                
                # Problem 5: t test cases with binary strings
                if all(c in '01' for c in data[2].strip()):
                    return 5
        except:
            pass
        
        return None
    
    def solve_problem1(self, data):
        """Rooks on chessboard"""
        n = int(data[0])
        k = int(data[1])
        
        # No valid configuration with more attacking pairs than n-1
        if k > n - 1:
            return "0"
        
        # For k = 0, the answer is n!
        if k == 0:
            return str(self.fact[n] % self.MOD)
        
        m = n - k  # the number of nonempty rows
        F = 0
        
        # Compute F(n, m) = Σ_{j=0}^{m} [(-1)^(m-j) * C(m, j) * j^n]
        for j in range(m + 1):
            sign = self.MOD - 1 if (m - j) & 1 else 1
            comb = (self.fact[m] * self.invfact[j] % self.MOD) * self.invfact[m - j] % self.MOD
            term = sign * comb % self.MOD
            term = term * pow(j, n, self.MOD) % self.MOD
            F = (F + term) % self.MOD
            
        ans = 2 * self.nCr(n, k) % self.MOD * F % self.MOD
        return str(ans)
    
    def solve_problem2(self, data):
        """Gregor's pawns"""
        t = int(data[0])
        results = []
        
        line_index = 1
        for _ in range(t):
            n = int(data[line_index])
            line_index += 1
            enemy = list(data[line_index])
            line_index += 1
            gregor = list(data[line_index])
            line_index += 1
            
            # Mark used enemy cells
            used = [False] * n
            count = 0
            
            # Try to advance each of Gregor's pawns
            for i in range(n):
                if gregor[i] == '1':
                    # Option 1: Try left diagonal capture
                    if i > 0 and enemy[i - 1] == '1' and not used[i - 1]:
                        count += 1
                        used[i - 1] = True
                    # Option 2: Try vertical move
                    elif enemy[i] == '0' and not used[i]:
                        count += 1
                        used[i] = True
                    # Option 3: Try right diagonal capture
                    elif i < n - 1 and enemy[i + 1] == '1' and not used[i + 1]:
                        count += 1
                        used[i + 1] = True
            
            results.append(str(count))
        
        return "\n".join(results)
    
    def solve_problem3(self, data):
        """King's minimum moves"""
        start = data[0].strip()
        dest = data[1].strip()
        
        # Convert chess coordinate to numerical coordinates
        def to_coords(pos):
            col = ord(pos[0]) - ord('a') + 1
            row = int(pos[1])
            return col, row
        
        sc, sr = to_coords(start)
        ec, er = to_coords(dest)
        
        moves = []
        
        # Find minimum moves from start to end
        while (sc, sr) != (ec, er):
            step = ""
            # Process horizontal move
            if sc < ec:
                step += "R"
                sc += 1
            elif sc > ec:
                step += "L"
                sc -= 1
            
            # Process vertical move
            if sr < er:
                step += "U"
                sr += 1
            elif sr > er:
                step += "D"
                sr -= 1
            
            moves.append(step)
        
        return str(len(moves)) + "\n" + "\n".join(moves)
    
    def solve_problem4(self, data):
        """Rooks on main diagonal"""
        t = int(data[0])
        results = []
        
        line_index = 1
        for _ in range(t):
            parts = data[line_index].split()
            n = int(parts[0])
            m = int(parts[1])
            line_index += 1
            
            # Track mappings of rows to columns for rooks not on main diagonal
            mapping = {}
            off_diag = 0
            
            for i in range(m):
                parts = data[line_index].split()
                x = int(parts[0])
                y = int(parts[1])
                line_index += 1
                
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
            
            # Answer is off-diagonal rooks + cycles
            results.append(str(off_diag + cycles))
        
        return "\n".join(results)
    
    def solve_problem5(self, data):
        """AquaMoon's chessboard"""
        t = int(data[0])
        results = []
        
        line_index = 1
        for _ in range(t):
            n = int(data[line_index])
            line_index += 1
            s = data[line_index].strip()
            line_index += 1
            
            n = len(s)  # Use actual length of string
            ones = s.count("1")
            
            # Count max disjoint adjacent "11" pairs with greedy scan
            r = 0
            i = 0
            while i < n - 1:
                if s[i] == "1" and s[i + 1] == "1":
                    r += 1
                    i += 2
                else:
                    i += 1
            
            # Answer is combinations formula
            ans = self.nCr((n - ones) + r, r)
            results.append(str(ans))
        
        return "\n".join(results)
    
    def solve(self, input_data=None):
        """Main solving function that detects and routes to the appropriate solver"""
        if input_data is None:
            input_data = sys.stdin.read()
            
        # Normalize input data format
        if isinstance(input_data, str):
            data = input_data.strip().splitlines()
        else:
            data = input_data
            
        problem_type = self.detect_problem(data)
        
        if problem_type == 1:
            return self.solve_problem1(data)
        elif problem_type == 2:
            return self.solve_problem2(data)
        elif problem_type == 3:
            return self.solve_problem3(data)
        elif problem_type == 4:
            return self.solve_problem4(data)
        elif problem_type == 5:
            return self.solve_problem5(data)
        else:
            return "Couldn't determine problem type"

def main():
    solver = ChessSolver()
    result = solver.solve()
    print(result)

if __name__ == '__main__':
    main()