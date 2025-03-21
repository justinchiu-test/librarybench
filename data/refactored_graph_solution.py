#include <bits/stdc++.h>
using namespace std;
 
// ------------------------------
// Global constants
const long long LINF = 1e18;
const int INF = 0x3f3f3f3f;
 
// --------------------------------------------------------
// Common Minimum Cost Flow structure used for Problems 1 and 2
struct Edge {
    int to, rev;
    int cap;
    long long cost;
    int flow;
};
 
struct MCMF {
    int n, source, sink;
    vector<vector<Edge>> adj;
    MCMF(int n, int source, int sink): n(n), source(source), sink(sink) {
        adj.resize(n);
    }
    void addEdge(int u, int v, int cap, long long cost) {
        Edge a = {v, (int)adj[v].size(), cap, cost, 0};
        Edge b = {u, (int)adj[u].size(), 0, -cost, 0};
        adj[u].push_back(a);
        adj[v].push_back(b);
    }
 
    // Returns pair {totalCost, totalFlow}
    pair<long long, int> minCostMaxFlow() {
        long long totCost = 0;
        int totFlow = 0;
        while (true) {
            vector<long long> dist(n, LINF);
            vector<int> parent(n, -1), parentEdge(n, -1);
            vector<int> inQueue(n, 0);
            dist[source] = 0;
            queue<int> q;
            q.push(source);
            inQueue[source] = 1;
            while(!q.empty()){
                int u = q.front();
                q.pop();
                inQueue[u] = 0;
                for (int i = 0; i < adj[u].size(); i++){
                    Edge &e = adj[u][i];
                    if(e.cap > e.flow && dist[e.to] > dist[u] + e.cost) {
                        dist[e.to] = dist[u] + e.cost;
                        parent[e.to] = u;
                        parentEdge[e.to] = i;
                        if(!inQueue[e.to]){
                            q.push(e.to);
                            inQueue[e.to] = 1;
                        }
                    }
                }
            }
            if(dist[sink] == LINF) break;
            int pushFlow = INF;
            int v = sink;
            while(v != source){
                int u = parent[v];
                int idx = parentEdge[v];
                pushFlow = min(pushFlow, adj[u][idx].cap - adj[u][idx].flow);
                v = u;
            }
            v = sink;
            while(v != source){
                int u = parent[v];
                int idx = parentEdge[v];
                adj[u][idx].flow += pushFlow;
                adj[v][adj[u][idx].rev].flow -= pushFlow;
                v = u;
            }
            totFlow += pushFlow;
            totCost += (long long) pushFlow * dist[sink];
        }
        return make_pair(totCost, totFlow);
    }
};
 
// ------------------------------
// Problem 1: Scheduling tasks on machines (using MCMF)
// Input: first line after problem id: n k, then n lines each: s t c
// Output: n numbers (0/1) indicating which task is executed.
void solveProblem1(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k;
    cin >> n >> k;
    struct Task { long long s, t, c, end; };
    vector<Task> tasks(n);
    for (int i = 0; i < n; i++){
        cin >> tasks[i].s >> tasks[i].t >> tasks[i].c;
        tasks[i].end = tasks[i].s + tasks[i].t - 1;
    }
    // Nodes:
    // source = 0
    // machine nodes: 1..k
    // For each task i, two nodes:
    //    part1 node: index = k + 1 + i
    //    part2 node: index = k + n + 1 + i
    // sink: index = k + 2*n + 1
    int source = 0;
    int machineStart = 1;
    int taskPart1Start = machineStart + k;
    int taskPart2Start = taskPart1Start + n;
    int sink = taskPart2Start + n;
    int totNodes = sink + 1;
    MCMF mcmf(totNodes, source, sink);
    // Source -> each machine node (cap=1)
    for (int i = 0; i < k; i++){
        mcmf.addEdge(source, machineStart + i, 1, 0);
    }
    int bigCap = 1000000000;
    // Each machine -> every task part1 node (cap = bigCap)
    for (int i = 0; i < k; i++){
        for (int j = 0; j < n; j++){
            mcmf.addEdge(machineStart + i, taskPart1Start + j, bigCap, 0);
        }
    }
    // For each task, add internal edge from its part1 to part2 (cap=1, cost=-profit)
    vector<pair<int,int>> taskEdgeIndex(n);
    for (int i = 0; i < n; i++){
        int u = taskPart1Start + i, v = taskPart2Start + i;
        int beforeSize = mcmf.adj[u].size();
        mcmf.addEdge(u, v, 1, -tasks[i].c);
        taskEdgeIndex[i] = {u, beforeSize}; // to later check if assigned
        // Connect part2 node -> sink (cap=1)
        mcmf.addEdge(v, sink, 1, 0);
    }
    // For every pair of distinct tasks (i, j), if task i finishes before j starts, connect:
    for (int i = 0; i < n; i++){
        for (int j = 0; j < n; j++){
            if(i==j) continue;
            if(tasks[i].end < tasks[j].s){
                int u = taskPart2Start + i;
                int v = taskPart1Start + j;
                mcmf.addEdge(u, v, 1, 0);
            }
        }
    }
    mcmf.minCostMaxFlow(); // run flow
    // Check the internal edge for each task
    vector<int> out(n, 0);
    for (int i = 0; i < n; i++){
        int u = taskEdgeIndex[i].first, idx = taskEdgeIndex[i].second;
        if(mcmf.adj[u][idx].flow > 0)
            out[i] = 1;
        else
            out[i] = 0;
    }
    for (int i = 0; i < n; i++){
        cout << out[i] << (i==n-1 ? "\n" : " ");
    }
}
 
// ------------------------------
// Problem 2: Team Selection (Two teams of sizes p and s)
// Input: first line after problem id: n p s
// then line of n programming skills and line of n sports skills.
// Output: maximum total strength, then one line listing programming team members, next line for sports team.
void solveProblem2(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, p, s;
    cin >> n >> p >> s;
    vector<int> prog(n), sport(n);
    for (int i = 0; i < n; i++) cin >> prog[i];
    for (int i = 0; i < n; i++) cin >> sport[i];
    // Build network:
    // Nodes: source = 0; programming node = 1; sports node = 2; student nodes = 3..(3+n-1); sink = 3+n.
    int source = 0, progNode = 1, sportNode = 2;
    int studentStart = 3, sink = studentStart + n;
    int totNodes = sink + 1;
    MCMF mcmf(totNodes, source, sink);
    mcmf.addEdge(source, progNode, p, 0);
    mcmf.addEdge(source, sportNode, s, 0);
    for (int i = 0; i < n; i++){
        mcmf.addEdge(progNode, studentStart + i, 1, -prog[i]);
        mcmf.addEdge(sportNode, studentStart + i, 1, -sport[i]);
        mcmf.addEdge(studentStart + i, sink, 1, 0);
    }
    auto res = mcmf.minCostMaxFlow();
    long long totalStrength = -res.first; // because we used negative cost edges
    vector<int> progTeam, sportTeam;
    for (auto &e : mcmf.adj[progNode]){
        if(e.to >= studentStart && e.to < studentStart+n && e.flow > 0){
            progTeam.push_back(e.to - studentStart + 1);
        }
    }
    for (auto &e : mcmf.adj[sportNode]){
        if(e.to >= studentStart && e.to < studentStart+n && e.flow > 0){
            sportTeam.push_back(e.to - studentStart + 1);
        }
    }
    cout << totalStrength << "\n";
    for (int i = 0; i < progTeam.size(); i++){
        cout << progTeam[i] << (i==progTeam.size()-1 ? "\n" : " ");
    }
    for (int i = 0; i < sportTeam.size(); i++){
        cout << sportTeam[i] << (i==sportTeam.size()-1 ? "\n" : " ");
    }
}
 
// ------------------------------
// Problem 3: Minimizing penalty while printing a sequence
// Given n numbers and m variables, we want to produce a program (assignments & prints)
// whose penalty (sum of set bits in assignments) is minimized.
// This solution uses a min-cost flow styled SPFA algorithm on a custom graph.
 
// Global arrays for Problem 3 (maximum nodes set to 600, edges 70000)
const int MAXV3 = 600, MAXE3 = 70000;
int G3[MAXV3];
int Queue3[MAXV3], Dist3[MAXV3], Pre3[MAXE3], Last3Arr[MAXV3];
int Data3[MAXE3], Weight3[MAXE3], Cost3[MAXE3], Next3[MAXE3];
bool Flag3[MAXV3];
int Count3;
 
int CalcCost (int x){
    if(x == 0) return 0;
    return (x & 1) + CalcCost(x >> 1);
}
 
void AddEdge3(int num, int u, int v, int w, int c) {
    Data3[num] = v;
    Weight3[num] = w;
    Cost3[num] = c;
    Next3[num] = G3[u];
    G3[u] = num;
}
 
void Connect3(int u, int v, int w, int c) {
    AddEdge3(Count3++, u, v, w, c);
    AddEdge3(Count3++, v, u, 0, -c);
}
 
int SPFA3(int S, int T, int totalNodes) {
    for (int i = 0; i < totalNodes; i++){
        Dist3[i] = INF;
        Flag3[i] = false;
    }
    queue<int> q;
    q.push(S);
    Dist3[S] = 0;
    Pre3[S] = -1;
    Flag3[S] = true;
    while(!q.empty()){
        int u = q.front();
        q.pop();
        Flag3[u] = false;
        for (int p = G3[u]; p != -1; p = Next3[p]){
            int v = Data3[p];
            if(Weight3[p] > 0 && Dist3[u] + Cost3[p] < Dist3[v]){
                Dist3[v] = Dist3[u] + Cost3[p];
                Pre3[v] = p;
                if(!Flag3[v]){
                    Flag3[v] = true;
                    q.push(v);
                }
            }
        }
    }
    if(Dist3[T] == INF) return -1;
    int v = T;
    while(v != S){
        int idx = Pre3[v];
        Weight3[idx]--;
        Weight3[idx^1]++;
        v = Data3[idx^1];
    }
    return Dist3[T];
}
 
// solveProblem3 builds the flow network and then constructs a program.
void solveProblem3(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, mVar;
    cin >> n >> mVar;
    vector<int> A(n);
    for (int i = 0; i < n; i++){
        cin >> A[i];
    }
    // Let N = n; then define nodes:
    // S = 2*n + 1, T = 2*n + 2; total nodes = T+1.
    int N = n;
    int S = 2 * N + 1, T = 2 * N + 2;
    int totalNodes = T + 1;
    for (int i = 0; i < totalNodes; i++){
        G3[i] = -1;
    }
    Count3 = 0;
    // Build network as described.
    for (int i = 0; i < N; i++){
        Connect3(S, i, 1, 0);
    }
    Connect3(S, N, mVar, 0);
    for (int i = 0; i < N; i++){
        for (int j = i+1; j < N; j++){
            if(A[i] == A[j])
                Connect3(i, N + j + 1, 1, 0);
            else
                Connect3(i, N + j + 1, 1, CalcCost(A[j]));
        }
    }
    for (int i = 0; i < N; i++){
        Connect3(N, N + i + 1, 1, CalcCost(A[i]));
    }
    for (int i = 1; i <= N; i++){
        Connect3(N + i, T, 1, 0);
    }
    int Ans = 0;
    while (SPFA3(S, T, totalNodes) != -1)
        Ans += Dist3[T];
 
    // Reconstruct an array Last: for each printed number i, record the predecessor
    vector<int> Last(N, N);
    for (int i = 0; i < N; i++){
        for (int p = G3[i]; p != -1; p = Next3[p]){
            int v = Data3[p];
            if(v >= N+1 && v <= 2*N && Weight3[p] == 0) {
                int j = v - N - 1;
                Last[j] = i;
            }
        }
    }
    int totalLines = N;
    for (int i = 0; i < N; i++){
        if(Last[i] == N || (Last[i] < N && A[Last[i]] != A[i]))
            totalLines++;
    }
    cout << totalLines << " " << Ans << "\n";
    vector<int> Var(N, -1);
    int varCount = 0;
    for (int i = 0; i < N; i++){
        if(Last[i] == N) {
            Var[i] = varCount++;
            char varName = 'a' + Var[i];
            cout << varName << "=" << A[i] << "\n";
            cout << "print(" << varName << ")\n";
        } else {
            if(A[i] == A[Last[i]]) {
                Var[i] = Var[Last[i]];
                char varName = 'a' + Var[i];
                cout << "print(" << varName << ")\n";
            } else {
                Var[i] = Var[Last[i]];
                char varName = 'a' + Var[i];
                cout << varName << "=" << A[i] << "\n";
                cout << "print(" << varName << ")\n";
            }
        }
    }
}
 
// ------------------------------
// Problem 4: Farmer John's road delay increases
// The graph is given by n,m then m edges, then q queries
// For each query (an integer x) output maximum possible delay for shortest path.
 
struct EdgeP4 {
    int to, nxt, w, cost;
};
 
const int MAXP4 = 100005;
EdgeP4 e4[MAXP4];
int head4[100005];
int tot4;
int dis4[100005], pre4[100005], lste4[100005], flow4[100005];
bool inq4[100005];
 
void addEdgeP4(int u, int v, int cap, int cost) {
    e4[++tot4] = {v, head4[u], cap, cost};
    head4[u] = tot4;
}
 
void addP4(int u, int v, int cap, int cost) {
    addEdgeP4(u, v, cap, cost);
    addEdgeP4(v, u, 0, -cost);
}
 
bool spfaP4(int s, int t, int n) {
    for (int i = 0; i <= n; i++){
        dis4[i] = INF;
        flow4[i] = INF;
        inq4[i] = false;
    }
    dis4[s] = 0;
    pre4[t] = -1;
    deque<int> dq;
    dq.push_back(s);
    inq4[s] = true;
    while(!dq.empty()){
        int u = dq.front();
        dq.pop_front();
        inq4[u] = false;
        for (int i = head4[u]; i != -1; i = e4[i].nxt) {
            int v = e4[i].to;
            if(e4[i].w > 0 && dis4[v] > dis4[u] + e4[i].cost){
                dis4[v] = dis4[u] + e4[i].cost;
                pre4[v] = u;
                lste4[v] = i;
                flow4[v] = min(flow4[u], e4[i].w);
                if(!inq4[v]){
                    inq4[v] = true;
                    dq.push_back(v);
                }
            }
        }
    }
    return pre4[t] != -1;
}
 
void solveProblem4(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    memset(head4, -1, sizeof(head4));
    tot4 = 1;
    for (int i = 1; i <= m; i++){
        int u, v, w;
        cin >> u >> v >> w;
        addP4(u, v, 1, w);
    }
    int Q;
    cin >> Q;
    long long maxflow = 0, mincost = 0;
    vector<pair<double,double>> vp;
    int s = 1, t = n;
    while(spfaP4(s, t, n)){
        int f = flow4[t];
        maxflow += f;
        mincost += f * dis4[t];
        vp.push_back({(double)maxflow, (double)mincost});
        int cur = t;
        while(cur != s){
            int i = lste4[cur];
            e4[i].w -= f;
            e4[i^1].w += f;
            cur = pre4[cur];
        }
    }
    while(Q--){
        int x;
        cin >> x;
        double res = 1e18;
        for (int i = 0; i < vp.size(); i++){
            res = min(res, (vp[i].second + x) / vp[i].first);
        }
        cout << fixed << setprecision(10) << res << "\n";
    }
}
 
// ------------------------------
// Problem 5: Maximum water flow with capacity increases
// Input: n k then an n x n matrix describing pipes.
 
const int MAXN5 = 55;
int head5[MAXN5];
int to5[10000], cap5[10000], cost5[10000], prv5[10000];
int M5;
int A5[MAXN5][MAXN5];
 
int dist5[MAXN5], f5[MAXN5];
bool inq5[MAXN5];
int Q5[1000], L5, R5;
 
void add_edge5(int u, int v, int c, int w) {
    to5[M5] = v; cap5[M5] = c; cost5[M5] = w; prv5[M5] = head5[u];
    head5[u] = M5++;
}
 
void add5(int u, int v, int c, int w) {
    add_edge5(u, v, c, w);
    add_edge5(v, u, 0, -w);
}
 
bool spfa5(int s, int t, int n) {
    for (int i = 0; i <= n; i++){
        dist5[i] = INF;
        inq5[i] = false;
    }
    dist5[s] = 0; f5[s] = INF;
    L5 = R5 = 0;
    Q5[R5++] = s;
    inq5[s] = true;
    while(L5 != R5) {
        int u = Q5[L5++];
        if(L5 == n+1) L5 = 0;
        inq5[u] = false;
        for (int i = head5[u]; i != -1; i = prv5[i]) {
            int v = to5[i];
            if(cap5[i] && dist5[v] > dist5[u] + cost5[i]) {
                dist5[v] = dist5[u] + cost5[i];
                f5[v] = min(f5[u], cap5[i]);
                if(!inq5[v]){
                    inq5[v] = true;
                    Q5[R5++] = v;
                    if(R5 == n+1) R5 = 0;
                }
            }
        }
    }
    return dist5[t] != INF;
}
 
void solveProblem5(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k;
    cin >> n >> k;
    for (int i = 1; i <= n; i++){
        for (int j = 1; j <= n; j++){
            cin >> A5[i][j];
        }
    }
    memset(head5, -1, sizeof(head5));
    M5 = 0;
    // For each positive pipe width, add two edges:
    // one with capacity A5[i][j] (cost 0) and one with capacity k (cost 1)
    for (int i = 1; i <= n; i++){
        for (int j = 1; j <= n; j++){
            if(A5[i][j] > 0){
                add5(i, j, A5[i][j], 0);
                add5(i, j, k, 1);
            }
        }
    }
    int s = 1, t = n;
    int ans = 0;
    while(spfa5(s, t, n)){
        int flow = f5[t];
        if(dist5[t] > 0)
            flow = min(flow, k / dist5[t]);
        if(flow == 0) break;
        int v = t;
        while(v != s){
            // Retrace with a simple predecessor search.
            // (For brevity we re-run a standard augmentation below.)
            // For a proper implementation one would store a predecessor; here we do a simple inline update.
            // We assume spfa5 computed a valid shortest path.
            // (Due to time constraints, we simulate the augmentation.)
            break;
        }
        // Instead, re-run a short augmentation using a temporary predecessor array:
        vector<int> parent(n+1, -1);
        vector<int> parentEdge(n+1, -1);
        for (int i = 0; i <= n; i++){
            dist5[i] = INF;
            inq5[i] = false;
        }
        dist5[s] = 0; f5[s] = INF;
        deque<int> dq;
        dq.push_back(s);
        inq5[s] = true;
        while(!dq.empty()){
            int u = dq.front();
            dq.pop_front();
            inq5[u] = false;
            for (int i = head5[u]; i != -1; i = prv5[i]){
                int v = to5[i];
                if(cap5[i] && dist5[v] > dist5[u] + cost5[i]){
                    dist5[v] = dist5[u] + cost5[i];
                    parent[v] = u;
                    parentEdge[v] = i;
                    f5[v] = min(f5[u], cap5[i]);
                    if(!inq5[v]){
                        inq5[v] = true;
                        dq.push_back(v);
                    }
                }
            }
        }
        if(dist5[t] == INF) break;
        flow = f5[t];
        if(dist5[t] > 0) flow = min(flow, k / dist5[t]);
        v = t;
        while(v != s){
            int i = parentEdge[v];
            cap5[i] -= flow;
            cap5[i^1] += flow;
            v = parent[v];
        }
        ans += flow;
        k -= flow * dist5[t];
    }
    cout << ans << "\n";
}
 
// ------------------------------
// Main: read the first integer to decide which problem to run.
int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int prob;
    cin >> prob;
    if(prob == 1)
        solveProblem1();
    else if(prob == 2)
        solveProblem2();
    else if(prob == 3)
        solveProblem3();
    else if(prob == 4)
        solveProblem4();
    else if(prob == 5)
        solveProblem5();
    return 0;
}