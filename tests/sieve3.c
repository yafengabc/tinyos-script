int a[100];
int n;
int main() {
    int i;
    int j;
    int count;
    n = 100;
    i = 0;
    while (i < n) {
        a[i] = 0;
        i = i + 1;
    }
    i = 2;
    while (i < n) {
        if (a[i] == 0) {
            j = i * i;
            while (j < n) {
                a[j] = 1;
                j = j + i;
            }
        }
        i = i + 1;
    }
    count = 0;
    i = 2;
    while (i < n) {
        if (a[i] == 0) {
            count = count + 1;
        }
        i = i + 1;
    }
    print(count);
    return count;
}
