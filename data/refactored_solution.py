#!/usr/bin/env python3
"""
Unified solution for five distinct Codeforces problems.
We “detect” which problem based on the input pattern:
  
  • Problem 1 (“rooks”):
      Input: exactly two tokens – two integers: n and k.
      
  • Problem 2 (“Gregor’s Pawns”):
      Input: first token is an integer t, and for each test case there are three tokens:
             an integer n, a binary string (enemy row), and another binary string (Gregor’s pawns). 
             (Total tokens = 1 + 3*t.)
      
  • Problem 3 (“King’s Shortest Path”):
      Input: the first token is non‐numeric. (Coordinates like "a8", etc.)
      
  • Problem 4 (“Rooks on the Diagonal”):
      Input: first token is integer t; then for each test case:
             a header line with two integers (n, m) and then m lines with two integers each.
             (Token count does not match Problems 2 or 5.)
      
  • Problem 5 (“1xn Pawn Moves Counting”):
      Input: first token is an integer t; then for each test case:
             a line containing an integer (declared n) and then a line containing a binary string.
             (Total tokens = 1 + 2*t.)
             
The main() function below reads the full input, performs a few tests,
and then calls the corresponding solver.
"""

########################################
# Problem 1 Solver
########################################
def solve_problem1():
    # Problem 1:
    # "Calculate the number of ways to place n rooks on an n×n chessboard so that
    # every empty cell is attacked and exactly k pairs of rooks attack each other."
    import sys
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    k = int(data[1])
    mod = 998244353
    if k > n - 1:
        sys.stdout.write("0")
        return
    # Precompute factorials up to n.
    max_val = n
    fact = [1]*(max_val+1)
    invfact = [1]*(max_val+1)
    for i in range(2, max_val+1):
        fact[i] = fact[i-1] * i % mod
    invfact[max_val] = pow(fact[max_val], mod-2, mod)
    for i in range(max_val, 0, -1):
        invfact[i-1] = invfact[i] * i % mod

    def nC(a, b):
        if b < 0 or b > a:
            return 0
        return fact[a] * invfact[b] % mod * invfact[a-b] % mod

    if k == 0:
        sys.stdout.write(str(fact[n] % mod))
        return
    m = n - k  # number of nonempty rows in the valid configuration.
    F = 0
    for j in range(m+1):
        sign = mod - 1 if ((m - j) & 1) else 1
        comb = fact[m] * invfact[j] % mod * invfact[m-j] % mod
        term = sign * comb % mod
        term = term * pow(j, n, mod) % mod
        F = (F + term) % mod
    ans = 2 * nC(n, k) % mod * F % mod
    sys.stdout.write(str(ans % mod))

########################################
# Problem 2 Solver
########################################
def solve_problem2():
    # Problem 2:
    # "Given a chessboard row with enemy pawns and Gregor’s pawns (binary strings),
    # find the maximum number of Gregor’s pawns that can reach the enemy row.
    # The greedy matching: for each Gregor pawn (from left to right) try left capture,
    # then vertical move, then right capture."
    import sys
    data = sys.stdin.read().split()
    if not data:
        return
    t = int(data[0])
    pos = 1
    out_lines = []
    for _ in range(t):
        n = int(data[pos]); pos += 1
        enemy = list(data[pos].strip()); pos += 1
        gregor = list(data[pos].strip()); pos += 1
        used = [False]*n
        count = 0
        for i in range(n):
            if gregor[i] == '1':
                if i > 0 and enemy[i-1] == '1' and not used[i-1]:
                    count += 1
                    used[i-1] = True
                elif enemy[i] == '0' and not used[i]:
                    count += 1
                    used[i] = True
                elif i < n-1 and enemy[i+1] == '1' and not used[i+1]:
                    count += 1
                    used[i+1] = True
        out_lines.append(str(count))
    sys.stdout.write("\n".join(out_lines))

########################################
# Problem 3 Solver
########################################
def solve_problem3():
    # Problem 3:
    # "Find a shortest sequence of moves for a king from square s to t.
    # In each move, the king moves by at most one step in the horizontal, vertical, 
    # or diagonal direction."
    import sys
    data = sys.stdin.read().splitlines()
    if not data:
        return
    start = data[0].strip()
    dest = data[1].strip()
    def to_coords(pos):
        return ord(pos[0]) - ord('a') + 1, int(pos[1])
    sc, sr = to_coords(start)
    ec, er = to_coords(dest)
    moves = []
    while (sc, sr) != (ec, er):
        step = ""
        if sc < ec:
            step += "R"; sc += 1
        elif sc > ec:
            step += "L"; sc -= 1
        if sr < er:
            step += "U"; sr += 1
        elif sr > er:
            step += "D"; sr -= 1
        moves.append(step)
    out_lines = [str(len(moves))] + moves
    sys.stdout.write("\n".join(out_lines))

########################################
# Problem 4 Solver
########################################
def solve_problem4():
    # Problem 4:
    # "Given m rooks on an n×n board (no two attack each other), 
    # compute the minimum number of moves to put all rooks on the main diagonal.
    # Answer = (# rooks not on diagonal) + (number of cycles in the mapping)."
    import sys
    data = sys.stdin.buffer.read().split()
    if not data:
        return
    t = int(data[0])
    pos = 1
    results = []
    for _ in range(t):
        n = int(data[pos]); m = int(data[pos+1]); pos += 2
        mapping = {}
        off_diag = 0
        for i in range(m):
            x = int(data[pos]); y = int(data[pos+1]); pos += 2
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
    sys.stdout.write("\n".join(results))

########################################
# Problem 5 Solver
########################################
def solve_problem5():
    # Problem 5:
    # "We are given a 1×n chessboard (n cells) with some cells occupied (binary string).
    # Pawns can jump two cells if the adjacent cell is occupied and the landing cell is empty.
    # Count the number of reachable states (mod 998244353). 
    # It turns out that the answer equals C( (n – ones) + r, r )
    # where ones = number of occupied cells and r = number of disjoint adjacent '11' pairs."
    import sys
    data = sys.stdin.read().splitlines()
    if not data:
        return
    t = int(data[0].strip())
    mod = 998244353
    maxN = 10**5 + 10
    fact = [1]*maxN
    invfact = [1]*maxN
    for i in range(2, maxN):
        fact[i] = fact[i-1] * i % mod
    invfact[-1] = pow(fact[-1], mod-2, mod)
    for i in range(maxN-1, 0, -1):
        invfact[i-1] = invfact[i] * i % mod
        
    def nCr(n, r):
        if r < 0 or r > n:
            return 0
        return fact[n] * invfact[r] % mod * invfact[n-r] % mod
    
    out_lines = []
    line_index = 1
    for _ in range(t):
        if line_index >= len(data): break
        try:
            declared_n = int(data[line_index].strip())
        except:
            declared_n = 0
        line_index += 1
        if line_index >= len(data): break
        s = data[line_index].strip()
        line_index += 1
        n = len(s)
        ones = s.count("1")
        r = 0
        i = 0
        while i < n-1:
            if s[i] == "1" and s[i+1]=="1":
                r += 1
                i += 2
            else:
                i += 1
        ans = nCr((n - ones) + r, r)
        out_lines.append(str(ans))
    sys.stdout.write("\n".join(out_lines))

########################################
# Main detection and dispatcher
########################################
def main():
    import sys
    # Read entire input tokens (split by whitespace)
    all_input = sys.stdin.read().split()
    if not all_input:
        return
    # Try to convert first token to integer.
    try:
        _ = int(all_input[0])
        first_is_int = True
    except:
        first_is_int = False
    # If the first token isn’t an integer then it must be Problem 3.
    if not first_is_int:
        sys.stdin.seek(0)
        solve_problem3()
        return
    total_tokens = len(all_input)
    # If exactly 2 tokens then Problem 1.
    if total_tokens == 2:
        sys.stdin.seek(0)
        solve_problem1()
        return
    # Let t0 be the first token.
    t0 = int(all_input[0])
    # For Problem 2, each test case has 3 tokens, so total tokens == 1 + 3*t0.
    if total_tokens == 1 + 3*t0:
        sys.stdin.seek(0)
        solve_problem2()
        return
    # For Problem 5, each test case has 2 tokens, total tokens == 1 + 2*t0.
    if total_tokens == 1 + 2*t0:
        sys.stdin.seek(0)
        solve_problem5()
        return
    # Otherwise assume Problem 4.
    sys.stdin.seek(0)
    solve_problem4()

if __name__ == '__main__':
    main()

