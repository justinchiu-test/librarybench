#include <bits/stdc++.h>
using namespace std;
using LL = long long;
const int MAX_N = 1e5 + 5;
struct Graph {
  int to, cap, cost, next;
} e[MAX_N * 50];
int fir[MAX_N], e_cnt;
void clearGraph() {
  memset(fir, -1, sizeof(fir));
  e_cnt = 0;
}
void Add_Edge(int u, int v, int c, int w) {
  e[e_cnt] = (Graph){v, c, w, fir[u]}, fir[u] = e_cnt++;
  e[e_cnt] = (Graph){u, 0, -w, fir[v]}, fir[v] = e_cnt++;
}
void AddEdge(int u, int v, int c, int w) {
  e[e_cnt] = (Graph){v, c, w, fir[u]}, fir[u] = e_cnt++;
  e[e_cnt] = (Graph){u, c, -w, fir[v]}, fir[v] = e_cnt++;
}
const LL INF = 1e18;
int S, T;
LL dis[MAX_N];
bool inq[MAX_N];
bool spfa() {
  queue<int> que;
  for (int i = 0; i <= T; i++) dis[i] = INF;
  dis[T] = 0, inq[T] = 1, que.push(T);
  while (!que.empty()) {
    int x = que.front();
    que.pop();
    for (int i = fir[x]; ~i; i = e[i].next) {
      int v = e[i].to, w = e[i ^ 1].cost;
      if (e[i ^ 1].cap && dis[v] > dis[x] + w) {
        dis[v] = dis[x] + w;
        if (!inq[v]) que.push(v), inq[v] = 1;
      }
    }
    inq[x] = 0;
  }
  return dis[S] != INF;
}
int tim, vis[MAX_N];
bool relabel() {
  LL res = INF;
  for (int x = 0; x <= T; x++) {
    if (vis[x] != tim) continue;
    for (int i = fir[x]; ~i; i = e[i].next) {
      int v = e[i].to;
      if (e[i].cap && vis[v] != tim)
        res = min(res, dis[v] + e[i].cost - dis[x]);
    }
  }
  if (res == INF) return 0;
  for (int i = 0; i <= T; i++)
    if (vis[i] == tim) dis[i] += res;
  return 1;
}
int dfs(int x, int f) {
  if (x == T || !f) return f;
  vis[x] = tim;
  int res = 0;
  for (int i = fir[x]; ~i; i = e[i].next) {
    int v = e[i].to, w = e[i].cost;
    if (e[i].cap && dis[x] == dis[v] + w && vis[v] != tim) {
      int d = dfs(v, min(f, e[i].cap));
      res += d, f -= d;
      e[i].cap -= d, e[i ^ 1].cap += d;
      if (!f) break;
    }
  }
  return res;
}
LL zkw() {
  spfa();
  LL res = 0, f = 0;
  do do {
      ++tim, f = dfs(S, 1e9);
      if (dis[S] >= 0) return res;
      res += dis[S] * f;
    } while (f);
  while (relabel());
  return res;
}
int N, a[205][205], Id[205][205], cnt;
int main() {
  clearGraph();
  scanf("%d", &N);
  for (int i = 1; i <= N; i++)
    for (int j = 1; j <= N; j++) scanf("%d", a[i] + j), Id[i][j] = ++cnt;
  S = 0, T = cnt + 1;
  for (int i = 1; i <= N; i++)
    for (int j = 1; j <= N; j++) {
      if (i != N && a[i][j] != -1 && a[i + 1][j] != -1)
        AddEdge(Id[i][j], Id[i + 1][j], 1, 0);
      if (j != N && a[i][j] != -1 && a[i][j + 1] != -1)
        AddEdge(Id[i][j], Id[i][j + 1], 1, 0);
      if (a[i][j] > 0)
        Add_Edge(S, Id[i][j], 1e9, -a[i][j]),
            Add_Edge(Id[i][j], T, 1e9, a[i][j]);
    }
  printf("%lld\n", -zkw());
  return 0;
}
