#include <bits/stdc++.h>
using namespace std;
template <class T>
bool ckmax(T& x, T y) {
  return x < y ? x = y, 1 : 0;
}
template <class T>
bool ckmin(T& x, T y) {
  return x > y ? x = y, 1 : 0;
}
inline int read() {
  int x = 0, f = 1;
  char ch = getchar();
  while (!isdigit(ch)) {
    if (ch == '-') f = 0;
    ch = getchar();
  }
  while (isdigit(ch)) x = x * 10 + ch - '0', ch = getchar();
  return f ? x : -x;
}
const int K = 103;
const int N = 52 * K;
const int M = 2 * (K + 52 + 52 * K + 2 * 52 * 52 * K);
const int inf = 0x3f3f3f3f;
int n, m, k, c, d, a[52], S, T, D;
int dis[N], mf, mc, inc[N], pre[N];
bool vis[N], inq[N];
struct edge {
  int nx, to, fl, c;
} e[M];
int et = 1, hed[N];
void addedge(int u, int v, int fl, int c) {
  e[++et].nx = hed[u], e[et].to = v, e[et].fl = fl, e[et].c = c, hed[u] = et;
}
void adde(int u, int v, int fl, int c) {
  addedge(u, v, fl, c), addedge(v, u, 0, -c);
}
int id(int dep, int x) { return (dep - 1) * n + x; }
bool spfa() {
  queue<int> q;
  for (int i = 1, iend = T; i <= iend; ++i) dis[i] = inf, inq[i] = 0;
  inc[S] = inf, dis[S] = 0, q.push(S);
  while (!q.empty()) {
    int u = q.front();
    q.pop(), inq[u] = 0;
    for (int i = hed[u]; i; i = e[i].nx) {
      int v = e[i].to;
      if (e[i].fl && ckmin(dis[v], dis[u] + e[i].c)) {
        pre[v] = i, inc[v] = min(e[i].fl, inc[u]);
        if (!inq[v]) inq[v] = 1, q.push(v);
      }
    }
  }
  return dis[T] < inf;
}
void EK() {
  int rl = inc[T];
  mf += rl;
  for (int u = T; u != S; u = e[pre[u] ^ 1].to)
    e[pre[u]].fl -= rl, e[pre[u] ^ 1].fl += rl, mc += e[pre[u]].c * rl;
}
signed main() {
  n = read(), m = read(), k = read(), c = read(), d = read(), D = k << 1,
  S = id(D, n) + 1, T = S + 1;
  for (int i = 1, iend = k; i <= iend; ++i)
    a[i] = read(), adde(S, id(1, a[i]), 1, 0);
  for (int i = 1, iend = m; i <= iend; ++i) {
    int x = read(), y = read();
    for (int j = 1, jend = D - 1; j <= jend; ++j)
      for (int l = 0, lend = k - 1; l <= lend; ++l)
        adde(id(j, x), id(j + 1, y), 1, (2 * l + 1) * d + c),
            adde(id(j, y), id(j + 1, x), 1, (2 * l + 1) * d + c);
  }
  for (int i = 1, iend = D - 1; i <= iend; ++i)
    for (int j = 1, jend = n; j <= jend; ++j)
      adde(id(i, j), id(i + 1, j), k, c);
  for (int i = 1, iend = D; i <= iend; ++i) adde(id(i, 1), T, k, 0);
  while (spfa()) EK();
  printf("%d\n", mc);
  return 0;
}
