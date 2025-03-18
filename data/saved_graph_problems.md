# Example 0

## Problem
There are n persons who initially don't know each other. On each morning, two of them, who were not friends before, become friends.

We want to plan a trip for every evening of m days. On each trip, you have to select a group of people that will go on the trip. For every person, one of the following should hold: 

  * Either this person does not go on the trip, 
  * Or at least k of his friends also go on the trip. 



Note that the friendship is not transitive. That is, if a and b are friends and b and c are friends, it does not necessarily imply that a and c are friends.

For each day, find the maximum number of people that can go on the trip on that day.

Input

The first line contains three integers n, m, and k (2 ≤ n ≤ 2 ⋅ 10^5, 1 ≤ m ≤ 2 ⋅ 10^5, 1 ≤ k < n) — the number of people, the number of days and the number of friends each person on the trip should have in the group.

The i-th (1 ≤ i ≤ m) of the next m lines contains two integers x and y (1≤ x, y≤ n, x≠ y), meaning that persons x and y become friends on the morning of day i. It is guaranteed that x and y were not friends before.

Output

Print exactly m lines, where the i-th of them (1≤ i≤ m) contains the maximum number of people that can go on the trip on the evening of the day i.

Examples

Input

4 4 2
2 3
1 2
1 3
1 4


Output

0
0
3
3


Input

5 8 2
2 1
4 2
5 4
5 2
4 3
5 1
4 1
3 2


Output

0
0
0
3
3
4
4
5


Input

5 7 2
1 5
3 2
2 5
3 4
1 2
5 3
1 3


Output

0
0
0
0
3
4
4

Note

In the first example, 

  * 1,2,3 can go on day 3 and 4. 



In the second example, 

  * 2,4,5 can go on day 4 and 5. 
  * 1,2,4,5 can go on day 6 and 7. 
  * 1,2,3,4,5 can go on day 8. 



In the third example, 

  * 1,2,5 can go on day 5. 
  * 1,2,3,5 can go on day 6 and 7. 

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;
const int module = 1000000007;
int main() {
  ios_base::sync_with_stdio(false);
  cin.tie(0);
  cout.tie(0);
  int n, m, k;
  cin >> n >> m >> k;
  vector<set<int>> to(n, set<int>());
  vector<pair<int, int>> edges(m);
  vector<int> nbr(n);
  for (int i = 0; i < m; ++i) {
    int a, b;
    cin >> a >> b;
    a--;
    b--;
    nbr[a]++;
    nbr[b]++;
    to[a].insert(b);
    to[b].insert(a);
    edges[i] = {a, b};
  }
  vector<bool> vis(n);
  int all = n;
  for (int i = 0; i < n; ++i) {
    if (!vis[i]) {
      if (nbr[i] < k) {
        queue<int> q;
        q.push(i);
        vis[i] = true;
        all--;
        while (!q.empty()) {
          int cur = q.front();
          q.pop();
          for (int t : to[cur]) {
            nbr[t]--;
            to[t].erase(cur);
            if (nbr[t] < k && !vis[t]) {
              q.push(t);
              vis[t] = true;
              all--;
            }
          }
        }
      }
    }
  }
  queue<int> q;
  vector<int> answer;
  answer.push_back(all);
  for (int i = m - 1; i > 0; i--) {
    auto [a, b] = edges[i];
    if (!vis[a] && !vis[b]) {
      to[a].erase(b);
      to[b].erase(a);
      nbr[a]--;
      nbr[b]--;
      if (nbr[a] < k) {
        q.push(a);
        vis[a] = true;
        all--;
      }
      if (nbr[b] < k) {
        q.push(b);
        vis[b] = true;
        all--;
      }
      while (!q.empty()) {
        int cur = q.front();
        q.pop();
        for (int t : to[cur]) {
          nbr[t]--;
          to[t].erase(cur);
          if (nbr[t] < k && !vis[t]) {
            q.push(t);
            vis[t] = true;
            all--;
          }
        }
      }
    }
    answer.push_back(all);
  }
  for (int i = answer.size() - 1; i >= 0; i--) {
    cout << answer[i] << "\n";
  }
}

```

# Example 1

## Problem
You are given an undirected graph with n vertices and m edges. Also, you are given an integer k.

Find either a clique of size k or a non-empty subset of vertices such that each vertex of this subset has at least k neighbors in the subset. If there are no such cliques and subsets report about it.

A subset of vertices is called a clique of size k if its size is k and there exists an edge between every two vertices from the subset. A vertex is called a neighbor of the other vertex if there exists an edge between them.

Input

The first line contains a single integer t (1 ≤ t ≤ 10^5) — the number of test cases. The next lines contain descriptions of test cases.

The first line of the description of each test case contains three integers n, m, k (1 ≤ n, m, k ≤ 10^5, k ≤ n).

Each of the next m lines contains two integers u, v (1 ≤ u, v ≤ n, u ≠ v), denoting an edge between vertices u and v.

It is guaranteed that there are no self-loops or multiple edges. It is guaranteed that the sum of n for all test cases and the sum of m for all test cases does not exceed 2 ⋅ 10^5.

Output

For each test case: 

If you found a subset of vertices such that each vertex of this subset has at least k neighbors in the subset in the first line output 1 and the size of the subset. On the second line output the vertices of the subset in any order.

If you found a clique of size k then in the first line output 2 and in the second line output the vertices of the clique in any order.

If there are no required subsets and cliques print -1.

If there exists multiple possible answers you can print any of them.

Example

Input


3
5 9 4
1 2
1 3
1 4
1 5
2 3
2 4
2 5
3 4
3 5
10 15 3
1 2
2 3
3 4
4 5
5 1
1 7
2 8
3 9
4 10
5 6
7 10
10 8
8 6
6 9
9 7
4 5 4
1 2
2 3
3 4
4 1
1 3


Output


2
4 1 2 3 
1 10
1 2 3 4 5 6 7 8 9 10 
-1

Note

In the first test case: the subset \{1, 2, 3, 4\} is a clique of size 4.

In the second test case: degree of each vertex in the original graph is at least 3. So the set of all vertices is a correct answer.

In the third test case: there are no cliques of size 4 or required subsets, so the answer is -1.

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;
using P = pair<int, int>;
const int M = 1000000007;
const long long LM = 1LL << 60;
vector<int> solve(const vector<vector<int>>& edge, int k) {
  int n = edge.size();
  queue<int> q;
  vector<int> deg(n);
  vector<bool> del(n);
  for (int i = 0; i < n; ++i) {
    deg[i] = edge[i].size();
    if (deg[i] < k) {
      del[i] = true;
      q.push(i);
    }
  }
  while (!q.empty()) {
    int p = q.front();
    q.pop();
    for (auto& i : edge[p]) {
      if (del[i]) continue;
      --deg[i];
      if (deg[i] < k) {
        del[i] = true;
        q.push(i);
      }
    }
  }
  vector<int> res;
  for (int i = 0; i < n; ++i) {
    if (!del[i]) {
      res.push_back(i);
    }
  }
  return res;
}
vector<int> solve2(const vector<vector<int>>& edge, int k) {
  int n = edge.size();
  queue<int> q;
  vector<int> deg(n);
  vector<bool> del(n);
  for (int i = 0; i < n; ++i) {
    deg[i] = edge[i].size();
    if (deg[i] < k - 1) {
      del[i] = true;
      q.push(i);
    }
  }
  while (!q.empty()) {
    int p = q.front();
    q.pop();
    for (auto& i : edge[p]) {
      if (del[i]) continue;
      --deg[i];
      if (deg[i] < k - 1) {
        del[i] = true;
        q.push(i);
      }
    }
  }
  vector<bool> pushed(n);
  for (int i = 0; i < n; ++i) {
    if (!del[i] && deg[i] == k - 1) {
      pushed[i] = true;
      q.push(i);
    }
  }
  vector<unordered_set<int>> edgeset(n);
  for (int i = 0; i < n; ++i) {
    for (auto& e : edge[i]) {
      edgeset[i].insert(e);
    }
  }
  while (!q.empty()) {
    int p = q.front();
    q.pop();
    if (deg[p] == k - 1) {
      vector<int> v;
      v.push_back(p);
      for (auto& i : edge[p]) {
        if (!del[i]) {
          v.push_back(i);
        }
      }
      bool ok = true;
      for (int i = 0; i < k && ok; ++i) {
        for (int j = i + 1; j < k; ++j) {
          if (!edgeset[v[i]].count(v[j])) {
            ok = false;
            break;
          }
        }
      }
      if (ok) {
        return v;
      }
    }
    for (auto& i : edge[p]) {
      if (del[i]) continue;
      --deg[i];
      if (deg[i] == k - 1 && !pushed[i]) {
        pushed[i] = true;
        q.push(i);
      }
    }
    del[p] = true;
  }
  return {};
}
int main() {
  cin.tie(0);
  ios::sync_with_stdio(0);
  int T;
  cin >> T;
  for (int _ = 0; _ < T; ++_) {
    int n, m, k;
    cin >> n >> m >> k;
    vector<vector<int>> edge(n);
    for (int i = 0; i < m; ++i) {
      int u, v;
      cin >> u >> v;
      --u;
      --v;
      edge[u].push_back(v);
      edge[v].push_back(u);
    }
    {
      vector<int> s0 = solve(edge, k);
      if (s0.size() > 0) {
        cout << 1 << ' ' << s0.size() << '\n';
        for (int i = 0; i < (int)s0.size(); ++i) {
          cout << s0[i] + 1 << (i + 1 < (int)s0.size() ? ' ' : '\n');
        }
        continue;
      }
    }
    {
      vector<int> s1 = solve2(edge, k);
      if (s1.size() > 0) {
        cout << 2 << '\n';
        for (int i = 0; i < (int)s1.size(); ++i) {
          cout << s1[i] + 1 << (i + 1 < (int)s1.size() ? ' ' : '\n');
        }
        continue;
      }
    }
    cout << -1 << '\n';
  }
  return 0;
}

```

# Example 2

## Problem
Hongcow is ruler of the world. As ruler of the world, he wants to make it easier for people to travel by road within their own countries.

The world can be modeled as an undirected graph with n nodes and m edges. k of the nodes are home to the governments of the k countries that make up the world.

There is at most one edge connecting any two nodes and no edge connects a node to itself. Furthermore, for any two nodes corresponding to governments, there is no path between those two nodes. Any graph that satisfies all of these conditions is stable.

Hongcow wants to add as many edges as possible to the graph while keeping it stable. Determine the maximum number of edges Hongcow can add.

Input

The first line of input will contain three integers n, m and k (1 ≤ n ≤ 1 000, 0 ≤ m ≤ 100 000, 1 ≤ k ≤ n) — the number of vertices and edges in the graph, and the number of vertices that are homes of the government. 

The next line of input will contain k integers c1, c2, ..., ck (1 ≤ ci ≤ n). These integers will be pairwise distinct and denote the nodes that are home to the governments in this world.

The following m lines of input will contain two integers ui and vi (1 ≤ ui, vi ≤ n). This denotes an undirected edge between nodes ui and vi.

It is guaranteed that the graph described by the input is stable.

Output

Output a single integer, the maximum number of edges Hongcow can add to the graph while keeping it stable.

Examples

Input

4 1 2
1 3
1 2


Output

2


Input

3 3 1
2
1 2
1 3
2 3


Output

0

Note

For the first sample test, the graph looks like this: 

<image> Vertices 1 and 3 are special. The optimal solution is to connect vertex 4 to vertices 1 and 2. This adds a total of 2 edges. We cannot add any more edges, since vertices 1 and 3 cannot have any path between them.

For the second sample test, the graph looks like this: 

<image> We cannot add any more edges to this graph. Note that we are not allowed to add self-loops, and the graph must be simple.

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;
int visited[1005];
int main() {
  int n, m, k;
  int ret = 0;
  int nbvmax = 0;
  cin >> n >> m >> k;
  vector<int> gov;
  vector<vector<int> > graph(n);
  memset(visited, 0, sizeof visited);
  for (int i = 0; i < k; i++) {
    int a;
    cin >> a;
    a--;
    gov.push_back(a);
  }
  for (int i = 0; i < m; i++) {
    int c1, c2;
    cin >> c1 >> c2;
    c1--;
    c2--;
    graph[c1].push_back(c2);
    graph[c2].push_back(c1);
  }
  for (int i = 0; i < gov.size(); i++) {
    int nbedge = 0;
    int nbver = 1;
    int g = gov[i];
    queue<int> Q;
    Q.push(g);
    visited[g] = 1;
    while (!Q.empty()) {
      int d = Q.front();
      Q.pop();
      for (int j = 0; j < graph[d].size(); j++) {
        nbedge++;
        if (!visited[graph[d][j]]) {
          visited[graph[d][j]] = 1;
          Q.push(graph[d][j]);
          nbver++;
        }
      }
    }
    nbedge = nbedge / 2;
    if (nbver > 1)
      ret += nbver - 1 + ((nbver - 1) * (nbver - 2)) / 2;
    else
      ret += nbver - 1;
    ret -= nbedge;
    nbvmax = max(nbvmax, nbver);
  }
  int cc = 0;
  int edgeplus = 0;
  for (int i = 0; i < n; i++) {
    if (visited[i] == 0) {
      cc++;
      for (int j = 0; j < graph[i].size(); j++) {
        if (!visited[graph[i][j]]) edgeplus++;
      }
    }
  }
  edgeplus /= 2;
  ret += cc * nbvmax;
  if (cc > 1) ret += (cc * (cc - 1)) / 2;
  ret -= edgeplus;
  cout << ret << endl;
}

```

# Example 3

## Problem
Valera conducts experiments with algorithms that search for shortest paths. He has recently studied the Floyd's algorithm, so it's time to work with it.

Valera's already written the code that counts the shortest distance between any pair of vertexes in a non-directed connected graph from n vertexes and m edges, containing no loops and multiple edges. Besides, Valera's decided to mark part of the vertexes. He's marked exactly k vertexes a1, a2, ..., ak.

Valera's code is given below.
    
    
      
    ans[i][j] // the shortest distance for a pair of vertexes i, j  
    a[i]  // vertexes, marked by Valera  
      
    for(i = 1; i <= n; i++) {  
        for(j = 1; j <= n; j++) {  
            if (i == j)  
                ans[i][j] = 0;  
            else  
                ans[i][j] = INF;  //INF is a very large number   
        }  
    }      
      
    for(i = 1; i <= m; i++) {  
        read a pair of vertexes u, v that have a non-directed edge between them;  
        ans[u][v] = 1;  
        ans[v][u] = 1;  
    }  
      
    for (i = 1; i <= k; i++) {  
        v = a[i];  
        for(j = 1; j <= n; j++)  
            for(r = 1; r <= n; r++)  
                ans[j][r] = min(ans[j][r], ans[j][v] + ans[v][r]);  
    }  
    

Valera has seen that his code is wrong. Help the boy. Given the set of marked vertexes a1, a2, ..., ak, find such non-directed connected graph, consisting of n vertexes and m edges, for which Valera's code counts the wrong shortest distance for at least one pair of vertexes (i, j). Valera is really keen to get a graph without any loops and multiple edges. If no such graph exists, print -1.

Input

The first line of the input contains three integers n, m, k (3 ≤ n ≤ 300, 2 ≤ k ≤ n , <image>) — the number of vertexes, the number of edges and the number of marked vertexes. 

The second line of the input contains k space-separated integers a1, a2, ... ak (1 ≤ ai ≤ n) — the numbers of the marked vertexes. It is guaranteed that all numbers ai are distinct.

Output

If the graph doesn't exist, print -1 on a single line. Otherwise, print m lines, each containing two integers u, v — the description of the edges of the graph Valera's been looking for.

Examples

Input

3 2 2
1 2


Output

1 3
2 3


Input

3 3 2
1 2


Output

-1

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;
int n, m, k;
bool marked[305];
int a, b;
vector<pair<int, int> > edges;
int main() {
  scanf("%d %d %d", &n, &m, &k);
  scanf("%d %d", &a, &b);
  marked[a] = marked[b] = true;
  for (int i = 2; i < k; i++) {
    int t;
    scanf("%d", &t);
    marked[t] = true;
  }
  if (k == n) {
    printf("-1\n");
    return 0;
  }
  int center;
  for (int i = 1; i <= n; i++) {
    if (!marked[i]) {
      center = i;
      break;
    }
  }
  for (int i = 1; i <= n; i++) {
    if (i != a && i != b) {
      edges.push_back(make_pair(a, i));
    }
  }
  edges.push_back(make_pair(b, center));
  if (edges.size() < m) {
    for (int i = 1; i <= n - 1; i++) {
      for (int j = i + 1; j <= n; j++) {
        if (i != a && j != a) {
          if (i == b || j == b) {
            if (i != center && j != center && !(marked[i] && marked[j])) {
              edges.push_back(make_pair(i, j));
            }
          } else {
            edges.push_back(make_pair(i, j));
          }
          if (edges.size() == m) break;
        }
      }
      if (edges.size() == m) break;
    }
  }
  if (edges.size() < m) {
    printf("-1\n");
    return 0;
  } else {
    for (int i = 0; i < edges.size(); i++) {
      printf("%d %d\n", edges[i].first, edges[i].second);
    }
  }
  return 0;
}

```

# Example 4

## Problem
Jzzhu is the president of country A. There are n cities numbered from 1 to n in his country. City 1 is the capital of A. Also there are m roads connecting the cities. One can go from city ui to vi (and vise versa) using the i-th road, the length of this road is xi. Finally, there are k train routes in the country. One can use the i-th train route to go from capital of the country to city si (and vise versa), the length of this route is yi.

Jzzhu doesn't want to waste the money of the country, so he is going to close some of the train routes. Please tell Jzzhu the maximum number of the train routes which can be closed under the following condition: the length of the shortest path from every city to the capital mustn't change.

Input

The first line contains three integers n, m, k (2 ≤ n ≤ 105; 1 ≤ m ≤ 3·105; 1 ≤ k ≤ 105).

Each of the next m lines contains three integers ui, vi, xi (1 ≤ ui, vi ≤ n; ui ≠ vi; 1 ≤ xi ≤ 109).

Each of the next k lines contains two integers si and yi (2 ≤ si ≤ n; 1 ≤ yi ≤ 109).

It is guaranteed that there is at least one way from every city to the capital. Note, that there can be multiple roads between two cities. Also, there can be multiple routes going to the same city from the capital.

Output

Output a single integer representing the maximum number of the train routes which can be closed.

Examples

Input

5 5 3
1 2 1
2 3 2
1 3 3
3 4 4
1 5 5
3 5
4 5
5 5


Output

2


Input

2 2 3
1 2 2
2 1 3
2 1
2 2
2 3


Output

2

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;
const int N = 100001;
const long long MAX = 123456897213124;
int n, m, k, ans;
vector<pair<int, long long> > a[N];
priority_queue<pair<long long, int> > q;
bool Visited[N];
int main() {
  ios_base::sync_with_stdio(0);
  cin >> n >> m >> k;
  for (int i = 1; i <= m; i++) {
    int u, v;
    long long x;
    cin >> u >> v >> x;
    a[u].push_back(make_pair(v, x));
    a[v].push_back(make_pair(u, x));
  }
  for (int i = 1; i <= k; i++) {
    int u;
    long long x;
    cin >> u >> x;
    q.push(make_pair(-x, u - N));
  }
  q.push(make_pair(0, 1));
  while (!q.empty()) {
    pair<long long, int> u = q.top();
    q.pop();
    if (u.second < 0) {
      u.second += N;
      if (Visited[u.second]) ans++;
    }
    if (Visited[u.second]) continue;
    Visited[u.second] = 1;
    for (int i = 0; i < (int)a[u.second].size(); i++)
      q.push(make_pair(u.first - a[u.second][i].second, a[u.second][i].first));
  }
  cout << ans;
  return 0;
}

```

# Example 5

## Problem
Little town Nsk consists of n junctions connected by m bidirectional roads. Each road connects two distinct junctions and no two roads connect the same pair of junctions. It is possible to get from any junction to any other junction by these roads. The distance between two junctions is equal to the minimum possible number of roads on a path between them.

In order to improve the transportation system, the city council asks mayor to build one new road. The problem is that the mayor has just bought a wonderful new car and he really enjoys a ride from his home, located near junction s to work located near junction t. Thus, he wants to build a new road in such a way that the distance between these two junctions won't decrease. 

You are assigned a task to compute the number of pairs of junctions that are not connected by the road, such that if the new road between these two junctions is built the distance between s and t won't decrease.

Input

The firt line of the input contains integers n, m, s and t (2 ≤ n ≤ 1000, 1 ≤ m ≤ 1000, 1 ≤ s, t ≤ n, s ≠ t) — the number of junctions and the number of roads in Nsk, as well as the indices of junctions where mayors home and work are located respectively. The i-th of the following m lines contains two integers ui and vi (1 ≤ ui, vi ≤ n, ui ≠ vi), meaning that this road connects junctions ui and vi directly. It is guaranteed that there is a path between any two junctions and no two roads connect the same pair of junctions.

Output

Print one integer — the number of pairs of junctions not connected by a direct road, such that building a road between these two junctions won't decrease the distance between junctions s and t.

Examples

Input

5 4 1 5
1 2
2 3
3 4
4 5


Output

0


Input

5 4 3 5
1 2
2 3
3 4
4 5


Output

5


Input

5 6 1 5
1 2
1 3
1 4
4 5
3 5
2 5


Output

3

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;
int main() {
  ios_base::sync_with_stdio(false);
  cin.tie(0), cout.tie(0);
  int i, j, k;
  int n, m, s, t;
  cin >> n >> m >> s >> t;
  vector<vector<int>> g(n + 1, vector<int>());
  for (i = 0; i < m; i++) {
    int x, y;
    cin >> x >> y;
    g[x].push_back(y);
    g[y].push_back(x);
  }
  queue<int> q;
  vector<int> vis(n + 1, -1);
  vector<int> a(n + 1, 0), b(n + 1, 0);
  vis[s] = 1;
  q.push(s);
  int d = 0;
  while (!q.empty()) {
    int z = q.size();
    while (z--) {
      int x = q.front();
      q.pop();
      a[x] = d;
      for (i = 0; i < g[x].size(); i++) {
        if (vis[g[x][i]] != 1) {
          vis[g[x][i]] = 1;
          q.push(g[x][i]);
        }
      }
    }
    d++;
  }
  queue<int> q1;
  vector<int> vis1(n + 1, -1);
  vis1[t] = 1;
  q1.push(t);
  d = 0;
  while (!q1.empty()) {
    int z = q1.size();
    while (z--) {
      int x = q1.front();
      q1.pop();
      b[x] = d;
      for (i = 0; i < g[x].size(); i++) {
        if (vis1[g[x][i]] != 1) {
          vis1[g[x][i]] = 1;
          q1.push(g[x][i]);
        }
      }
    }
    d++;
  }
  int c = 0;
  int min = a[t];
  for (i = 1; i <= n; i++) {
    for (j = i + 1; j <= n; j++) {
      int f = 0;
      for (k = 0; k < g[i].size(); k++) {
        if (g[i][k] == j) {
          f = 1;
          break;
        }
      }
      if (f == 1) continue;
      if (a[i] + b[j] + 1 >= min && a[j] + b[i] + 1 >= min) {
        c++;
      }
    }
  }
  cout << c;
  return 0;
}

```