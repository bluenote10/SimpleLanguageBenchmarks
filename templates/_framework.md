The framework allows to quickly run a set of benchmarks and generates output to visualize the results.
All HTML on this page is auto-generated.

Each benchmark problem is split into **stages**, i.e., the solution is computed in several steps and
each step is measured individually (implementations are responsible themselves to measure the time for each step).
The total runtime is obtained by adding up the runtimes of all stages.

In some cases splitting the solutions into several steps will feel slightly non-idiomatic and inefficient,
but it comes with the benefit to disentangle for instance I/O from the computations.
Moreover, it sometimes reveals interesting results like a language being particularly fast in a certain step
while being slow in a different step.

Each benchmark is performed with three different problem **sizes**: Currently, each problem comes in a
**s**mall, **m**edium, and **l**arge variant.