# Simple Language Benchmarks

Benchmark collection of random problem + language combinations.

Comes with a framework making it easy to contribute, run, and visualize new solutions.
This website is auto-generated from the results.

[Benchmarks page](https://bluenote10.github.io/SimpleLanguageBenchmarks)

Disclaimer:
This is a fun project, without putting too much though into experiment design.
Draw conclusions at your own risk.



## Philosophy


- **Simple solutions first**: The first implementation for every language should be a non-optimized, naive, or idiomatic attempt
  at solving the problem. This allows to get a feeling of the out-of-the-box performance of a language, i.e., the performance
  one can expect without thinking about optimization.
  For many languages this implies to avoid parallelization and stick to a simple single-threaded solution.
  Additional implementations may use any kind of optimization.
- **Code elegance**: Instead of trying to measure code complexity by some metric, the framework tries to make it very easy to jump into the source code
  of each individual implementation, allowing to study the code directly on Github.
- **No excluded languages**: In contrast to the [benchmarksgame](http://benchmarksgame.alioth.debian.org/play.html)
  no languages are forbidden per-se. In particular the goal is to add languages which are excluded in other benchmarks (e.g. Nim, Crystal, and Julia).



## About the Framework

The framework allows to quickly run a set of benchmarks and generates output to visualize the results.
All HTML on this page is auto-generated.

Each benchmark problem is split into **stages**, i.e., the solution is computed in several steps and
each step is measured individually (implementations are responsible themselves to measure the time for each step).
In some cases splitting the solutions into several steps will feel slightly non-idiomatic and inefficient,
but it comes with the benefit to disentangle e.g. I/O from the computations and in some cases reveals
interesting results like a language being particularly good/bad in certain steps.

Each benchmark is performed with three different problem **sizes**: Currently, each problem comes in a
**s**mall, **m**edium, and **l**arge variant.

## Run Benchmarks

You can run all benchmarks for yourself or even create your own set of benchmarks.
The main framework is written in Python, and should be reproducible on any UNIX based system.

TODO: extend documentation

## Contribute

Contribution of any kind are highly welcome.
In particular it would be nice to see (more) implementations e.g. for the languages:
Nim, Rust, Go, Haskell, Closure, Kotlin, Julia, R, Crystal, Racket, Lua, Ruby, Java...

## License

This project is licensed under the terms of the MIT license.


