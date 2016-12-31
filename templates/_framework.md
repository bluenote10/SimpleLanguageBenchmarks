The framework allows to quickly run a set of benchmarks and generates output to visualize the results.
All HTML on this page is auto-generated.

Each benchmark problem is split into **stages**, i.e., the solution is computed in several steps and
each step is measured individually (implementations are responsible themselves to measure the time for each step).
In some cases splitting the solutions into several steps will feel slightly non-idiomatic and inefficient,
but it comes with the benefit to disentangle e.g. I/O from the computations and in some cases reveals
interesting results like a language being particularly good/bad in certain steps.

Each benchmark is performed with three different problem **sizes**: Currently, each problem comes in a
**s**mall, **m**edium, and **l**arge variant.