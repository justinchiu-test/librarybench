#include <bits/stdc++.h>
#pragma GCC optimize(2)
using namespace std;
inline int read() {
  char c = getchar();
  int x = 0;
  bool f = 0;
  for (; !isdigit(c); c = getchar()) f ^= !(c ^ 45);
  for (; isdigit(c); c = getchar()) x = (x << 1) + (x << 3) + (c ^ 48);
  if (f) x = -x;
  return x;
}
int n, m, s, t, maxflow, mincost;
int dis[100005], pre[100005], lste[100005], flow[100005];
bool inq[100005];
struct edge {
  int to, nxt, w, cost;
} e[100005];
int tot = 1, head[100005];
inline void adde(int u, int v, int w, int c) {
  e[++tot] = (edge){v, head[u], w, c};
  head[u] = tot;
}
inline void add(int u, int v, int w, int c) {
  adde(u, v, w, c);
  adde(v, u, 0, -c);
}
bool spfa(int s, int t) {
  queue<int> q;
  memset(dis, 63, sizeof dis);
  memset(flow, 63, sizeof flow);
  memset(inq, 0, sizeof inq);
  dis[s] = 0, pre[t] = -1;
  q.push(s);
  while (!q.empty()) {
    int u = q.front();
    q.pop();
    inq[u] = 0;
    for (int i = head[u]; i; i = e[i].nxt) {
      int v = e[i].to;
      if (e[i].w > 0 && dis[v] > dis[u] + e[i].cost) {
        dis[v] = dis[u] + e[i].cost;
        pre[v] = u, lste[v] = i;
        flow[v] = min(flow[u], e[i].w);
        if (!inq[v]) inq[v] = 1, q.push(v);
      }
    }
  }
  return pre[t] != -1;
}
vector<pair<double, double> > v;
void mcmf(int s, int t) {
  while (spfa(s, t)) {
    int u = t;
    maxflow += flow[t], mincost += flow[t] * dis[t];
    v.push_back(make_pair(1.0 * maxflow, 1.0 * mincost));
    while (u != s) {
      int E = lste[u];
      e[E].w -= flow[t], e[E ^ 1].w += flow[t];
      u = pre[u];
    }
  }
}
signed main() {
  n = read(), m = read();
  for (register int i = (1); i <= (m); ++i) {
    int u = read(), v = read(), w = read();
    add(u, v, 1, w);
  }
  mcmf(1, n);
  int Q = read();
  while (Q--) {
    int x = read();
    double res = 1e18;
    for (register int i = (0); i <= (maxflow - 1); ++i)
      res = min(res, (v[i].second + x) / v[i].first);
    printf("%.10lf\n", res);
  }
  return 0;
}
