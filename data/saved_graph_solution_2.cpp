#include <bits/stdc++.h>
int add(int a, int b) { return a == INT_MAX || b == INT_MAX ? INT_MAX : a + b; }
int dsu[100000];
int find(int i) { return dsu[i] < 0 ? i : (dsu[i] = find(dsu[i])); }
void join(int i, int j) {
  i = find(i);
  j = find(j);
  if (i == j) return;
  if (dsu[i] <= dsu[j]) {
    dsu[i] += dsu[j];
    dsu[j] = i;
  } else {
    dsu[j] += dsu[i];
    dsu[i] = j;
  }
}
int main() {
  static int cc[100000], kk[500], dd[500][500];
  int n, m, k, h, i, j;
  scanf("%d%d%d", &n, &m, &k);
  j = 0;
  for (i = 0; i < k; i++) {
    int c;
    scanf("%d", &c);
    kk[i] = c;
    while (c-- > 0) cc[j++] = i;
  }
  for (i = 0; i < k; i++)
    for (j = 0; j < k; j++) dd[i][j] = INT_MAX;
  for (i = 0; i < n; i++) dsu[i] = -1;
  while (m-- > 0) {
    int u, v, x;
    int i, j;
    scanf("%d%d%d", &u, &v, &x);
    u--, v--;
    i = cc[u], j = cc[v];
    if (dd[i][j] > x) dd[i][j] = dd[j][i] = x;
    if (x == 0) join(u, v);
  }
  for (i = 1; i < n; i++)
    if (cc[i] == cc[i - 1] && find(i) != find(i - 1)) {
      printf("No\n");
      return 0;
    }
  for (h = 0; h < k; h++)
    for (i = 0; i < k; i++)
      for (j = 0; j < k; j++) {
        int x = add(dd[i][h], dd[h][j]);
        if (dd[i][j] > x) dd[i][j] = dd[j][i] = x;
      }
  printf("Yes\n");
  for (i = 0; i < k; i++) {
    for (j = 0; j < k; j++)
      printf("%d ", i == j ? 0 : dd[i][j] == INT_MAX ? -1 : dd[i][j]);
    printf("\n");
  }
  return 0;
}
