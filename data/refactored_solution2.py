import sys
import math
import numpy as np
from dataclasses import dataclass

MOD = 998244353
# Precompute factorials up to MAX_N. For problem1 we need up to 200000 so we choose a little above.
MAX_N = 200010
_fact = [1] * (MAX_N)
_invfact = [1] * (MAX_N)
for i in range(2, MAX_N):
    _fact[i] = _fact[i-1] * i % MOD
_invfact[MAX_N-1] = pow(_fact[MAX_N-1], MOD-2, MOD)
for i in range(MAX_N-1, 0, -1):
    _invfact[i-1] = _invfact[i] * i % MOD

def nCr(n, r):
    """Compute n choose r modulo MOD."""
    if r < 0 or r > n:
        return 0
    return _fact[n] * _invfact[r] % MOD * _invfact[n-r] % MOD

###############################################################################
# Chessboard class with a 2D numpy array representation.
###############################################################################
@dataclass
class Chessboard:
    board: np.ndarray

    @classmethod
    def create(cls, nrows: int, ncols: int, fill=0):
        return cls(np.full((nrows, ncols), fill))
    
    def set_cell(self, row: int, col: int, value):
        self.board[row, col] = value

    def get_cell(self, row: int, col: int):
        return self.board[row, col]

###############################################################################
# Problem 1 Solver: Rooks on n x n board with attack pair conditions.
# Input: a single line containing two integers n and k.
###############################################################################
def solve_problem1(input_data: str) -> str:
    # Read the two numbers from input.
    data = input_data.split()
    if not data:
        return ""
    n = int(data[0])
    k = int(data[1])
    if k > n - 1:
        return "0"
    if k == 0:
        # When k == 0, the answer is exactly n!
        return str(_fact[n] % MOD)
    
    m = n - k  # m = number of nonempty rows in a valid configuration
    F = 0
    for j in range(m+1):
        sign = MOD - 1 if ((m - j) & 1) else 1
        comb = _fact[m] * _invfact[j] % MOD * _invfact[m - j] % MOD
        term = sign * comb % MOD
        term = term * pow(j, n, MOD) % MOD
        F = (F + term) % MOD
    # Final answer (with a factor of 2 * C(n,k))
    ans = 2 * nCr(n, k) % MOD * F % MOD
    return str(ans % MOD)

###############################################################################
# Problem 2 Solver: Gregor’s Pawn advancement on chessboard rows.
# Input: t test cases.
# Each test case: an integer n, then a string (enemy row) and a string (Gregor’s row).
###############################################################################
def solve_problem2(input_data: str) -> str:
    lines = input_data.splitlines()
    t = int(lines[0].strip())
    pos = 1
    results = []
    for _ in range(t):
        n = int(lines[pos].strip())
        pos += 1
        enemy = list(lines[pos].strip())
        pos += 1
        gregor = list(lines[pos].strip())
        pos += 1
        used = [False] * n
        count = 0
        for i in range(n):
            if gregor[i] == '1':
                # Try capturing from left neighbor.
                if i > 0 and enemy[i-1] == '1' and not used[i-1]:
                    count += 1
                    used[i-1] = True
                # Try moving straight upward.
                elif enemy[i] == '0' and not used[i]:
                    count += 1
                    used[i] = True
                # Try capturing from right neighbor.
                elif i < n-1 and enemy[i+1] == '1' and not used[i+1]:
                    count += 1
                    used[i+1] = True
        results.append(str(count))
    return "\n".join(results)

###############################################################################
# Problem 3 Solver: Minimum King moves on an 8x8 chessboard.
# Input: two lines, each with a chess coordinate (e.g. "a8" and "h1").
###############################################################################
def solve_problem3(input_data: str) -> str:
    lines = input_data.splitlines()
    if len(lines) < 2:
        return ""
    start = lines[0].strip()
    dest = lines[1].strip()
    
    # For demonstration we create an 8x8 chessboard (though not strictly needed).
    board = Chessboard.create(8, 8, fill='.')
    
    def to_coords(pos):
        col = ord(pos[0]) - ord('a') + 1
        row = int(pos[1])
        return col, row
    sc, sr = to_coords(start)
    ec, er = to_coords(dest)
    moves = []
    while (sc, sr) != (ec, er):
        step = ""
        if sc < ec:
            step += "R"
            sc += 1
        elif sc > ec:
            step += "L"
            sc -= 1
        if sr < er:
            step += "U"
            sr += 1
        elif sr > er:
            step += "D"
            sr -= 1
        moves.append(step)
    out_lines = [str(len(moves))]
    out_lines.extend(moves)
    return "\n".join(out_lines)

###############################################################################
# Problem 4 Solver: Minimal moves to place rooks on the main diagonal.
# Input: t test cases.
# Each test case: first a line with two integers n and m, then m lines with two integers each.
###############################################################################
def solve_problem4(input_data: str) -> str:
    data = input_data.split()
    pos = 0
    t = int(data[pos])
    pos += 1
    results = []
    for _ in range(t):
        n = int(data[pos]); m = int(data[pos+1])
        pos += 2
        mapping = {}
        off_diag = 0
        for i in range(m):
            x = int(data[pos]); y = int(data[pos+1])
            pos += 2
            if x == y:
                continue
            mapping[x] = y
            off_diag += 1
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
        results.append(str(off_diag + cycles))
    return "\n".join(results)

###############################################################################
# Problem 5 Solver: 1 × n Chessboard Pawn Moves.
# Input: t test cases.
# Each test case: an integer n followed by a binary string representing the board.
###############################################################################
def solve_problem5(input_data: str) -> str:
    lines = input_data.splitlines()
    t = int(lines[0].strip())
    pos = 1
    out_lines = []
    for _ in range(t):
        declared = lines[pos].strip()
        try:
            n_declared = int(declared)
        except:
            n_declared = 0
        pos += 1
        s = lines[pos].strip()
        pos += 1
        n = len(s)
        ones = s.count("1")
        r = 0
        i = 0
        while i < n - 1:
            if s[i] == "1" and s[i+1] == "1":
                r += 1
                i += 2
            else:
                i += 1
        ans = nCr((n - ones) + r, r)
        out_lines.append(str(ans))
    return "\n".join(out_lines)

###############################################################################
# Detection: Examine the input pattern to decide which problem it is.
###############################################################################
def detect_problem(input_data: str) -> int:
    """
    Return an integer in {1,2,3,4,5} indicating which problem to run.
     
    Detection strategy:
    - If the first two nonempty lines look like chessboard coordinates e.g. "a8", "h1" then it's Problem 3.
    - Else, if the whitespace‐split input has exactly 2 tokens (both numbers) then problem1.
    - Else, the first token is interpreted as t (number of test cases). Then by checking the second line:
         • if it splits into two tokens then it is Problem 4.
         • if one token then use the total number of remaining lines: 
            – if exactly 3*t lines follow it’s Problem 2,
            – if exactly 2*t lines follow it’s Problem 5.
    - Otherwise, default to Problem 1.
    """
    lines = input_data.strip().splitlines()
    if not lines:
        return 0
    def is_coord(s):
        return len(s)==2 and s[0] in "abcdefgh" and s[1] in "12345678"
    if len(lines) >= 2 and is_coord(lines[0].strip()) and is_coord(lines[1].strip()):
        return 3
    tokens = input_data.split()
    # Check if exactly two tokens (numbers) -- Problem 1.
    if len(tokens) == 2 and tokens[0].isdigit() and tokens[1].isdigit():
        return 1
    # Otherwise assume first token is t.
    try:
        t_val = int(tokens[0])
    except:
        t_val = -1
    if len(lines) >= 2:
        parts = lines[1].strip().split()
        if len(parts) == 2:
            return 4
        elif len(parts) == 1:
            remaining = len(lines) - 1
            if remaining == 3 * t_val:
                return 2
            elif remaining == 2 * t_val:
                return 5
    return 1

###############################################################################
# Main function that reads input and calls the correct solver.
###############################################################################
def main():
    input_data = sys.stdin.read()
    if not input_data:
        return
    prob_id = detect_problem(input_data)
    if prob_id == 1:
        output = solve_problem1(input_data)
    elif prob_id == 2:
        output = solve_problem2(input_data)
    elif prob_id == 3:
        output = solve_problem3(input_data)
    elif prob_id == 4:
        output = solve_problem4(input_data)
    elif prob_id == 5:
        output = solve_problem5(input_data)
    else:
        output = ""
    sys.stdout.write(output)

if __name__ == '__main__':
    main()