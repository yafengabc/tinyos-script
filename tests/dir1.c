int main() {
    char name[32];
    int i;
    int n;

    for (i = 0; i < 200; i = i + 1) {
        n = readdir(i, name, 32);
        if (n <= 0)
            break;
        print(name);
        printf("\n");
    }
    print(isdir("/bin"));
    print(isdir("/readme.txt"));
    print(isdir("/nope"));
    return 0;
}
