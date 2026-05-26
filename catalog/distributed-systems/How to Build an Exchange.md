---
source: https://www.youtube.com/watch?v=b1e4t2k2KJY
type: video
file: "[[How to Build an Exchange.webm]]"
tags:
  - market-microstructure
  - low-latency
  - jane-street
  - matching-engines
  - replication
  - lecture
---

## Description

Electronic exchanges play an important role in the world financial system, acting as focal points where actors from across the world meet to trade with each other.

But building an exchange is a difficult technical challenge, requiring high transaction rates, low, deterministic response times, fairness, and reliability.

This talk looks at the question of how to design an exchange through the lens of JX, a crossing engine we built at Jane Street in the last two years.  Performance plays an interesting role in this design, in that, although the end-to-end latency of the system is not important in and of itself, the ability of individual components of JX to handle messages rates in the 500k/sec range with latencies in the single-digit microseconds helped us build a replicated system that is both simple and robust.

## Auto Summary

Brian Nigito, a senior technologist at Jane Street and former Chief Software Architect at Island ECN (widely regarded as the birthplace of the modern electronic exchange), draws on over two decades of exchange-level and high-frequency trading experience across Citadel, GETCO, and Chi-X Europe. This was the inaugural Jane Street public tech talk, held at their New York office in February 2017. The central architectural insight is that JX's replication layer uses reliable multicast rather than consensus protocols like Paxos, a design made viable only because every component can sustain 500k msg/sec at single-digit-microsecond latency, making raw performance an enabler of simplicity rather than an end in itself.

