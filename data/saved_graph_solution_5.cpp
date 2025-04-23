#include <bits/stdc++.h>
using namespace std;
int h[100][100];
int main() {
  int n, d;
  cin >> n >> d;
  vector<int> a(n), x(n), y(n);
  for (int i = 0; i < (int)n - 2; ++i) {
    cin >> a[i + 1];
  }
  for (int i = 0; i < (int)n; ++i) {
    cin >> x[i] >> y[i];
  }
  for (int i = 0; i < (int)n; ++i)
    for (int j = 0; j < (int)n; ++j)
      h[i][j] = (abs(x[i] - x[j]) + abs(y[i] - y[j])) * d - a[i];
  for (int i = 0; i < (int)n; ++i) h[i][i] = 0;
  for (int k = 0; k < (int)n; ++k)
    for (int i = 0; i < (int)n; ++i)
      for (int j = 0; j < (int)n; ++j)
        h[i][j] = min(h[i][j], h[i][k] + h[k][j]);
  cout << h[0][n - 1] << endl;
}
