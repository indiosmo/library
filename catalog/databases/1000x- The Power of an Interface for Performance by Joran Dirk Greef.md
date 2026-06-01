---
source: https://www.youtube.com/watch?v=yKgfk8lTQuE
type: video
file: "[[1000x- The Power of an Interface for Performance by Joran Dirk Greef.webm]]"
tags:
  - tigerbeetle
  - performance
  - systems-programming
  - api-design
  - zig
  - concurrency
  - financial-systems
---

## Description

As systems programmers, we tend to think of performance as all the low-level techniques we can and should apply in the implementation of a system.
For example, static memory allocation, amortization, zero-deserialization, zero-copy, direct memory access, memory locality, data-oriented design, cache-line alignment, explicit limits, concurrency, parallelism, pipelining, scheduling, hardware acceleration, branch prediction, vectorization, loop unrolling, profiling, io_uring, or more explicit systems languages such as Zig or Rust.

However, while these techniques can increase performance by 10% or even 2x or 10x, and while they are important (and all add up!), they typically do not achieve the two to three order of magnitude gains required to really move the needle, and break the sound barrier.

Worse, no matter the skill of the craftsperson, or the quality of their implementation, these techniques may be powerless to push past the bottleneck of broken protocols or flawed function signatures, if these interfaces are not co-designed in view of the system.

Yet, for all their power to destroy performance, interfaces are also the doors and windows of our architectures, and as mediators of information exchange to and from our implementations, they have power to unlock performance!
Join us as we deconstruct and reconstruct one of the world's most popular interfaces, to show the power of an interface for performance.

https://www.linkedin.com/in/joran-dirk-greef/
https://x.com/jorandirkgreef
https://tigerbeetle.com/

## Auto Summary

Joran Dirk Greef is the founder and CEO of TigerBeetle, an open-source financial accounting database written in Zig. The talk uses TigerBeetle's design to argue that the interface (programming model) - not low-level implementation tricks - is what unlocks orders-of-magnitude gains, with the central example being amortizing away network round-trips through batching and a rethink of database concurrency control to escape the per-account transaction ceiling that general-purpose databases hit on contended hot keys. The PostgreSQL consultancy Cybertec later reproduced similar order-of-magnitude improvements by applying the talk's batching and tight-core-loop patterns to a conventional RDBMS.

