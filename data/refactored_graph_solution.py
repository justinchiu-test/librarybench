#include <bits/stdc++.h>
using namespace std;
 
// ----------------- Problem 1 Solver -----------------
// "Time" game: Given n stations and a bonus at stations 2..n–1,
// moving cost is (Manhattan_distance * d) and when leaving station i you “gain” bonus[i].
// We want the minimum extra time (money) needed; use Floyd–Warshall.
void solveProblem1(){
    int n, d;
    cin >> n >> d;
    vector<int> bonus(n+1, 0); // 1-indexed; bonus for station 1 and n remain 0.
    for (int i = 2; i <= n-1; i++){
        cin >> bonus[i];
    }
    vector<int> xs(n+1), ys(n+1);
    for (int i = 1; i <= n; i++){
        cin >> xs[i] >> ys[i];
    }
    // Build cost matrix.
    vector<vector<int>> cost(n+1, vector<int>(n+1, 0));
    for (int i = 1; i <= n; i++){
        for (int j = 1; j <= n; j++){
            if (i == j) {
                cost[i][j] = 0;
            } else {
                int md = abs(xs[i] - xs[j]) + abs(ys[i] - ys[j]);
                cost[i][j] = md * d - bonus[i];
            }
        }
    }
    // Compute all–pairs shortest cost.
    for (int k = 1; k <= n; k++){
        for (int i = 1; i <= n; i++){
            for (int j = 1; j <= n; j++){
                cost[i][j] = min(cost[i][j], cost[i][k] + cost[k][j]);
            }
        }
    }
    cout << cost[1][n] << "\n";
}
 
// ----------------- Problem 2 Solver -----------------
// Greg’s game: We are given a complete directed graph (n vertices)
// and an order in which vertices are removed. Before each removal, the
// sum of shortest path lengths between every pair of remaining vertices is needed.
// We use the standard reverse–process Floyd Warshall.
void solveProblem2(){
    int n;
    cin >> n;
    vector<vector<long long>> dist(n, vector<long long>(n, 0));
    for (int i = 0; i < n; i++){
        for (int j = 0; j < n; j++){
            cin >> dist[i][j];
        }
    }
    vector<int> order(n);
    for (int i = 0; i < n; i++){
        cin >> order[i];
        order[i]--; // convert to 0-index
    }
    vector<bool> active(n, false);
    vector<long long> ans(n, 0);
    for (int idx = n - 1; idx >= 0; idx--){
        int k = order[idx];
        active[k] = true;
        for (int i = 0; i < n; i++){
            for (int j = 0; j < n; j++){
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
            }
        }
        long long sum = 0;
        for (int i = 0; i < n; i++){
            if (!active[i]) continue;
            for (int j = 0; j < n; j++){
                if (active[j])
                    sum += dist[i][j];
            }
        }
        ans[idx] = sum;
    }
    for (int i = 0; i < n; i++){
        cout << ans[i] << (i == n - 1 ? "\n" : " ");
    }
}
 
// ----------------- Problem 3 Solver -----------------
// Bacteria energy transfers: There are n bacteria of k types (given by counts – consecutive in order).
// Also given m ways to transfer energy (each with a cost x). Only zero–cost transfers are “free” and must
// connect all bacteria of the same type. Additionally, we want to compute a k×k matrix (one per type) where
// cell [i][j] is the minimal cost connecting type i to type j.
void solveProblem3(){
    int n, m, k; 
    cin >> n >> m >> k;
    vector<int> typeCount(k);
    vector<int> bactType(n, 0);
    int idx = 0;
    for (int i = 0; i < k; i++){
        cin >> typeCount[i];
        for (int j = 0; j < typeCount[i]; j++){
            bactType[idx++] = i;
        }
    }
    // DSU for connectivity via zero-cost transfers.
    vector<int> dsu(n, -1);
    function<int(int)> findDSU = [&](int a) -> int {
        return dsu[a] < 0 ? a : dsu[a] = findDSU(dsu[a]);
    };
    auto unionDSU = [&](int a, int b) {
        a = findDSU(a); b = findDSU(b);
        if(a == b) return;
        if(dsu[a] <= dsu[b]){
            dsu[a] += dsu[b];
            dsu[b] = a;
        } else {
            dsu[b] += dsu[a];
            dsu[a] = b;
        }
    };
 
    const int INF_INT = INT_MAX;
    vector<vector<int>> mat(k, vector<int>(k, INF_INT));
    for (int i = 0; i < k; i++){
        mat[i][i] = 0;
    }
    for (int i = 0; i < m; i++){
        int u, v, x;
        cin >> u >> v >> x;
        u--; v--;
        int t1 = bactType[u], t2 = bactType[v];
        if(x < mat[t1][t2]){
            mat[t1][t2] = x;
            mat[t2][t1] = x;
        }
        if(x == 0)
            unionDSU(u, v);
    }
    // Check that every pair of bacteria of the same type are connected via 0–cost transfers.
    idx = 0;
    for (int t = 0; t < k; t++){
        int start = idx, end = idx + typeCount[t];
        for (int i = start+1; i < end; i++){
            if(findDSU(i) != findDSU(i-1)){
                cout << "No\n";
                return;
            }
        }
        idx += typeCount[t];
    }
    // Compute shortest paths on the k–by–k type–graph.
    for (int h = 0; h < k; h++){
        for (int i = 0; i < k; i++){
            for (int j = 0; j < k; j++){
                if((long long)mat[i][h] + mat[h][j] < mat[i][j])
                    mat[i][j] = mat[i][h] + mat[h][j];
            }
        }
    }
    cout << "Yes\n";
    for (int i = 0; i < k; i++){
        for (int j = 0; j < k; j++){
            if(i == j)
                cout << 0;
            else if(mat[i][j] == INF_INT)
                cout << -1;
            else
                cout << mat[i][j];
            cout << (j==k-1 ? "\n" : " ");
        }
    }
}
 
// ----------------- Problem 4 Solver -----------------
// Berland roads: Given n cities and m bidirectional roads (possibly not all pairs are connected),
// for every pair (s, t) (with s < t) compute the number of roads lying on at least one shortest path.
void solveProblem4(){
    int n, m;
    cin >> n >> m;
    const int INF = 0x3f3f3f3f; 
    vector<vector<int>> c(n, vector<int>(n, INF));
    vector<vector<int>> d(n, vector<int>(n, INF));
    vector<vector<int>> dp(n, vector<int>(n, 0));
    for (int i = 0; i < n; i++){
        c[i][i] = 0;
        d[i][i] = 0;
    }
    for (int i = 0; i < m; i++){
        int u, v, w;
        cin >> u >> v >> w;
        u--; v--;
        c[u][v] = w;
        c[v][u] = w;
        d[u][v] = w;
        d[v][u] = w;
    }
    // Compute all–pairs shortest distances.
    for (int k = 0; k < n; k++){
        for (int i = 0; i < n; i++){
            for (int j = 0; j < n; j++){
                d[i][j] = min(d[i][j], d[i][k] + d[k][j]);
            }
        }
    }
    // For each directed edge that exists, add to dp if it “fits” in a shortest–path extension.
    for (int i = 0; i < n; i++){
        for (int j = 0; j < n; j++){
            if(c[i][j] != INF){
                for (int k = 0; k < n; k++){
                    if(d[i][k] == c[i][j] + d[j][k])
                        dp[i][k]++;
                }
            }
        }
    }
    // For each pair (s,t), s < t, sum contributions.
    vector<int> results;
    for (int i = 0; i < n; i++){
        for (int j = i+1; j < n; j++){
            int roadsCount = 0;
            for (int k = 0; k < n; k++){
                if(d[i][j] == d[i][k] + d[k][j])
                    roadsCount += dp[k][j];
            }
            results.push_back(roadsCount);
        }
    }
    for (int i = 0; i < (int)results.size(); i++){
        cout << results[i] << (i+1 == results.size() ? "\n" : " ");
    }
}
 
// ----------------- Problem 5 Solver -----------------
// Berland police station: The road network (unweighted, connected) has cities numbered 1..n
// (capital cities are 1 and n). When a police station is set at a city p,
// every road incident to p becomes safe. Residents always take some shortest path (of unit–edge lengths) from 1 to n.
// If p is 1 or n, each shortest path gets one safe edge; if p is another vertex on a given shortest path,
// then that path gets 2 safe edges. We choose p to maximize the average safe roads over all shortest paths.
void solveProblem5(){
    int n, m;
    cin >> n >> m;
    const int INF = 5000; // safe "infinite" distance (> possible shortest distance)
    vector<vector<int>> dp(n+1, vector<int>(n+1, INF));
    vector<vector<double>> ways(n+1, vector<double>(n+1, 0.0));
    for (int i = 1; i <= n; i++){
        dp[i][i] = 0;
    }
    // Input roads (bidirectional, each road cost = 1)
    for (int i = 0; i < m; i++){
        int a, b;
        cin >> a >> b;
        dp[a][b] = 1;
        dp[b][a] = 1;
        ways[a][b] = 1.0;
        ways[b][a] = 1.0;
    }
    // Floyd Warshall: compute shortest distances and count number of shortest paths.
    for (int k = 1; k <= n; k++){
        for (int i = 1; i <= n; i++){
            for (int j = 1; j <= n; j++){
                int cand = dp[i][k] + dp[k][j];
                if(cand < dp[i][j]){
                    dp[i][j] = cand;
                    ways[i][j] = 0.0;
                    ways[i][j] += ways[i][k] * ways[k][j];
                }
                else if(cand == dp[i][j]){
                    ways[i][j] += ways[i][k] * ways[k][j];
                }
            }
        }
    }
    double totalPaths = ways[1][n];
    // If we place the station at 1 or n, each shortest path gets one safe road.
    double best = totalPaths;
    // Otherwise, if city i (2 <= i <= n-1 and lies on some shortest path)
    // then each such shortest path gets 2 safe roads.
    for (int i = 2; i < n; i++){
        if(dp[1][i] + dp[i][n] == dp[1][n]){
            best = max(best, 2.0 * ways[1][i] * ways[i][n]);
        }
    }
    double ans = best / totalPaths;
    cout << fixed << setprecision(12) << ans << "\n";
}
 
// ----------------- Main -----------------
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
            break;
    }
    return 0;
}