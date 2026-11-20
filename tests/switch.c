enum { RED, GREEN = 5, BLUE };

int f(int x) {
    switch (x) {
    case RED:
        return 1;
    case GREEN:
        return 2;
    case BLUE:
        return 3;
    default:
        return 9;
    }
}

int main() {
    int s = 0;
    int i;
    int n = 0;
    int c = 0;

    s += f(RED);
    s += f(GREEN);
    s += f(BLUE);
    s += f(99);

    for (i = 0; i < 3; i++) {
        switch (i) {
        case 0:
            s += 10;
            break;
        case 1:
            s += 20;
        case 2:
            s += 30;
            break;
        default:
            s += 100;
        }
    }

    for (i = 0; i < 3; i++) {
        switch (i) {
        case 0:
            break;
        default:
            n++;
        }
    }

    for (i = 0; i < 4; i++) {
        switch (i) {
        case 1:
            continue;
        default:
            c++;
        }
    }

    print(s);
    print(n);
    print(c);
    return s;
}
