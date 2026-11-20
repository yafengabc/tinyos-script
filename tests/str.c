char greeting[8] = "xy";
char scratch[32];
string shared;

string pick() {
    return "from-fn";
}

int slen(char text[]) {
    return strlen(text);
}

int localtest() {
    char tmp[8] = "loc";
    tmp[2] = 'X';
    printf("loc=%s\n", tmp);
    return strlen(tmp);
}

int main() {
    char c;
    int n;
    string s = "hello";

    scratch[0] = 'H';
    scratch[1] = 'i';
    scratch[2] = 0;
    print(scratch);
    printf("\n");

    c = 'A';
    print(c);
    printf("\n");

    shared = s;
    print(shared);
    printf("\n");
    print(pick());
    printf("\n");

    n = strlen(s);
    print(n);
    printf("\n");
    print(slen("abcd"));
    printf("\n");
    print("lit");
    printf("\n");
    print(localtest());
    printf("\n");

    strlcpy(scratch, "world", 32);
    print(scratch);
    printf("\n");
    strlcat(scratch, "!", 32);
    print(scratch);
    printf("\n");

    scratch[0] += 1;
    print(scratch);
    printf("\n");

    greeting[0] = 'X';
    printf("g=%s\n", greeting);

    print(strcmp(scratch, "xorld!"));
    printf("\n");
    print(atoi("-42"));
    printf("\n");

    printf("name=%s\n", greeting);
    printf("n=%d\n", n);
    return n;
}
