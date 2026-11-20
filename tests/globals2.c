int g;
int ga[3];
char gs[8];

int inc() {
    g = g + 1;
    return g;
}

int main() {
    g = 5;
    print(inc());
    print(inc());

    ga[0] = 7;
    ga[1] = 8;
    print(ga[0] + ga[1]);

    strlcpy(gs, "ok", 8);
    print(gs);
    printf("\n");
    return g;
}
