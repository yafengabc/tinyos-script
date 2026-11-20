int main() {
    int s;

    s = 0;
    switch (2) {
    case 1:
        s = 10;
        break;
    case 2:
        s = 20;
    case 3:
        s = s + 3;
        break;
    default:
        s = 99;
    }
    print(s);

    switch (9) {
    case 1:
        s = 1;
        break;
    default:
        s = 99;
    }
    print(s);
    return s;
}
