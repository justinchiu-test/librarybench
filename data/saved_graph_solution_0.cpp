#include <bits/stdc++.h>
using namespace std;
int n, d;
int a[105], x[105], y[105], dis[105][105];
int main() {
  int i, j, k;
  cin >> n >> d;
  for (i = 2; i < n; i++) cin >> a[i];
  for (i = 1; i <= n; i++) cin >> x[i] >> y[i];
  for (i = 1; i <= n; i++)
    for (j = 1; j <= n; j++)
      if (i != j) dis[i][j] = (abs(x[i] - x[j]) + abs(y[i] - y[j])) * d - a[i];
  for (k = 1; k <= n; k++)
    for (i = 1; i <= n; i++)
      for (j = 1; j <= n; j++)
        dis[i][j] =
            ((dis[i][j]) > (dis[i][k] + dis[k][j]) ? (dis[i][k] + dis[k][j])
                                                   : (dis[i][j]));
  cout << dis[1][n] << endl;
  return 0;
}
