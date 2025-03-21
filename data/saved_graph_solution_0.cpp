#include <bits/stdc++.h>
using namespace std;
const int MAX = 2e5 + 5, MOD = 1e9 + 7, MAXLG = log2(MAX) + 1;
const long long inf = 1e18 + 5;
struct edge {
  int v, rev;
  long long cap, cost, flow;
  edge() {}
  edge(int v, int rev, long long cap, long long cost)
      : v(v), rev(rev), cap(cap), cost(cost), flow(0) {}
};
struct mcmf {
  int src, sink, nodes;
  vector<int> par, idx;
  vector<bool> inq;
  vector<long long> dis;
  vector<vector<edge>> g;
  mcmf() {}
  mcmf(int src, int sink, int nodes)
      : src(src),
        sink(sink),
        nodes(nodes),
        par(nodes),
        idx(nodes),
        inq(nodes),
        dis(nodes),
        g(nodes) {}
  void add_edge(int u, int v, long long cap, long long cost,
                bool directed = true) {
    edge _u = edge(v, g[v].size(), cap, cost);
    edge _v = edge(u, g[u].size(), 0, -cost);
    g[u].push_back(_u);
    g[v].push_back(_v);
    if (!directed) add_edge(v, u, cap, cost, true);
  }
  bool spfa() {
    for (int i = 0; i < nodes; i++) {
      dis[i] = inf, inq[i] = false;
    }
    queue<int> q;
    q.push(src);
    dis[src] = 0, par[src] = -1, inq[src] = true;
    while (!q.empty()) {
      int u = q.front();
      q.pop();
      inq[u] = false;
      for (int i = 0; i < g[u].size(); i++) {
        edge &e = g[u][i];
        if (e.cap <= e.flow) continue;
        if (dis[e.v] > dis[u] + e.cost) {
          dis[e.v] = dis[u] + e.cost;
          par[e.v] = u, idx[e.v] = i;
          if (!inq[e.v]) inq[e.v] = true, q.push(e.v);
        }
      }
    }
    return (dis[sink] != inf);
  }
  pair<long long, long long> solve() {
    long long mincost = 0, maxflow = 0;
    while (spfa()) {
      long long bottleneck = inf;
      for (int u = par[sink], v = idx[sink]; u != -1; v = idx[u], u = par[u]) {
        edge &e = g[u][v];
        bottleneck = min(bottleneck, e.cap - e.flow);
      }
      for (int u = par[sink], v = idx[sink]; u != -1; v = idx[u], u = par[u]) {
        edge &e = g[u][v];
        e.flow += bottleneck;
        g[e.v][e.rev].flow -= bottleneck;
      }
      mincost += bottleneck * dis[sink], maxflow += bottleneck;
    }
    return make_pair(mincost, maxflow);
  }
};
int arr[MAX];
pair<pair<int, int>, int> task[1005];
int ind[1005];
int main() {
  ios::sync_with_stdio(false);
  cin.tie(NULL);
  ;
  int n, k;
  cin >> n >> k;
  for (int i = 1; i <= n; i++)
    cin >> task[i].first.first >> task[i].first.second >> task[i].second;
  int src, sink, nodes;
  src = 0, sink = k + 2 * n + 1, nodes = sink + 1;
  mcmf F(src, sink, nodes);
  for (int i = 1; i <= k; i++) {
    F.add_edge(src, i, 1, 0);
    for (int j = 1; j <= n; j++) F.add_edge(i, j + k, inf, 0);
  }
  for (int i = 1; i <= n; i++) {
    ind[i] = F.g[i + k].size();
    F.add_edge(i + k, i + k + n, 1, -task[i].second);
    F.add_edge(i + k + n, sink, 1, 0);
    int ed = task[i].first.first + task[i].first.second - 1;
    for (int j = 1; j <= n; j++) {
      if (i == j) continue;
      if (ed < task[j].first.first) {
        F.add_edge(i + k + n, j + k, 1, 0);
      }
    }
  }
  pair<long long, long long> p = F.solve();
  for (int i = 1; i <= n; i++) {
    edge &e = F.g[i + k][ind[i]];
    if (e.flow)
      cout << 1 << " ";
    else
      cout << 0 << " ";
  }
  cout << "\n";
}
