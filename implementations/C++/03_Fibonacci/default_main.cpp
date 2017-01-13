
#include <iostream>
#include <cstdlib>
#include <chrono>


long fibonacci_naive(int N) {
  if (N < 2) {
    return N;
  } else {
    return fibonacci_naive(N-1) + fibonacci_naive(N-2);
  }
}

long fibonacci_tailrec(int N, long a = 0, long b = 1) {
  if (N == 0) {
    return a;
  } else {
    return fibonacci_tailrec(N-1, b, a+b);
  }
}

long fibonacci_iterative(int N) {
  long a = 0;
  long b = 1;
  while (N > 0) {
    long tmp = a;
    a = b;
    b = b + tmp;
    --N;
  }
  return a;
}

int main(int argc, char** argv) {

  std::chrono::system_clock::time_point t1;
  std::chrono::system_clock::time_point t2;
  float elapsed_seconds;

  if (argc != 3) {
    exit(EXIT_FAILURE);
  }
  int N = std::stoi(argv[1]);
  int M = std::stoi(argv[2]);

  // naive
  t1 = std::chrono::system_clock::now();
  long f1 = fibonacci_naive(N);
  t2 = std::chrono::system_clock::now();
  elapsed_seconds = std::chrono::duration<float>(t2 - t1).count();
  std::cout << elapsed_seconds << std::endl;

  // tail recursive
  t1 = std::chrono::system_clock::now();
  long checksum_f2 = 0;
  for (int i = 0; i < M; ++i) {
    checksum_f2 += fibonacci_tailrec(N);
    checksum_f2 %= 2147483647;
  }
  t2 = std::chrono::system_clock::now();
  elapsed_seconds = std::chrono::duration<float>(t2 - t1).count();
  std::cout << elapsed_seconds << std::endl;

  // iterative
  t1 = std::chrono::system_clock::now();
  long checksum_f3 = 0;
  for (int i = 0; i < M; ++i) {
    checksum_f3 += fibonacci_iterative(N);
    checksum_f3 %= 2147483647;
  }
  t2 = std::chrono::system_clock::now();
  elapsed_seconds = std::chrono::duration<float>(t2 - t1).count();
  std::cout << elapsed_seconds << std::endl;

  // print checks
  std::cout << f1 << std::endl;
  std::cout << checksum_f2 << std::endl;
  std::cout << checksum_f3 << std::endl;
}

