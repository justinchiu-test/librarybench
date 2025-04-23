# Example 0

## Problem
There are n lamps on a line, numbered from 1 to n. Each one has an initial state off (0) or on (1).

You're given k subsets A_1, …, A_k of \{1, 2, ..., n\}, such that the intersection of any three subsets is empty. In other words, for all 1 ≤ i_1 < i_2 < i_3 ≤ k, A_{i_1} ∩ A_{i_2} ∩ A_{i_3} = ∅.

In one operation, you can choose one of these k subsets and switch the state of all lamps in it. It is guaranteed that, with the given subsets, it's possible to make all lamps be simultaneously on using this type of operation.

Let m_i be the minimum number of operations you have to do in order to make the i first lamps be simultaneously on. Note that there is no condition upon the state of other lamps (between i+1 and n), they can be either off or on.

You have to compute m_i for all 1 ≤ i ≤ n.

Input

The first line contains two integers n and k (1 ≤ n, k ≤ 3 ⋅ 10^5).

The second line contains a binary string of length n, representing the initial state of each lamp (the lamp i is off if s_i = 0, on if s_i = 1).

The description of each one of the k subsets follows, in the following format:

The first line of the description contains a single integer c (1 ≤ c ≤ n) — the number of elements in the subset.

The second line of the description contains c distinct integers x_1, …, x_c (1 ≤ x_i ≤ n) — the elements of the subset.

It is guaranteed that: 

  * The intersection of any three subsets is empty; 
  * It's possible to make all lamps be simultaneously on using some operations. 

Output

You must output n lines. The i-th line should contain a single integer m_i — the minimum number of operations required to make the lamps 1 to i be simultaneously on.

Examples

Input


7 3
0011100
3
1 4 6
3
3 4 7
2
2 3


Output


1
2
3
3
3
3
3


Input


8 6
00110011
3
1 3 8
5
1 2 5 6 7
2
6 8
2
3 5
2
4 7
1
2


Output


1
1
1
1
1
1
4
4


Input


5 3
00011
3
1 2 3
1
4
3
3 4 5


Output


1
1
1
1
1


Input


19 5
1001001001100000110
2
2 3
2
5 6
2
8 9
5
12 13 14 15 16
1
19


Output


0
1
1
1
2
2
2
3
3
3
3
4
4
4
4
4
4
4
5

Note

In the first example: 

  * For i = 1, we can just apply one operation on A_1, the final states will be 1010110; 
  * For i = 2, we can apply operations on A_1 and A_3, the final states will be 1100110; 
  * For i ≥ 3, we can apply operations on A_1, A_2 and A_3, the final states will be 1111111. 



In the second example: 

  * For i ≤ 6, we can just apply one operation on A_2, the final states will be 11111101; 
  * For i ≥ 7, we can apply operations on A_1, A_3, A_4, A_6, the final states will be 11111111. 

## Solution
```cpp
from sys import stdin
input = stdin.readline

n , k = [int(i) for i in input().split()]
pairs = [i + k for i in range(k)] + [i for i in range(k)]
initial_condition = list(map(lambda x: x == '1',input().strip()))
data = [i for i in range(2*k)] 
constrain = [-1] * (2*k)
h = [0] * (2*k)
L = [1] * k + [0] * k
dp1 = [-1 for i in range(n)]
dp2 = [-1 for i in range(n)]
for i in range(k):
    input()
    inp = [int(j) for j in input().split()]
    for s in inp:
        if dp1[s-1] == -1:dp1[s-1] = i
        else:dp2[s-1] = i

pfsums = 0
ans = []


def remove_pfsum(s1):
    global pfsums
    if constrain[s1] == 1:
        pfsums -= L[s1]
    elif constrain[pairs[s1]] == 1:
        pfsums -= L[pairs[s1]]
    else:
        pfsums -= min(L[s1],L[pairs[s1]])

def sh(i):
    while i != data[i]:
        i = data[i]
    return i

def upd_pfsum(s1):
    global pfsums
    if constrain[s1] == 1:
        pfsums += L[s1]
    elif constrain[pairs[s1]] == 1:
        pfsums += L[pairs[s1]]
    else:
        pfsums += min(L[s1],L[pairs[s1]])

def ms(i,j):
    i = sh(i) ; j = sh(j)
    cons = max(constrain[i],constrain[j])

    if h[i] < h[j]:
        data[i] = j
        L[j] += L[i]
        constrain[j] = cons
        return j
    else:
        data[j] = i
        if h[i] == h[j]:
            h[i] += 1
        L[i] += L[j]
        constrain[i] = cons
        return i

for i in range(n):
    if dp1[i] == -1 and dp2[i] == -1:
        pass
    elif dp2[i] == -1:
        s1 = sh(dp1[i])
        remove_pfsum(s1)
        constrain[s1] = 0 if initial_condition[i] else 1
        constrain[pairs[s1]] = 1 if initial_condition[i] else 0
        upd_pfsum(s1)
    else:
        s1 = sh(dp1[i]) ; s2 = sh(dp2[i])
        if s1 == s2 or pairs[s1] == s2:
            pass
        else:
            remove_pfsum(s1)
            remove_pfsum(s2)
            if initial_condition[i]:
                new_s1 = ms(s1,s2)
                new_s2 = ms(pairs[s1],pairs[s2])
            else:
                new_s1 = ms(s1,pairs[s2])
                new_s2 = ms(pairs[s1],s2)
            pairs[new_s1] = new_s2
            pairs[new_s2] = new_s1
            upd_pfsum(new_s1)

    ans.append(pfsums)

for i in ans:
    print(i)

```

# Example 1

## Problem
There are n lamps on a line, numbered from 1 to n. Each one has an initial state off (0) or on (1).

You're given k subsets A_1, …, A_k of \{1, 2, ..., n\}, such that the intersection of any three subsets is empty. In other words, for all 1 ≤ i_1 < i_2 < i_3 ≤ k, A_{i_1} ∩ A_{i_2} ∩ A_{i_3} = ∅.

In one operation, you can choose one of these k subsets and switch the state of all lamps in it. It is guaranteed that, with the given subsets, it's possible to make all lamps be simultaneously on using this type of operation.

Let m_i be the minimum number of operations you have to do in order to make the i first lamps be simultaneously on. Note that there is no condition upon the state of other lamps (between i+1 and n), they can be either off or on.

You have to compute m_i for all 1 ≤ i ≤ n.

Input

The first line contains two integers n and k (1 ≤ n, k ≤ 3 ⋅ 10^5).

The second line contains a binary string of length n, representing the initial state of each lamp (the lamp i is off if s_i = 0, on if s_i = 1).

The description of each one of the k subsets follows, in the following format:

The first line of the description contains a single integer c (1 ≤ c ≤ n) — the number of elements in the subset.

The second line of the description contains c distinct integers x_1, …, x_c (1 ≤ x_i ≤ n) — the elements of the subset.

It is guaranteed that: 

  * The intersection of any three subsets is empty; 
  * It's possible to make all lamps be simultaneously on using some operations. 

Output

You must output n lines. The i-th line should contain a single integer m_i — the minimum number of operations required to make the lamps 1 to i be simultaneously on.

Examples

Input


7 3
0011100
3
1 4 6
3
3 4 7
2
2 3


Output


1
2
3
3
3
3
3


Input


8 6
00110011
3
1 3 8
5
1 2 5 6 7
2
6 8
2
3 5
2
4 7
1
2


Output


1
1
1
1
1
1
4
4


Input


5 3
00011
3
1 2 3
1
4
3
3 4 5


Output


1
1
1
1
1


Input


19 5
1001001001100000110
2
2 3
2
5 6
2
8 9
5
12 13 14 15 16
1
19


Output


0
1
1
1
2
2
2
3
3
3
3
4
4
4
4
4
4
4
5

Note

In the first example: 

  * For i = 1, we can just apply one operation on A_1, the final states will be 1010110; 
  * For i = 2, we can apply operations on A_1 and A_3, the final states will be 1100110; 
  * For i ≥ 3, we can apply operations on A_1, A_2 and A_3, the final states will be 1111111. 



In the second example: 

  * For i ≤ 6, we can just apply one operation on A_2, the final states will be 11111101; 
  * For i ≥ 7, we can apply operations on A_1, A_3, A_4, A_6, the final states will be 11111111. 

## Solution
```cpp
from sys import stdin
input = stdin.readline

n , k = [int(i) for i in input().split()]
pairs = [i + k for i in range(k)] + [i for i in range(k)]
initial_condition = list(map(lambda x: x == '1',input().strip()))
data = [i for i in range(2*k)] 
constrain = [-1] * (2*k)
h = [0] * (2*k)
L = [1] * k + [0] * k
dp1 = [-1 for i in range(n)]
dp2 = [-1 for i in range(n)]
for i in range(k):
    input()
    inp = [int(j) for j in input().split()]
    for s in inp:
        if dp1[s-1] == -1:dp1[s-1] = i
        else:dp2[s-1] = i

pfsums = 0
ans = []


def remove_pfsum(s1):
    global pfsums
    if constrain[s1] == 1:
        pfsums -= L[s1]
    elif constrain[pairs[s1]] == 1:
        pfsums -= L[pairs[s1]]
    else:
        pfsums -= min(L[s1],L[pairs[s1]])

def sh(i):
    while i != data[i]:
        i = data[i]
    return i

def upd_pfsum(s1):
    global pfsums
    if constrain[s1] == 1:
        pfsums += L[s1]
    elif constrain[pairs[s1]] == 1:
        pfsums += L[pairs[s1]]
    else:
        pfsums += min(L[s1],L[pairs[s1]])

def ms(i,j):
    i = sh(i) ; j = sh(j)
    cons = max(constrain[i],constrain[j])

    if h[i] < h[j]:
        data[i] = j
        L[j] += L[i]
        constrain[j] = cons
        return j
    else:
        data[j] = i
        if h[i] == h[j]:
            h[i] += 1
        L[i] += L[j]
        constrain[i] = cons
        return i

for i in range(n):
    if dp1[i] == -1 and dp2[i] == -1:
        pass
    elif dp2[i] == -1:
        s1 = sh(dp1[i])
        remove_pfsum(s1)
        constrain[s1] = 0 if initial_condition[i] else 1
        constrain[pairs[s1]] = 1 if initial_condition[i] else 0
        upd_pfsum(s1)
    else:
        s1 = sh(dp1[i]) ; s2 = sh(dp2[i])
        if s1 == s2 or pairs[s1] == s2:
            pass
        else:
            remove_pfsum(s1)
            remove_pfsum(s2)
            if initial_condition[i]:
                new_s1 = ms(s1,s2)
                new_s2 = ms(pairs[s1],pairs[s2])
            else:
                new_s1 = ms(s1,pairs[s2])
                new_s2 = ms(pairs[s1],s2)
            pairs[new_s1] = new_s2
            pairs[new_s2] = new_s1
            upd_pfsum(new_s1)

    ans.append(pfsums)

for i in ans:
    print(i)

```

# Example 2

## Problem
Ari the monster is not an ordinary monster. She is the hidden identity of Super M, the Byteforces’ superhero. Byteforces is a country that consists of n cities, connected by n - 1 bidirectional roads. Every road connects exactly two distinct cities, and the whole road system is designed in a way that one is able to go from any city to any other city using only the given roads. There are m cities being attacked by humans. So Ari... we meant Super M have to immediately go to each of the cities being attacked to scare those bad humans. Super M can pass from one city to another only using the given roads. Moreover, passing through one road takes her exactly one kron - the time unit used in Byteforces. 

<image>

However, Super M is not on Byteforces now - she is attending a training camp located in a nearby country Codeforces. Fortunately, there is a special device in Codeforces that allows her to instantly teleport from Codeforces to any city of Byteforces. The way back is too long, so for the purpose of this problem teleportation is used exactly once.

You are to help Super M, by calculating the city in which she should teleport at the beginning in order to end her job in the minimum time (measured in krons). Also, provide her with this time so she can plan her way back to Codeforces.

Input

The first line of the input contains two integers n and m (1 ≤ m ≤ n ≤ 123456) - the number of cities in Byteforces, and the number of cities being attacked respectively.

Then follow n - 1 lines, describing the road system. Each line contains two city numbers ui and vi (1 ≤ ui, vi ≤ n) - the ends of the road i.

The last line contains m distinct integers - numbers of cities being attacked. These numbers are given in no particular order.

Output

First print the number of the city Super M should teleport to. If there are many possible optimal answers, print the one with the lowest city number.

Then print the minimum possible time needed to scare all humans in cities being attacked, measured in Krons.

Note that the correct answer is always unique.

Examples

Input

7 2
1 2
1 3
1 4
3 5
3 6
3 7
2 7


Output

2
3


Input

6 4
1 2
2 3
2 4
4 5
4 6
2 4 5 6


Output

2
4

Note

In the first sample, there are two possibilities to finish the Super M's job in 3 krons. They are:

<image> and <image>.

However, you should choose the first one as it starts in the city with the lower number.

## Solution
```cpp
def f(k, h):
    print(k, h)
    exit()

def g(p):
    i = p.pop()
    return i, t[i]

import sys

d = list(map(int, sys.stdin.read().split()))

n, m = d[0], d[1]
if n == 1: f(1, 0)
k = 2 * n

t = [[0, set(), i, 0] for i in range(n + 1)]
for i in d[k:]: t[i][0] = 1

for a, b in zip(d[2:k:2], d[3:k:2]):
    t[a][1].add(b)
    t[b][1].add(a)

p = ([], [])
for x in t:
    if len(x[1]) == 1: p[x[0]].append(x[2])

k = s = 1
while p[0]:
    i, x = g(p[0])
    j, y = g(x[1])
    y[1].remove(i)
    if len(y[1]) == 1: p[y[0]].append(j)

if len(p[k]) == 1: f(p[k][0], 0)
for i in p[k]: t[i][3] = 1

while 1:
    s += 2
    i, x = g(p[k])
    j, y = g(x[1])
    if len(y[1]) == 1: f(min(x[2], y[2]), s - x[3] - y[3])
    x[3] += 1
    if x[3] > y[3]: y[2:] = x[2:]
    elif x[3] == y[3]: y[2] = min(x[2], y[2])
    y[1].remove(i)
    if len(y[1]) == 1: p[1 - k].append(j)
    if not p[k]: k = 1 - k
```

# Example 3

## Problem
Denis, after buying flowers and sweets (you will learn about this story in the next task), went to a date with Nastya to ask her to become a couple. Now, they are sitting in the cafe and finally... Denis asks her to be together, but ... Nastya doesn't give any answer. 

The poor boy was very upset because of that. He was so sad that he punched some kind of scoreboard with numbers. The numbers are displayed in the same way as on an electronic clock: each digit position consists of 7 segments, which can be turned on or off to display different numbers. The picture shows how all 10 decimal digits are displayed: 

<image>

After the punch, some segments stopped working, that is, some segments might stop glowing if they glowed earlier. But Denis remembered how many sticks were glowing and how many are glowing now. Denis broke exactly k segments and he knows which sticks are working now. Denis came up with the question: what is the maximum possible number that can appear on the board if you turn on exactly k sticks (which are off now)? 

It is allowed that the number includes leading zeros.

Input

The first line contains integer n (1 ≤ n ≤ 2000) — the number of digits on scoreboard and k (0 ≤ k ≤ 2000) — the number of segments that stopped working.

The next n lines contain one binary string of length 7, the i-th of which encodes the i-th digit of the scoreboard.

Each digit on the scoreboard consists of 7 segments. We number them, as in the picture below, and let the i-th place of the binary string be 0 if the i-th stick is not glowing and 1 if it is glowing. Then a binary string of length 7 will specify which segments are glowing now.

<image>

Thus, the sequences "1110111", "0010010", "1011101", "1011011", "0111010", "1101011", "1101111", "1010010", "1111111", "1111011" encode in sequence all digits from 0 to 9 inclusive.

Output

Output a single number consisting of n digits — the maximum number that can be obtained if you turn on exactly k sticks or -1, if it is impossible to turn on exactly k sticks so that a correct number appears on the scoreboard digits.

Examples

Input


1 7
0000000


Output


8

Input


2 5
0010010
0010010


Output


97

Input


3 5
0100001
1001001
1010011


Output


-1

Note

In the first test, we are obliged to include all 7 sticks and get one 8 digit on the scoreboard.

In the second test, we have sticks turned on so that units are formed. For 5 of additionally included sticks, you can get the numbers 07, 18, 34, 43, 70, 79, 81 and 97, of which we choose the maximum — 97.

In the third test, it is impossible to turn on exactly 5 sticks so that a sequence of numbers appears on the scoreboard.

## Solution
```cpp
import sys,os,io
# input = io.BytesIO(os.read(0, os.fstat(0).st_size)).readline
input = sys.stdin.readline

def cout(a):
    for i in a:
        print(i,end="")
    print()

n,m = [int(i) for i in input().split()]
a = []
b = [[1,1,1,0,1,1,1],[0,0,1,0,0,1,0],[1,0,1,1,1,0,1],[1,0,1,1,0,1,1],[0,1,1,1,0,1,0],[1,1,0,1,0,1,1],[1,1,0,1,1,1,1],[1,0,1,0,0,1,0],[1,1,1,1,1,1,1],[1,1,1,1,0,1,1]]
for i in range (n):
    a.append([int(i) for i in input().strip()])

cnt = [0]*n
for i in range (n):
    mini = 7
    for j in range (9,-1,-1):
        cs = 0
        for k in range (7):
            if a[i][k]==1 and b[j][k]==0:
                cs = 10
                break
            if a[i][k]==0 and b[j][k]==1:
                cs+=1
        mini = min(cs, mini)
    cnt[i] = mini

cnt1 = [0]*(n+1)
for i in range (n):
    cnt1[i] = 7-sum(a[i])

for i in range (n-2, -1, -1):
    cnt[i]+=cnt[i+1]
    cnt1[i]+=cnt1[i+1]
cnt.append(0)

if cnt[0]>m or m>cnt1[0]:
    print(-1)
    exit()
extra = m
final = []
if n==1:
    for i in range (n):
        for j in range (9, -1, -1):
            cs = 0
            for k in range (7):
                if a[i][k]==1 and b[j][k]==0:
                    cs = -1
                    break
                if a[i][k]==0 and b[j][k]==1:
                    cs += 1
            if cs==-1:
                continue
            if (extra - cs)>= cnt[i+1] and (extra - cs)<=cnt1[i+1]:
                final.append(j)
                extra -= cs
                break
    if len(final)==0:
        print(-1)
    else:
        for i in final:
            print(i,end="")
        print()
    exit()

lastcs = 0
for i in range (n-2):
    for j in range (9, -1, -1):
        cs = 0
        for k in range (7):
            if a[i][k]==1 and b[j][k]==0:
                cs = -1
                break
            if a[i][k]==0 and b[j][k]==1:
                cs += 1
        if cs==-1:
            continue
        if (extra - cs)>= cnt[i+1] and (extra - cs)<=cnt1[i+1]:
            final.append(j)
            extra -= cs
            lastcs = cs
            break

if n>=3:
    extra += lastcs
available1 = set()
available2 = set()
for i  in range (1,3):
    for j in range (9, -1, -1):
        cs = 0
        for k in range (7):
            if a[-i][k]==1 and b[j][k]==0:
                cs = -1
                break
            if a[-i][k]==0 and b[j][k]==1:
                cs += 1
        if cs==-1:
            continue
        if i==1:
            available1.add(cs)
        else:
            available2.add(cs)

if n==2:
    available = list(available1)
    for i in range (n-2, n):
        for j in range (9, -1, -1):
            cs = 0
            for k in range (7):
                if a[i][k]==1 and b[j][k]==0:
                    cs = -1
                    break
                if a[i][k]==0 and b[j][k]==1:
                    cs += 1
            if cs==-1:
                continue
            if (extra - cs)>= cnt[i+1] and (extra - cs)<=cnt1[i+1] and (extra - cs)in available:
                final.append(j)
                available = [0]
                extra -= cs
                break
else:
    if len(final):
        final.pop()
    available = []
    for i in available1:
        for j in available2:
            available.append(i+j)
    i = n-3

    for j in range (9, -1, -1):
        cs = 0
        for k in range (7):
            if a[n-3][k]==1 and b[j][k]==0:
                cs = -1
                break
            if a[n-3][k]==0 and b[j][k]==1:
                cs += 1
        if cs==-1:
            continue
        if (extra - cs)>= cnt[i+1] and (extra - cs)<=cnt1[i+1] and (extra - cs)in available:
            final.append(j)
            extra -= cs
            break
    available = list(available1)
    for i in range (n-2, n):
        for j in range (9, -1, -1):
            cs = 0
            for k in range (7):
                if a[i][k]==1 and b[j][k]==0:
                    cs = -1
                    break
                if a[i][k]==0 and b[j][k]==1:
                    cs += 1
            if cs==-1:
                continue
            if (extra - cs)>= cnt[i+1] and (extra - cs)<=cnt1[i+1] and (extra - cs)in available:
                final.append(j)
                available = [0]
                extra -= cs
                break
if len(final)<n:
    print(-1)
else:
    for i in final:
        print(i,end="")
    print()
```

# Example 4

## Problem
There are n lamps on a line, numbered from 1 to n. Each one has an initial state off (0) or on (1).

You're given k subsets A_1, …, A_k of \{1, 2, ..., n\}, such that the intersection of any three subsets is empty. In other words, for all 1 ≤ i_1 < i_2 < i_3 ≤ k, A_{i_1} ∩ A_{i_2} ∩ A_{i_3} = ∅.

In one operation, you can choose one of these k subsets and switch the state of all lamps in it. It is guaranteed that, with the given subsets, it's possible to make all lamps be simultaneously on using this type of operation.

Let m_i be the minimum number of operations you have to do in order to make the i first lamps be simultaneously on. Note that there is no condition upon the state of other lamps (between i+1 and n), they can be either off or on.

You have to compute m_i for all 1 ≤ i ≤ n.

Input

The first line contains two integers n and k (1 ≤ n, k ≤ 3 ⋅ 10^5).

The second line contains a binary string of length n, representing the initial state of each lamp (the lamp i is off if s_i = 0, on if s_i = 1).

The description of each one of the k subsets follows, in the following format:

The first line of the description contains a single integer c (1 ≤ c ≤ n) — the number of elements in the subset.

The second line of the description contains c distinct integers x_1, …, x_c (1 ≤ x_i ≤ n) — the elements of the subset.

It is guaranteed that: 

  * The intersection of any three subsets is empty; 
  * It's possible to make all lamps be simultaneously on using some operations. 

Output

You must output n lines. The i-th line should contain a single integer m_i — the minimum number of operations required to make the lamps 1 to i be simultaneously on.

Examples

Input


7 3
0011100
3
1 4 6
3
3 4 7
2
2 3


Output


1
2
3
3
3
3
3


Input


8 6
00110011
3
1 3 8
5
1 2 5 6 7
2
6 8
2
3 5
2
4 7
1
2


Output


1
1
1
1
1
1
4
4


Input


5 3
00011
3
1 2 3
1
4
3
3 4 5


Output


1
1
1
1
1


Input


19 5
1001001001100000110
2
2 3
2
5 6
2
8 9
5
12 13 14 15 16
1
19


Output


0
1
1
1
2
2
2
3
3
3
3
4
4
4
4
4
4
4
5

Note

In the first example: 

  * For i = 1, we can just apply one operation on A_1, the final states will be 1010110; 
  * For i = 2, we can apply operations on A_1 and A_3, the final states will be 1100110; 
  * For i ≥ 3, we can apply operations on A_1, A_2 and A_3, the final states will be 1111111. 



In the second example: 

  * For i ≤ 6, we can just apply one operation on A_2, the final states will be 11111101; 
  * For i ≥ 7, we can apply operations on A_1, A_3, A_4, A_6, the final states will be 11111111. 

## Solution
```cpp
from sys import stdin

class disjoinSet(object):
    def __init__(self,n):
        self.father = [x for x in range(0,n+1)]
        self.rank = [0 for x in range(0,n+1)]

    def setOf(self, x):
        if(self.father[x] != x):
            self.father[x] = self.setOf(self.father[x])
        return self.father[x]

    def Merge(self,x,y):
        xR = self.setOf(x)
        yR = self.setOf(y)
        if(xR == yR):
            return
        if self.rank[xR] < self.rank[yR]:            
            self.father[xR] = yR
            size[yR] += size[xR]
        elif self.rank[xR] > self.rank[yR]:
            self.father[yR] = xR
            size[xR] += size[yR]
        else:
            self.father[yR] = xR
            size[xR] += size[yR]
            self.rank[xR] +=1

def cal(x):
    return min(size[dsu.setOf(x)],size[dsu.setOf(x+k)])

def Solve(i):   
    global ans
    cant = col[i][0]
    if cant == 2:
        x = col[i][1]
        y = col[i][2]
        if S[i] == 1:
            if dsu.setOf(x) == dsu.setOf(y):
                return
            ans -=cal(x) + cal(y)
            dsu.Merge(x,y)
            dsu.Merge(x+k,y+k)
            ans +=cal(y)
        else:
            if dsu.setOf(x) == dsu.setOf(y+k):
                return
            ans -=cal(x)+cal(y)
            dsu.Merge(x,y+k)
            dsu.Merge(x+k,y)
            ans +=cal(y)    
    elif cant == 1:
        x = col[i][1]
        if S[i] == 1:
            if dsu.setOf(x) == dsu.setOf(0):
                return
            ans -=cal(x)
            dsu.Merge(x,0)
            ans +=cal(x)
        else:
            if dsu.setOf(x+k) == dsu.setOf(0):
                return
            ans -=cal(x)
            dsu.Merge(x+k,0)
            ans +=cal(x)    



n,k = map(int,input().split())
S = [1]+list(map(int,list(stdin.readline().strip())))

dsu = disjoinSet(k*2+1)
    
col = [[0 for _ in range(3)] for _ in range(n+2)]
size = [0 for _ in range(k*2+1)]
ans = 0

for i in range(1,k+1):
    c = stdin.readline()
    c = int(c)
    conjunto = [1]+list(map(int,list(stdin.readline().split())))
    for j in range(1,len(conjunto)):
        x = conjunto[j]                        
        col[x][0] = col[x][0]+1
        col[x][col[x][0]] = i


for i in range(1,k+1):
    size[i]=1
size[0]=3*10e5

for i in range(1,n+1):    
    Solve(i)
    print(ans)

```

# Example 5

## Problem
Gargari got bored to play with the bishops and now, after solving the problem about them, he is trying to do math homework. In a math book he have found k permutations. Each of them consists of numbers 1, 2, ..., n in some order. Now he should find the length of the longest common subsequence of these permutations. Can you help Gargari?

You can read about longest common subsequence there: https://en.wikipedia.org/wiki/Longest_common_subsequence_problem

Input

The first line contains two integers n and k (1 ≤ n ≤ 1000; 2 ≤ k ≤ 5). Each of the next k lines contains integers 1, 2, ..., n in some order — description of the current permutation.

Output

Print the length of the longest common subsequence.

Examples

Input

4 3
1 4 2 3
4 1 2 3
1 2 4 3


Output

3

Note

The answer for the first test sample is subsequence [1, 2, 3].

## Solution
```cpp
from sys import stdin, stdout, setrecursionlimit
input = stdin.readline
# import string
# characters = string.ascii_lowercase
# digits = string.digits
# setrecursionlimit(int(1e6))
# dir = [-1,0,1,0,-1]
# moves = 'NESW'
inf = float('inf')
from functools import cmp_to_key
from collections import defaultdict as dd
from collections import Counter, deque
from heapq import *
import math
from math import floor, ceil, sqrt
def geti(): return map(int, input().strip().split())
def getl(): return list(map(int, input().strip().split()))
def getis(): return map(str, input().strip().split())
def getls(): return list(map(str, input().strip().split()))
def gets(): return input().strip()
def geta(): return int(input())
def print_s(s): stdout.write(s+'\n')


def solve():
    n, k = geti()
    mat = []
    pos = [[-1]*(n+1) for _ in range(k)]
    for i in range(k):
        mat.append(getl())
        for j in range(n):
            pos[i][mat[-1][j]] = j
    dp = [1]*n
    for i in range(n):
        for j in range(i):
            for now in range(k):
                if pos[now][mat[0][i]] <= pos[now][mat[0][j]]:
                    break
            else:
                dp[i] = max(dp[i], dp[j] + 1)
        # print(i, dp)
    ans = max(dp)
    print(ans)



if __name__=='__main__':
    solve()

```