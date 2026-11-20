int main() {
    int i;
    int s;
    i = 0;
    s = 0;
    while (i < 1000000) {
        s = s + i;
        i = i + 1;
    }
    print(s);
    return s;
}
