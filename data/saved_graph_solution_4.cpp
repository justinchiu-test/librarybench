#include <bits/stdc++.h>
using namespace std;
int dp[303][303];
double p[303][303];
int n, m, a, b;
double x;
int main() {
  cin >> n >> m;
  for (int i = 1; i < 200; ++i)
    for (int j = 1; j < 300; ++j) dp[i][j] = 5000;
  for (int i = 0; i < m; ++i) {
    cin >> a >> b;
    dp[a][b] = dp[b][a] = p[a][b] = p[b][a] = 1;
  }
  for (int k = 1; k <= n; ++k)
    for (int i = 1; i <= n; ++i)
      for (int j = 1; j <= n; ++j)
        if ((a = dp[i][k] + dp[k][j]) <= dp[i][j]) {
          if (a < dp[i][j]) p[i][j] = 0;
          dp[i][j] = a;
          p[i][j] += p[i][k] * p[k][j];
        }
  x = p[1][n];
  for (int i = 2; i < n; ++i)
    if (dp[1][i] + dp[i][n] == dp[1][n]) x = max(x, 2 * p[1][i] * p[i][n]);
  printf("%0.9lf\n", x / p[1][n]);
}
