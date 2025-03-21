#include <bits/stdc++.h>
using namespace std;
 
// ---------------------
// Common MCMF code and helpers
// ---------------------
 
// Edge structure used in MCMF.
struct Edge {
    int to, rev, cap;
    long long cost;
    int flow; // for bookkeeping
    Edge(int _to, int _rev, int _cap, long long _cost)
        : to(_to), rev(_rev), cap(_cap), cost(_cost), flow(0) {}
};
 
// Generic Min Cost Flow implementation using SPFA.
struct MinCostFlow {
    int n;
    vector<vector<Edge>> graph;
    vector<long long> dist;
    vector<int> parent, parentEdge;
    const long long INF = 1e18;
 
    MinCostFlow(int _n) : n(_n), graph(_n), dist(_n), parent(_n), parentEdge(_n) {}
 
    void addEdge(int u, int v, int cap, long long cost) {
        graph[u].push_back(Edge(v, (int)graph[v].size(), cap, cost));
        graph[v].push_back(Edge(u, (int)graph[u].size()-1, 0, -cost));
    }
 
    // Computes min–cost max–flow from s to t. Returns {maxFlow, minCost}.
    pair<int,long long> minCostMaxFlow (int s, int t) {
        int flow = 0;
        long long cost = 0;
        while(true){
            fill(dist.begin(), dist.end(), INF);
            vector<bool> inQueue(n, false);
            dist[s] = 0;
            queue<int> q;
            q.push(s);
            inQueue[s] = true;
            while(!q.empty()){
                int u = q.front();
                q.pop();
                inQueue[u] = false;
                for (int i = 0; i < graph[u].size(); i++){
                    Edge &e = graph[u][i];
                    if(e.cap > 0 && dist[e.to] > dist[u] + e.cost) {
                        dist[e.to] = dist[u] + e.cost;
                        parent[e.to] = u;
                        parentEdge[e.to] = i;
                        if(!inQueue[e.to]){
                            inQueue[e.to] = true;
                            q.push(e.to);
                        }
                    }
                }
            }
            if(dist[t] == INF) break;
            int pushFlow = INT_MAX;
            for (int cur = t; cur != s; cur = parent[cur])
                pushFlow = min(pushFlow, graph[parent[cur]][parentEdge[cur]].cap);
            flow += pushFlow;
            cost += pushFlow * dist[t];
            for (int cur = t; cur != s; cur = parent[cur]){
                Edge &e = graph[parent[cur]][parentEdge[cur]];
                e.cap -= pushFlow;
                graph[cur][e.rev].cap += pushFlow;
                e.flow += pushFlow;
                graph[cur][e.rev].flow -= pushFlow;
            }
        }
        return {flow, cost};
    }
 
    // Additional routine: record the sequence of augmentations.
    vector<pair<int,long long>> minCostFlowAugmentations (int s, int t) {
        vector<pair<int,long long>> aug;
        int flow = 0;
        long long cost = 0;
        while(true){
            fill(dist.begin(), dist.end(), INF);
            vector<bool> inQueue(n, false);
            dist[s] = 0;
            queue<int> q;
            q.push(s);
            inQueue[s] = true;
            while(!q.empty()){
                int u = q.front();
                q.pop();
                inQueue[u] = false;
                for (int i = 0; i < graph[u].size(); i++){
                    Edge &e = graph[u][i];
                    if(e.cap > 0 && dist[e.to] > dist[u] + e.cost) {
                        dist[e.to] = dist[u] + e.cost;
                        parent[e.to] = u;
                        parentEdge[e.to] = i;
                        if(!inQueue[e.to]){
                            inQueue[e.to] = true;
                            q.push(e.to);
                        }
                    }
                }
            }
            if(dist[t] == INF) break;
            int pushFlow = INT_MAX;
            for (int cur = t; cur != s; cur = parent[cur])
                pushFlow = min(pushFlow, graph[parent[cur]][parentEdge[cur]].cap);
            flow += pushFlow;
            cost += pushFlow * dist[t];
            aug.push_back({flow, cost});
            for (int cur = t; cur != s; cur = parent[cur]){
                Edge &e = graph[parent[cur]][parentEdge[cur]];
                e.cap -= pushFlow;
                graph[cur][e.rev].cap += pushFlow;
                e.flow += pushFlow;
                graph[cur][e.rev].flow -= pushFlow;
            }
        }
        return aug;
    }
};
 
// A helper to count the number of set bits.
inline int countSetBits(int x) {
    return __builtin_popcount(x);
}
 
// ---------------------
// Problem 1: Task Scheduling (Machines & Tasks)
// ---------------------
 
// Given n tasks (with start s, duration t, profit c) and k machines, schedule a set of tasks 
// (non–overlapping on any machine) to maximize total profit. We output a binary 
// vector of length n indicating which tasks are performed.
void solveProblem1(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
 
    int n, k;
    cin >> n >> k;
    struct Task { int s, t, profit; };
    vector<Task> tasks(n);
    for (int i = 0; i < n; i++){
        cin >> tasks[i].s >> tasks[i].t >> tasks[i].profit;
    }
    // Construct network:
    //   source = 0;
    //   machine nodes: 1 ... k;
    //   task in–nodes: k+1 ... k+n;
    //   task out–nodes: k+n+1 ... k+2*n;
    //   sink = k+2*n+1.
    int source = 0;
    int sink = k + 2*n + 1;
    int totNodes = sink + 1;
    int INF_CAP = 1000000000;
 
    MinCostFlow mcmf(totNodes);
    // Source -> each machine (cap=1, cost=0)
    for (int i = 1; i <= k; i++){
        mcmf.addEdge(source, i, 1, 0);
    }
    // Machine -> every task in–node (cap=INF, cost=0)
    for (int i = 1; i <= k; i++){
        for (int j = 0; j < n; j++){
            mcmf.addEdge(i, k + 1 + j, INF_CAP, 0);
        }
    }
    // For each task j, add an edge from in–node (k+1+j) to out–node (k+n+1+j)
    // with capacity 1 and cost = -profit.
    vector<int> taskEdgeIndex(n, 0);
    for (int j = 0; j < n; j++){
        int curSize = mcmf.graph[k + 1 + j].size();
        mcmf.addEdge(k + 1 + j, k + n + 1 + j, 1, -tasks[j].profit);
        taskEdgeIndex[j] = curSize;
        // Task out–node -> sink.
        mcmf.addEdge(k + n + 1 + j, sink, 1, 0);
    }
    // For each pair of tasks i and j, if task i finishes before task j starts,
    // add an edge from task i’s out–node to task j’s in–node.
    for (int i = 0; i < n; i++){
        int finish_time = tasks[i].s + tasks[i].t - 1;
        for (int j = 0; j < n; j++){
            if(i == j) continue;
            if(finish_time < tasks[j].s)
                mcmf.addEdge(k + n + 1 + i, k + 1 + j, 1, 0);
        }
    }
    auto res = mcmf.minCostMaxFlow(source, sink);
    vector<int> ans(n, 0);
    // For each task j, check the edge from its in–node to out–node.
    for (int j = 0; j < n; j++){
        Edge e = mcmf.graph[k + 1 + j][taskEdgeIndex[j]];
        ans[j] = (e.flow > 0) ? 1 : 0;
    }
    for (int j = 0; j < n; j++){
        cout << ans[j] << " ";
    }
    cout << "\n";
}
 
// ---------------------
// Problem 2: Two Teams (Programming and Sports)
// ---------------------
 
// There are n students; exactly p must go to the programming team and s to the sports team.
// Each student i has two skills (prog[i] and spo[i]) and the combined strength is the sum.
// We construct a flow network to maximize the total sum.
void solveProblem2(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
 
    int n, p, s;
    cin >> n >> p >> s;
    vector<int> prog(n), spo(n);
    for (int i = 0; i < n; i++)
        cin >> prog[i];
    for (int i = 0; i < n; i++)
        cin >> spo[i];
    // Nodes:
    //   source = 0;
    //   programming team node = 1;
    //   sports team node = 2;
    //   student nodes: 3 ... 3+n-1;
    //   sink = 3+n.
    int source = 0, progNode = 1, sportNode = 2;
    int studentStart = 3, sink = 3 + n;
    int totNodes = sink + 1;
 
    MinCostFlow mcmf(totNodes);
    mcmf.addEdge(source, progNode, p, 0);
    mcmf.addEdge(source, sportNode, s, 0);
    vector<int> progEdgeIndex(n, -1), sportEdgeIndex(n, -1);
    for (int i = 0; i < n; i++){
        int studentNode = studentStart + i;
        int idxProg = mcmf.graph[progNode].size();
        mcmf.addEdge(progNode, studentNode, 1, -prog[i]);
        progEdgeIndex[i] = idxProg;
        int idxSport = mcmf.graph[sportNode].size();
        mcmf.addEdge(sportNode, studentNode, 1, -spo[i]);
        sportEdgeIndex[i] = idxSport;
        mcmf.addEdge(studentNode, sink, 1, 0);
    }
    auto res = mcmf.minCostMaxFlow(source, sink);
    vector<int> teamProg, teamSport;
    for (int i = 0; i < n; i++){
        int studentNode = studentStart + i;
        if(mcmf.graph[progNode][progEdgeIndex[i]].flow > 0)
            teamProg.push_back(i+1);
        else if(mcmf.graph[sportNode][sportEdgeIndex[i]].flow > 0)
            teamSport.push_back(i+1);
    }
    int totalStrength = -res.second;
    cout << totalStrength << "\n";
    for (int i = 0; i < teamProg.size(); i++){
        cout << teamProg[i] << (i+1 == teamProg.size() ? "\n" : " ");
    }
    for (int i = 0; i < teamSport.size(); i++){
        cout << teamSport[i] << (i+1 == teamSport.size() ? "\n" : " ");
    }
}
 
// ---------------------
// Problem 3: Shakespeare’s Program Minimization
// ---------------------
 
// We want to print a sequence of n integers using m variables (a, b, c, …).
// Two operations are allowed: an assignment "var=integer" (penalty = popcount(integer))
// and "print(var)". We construct a MCMF instance so that the chosen matching minimizes total penalty.
// Graph construction follows the published solution.
 
void solveProblem3(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
 
    int n, mVars;
    cin >> n >> mVars;
    vector<int> A(n);
    for (int i = 0; i < n; i++)
        cin >> A[i];
    // Nodes:
    //   Left part: 0 .. n-1
    //   Special node: n
    //   Right part: n+1 .. 2*n
    //   Source S = 2*n+1, Sink T = 2*n+2.
    int totalNodes = 2*n + 3;
    int S = 2*n + 1, T = 2*n + 2;
    MinCostFlow mcmf(totalNodes);
    // S -> each left part node (cap 1, cost 0)
    for (int i = 0; i < n; i++)
        mcmf.addEdge(S, i, 1, 0);
    // S -> special node (n) (cap = mVars, cost 0)
    mcmf.addEdge(S, n, mVars, 0);
    // For each i (0<=i<n) and for each j > i, add edge from i -> (n+j+1) with:
    // cost = 0 if A[i] == A[j] else popcount(A[j])
    for (int i = 0; i < n; i++){
        for (int j = i+1; j < n; j++){
            int cost = (A[i] == A[j] ? 0 : countSetBits(A[j]));
            mcmf.addEdge(i, n + j + 1, 1, cost);
        }
    }
    // For each i, add edge from special node (n) -> (n+i+1) with cost = popcount(A[i]).
    for (int i = 0; i < n; i++){
        mcmf.addEdge(n, n + i + 1, 1, countSetBits(A[i]));
    }
    // Each right part node -> Sink (cap 1, cost 0)
    for (int i = 0; i < n; i++){
        mcmf.addEdge(n + i + 1, T, 1, 0);
    }
    auto res = mcmf.minCostMaxFlow(S, T);
    int penalty = res.second;
    // Reconstruct the matching.
    // For each right node representing the i–th printed integer (node r = n+i+1),
    // find an incoming edge from u in [0, n] (left part or special node) with flow > 0.
    vector<int> Last(n, -1);
    for (int i = 0; i < n; i++){
        int r = n + i + 1;
        for (int u = 0; u <= n; u++){
            for (auto &e : mcmf.graph[u]){
                if(e.to == r && e.flow > 0)
                    Last[i] = u; // u == n means a new assignment.
            }
        }
    }
    // Now generate commands. For each printed integer at position i:
    // If Last[i] == n, then a new assignment is performed.
    // Otherwise if A[i] differs from A[Last[i]] then assignment is made; if equal then just print.
    vector<int> Var(n, -1); // variable index used.
    int nextVar = 0, assignCount = 0;
    vector<string> program;
    for (int i = 0; i < n; i++){
        bool needAssign = false;
        if(Last[i] == n) {
            needAssign = true;
        } else {
            if(A[i] != A[Last[i]])
                needAssign = true;
            else
                needAssign = false;
        }
        if(needAssign){
            Var[i] = nextVar++;
            assignCount++;
            char letter = 'a' + Var[i];
            program.push_back(string(1, letter) + "=" + to_string(A[i]));
            program.push_back("print(" + string(1, letter) + ")");
        } else {
            Var[i] = Var[Last[i]];
            char letter = 'a' + Var[i];
            program.push_back("print(" + string(1, letter) + ")");
        }
    }
    int totalCommands = n + assignCount;
    cout << totalCommands << " " << penalty << "\n";
    for (auto &cmd : program)
        cout << cmd << "\n";
}
 
// ---------------------
// Problem 4: Farmer John's Plan
// ---------------------
 
// Given a directed graph of fields (n nodes, m edges with travel times),
// we compute augmentations (each with capacity 1) using MCMF and then, for each query plan
// with extra available time x, we output the maximum shortest–path time achievable (with error tolerance 1e-6).
void solveProblem4(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
 
    int n, m;
    cin >> n >> m;
    int source = 0, sink = n - 1;
    MinCostFlow mcmf(n);
    for (int i = 0; i < m; i++){
        int u, v, w;
        cin >> u >> v >> w;
        u--; v--;
        mcmf.addEdge(u, v, 1, w);
    }
    vector<pair<int,long long>> aug = mcmf.minCostFlowAugmentations(source, sink);
    int Q;
    cin >> Q;
    cout << fixed << setprecision(10);
    while(Q--){
        int x;
        cin >> x;
        double best = 1e18;
        for(auto &p : aug){
            int f = p.first;
            long long c = p.second;
            double candidate = (c + x) / (double) f;
            best = min(best, candidate);
        }
        cout << best << "\n";
    }
}
 
// ---------------------
// Problem 5: Berland Plumber
// ---------------------
 
// Given an n x n matrix A of pipe widths (0 = no pipe) and an extra total width k,
// we want to maximize the total flow from tank 1 to tank n.
// For each positive A[i][j] we add two edges: one with capacity A[i][j] (cost 0)
// and one with capacity k (cost 1).
 
struct EdgeSimple {
    int to, rev, cap;
    int cost;
    EdgeSimple(int _to, int _rev, int _cap, int _cost)
        : to(_to), rev(_rev), cap(_cap), cost(_cost) {}
};
 
// Add a directed edge in the residual graph.
void addEdge(vector<vector<EdgeSimple>> &gr, int u, int v, int cap, int cost) {
    gr[u].push_back(EdgeSimple(v, gr[v].size(), cap, cost));
    gr[v].push_back(EdgeSimple(u, gr[u].size()-1, 0, -cost));
}
 
// SPFA routine for Problem 5.
bool spfaProblem5(int s, int t, vector<int>& dist, vector<int>& parent, vector<int>& parentEdge, const vector<vector<EdgeSimple>> &gr, int n) {
    const int INF_INT = 0x3f3f3f3f;
    fill(dist.begin(), dist.end(), INF_INT);
    vector<bool> inQueue(n, false);
    dist[s] = 0;
    queue<int> q;
    q.push(s);
    inQueue[s] = true;
    while(!q.empty()){
        int u = q.front();
        q.pop();
        inQueue[u] = false;
        for (int i = 0; i < gr[u].size(); i++){
            const EdgeSimple &e = gr[u][i];
            if(e.cap > 0 && dist[e.to] > dist[u] + e.cost){
                dist[e.to] = dist[u] + e.cost;
                parent[e.to] = u;
                parentEdge[e.to] = i;
                if(!inQueue[e.to]){
                    inQueue[e.to] = true;
                    q.push(e.to);
                }
            }
        }
    }
    return (dist[t] != 0x3f3f3f3f);
}
 
// Custom flow routine for Problem 5: while an augmenting path of cost <= current budget exists, send as much flow as possible subject to budget.
void solveProblem5(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
 
    int n, k;
    cin >> n >> k;
    vector<vector<int>> A(n, vector<int>(n,0));
    for (int i = 0; i < n; i++){
        for (int j = 0; j < n; j++){
            cin >> A[i][j];
        }
    }
    vector<vector<EdgeSimple>> gr(n);
    // For every positive width, add two edges.
    for (int i = 0; i < n; i++){
        for (int j = 0; j < n; j++){
            if(A[i][j] > 0) {
                addEdge(gr, i, j, A[i][j], 0);
                addEdge(gr, i, j, k, 1);
            }
        }
    }
    int flow = 0;
    int ans = 0;
    const int INF_INT = 0x3f3f3f3f;
    vector<int> dist(n), parent(n), parentEdge(n);
    while(spfaProblem5(0, n-1, dist, parent, parentEdge, gr, n)){
        if(dist[n-1] > k) break;
        int pushFlow = INF_INT;
        for (int v = n-1; v != 0; v = parent[v])
            pushFlow = min(pushFlow, gr[parent[v]][parentEdge[v]].cap);
        int possible = pushFlow;
        if(dist[n-1] > 0)
            possible = min(pushFlow, k / dist[n-1]);
        flow += possible;
        ans += possible;
        for (int v = n-1; v != 0; v = parent[v]){
            int idx = parentEdge[v];
            gr[parent[v]][idx].cap -= possible;
            gr[v][gr[parent[v]][idx].rev].cap += possible;
        }
        k -= dist[n-1] * possible;
    }
    cout << ans << "\n";
}
 
// ---------------------
// Main: choose solver based on first input line
// ---------------------
 
int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
 
    int problem;
    cin >> problem;
    if(problem == 1)
        solveProblem1();
    else if(problem == 2)
        solveProblem2();
    else if(problem == 3)
        solveProblem3();
    else if(problem == 4)
        solveProblem4();
    else if(problem == 5)
        solveProblem5();
 
    return 0;
}