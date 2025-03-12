#!/usr/bin/env python3
"""
Unified solution for multiple Codeforces problems.
Each problem is solved by a dedicated solver function that uses shared helper classes and functions.
We also provide a Chessboard class (backed by a 2D numpy array) as a common representation.
The main() function automatically detects which problem is being presented based on the input format.
"""

import sys
import numpy as np
from dataclasses import dataclass

# ----------------------- Shared Library Code -----------------------

class Chessboard:
    """
    A simple Chessboard class using a 2D numpy array.
    Although not used by every problem, it is provided as a shared representation.
    """
    def __init__(self, rows: int = 8, cols: int = 8, board=None):
        if board is not None:
            self.board = board
            self.rows, self.cols = board.shape
        else:
            self.rows = rows
            self.cols = cols
            self.board = np.zeros((rows, cols), dtype=int)

    def place_piece(self, row: int, col: int, piece: int = 1):
        self.board[row][col] = piece

    def __str__(self):
        return str(self.board)

class Combinatorics:
    """
    Utility class for computing factorials and combination nCr modulo mod.
    Precomputes factorials and inverse factorials up to max_n.
    """
    def __init__(self, max_n: int, mod: int):
        self.mod = mod
        self.fact = [1] * (max_n + 1)
        self.invfact = [1] * (max_n + 1)
        for i in range(2, max_n + 1):
            self.fact[i] = self.fact[i - 1] * i % mod
        self.invfact[max_n] = pow(self.fact[max_n], mod - 2, mod)
        for i in range(max_n, 0, -1):
            self.invfact[i - 1] = self.invfact[i] * i % mod

    def nCr(self, n: int, r: int) -> int:
        if r < 0 or r > n:
            return 0
        return self.fact[n] * self.invfact[r] % self.mod * self.invfact[n - r] % self.mod

# ----------------------- Problem Solvers -----------------------

def solve_problem1(tokens, lines):
    """
    Problem 1: Count the number of ways to place n rooks on an n×n chessboard so that:
      - every empty cell is under attack, and
      - exactly k pairs of rooks attack each other.
    Input format: a single line containing two integers: n k
    """
    mod = 998244353
    n = int(tokens[0])
    k = int(tokens[1])
    if k > n - 1:
        print(0)
        return
    comb_obj = Combinatorics(n, mod)
    if k == 0:
        print(comb_obj.fact[n] % mod)
        return
    m = n - k  # number of nonempty rows when every column is used
    F = 0
    # Compute F(n, m) = Σ_{j=0}^{m} [(-1)^(m-j) * C(m, j) * j^n]
    for j in range(m + 1):
        sign = mod - 1 if ((m - j) & 1) else 1
        # Compute combination: C(m, j)
        comb_m_j = (comb_obj.fact[m] * comb_obj.invfact[j] % mod) * comb_obj.invfact[m - j] % mod
        term = sign * comb_m_j % mod * pow(j, n, mod) % mod
        F = (F + term) % mod
    C_n_k = comb_obj.fact[n] * comb_obj.invfact[k] % mod * comb_obj.invfact[n - k] % mod
    ans = 2 * C_n_k % mod * F % mod
    print(ans % mod)

def solve_problem2(tokens, lines):
    """
    Problem 2: Given a chessboard with enemy pawns on row 1 and Gregor's pawns on row n,
    count the maximum number of Gregor’s pawns that can reach row 1 following the moving rules.
    Input format:
       The first line contains integer t (number of test cases),
       For each test case:
         First line: integer n
         Second line: enemy string (binary, length n)
         Third line: gregor string (binary, length n)
    """
    mod = 998244353  # not used but standard mod is defined in problems
    t = int(tokens[0])
    pos = 1
    results = []
    for _ in range(t):
        n = int(tokens[pos])
        pos += 1
        enemy = list(tokens[pos].strip())
        pos += 1
        gregor = list(tokens[pos].strip())
        pos += 1
        used = [False] * n
        count = 0
        for i in range(n):
            if gregor[i] == '1':
                # Option 1: Capture from left neighbor if available.
                if i > 0 and enemy[i - 1] == '1' and not used[i - 1]:
                    count += 1
                    used[i - 1] = True
                # Option 2: Move straight if cell is empty.
                elif enemy[i] == '0' and not used[i]:
                    count += 1
                    used[i] = True
                # Option 3: Capture from right neighbor if available.
                elif i < n - 1 and enemy[i + 1] == '1' and not used[i + 1]:
                    count += 1
                    used[i + 1] = True
        results.append(str(count))
    print("\n".join(results))

def solve_problem3(tokens, lines):
    """
    Problem 3: Find the shortest sequence of king moves from square s to square t.
    Input format: Two lines containing chess coordinates (e.g., "a8", "h1").
    Allowed moves: L, R, U, D, LU, LD, RU, RD.
    """
    if len(lines) < 2:
        return
    start = lines[0].strip()
    dest = lines[1].strip()

    def to_coords(pos: str):
        col = ord(pos[0]) - ord('a') + 1
        row = int(pos[1])
        return col, row

    sc, sr = to_coords(start)
    ec, er = to_coords(dest)
    moves = []
    # The optimal number of moves is max(|dx|, |dy|)
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
    print("\n".join(out_lines))

def solve_problem4(tokens, lines):
    """
    Problem 4: Given m non-attacking rooks on an n×n board, determine the minimum number
    of moves required to reposition all rooks onto the main diagonal.
    Input format:
       The first line contains integer t (number of test cases).
       For each test case:
         First line: two integers n and m.
         Next m lines: two integers each representing the rook's position (x, y).
    """
    t = int(tokens[0])
    pos = 1
    results = []
    for _ in range(t):
        n = int(tokens[pos])
        m = int(tokens[pos + 1])
        pos += 2
        mapping = {}
        off_diag = 0
        for i in range(m):
            x = int(tokens[pos])
            y = int(tokens[pos + 1])
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
    print("\n".join(results))

def solve_problem5(tokens, lines):
    """
    Problem 5: Given a 1×n chessboard with pawns in some cells, count the number of reachable states
    using operations that move a pawn two cells (jumping over an adjacent pawn).
    Input format:
       The first line contains integer t (number of test cases).
       For each test case:
         First line: integer n (declared length, may be unreliable)
         Second line: binary string of length n.
       The answer for each test case is C((n - ones) + r, r) mod 998244353,
       where ones = count of '1's and r = maximum number of disjoint adjacent "11" pairs.
    """
    mod = 998244353
    t = int(tokens[0])
    pos = 1
    results = []
    maxN = 10**5 + 5
    comb_obj = Combinatorics(maxN, mod)
    for _ in range(t):
        # Read declared n (not used because actual string length is used)
        _ = int(tokens[pos])
        pos += 1
        s = tokens[pos].strip()
        pos += 1
        n = len(s)
        ones = s.count("1")
        r = 0
        i = 0
        while i < n - 1:
            if s[i] == "1" and s[i + 1] == "1":
                r += 1
                i += 2
            else:
                i += 1
        ans = comb_obj.nCr((n - ones) + r, r)
        results.append(str(ans))
    print("\n".join(results))

# ----------------------- Problem Detection -----------------------

def detect_problem_and_solve():
    """
    Detects which problem is being solved based on the input pattern and delegates to the proper solver.
    The detection uses token count and simple heuristics:
      - Problem 1: Two tokens on input, both integers (n, k).
      - Problem 3: Two lines of input with non-numeric first token (e.g. "a8" and "h1").
      - Problems 2, 4, 5: First token is integer t, then structure differs.
          * Problem 5: Total tokens = 2*t + 1.
          * Problem 2: Total tokens = 3*t + 1 (each test case: n, enemy string, gregor string) 
                     or if the enemy string length equals the integer n.
          * Otherwise, it's Problem 4.
    """
    data = sys.stdin.read()
    if not data:
        return
    lines = data.splitlines()
    tokens = data.split()
    
    # If there are only 2 tokens, check if both are numeric.
    if len(tokens) == 2:
        try:
            _ = int(tokens[0])
            _ = int(tokens[1])
            # Likely Problem 1.
            solve_problem1(tokens, lines)
            return
        except Exception:
            solve_problem3(tokens, lines)
            return

    # If the first token cannot be converted to int, it's Problem 3.
    try:
        _ = int(tokens[0])
        first_token_is_int = True
    except Exception:
        first_token_is_int = False
    if not first_token_is_int:
        solve_problem3(tokens, lines)
        return

    # Now first token is an integer.
    t_val = int(tokens[0])
    # Check for Problem 5: expected total tokens = 2*t + 1.
    if len(tokens) == 2 * t_val + 1:
        solve_problem5(tokens, lines)
        return

    # Next, check for Problem 2: if each test case has 3 tokens (n, enemy string, gregor string).
    if len(tokens) == 3 * t_val + 1:
        solve_problem2(tokens, lines)
        return

    # A heuristic: In Problem 2, for the first test case, tokens[1] is n and tokens[2] should be an enemy string of length n.
    try:
        n_candidate = int(tokens[1])
        if len(tokens[2].strip()) == n_candidate:
            # This suggests Problem 2.
            solve_problem2(tokens, lines)
            return
    except Exception:
        pass

    # If not Problem 2 or Problem 5, then assume Problem 4.
    solve_problem4(tokens, lines)

# ----------------------- Main -----------------------

def main():
    detect_problem_and_solve()

if __name__ == '__main__':
    main()