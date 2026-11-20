int main() {
    int i;
    int j;
    int s;

    s = 0;
    for (i = 0; i < 5; i = i + 1) {
        if (i == 2)
            continue;
        s = s + i;
    }
    print(s);

    i = 0;
    while (i < 10) {
        i = i + 1;
        if (i == 4)
            break;
    }
    print(i);

    do {
        s = s + 1;
    } while (s < 10);
    print(s);

    for (i = 0; i < 3; i = i + 1) {
        for (j = 0; j < 3; j = j + 1) {
            if (j == 1)
                break;
            s = s + 1;
        }
    }
    print(s);
    return 0;
}
