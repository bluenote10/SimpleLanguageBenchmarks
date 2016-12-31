
- **Simple solutions first**: The first implementation for every language should be a non-optimized, naive, or idiomatic attempt
  at solving the problem. This allows to get a feeling of the out-of-the-box performance of a language, i.e., the performance
  one can expect without thinking about optimization.
  For many languages this implies to avoid parallelization and stick to a simple single-threaded solution.
  Additional implementations may use any kind of optimization.
- **Code elegance**: Instead of trying to measure code complexity by some metric, the framework tries to make it very easy to jump into the source code
  of each individual implementation, allowing to study the code directly on Github.
- **No excluded languages**: In contrast to the [benchmarksgame](http://benchmarksgame.alioth.debian.org/play.html)
  no languages are forbidden per-se. In particular the goal is to add languages which are excluded in other benchmarks (e.g. Nim, Crystyl, and Julia).

