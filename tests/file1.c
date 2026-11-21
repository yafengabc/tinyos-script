int main() {
    int fd;
    int n;
    char buf[16];

    fd = create("/f1.txt");
    print(fd >= 0);
    print(write(fd, "hello", 5));
    print(close(fd));

    fd = open("/f1.txt");
    n = read(fd, buf, 16);
    buf[n] = 0;
    print(n);
    print(buf);
    printf("\n");
    print(close(fd));
    print(unlink("/f1.txt"));
    return 0;
}
