use std::env;
use std::process;
use std::time::{Instant, Duration};

fn fibonacci_naive(n: u64) -> u64 {
    if n < 2 {
        n
    } else {
        fibonacci_naive(n-1) + fibonacci_naive(n-2)
    }
}

fn fibonacci_tailrec(n: u64, a: u64, b: u64) -> u64 {
    if n == 0 {
        a
    } else {
        fibonacci_tailrec(n-1, b, a+b)
    }
}

fn fibonacci_iterative(n_orig: u64) -> u64 {
    let mut a: u64 = 0;
    let mut b: u64 = 1;
    let mut n = n_orig;
    while n > 0 {
        // unclear if Rust supports syntax like this (https://github.com/rust-lang/rust/issues/10174):
        // (a, b) = (b, a + b);
        let tmp = a;
        a = b;
        b = a + tmp;
        n -= 1;
    }
    a
}

fn duration_in_sec(d: Duration) -> f64 {
    (d.as_secs() as f64) + ((d.subsec_nanos() as f64) / 1_000_000_000 as f64)
}

fn main() {
    let args: Vec<_> = env::args().collect();
    if args.len() != 3 {
        println!("Unexpected number of arguments.");
        process::exit(1);
    }

    let n = args[1].parse::<u64>().unwrap();
    let m = args[2].parse::<u64>().unwrap();

    let time1 = Instant::now();
    let f1 = fibonacci_naive(n);
    println!("{}", duration_in_sec(time1.elapsed()));

    let time2 = Instant::now();
    let mut checksum_f2 = 0;
    for _ in 0..m {
        checksum_f2 += fibonacci_tailrec(n, 0, 1);
        checksum_f2 %= 2147483647
    }
    println!("{}", duration_in_sec(time2.elapsed()));

    let time3 = Instant::now();
    let mut checksum_f3 = 0;
    for _ in 0..m {
        checksum_f3 += fibonacci_iterative(n);
        checksum_f3 %= 2147483647
    }
    println!("{}", duration_in_sec(time3.elapsed()));

    println!("{}", f1);
    println!("{}", checksum_f2);
    println!("{}", checksum_f3);
}