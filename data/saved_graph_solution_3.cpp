#include <bits/stdc++.h>
using namespace std;
const int N = 5e2 + 5;
int n, d[N][N], c[N][N], dp[N][N];
void floyd() {
  memcpy(d, c, sizeof(c));
  for (int i = 1; i <= n; i++) d[i][i] = 0;
  for (int k = 1; k <= n; k++)
    for (int i = 1; i <= n; i++)
      for (int j = 1; j <= n; j++) d[i][j] = min(d[i][j], d[i][k] + d[k][j]);
}
int main() {
  int m;
  scanf("%d%d", &n, &m);
  memset(c, 0x3f, sizeof(c));
  const int inf = c[0][0];
  while (m--) {
    int u, v, w;
    scanf("%d%d%d", &u, &v, &w);
    c[u][v] = c[v][u] = w;
  }
  floyd();
  for (int i = 1; i <= n; i++)
    for (int j = 1; j <= n; j++) {
      for (int k = 1; k <= n; k++) {
        if (c[i][j] != inf && d[i][k] == c[i][j] + d[j][k]) {
          ++dp[i][k];
        }
      }
    }
  for (int i = 1; i <= n; i++)
    for (int j = i + 1; j <= n; j++) {
      int ans = 0;
      for (int k = 1; k <= n; k++)
        if (d[i][j] == d[i][k] + d[k][j]) ans += dp[k][j];
      printf("%d%c", ans, (i == n - 1 && j == n) ? '\n' : ' ');
    }
  return 0;
}
