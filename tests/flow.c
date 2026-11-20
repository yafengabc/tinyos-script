int main() {
    int i;
    int s = 0;
    int j = 0;
    int k = 0;

    for (i = 0; i < 10; i++) {
        if (i == 5) continue;
        if (i == 8) break;
        s += i;
    }

    do {
        j++;
    } while (j < 3);

    while (k < 5) {
        k++;
        if (k == 2) continue;
        if (k == 4) break;
    }

    for (int q = 0; q < 3; q++) {
        s += q;
    }

    print(s);
    print(j);
    print(k);
    return s;
}
