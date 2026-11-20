int pick(int n) {
    int r;

    r = 0;
    switch (n) {
    case 0:
        r = 100;
        break;
    case 1:
        r = 101;
        break;
    case 2:
        r = 102;
        break;
    case 3:
        r = 103;
        break;
    case 4:
        r = 104;
        break;
    case 5:
        r = 105;
        break;
    case 6:
        r = 106;
        break;
    case 7:
        r = 107;
        break;
    case 8:
        r = 108;
        break;
    case 9:
        r = 109;
        break;
    case 10:
        r = 110;
        break;
    case 11:
        r = 111;
        break;
    case 12:
        r = 112;
        break;
    case 13:
        r = 113;
        break;
    case 14:
        r = 114;
        break;
    case 15:
        r = 115;
        break;
    case 16:
        r = 116;
    case 17:
        r = r + 1;
        break;
    default:
        r = -1;
    }
    return r;
}

int main() {
    int s;
    int i;

    s = 0;
    for (i = 0; i < 20; i = i + 1)
        s = s + pick(i);
    print(s);
    print(pick(16));
    print(pick(17));
    print(pick(99));
    return 0;
}
