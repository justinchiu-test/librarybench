#include <bits/stdc++.h>
using namespace std;
const int mod = 1e9 + 7;
const long long int INF = 9e18 + 2e17;
const int inf = 2e9;
const int N = 1e3 + 22;
const double eps = 1e-10;
const double PI = 3.14159265;
long long int w[505][505], x[505], ans[505];
void solve() {
  int n;
  cin >> n;
  for (int i = 1; i <= n; i++) {
    for (int j = 1; j <= n; j++) cin >> w[i][j];
  }
  for (int k = 1; k <= n; k++) cin >> x[k];
  for (int k = n; k; k--) {
    for (int i = 1; i <= n; i++) {
      for (int j = 1; j <= n; j++) {
        w[i][j] = min(w[i][j], w[i][x[k]] + w[x[k]][j]);
      }
    }
    for (int i = k; i <= n; i++) {
      for (int j = k; j <= n; j++) ans[k] += w[x[i]][x[j]];
    }
  }
  for (int i = 1; i <= n; i++) cout << ans[i] << ' ';
  return;
}
int main() {
  ios::sync_with_stdio(false);
  cin.tie(NULL);
  cout.tie(NULL);
  solve();
  return 0;
}
