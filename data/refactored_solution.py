def solve_chess_splitting(s: str) -> bool:
    """
    Problem 1: Split a string into 4 distinct non-empty parts.
    
    Returns True if string can be split, False otherwise.
    """
    n = len(s)
    if n < 4:
        return False

    # Special-case: if all characters are identical, the only way to differentiate
    # four parts is by having different lengths. The minimum four distinct positive
    # integers sum to 1+2+3+4 = 10; thus if n >= 10, we can choose (for example)
    # 1, 2, 3, and n−6. Otherwise, it is impossible.
    if len(set(s)) == 1:
        return n >= 10

    # The known heuristic: if a valid splitting exists, then one exists where the first
    # three segments (a, b, c) are fairly short. Restricting their lengths to at most 10
    # yields at most 10^3 iterations per test case which is fast enough.
    max_seg_len = min(10, n)
    # i splits s into a and the remainder; we need at least 3 characters after a.
    for i in range(1, min(n - 2, max_seg_len) + 1):
        a = s[:i]
        # j splits the remainder, leaving room for 2 parts (c and d)
        # Ensure b is non-empty and j <= n-1.
        for j in range(i + 1, min(n - 1, i + max_seg_len) + 1):
            b = s[i:j]
            # k splits the rest into c and d (d must be nonempty)
            for k in range(j + 1, min(n, j + max_seg_len)):
                c = s[j:k]
                d = s[k:]
                # All four parts must be pairwise distinct.
                if len({a, b, c, d}) == 4:
                    return True
    return False

def solve_chess_path_sum(n: int, m: int, grid: list) -> bool:
    """
    Problem 2: Check if there's a path from top-left to bottom-right with sum 0.
    
    Returns True if such a path exists, False otherwise.
    """
    # The number of cells in any valid path is (n + m - 1).
    # Every cell contributes either +1 or -1 so the total sum mod2 is the same as (n+m-1) mod2.
    # Thus, unless (n+m-1) is even we cannot have a total sum of zero.
    if (n + m - 1) % 2 != 0:
        return False
    
    # A large value (max path length <= n+m-1 <= 2000, so 10**9 is plenty)
    INF = 10**9
    
    # Initialize DP tables:
    # dp_min[i][j] = minimum sum along any path to (i,j)
    # dp_max[i][j] = maximum sum along any path to (i,j)
    dp_min = [[INF] * m for _ in range(n)]
    dp_max = [[-INF] * m for _ in range(n)]
    dp_min[0][0] = grid[0][0]
    dp_max[0][0] = grid[0][0]

    # Process in order (only "down" and "right" moves are allowed)
    for i in range(n):
        for j in range(m):
            if i == 0 and j == 0:
                continue
            cur = grid[i][j]
            cand_min = INF
            cand_max = -INF
            if i > 0:
                cand_min = min(cand_min, dp_min[i-1][j])
                cand_max = max(cand_max, dp_max[i-1][j])
            if j > 0:
                cand_min = min(cand_min, dp_min[i][j-1])
                cand_max = max(cand_max, dp_max[i][j-1])
            dp_min[i][j] = cand_min + cur
            dp_max[i][j] = cand_max + cur

    final_min = dp_min[n-1][m-1]
    final_max = dp_max[n-1][m-1]
    # Notice: The reachable sums at (n-1, m-1) are all of the same parity (even in our case)
    # and form all numbers in the interval [final_min, final_max] with that parity.
    # Hence, a path with sum 0 exists if 0 lies in the interval and the parity condition holds:
    return final_min <= 0 <= final_max and ((0 - final_min) % 2 == 0)

def solve_chess_tree_paths(n: int, u: int, v: int) -> int:
    """
    Problem 3: Count pairs of nodes with the same path configuration in a binary tree.
    
    Returns the count of such pairs.
    """
    # get_parent(x): for x>=2: even --> x//2; odd --> (x–1)//2.
    # And we define get_parent(1)=0 and get_parent(0)=0.
    def get_parent(x):
        if x <= 1:
            return 0
        return x // 2 if (x & 1) == 0 else (x - 1) // 2

    # The depth (distance from the root) for a positive node is: depth(x)=x.bit_length()-1.
    # We define depth(0)=0.
    def depth(x):
        if x <= 0:
            return 0
        return x.bit_length() - 1

    # Compute LCA(u,v) by lifting the deeper node up until the depths agree.
    # (Using our get_parent the special case is handled so that if one of u,v is 0, we return 0.)
    def lca(x, y):
        dx = depth(x)
        dy = depth(y)
        while dx > dy:
            x = get_parent(x)
            dx -= 1
        while dy > dx:
            y = get_parent(y)
            dy -= 1
        while x != y:
            x = get_parent(x)
            y = get_parent(y)
        return x

    # To "extract" the path configuration (the unique sequence of moves) from a starting node
    # up to some ancestor anc, we simulate "up-moves". When at a node:
    #   – if it is even then it came from a left–child move so record "L",
    #   – if odd then record "R".
    def get_up_commands(start, anc):
        cmds = []
        cur = start
        while cur != anc:
            # to avoid an infinite loop (if anc is not actually reached) we break if cur==0
            if cur == 0:
                break
            if (cur & 1) == 0:
                cmds.append("L")
                cur //= 2
            else:
                cmds.append("R")
                cur = (cur - 1) // 2
        return cmds

    # The downward commands from anc to node are simply the reversal of the upward commands
    # computed from node to anc.
    def get_down_commands(node, anc):
        cmds = get_up_commands(node, anc)
        cmds.reverse()
        return cmds

    # A sequence of downward commands defines a linear function f on candidate ancestor x.
    # (Each "L" maps x -> 2*x; each "R" maps x -> 2*x+1.)
    def compute_linear(cmds):
        A = 1
        B = 0
        for c in cmds:
            if c == "L":
                A *= 2
                B *= 2
            else:  # "R"
                A *= 2
                B = B * 2 + 1
        return A, B

    # For positive divisor b, our version of ceiling division works also with negative numerators.
    def ceil_div(a, b):
        return -(-a // b)
    
    # Compute LCA
    L = lca(u, v)
    # Upward commands from u to L; then reverse to get the function that "builds" u from L.
    up_cmds = get_up_commands(u, L)
    up_cmds_rev = list(reversed(up_cmds))
    A1, B1 = compute_linear(up_cmds_rev)
    # Downward commands from L to v yield the function for v.
    down_cmds = get_down_commands(v, L)
    A2, B2 = compute_linear(down_cmds)
    
    # Solve for x subject to
    #    1 ≤ A1*x+B1 ≤ n   and   1 ≤ A2*x+B2 ≤ n, with x ≥ 1.
    lb1 = ceil_div(1 - B1, A1)
    ub1 = (n - B1) // A1
    lb2 = ceil_div(1 - B2, A2)
    ub2 = (n - B2) // A2
    LB = max(1, lb1, lb2)
    UB = min(ub1, ub2)
    if LB > UB:
        return 0
    return UB - LB + 1

def solve_chess_green_square(n: int, A: list, B: list) -> int:
    """
    Problem 4: Find the largest green square in a garden.
    
    Returns the side length of the largest green square.
    """
    # Given a window of contiguous rows (i to i+L-1),
    # the green segment in that window is the intersection
    # of all individual row segments:
    #    [max(A[i...i+L-1]), min(B[i...i+L-1])]
    # We need to check if this intersection is wide enough
    # (i.e. its length >= L) so that it can contain L contiguous green cells.
    
    # check(L) returns True if there exists a contiguous group of L rows
    # such that (minB - maxA + 1) >= L.
    def check(L):
        dq_max = deque()  # For sliding window maximum of A (stores indices) 
        dq_min = deque()  # For sliding window minimum of B (stores indices)
        
        for j in range(n):
            # For maximum: remove all indices from the right whose A values are <= A[j]
            while dq_max and A[j] >= A[dq_max[-1]]:
                dq_max.pop()
            dq_max.append(j)
            
            # For minimum: remove all indices from the right whose B values are >= B[j]
            while dq_min and B[j] <= B[dq_min[-1]]:
                dq_min.pop()
            dq_min.append(j)
            
            # Once we have processed at least L rows, check the current window [i, j]
            if j >= L - 1:
                i = j - L + 1  # starting index of the current window
                
                # Remove indices that are outside the current window.
                while dq_max and dq_max[0] < i:
                    dq_max.popleft()
                while dq_min and dq_min[0] < i:
                    dq_min.popleft()
                
                # The current window's intersection is:
                #   [max(A[i...j]), min(B[i...j])] = [A[dq_max[0]], B[dq_min[0]]]
                if B[dq_min[0]] - A[dq_max[0]] + 1 >= L:
                    return True
        return False

    # Binary search over possible square sizes L (from 1 to n)
    lo, hi = 1, n
    ans = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if check(mid):
            ans = mid
            lo = mid + 1
        else:
            hi = mid - 1

    return ans

def solve_chess_perfect_digits(a: int, b: int) -> int:
    """
    Problem 5: Count perfect squares consisting only of perfect digits.
    
    Returns the count of such squares in the range [a, b] or, if a > b,
    returns the negative of the count in (b, a].
    """
    # Generate all perfect squares <= max_limit that consist only of allowed digits: '0','1','4','9'.
    def generate_perfect_digit_squares(max_limit):
        allowed_digits = set("0149")
        valid_squares = []
        max_n = int(max_limit ** 0.5)
        for n in range(1, max_n + 1):
            square = n * n
            if square > max_limit:
                break
            # Check that every digit in the square is in the allowed set.
            if all(ch in allowed_digits for ch in str(square)):
                valid_squares.append(square)
        return valid_squares
    
    # Precompute all valid perfect digit squares up to 10^10.
    MAX_LIMIT = 10**10
    valid = generate_perfect_digit_squares(MAX_LIMIT)
    valid.sort()
    
    if a <= b:
        # Count numbers in [a, b]
        cnt = bisect.bisect_right(valid, b) - bisect.bisect_left(valid, a)
    else:
        # For a > b, the convention from test cases is to count in (b, a] only
        # and then return the negative of that count.
        cnt = -(bisect.bisect_right(valid, a) - bisect.bisect_right(valid, b))
    
    return cnt

def main():
    """Main function to handle all problem types based on input pattern."""
    lines = sys.stdin.read().strip().split('\n')
    if not lines:
        return
    
    # First line generally contains number of test cases
    first_line = lines[0].strip().split()
    
    # Detect problem type based on pattern matching
    
    # Problem 1: String splitting (simple format with strings to be split)
    if len(first_line) == 1 and lines[1].isalpha():
        t = int(first_line[0])
        results = []
        for i in range(1, t + 1):
            s = lines[i].strip()
            results.append("YES" if solve_chess_splitting(s) else "NO")
        sys.stdout.write("\n".join(results))
        
    # Problem 2: Path sum in grid (n, m followed by grid values)
    elif len(lines) > 1 and len(lines[1].split()) == 2:
        t = int(first_line[0])
        line_idx = 1
        results = []
        
        for _ in range(t):
            n, m = map(int, lines[line_idx].split())
            line_idx += 1
            
            grid = []
            for i in range(n):
                grid.append(list(map(int, lines[line_idx].split())))
                line_idx += 1
                
            results.append("YES" if solve_chess_path_sum(n, m, grid) else "NO")
            
        sys.stdout.write("\n".join(results))
        
    # Problem 3: Tree paths (three integers n, u, v per query)
    elif len(first_line) == 1 and len(lines[1].split()) == 3:
        q = int(first_line[0])
        results = []
        
        for i in range(1, q + 1):
            n