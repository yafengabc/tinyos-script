int main() {
    char b[6];
    string s;
    string t;

    b[0] = 'a';
    b[1] = 'b';
    b[2] = 0;
    print(b);
    printf("\n");

    s = "hello";
    t = s;
    print(t);
    printf("\n");

    print(strlen(""));
    printf("\n");
    print(strcmp("abc", "abd"));
    printf("\n");
    print(strcmp("abc", "abc"));
    printf("\n");

    strlcpy(b, "abcdefgh", 4);
    print(b);
    printf("\n");
    strlcat(b, "Z", 6);
    print(b);
    printf("\n");

    print(atoi("  +42x"));
    printf("\n");
    print(atoi("-7"));
    printf("\n");
    return 0;
}
