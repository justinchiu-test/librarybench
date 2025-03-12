#!/usr/bin/env python3
import sys
import math
import numpy as np
from dataclasses import dataclass

# Global constant
mod = 998244353

##################################################
# COMMON LIBRARY CODE
##################################################

@dataclass
class Chessboard:
    # Simple chessboard using a 2D numpy array.
    board: np.ndarray

    @classmethod
    def create(cls, rows: int, cols: int, fill=0):
        arr = np.full((rows, cols), fill)
        return cls(arr)

    def set_piece(self, r: int, c: int, value):
        self.board[r, c] = value

    def get_piece(self, r: int, c: int):
        return self.board[r, c]

    def __str__(self):
        return str(self.board)

def prepare_factorials(max_n):
    # Precompute factorials and their modular inverses for 0...max_n.
    fact = [1] * (max_n+1)
    invfact = [1] * (max_n+1)
    for i in range(2, max_n+1):
        fact[i] = fact[i-1] * i % mod
    invfact[max_n] = pow(fact[max_n], mod-2, mod)
    for i in range(max_n, 0, -1):
        invfact[i-1] = invfact[i] * i % mod
    return fact, invfact

def nCr(n, r, fact, invfact):
    if r < 0 or r > n:
        return 0
    return fact[n] * invfact[r] % mod * invfact[n - r] % mod

##################################################
# PROBLEM 1: Rook Placement with Attacks (n, k)
##################################################
def solve_problem1(tokens):
    # Expected tokens: [n, k]
    n = int(tokens[0])
    k = int(tokens[1])
    if k > n - 1:
        return "0"
    fact, invfact = prepare_factorials(n)
    # Helper for combination
    def nC(a, b):
        if b < 0 or b > a:
            return 0
        return fact[a] * invfact[b] % mod * invfact[a - b] % mod

    if k == 0:
        return str(fact[n] % mod)
    m = n - k  # Nonempty rows count.
    F = 0
    # Sum_{j=0}^{m} (-1)^(m-j)·C(m, j)·j^n modulo mod.
    for j in range(m+1):
        sign = mod - 1 if ((m - j) & 1) else 1
        comb = (fact[m] * invfact[j] % mod) * invfact[m - j] % mod
        term = sign * comb % mod
        term = term * pow(j, n, mod) % mod
        F = (F + term) % mod
    ans = 2 * nC(n, k) % mod * F % mod
    return str(ans % mod)

##################################################
# PROBLEM 2: Gregor's Pawns reaching enemy row.
##################################################
def solve_problem2(tokens):
    # Expected tokens: first token is t, then for each test:
    # n, enemy-string, gregor-string.
    t = int(tokens[0])
    pos = 1
    results = []
    for _ in range(t):
        n = int(tokens[pos])
        pos += 1
        enemy = list(tokens[pos])
        pos += 1
        gregor = list(tokens[pos])
        pos += 1
        used = [False] * n
        count = 0
        for i in range(n):
            if gregor[i] == '1':
                if i > 0 and enemy[i-1]=='1' and not used[i-1]:
                    count += 1
                    used[i-1] = True
                elif enemy[i]=='0' and not used[i]:
                    count += 1
                    used[i] = True
                elif i < n-1 and enemy[i+1]=='1' and not used[i+1]:
                    count += 1
                    used[i+1] = True
        results.append(str(count))
    return "\n".join(results)

##################################################
# PROBLEM 3: King's Minimum Moves from s to t.
##################################################
def solve_problem3(tokens):
    # Expected tokens: [start, dest], e.g., "a8" and "h1".
    def to_coords(pos):
        # Convert coordinate string to 1-indexed numeric (col, row)
        col = ord(pos[0]) - ord('a') + 1
        row = int(pos[1])
        return col, row
    start = tokens[0].strip()
    dest = tokens[1].strip()
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

##################################################
# PROBLEM 4: Moving Rooks to Main Diagonal.
##################################################
def solve_problem4(tokens):
    # Expected tokens: first token is t, then for each test:
    # first line contains n and m, then m lines with x and y.
    t = int(tokens[0])
    pos = 1
    results = []
    for _ in range(t):
        n = int(tokens[pos]); m = int(tokens[pos+1])
        pos += 2
        mapping = {}
        off_diag = 0
        for i in range(m):
            x = int(tokens[pos]); y = int(tokens[pos+1])
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

##################################################
# PROBLEM 5: 1xn Board Reachable States Count.
##################################################
def solve_problem5(tokens):
    # Expected tokens: first token is t, then for each test:
    # an integer n then a binary string of length n.
    t = int(tokens[0])
    pos = 1
    results = []
    test_cases = []
    max_val = 0
    for _ in range(t):
        declared_n = int(tokens[pos])
        pos += 1
        s = tokens[pos].strip()
        pos += 1
        n = len(s)
        test_cases.append((n, s))
        if n > max_val:
            max_val = n
    # In combination, the maximum argument is (n - ones) + r.
    max_n_arg = max_val + (max_val // 2) + 5
    fact, invfact = prepare_factorials(max_n_arg)
    for (n, s) in test_cases:
        ones = s.count("1")
        r = 0
        i = 0
        while i < n-1:
            if s[i]=='1' and s[i+1]=='1':
                r += 1
                i += 2
            else:
                i += 1
        ans = nCr((n - ones) + r, r, fact, invfact)
        results.append(str(ans))
    return "\n".join(results)

##################################################
# MAIN: Detect which problem and call solver
##################################################
def main():
    data = sys.stdin.read().split()
    if not data:
        return

    # Case 1: If first token is not a pure digit then it is (most likely) Problem 3.
    if not data[0].isdigit():
        # For example, input: "a8" "h1"
        res = solve_problem3(data)
        sys.stdout.write(res)
        return

    # Otherwise, first token is digit. Try to decide based on total token count.
    total_tokens = len(data)
    # If exactly 2 tokens, then Problem 1 (n and k).
    if total_tokens == 2:
        res = solve_problem1(data)
        sys.stdout.write(res)
        return

    # Let t be the first token (number of test cases).
    t = int(data[0])
    # If the test format uses exactly 1+2*t tokens then it is Problem 5,
    # i.e. each test case takes 2 tokens (n and a state string).
    if total_tokens == 1 + 2 * t:
        res = solve_problem5(data)
        sys.stdout.write(res)
        return
    # If the test format uses exactly 1+3*t tokens then it is Problem 2,
    # i.e. each test uses 3 tokens (n, enemy string, gregor string).
    if total_tokens == 1 + 3 * t:
        res = solve_problem2(data)
        sys.stdout.write(res)
        return
    # Otherwise, assume Problem 4.
    res = solve_problem4(data)
    sys.stdout.write(res)

if __name__ == '__main__':
    main()