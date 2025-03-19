#include <bits/stdc++.h>
using namespace std;

/* 
   This unified solution supports five different problems.
   The first integer in the input tells which problem to solve:
      1 : Trip Planning
      2 : Train Routes
      3 : Grid Running
      4 : Socks Repainting
      5 : Ski Resort
   Each problem’s input then follows.
   Common functionality is refactored into smaller helper functions.
*/

/* ---------------- Problem 1: Trip Planning ----------------
   There are n persons with friendship connections added over m days.
   A person is “removed” (cannot go on a trip) if his friend‐count is below k.
   We simulate the removal process (and its propagation) and then “undo” the 
   friend‐additions in reverse order.
*/
 
// Propagate removal from vertex 'start' (0-indexed).
// It decrements the current count (currCount) as persons become removed.
void propagateRemoval(int start, int k, vector<int> &deg, vector<bool> &removed, 
                      vector<vector<int>> &friends, int &currCount) {
    queue<int> q;
    q.push(start);
    removed[start] = true;
    currCount--;
    while(!q.empty()){
        int u = q.front(); q.pop();
        for(auto v : friends[u]){
            if(!removed[v]){
                deg[v]--;
                if(deg[v] < k) {
                    removed[v] = true;
                    currCount--;
                    q.push(v);
                }
            }
        }
    }
}
 
void solveProblem1(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int n, m, k;
    cin >> n >> m >> k;
    // persons are indexed 0..n-1.
    vector<pair<int,int>> edges(m);
    vector<vector<int>> friends(n);
    vector<int> deg(n,0);
    
    for (int i = 0; i < m; i++){
        int u, v; 
        cin >> u >> v;
        u--; v--;
        edges[i] = {u, v};
        deg[u]++; deg[v]++;
        friends[u].push_back(v);
        friends[v].push_back(u);
    }
    
    int currCount = n;
    vector<bool> removed(n, false);
    // Initial removal round: remove any person with degree < k.
    for (int i = 0; i < n; i++){
        if(!removed[i] && deg[i] < k){
            propagateRemoval(i, k, deg, removed, friends, currCount);
        }
    }
    
    // ans[i] will store answer for day i (starting indexing at 1 for output)
    vector<int> ans(m+1, 0);
    ans[m] = currCount;
    // Process days in reverse order (undo each edge addition)
    for (int i = m-1; i >= 0; i--){
        int u = edges[i].first, v = edges[i].second;
        // "Remove" the edge: update degree if vertex is still live.
        if(!removed[u])
            deg[v]--;
        if(!removed[v])
            deg[u]--;
        // Also remove the edge from the friend list (pop_back because insertion order is preserved).
        friends[u].pop_back();
        friends[v].pop_back();
 
        // Check if this removal causes either vertex to lose enough friends.
        if(!removed[u] && deg[u] < k) {
            propagateRemoval(u, k, deg, removed, friends, currCount);
        }
        if(!removed[v] && deg[v] < k) {
            propagateRemoval(v, k, deg, removed, friends, currCount);
        }
        ans[i] = currCount;
    }
    // Print result: one answer per day (starting from day 1)
    for (int i = 1; i <= m; i++){
        cout << ans[i] << "\n";
    }
}

/* ---------------- Problem 2: Train Routes ----------------
   We wish to close maximum redundant train routes. We compute shortest distances 
   from the capital (node 1) using both roads and trains.
   To distinguish train routes from roads, we encode the node id as negative (with offset).
   (This solution mimics the provided solution using a modified Dijkstra.)
*/
 
void solveProblem2(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int n, m, k;
    cin >> n >> m >> k;
    // Build graph for roads: 1-indexed.
    vector<vector<pair<int, long long>>> graph(n+1);
    for (int i = 0; i < m; i++){
        int u, v; 
        long long w;
        cin >> u >> v >> w;
        graph[u].push_back({v, w});
        graph[v].push_back({u, w});
    }
    // Priority queue stores pairs: (negative distance, marker)
    // For train routes, we encode node as (s - OFFSET) to mark them.
    const int OFFSET = 100001; // chosen > n
    priority_queue<pair<long long,int>> pq;
    for (int i = 0; i < k; i++){
        int s; 
        long long y;
        cin >> s >> y;
        pq.push({-y, s - OFFSET});
    }
    // Also push the capital (node 1) with distance 0.
    pq.push({0, 1});
 
    vector<bool> used(n+1, false);
    int ans = 0;
    while(!pq.empty()){
        auto cur = pq.top(); pq.pop();
        int node;
        long long d = cur.first; // negative distance
        bool isTrain = false;
        if(cur.second < 0) {
            node = cur.second + OFFSET;
            isTrain = true;
            if(used[node]) { 
                ans++; 
                continue;
            }
        } else {
            node = cur.second;
        }
        if(used[node]) continue;
        used[node] = true;
        for(auto &edge : graph[node]){
            int nxt = edge.first;
            long long nd = d - edge.second; // update negative distance
            if(used[nxt]) continue;
            pq.push({nd, nxt});
        }
    }
    cout << ans << "\n";
}

/* ---------------- Problem 3: Grid Running ----------------
   Olya needs to move from (sx,sy) to (ex,ey) in a grid.
   In one second she can “run” 1 to k cells in one fixed direction (only through empty cells).
   We run a standard multi–step BFS.
*/
 
void solveProblem3(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int n, m, k;
    cin >> n >> m >> k;
    vector<string> grid(n);
    for (int i = 0; i < n; i++){
        cin >> grid[i];
    }
    int sx, sy, ex, ey;
    cin >> sx >> sy >> ex >> ey;
    sx--; sy--; ex--; ey--;
    
    const int INF = 1e9;
    vector<vector<int>> dist(n, vector<int>(m, INF));
    deque<pair<int,int>> dq;
    dist[sx][sy] = 0;
    dq.push_back({sx,sy});
    
    // Four possible directions: up, down, left, right.
    int dx[4] = {-1,1,0,0}, dy[4] = {0,0,-1,1};
    while(!dq.empty()){
        auto cur = dq.front();
        dq.pop_front();
        int cx = cur.first, cy = cur.second;
        int currStep = dist[cx][cy];
        for (int d = 0; d < 4; d++){
            for (int step = 1; step <= k; step++){
                int nx = cx + dx[d]*step, ny = cy + dy[d]*step;
                if(nx < 0 || nx >= n || ny < 0 || ny >= m) break;
                if(grid[nx][ny] == '#') break;
                if(dist[nx][ny] < currStep + 1) break;
                if(dist[nx][ny] == currStep + 1) continue;
                dist[nx][ny] = currStep + 1;
                dq.push_back({nx,ny});
            }
        }
    }
    cout << (dist[ex][ey] == INF ? -1 : dist[ex][ey]) << "\n";
}

/* ---------------- Problem 4: Socks Repainting ----------------
   We have n socks with initial colors and m days’ instructions which pair up socks.
   We use DSU (union–find) to group all socks required together and, in each component,
   we repaint all socks to the majority color.
*/
 
struct DSU {
    vector<int> parent, size;
    DSU(int n) {
        parent.resize(n); size.resize(n,1);
        for(int i = 0; i < n; i++) parent[i] = i;
    }
    int findp(int a) {
        return parent[a] == a ? a : parent[a] = findp(parent[a]);
    }
    void unite(int a, int b){
        a = findp(a), b = findp(b);
        if(a == b) return;
        if(size[a] < size[b]) swap(a, b);
        parent[b] = a;
        size[a] += size[b];
    }
};
 
void solveProblem4(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int n, m, k;
    cin >> n >> m >> k;
    vector<int> colors(n);
    for (int i = 0; i < n; i++){
        cin >> colors[i];
    }
    DSU dsu(n);
    for (int i = 0; i < m; i++){
        int u, v;
        cin >> u >> v;
        dsu.unite(u-1, v-1);
    }
    // Gather socks by their component.
    unordered_map<int, vector<int>> comp;
    for (int i = 0; i < n; i++){
        comp[ dsu.findp(i) ].push_back(i);
    }
    long long ans = 0;
    for(auto &entry : comp){
        unordered_map<int,int> freq;
        int compSize = entry.second.size();
        int maxFreq = 0;
        for(auto idx : entry.second){
            freq[ colors[idx] ]++;
            maxFreq = max(maxFreq, freq[ colors[idx] ]);
        }
        ans += (compSize - maxFreq);
    }
    cout << ans << "\n";
}

/* ---------------- Problem 5: Ski Resort ----------------
   The ski resort consists of n landing spots and m directed tracks (each from a lower–numbered spot to a higher–numbered spot).
   A dangerous path is one that uses at least two tracks.
   We wish to close some spots (remove all incident tracks) so that no dangerous path remains,
   while closing at most (4/7) * n spots. One valid greedy solution is given below.
*/
 
void solveProblem5(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int t;
    cin >> t;
    while(t--){
        int n, m;
        cin >> n >> m;
        // For each spot 1-indexed, record incoming edges.
        vector<vector<int>> incoming(n+1);
        vector<int> closed(n+1, 0);
        for (int i = 0; i < m; i++){
            int u, v; 
            cin >> u >> v;
            incoming[v].push_back(u);
        }
        vector<int> ans;
        // For every spot, check if it can be the end of a dangerous (>=2 track) path using open spots.
        for (int i = 1; i <= n; i++){
            bool needClose = false;
            for (int j : incoming[i]){
                if(closed[j]) continue;
                for (int k : incoming[j]){
                    if(!closed[k]){
                        needClose = true;
                        break;
                    }
                }
                if(needClose) break;
            }
            if(needClose){
                closed[i] = 1;
                ans.push_back(i);
            }
        }
        cout << ans.size() << "\n";
        for(auto spot : ans)
            cout << spot << " ";
        cout << "\n";
    }
}
 
/* ---------------- Main ----------------
   It reads the problem number and calls the corresponding solver.
 */
 
int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int problem;
    cin >> problem;
    switch(problem){
        case 1:
            solveProblem1();
            break;
        case 2:
            solveProblem2();
            break;
        case 3:
            solveProblem3();
            break;
        case 4:
            solveProblem4();
            break;
        case 5:
            solveProblem5();
            break;
        default:
            // Unknown problem number.
            break;
    }
    return 0;
}