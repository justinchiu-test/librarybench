#include <bits/stdc++.h>
using namespace std;
const int maxn = 3e5;
const int base = 1e9 + 7;
int n, m, q;
int x[maxn], y[maxn];
int l[maxn], r[maxn], s[maxn], t[maxn];
int ans[maxn];
int d[2000][2000];
vector<int> lst[maxn];
int main() {
  ios_base::sync_with_stdio(0);
  cin >> n >> m >> q;
  for (int i = 1; i <= m; i++) cin >> x[i] >> y[i];
  for (int i = 1; i <= q; i++) {
    cin >> l[i] >> r[i] >> s[i] >> t[i];
    lst[l[i]].push_back(i);
  }
  for (int i = 1; i <= n; i++)
    for (int j = 1; j <= n; j++) d[i][j] = 1e9;
  for (int i = 1; i <= n; i++) d[i][i] = 0;
  for (int i = m; i >= 1; i--) {
    for (int j = 1; j <= n; j++) {
      int k1 = d[x[i]][j];
      int k2 = d[y[i]][j];
      d[x[i]][j] = min(k1, k2);
      d[y[i]][j] = min(k1, k2);
    }
    d[x[i]][y[i]] = i;
    d[y[i]][x[i]] = i;
    for (int j = 0; j < lst[i].size(); j++) {
      int x = lst[i][j];
      if (d[s[x]][t[x]] <= r[x]) ans[x] = 1;
    }
  }
  for (int i = 1; i <= q; i++)
    if (ans[i] == 0)
      cout << "No\n";
    else
      cout << "Yes\n";
  return 0;
}
