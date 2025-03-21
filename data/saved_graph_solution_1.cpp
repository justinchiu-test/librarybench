#include <bits/stdc++.h>
using namespace std;
const int INF = 0x3f3f3f3f;
const int maxn = 3100 + 5;
const int maxm = 20000 + 5;
int n, m;
int head[maxn], to[maxm], nx[maxm], flow[maxm], cost[maxm], ppp;
int dis[maxn], minflow[maxn];
bool flag[maxn];
pair<int, int> par[maxn];
struct MIN_COST_MAX_FLOW {
  void init() {
    memset(head, -1, sizeof(head));
    ppp = 0;
  }
  bool spfa(int s, int t) {
    int u, v;
    fill(dis, dis + maxn, INF);
    memset(flag, 0, sizeof(flag));
    dis[s] = 0;
    minflow[s] = INF;
    queue<int> q;
    q.push(s);
    while (!q.empty()) {
      u = q.front();
      q.pop();
      flag[u] = 0;
      for (int i = head[u]; ~i; i = nx[i]) {
        v = to[i];
        if (flow[i] && dis[v] > dis[u] + cost[i]) {
          dis[v] = dis[u] + cost[i];
          par[v] = (make_pair(u, i));
          minflow[v] = min(minflow[u], flow[i]);
          if (!flag[v]) {
            flag[v] = 1;
            q.push(v);
          }
        }
      }
    }
    if (dis[t] == INF) return 0;
    return 1;
  }
  int solve(int s, int t) {
    int ans = 0, p;
    while (spfa(s, t)) {
      p = t;
      while (p != s) {
        flow[par[p].second] -= minflow[t];
        flow[par[p].second ^ 1] += minflow[t];
        p = par[p].first;
      }
      ans += dis[t];
    }
    return ans;
  }
  void add_edge(int u, int v, int f, int c) {
    to[ppp] = v, nx[ppp] = head[u], flow[ppp] = f, cost[ppp] = c,
    head[u] = ppp++;
    to[ppp] = u, nx[ppp] = head[v], flow[ppp] = 0, cost[ppp] = -c,
    head[v] = ppp++;
  }
} mcmf;
vector<int> programming, sport;
int pro[maxn], spo[maxn];
int main() {
  int n, p, s;
  scanf("%d%d%d", &n, &p, &s);
  for (int i = 1; i <= n; i++) scanf("%d", &pro[i]);
  for (int i = 1; i <= n; i++) scanf("%d", &spo[i]);
  int start = 0, tank = n + 1;
  int pp = n + 2, ss = n + 3;
  mcmf.init();
  mcmf.add_edge(start, pp, p, 0);
  mcmf.add_edge(start, ss, s, 0);
  for (int i = 1; i <= n; i++) {
    mcmf.add_edge(pp, i, 1, -pro[i]);
    mcmf.add_edge(ss, i, 1, -spo[i]);
    mcmf.add_edge(i, tank, 1, 0);
  }
  int ans = mcmf.solve(start, tank);
  for (int i = 1; i <= n; i++) {
    for (int j = head[i]; ~j; j = nx[j]) {
      if (flow[j] && to[j] == pp) {
        programming.push_back(i);
      }
    }
  }
  for (int i = 1; i <= n; i++) {
    for (int j = head[i]; ~j; j = nx[j]) {
      if (flow[j] && to[j] == ss) {
        sport.push_back(i);
      }
    }
  }
  printf("%d\n", -ans);
  for (int i = 0; i < programming.size(); i++) {
    printf("%d%c", programming[i], i == programming.size() - 1 ? '\n' : ' ');
  }
  for (int i = 0; i < sport.size(); i++) {
    printf("%d%c", sport[i], i == sport.size() - 1 ? '\n' : ' ');
  }
  return 0;
}
