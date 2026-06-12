---
source: https://www.youtube.com/watch?v=wVRZESuXMdQ
type: video
file: "[[Webinar- A Deep Dive into Sequencer Architectures.webm]]"
tags:
  - low-latency-trading
  - aeron
  - state-machine-replication
  - consensus
  - high-availability
  - fault-tolerance
  - webinar
---

## Description

Join Adaptive’s Paul Weiss and David Smith and discover how sequencer architectures deliver deterministic, low‑latency trading workflows at scale. We break down non‑gating, gating, and consensus designs; show how state machine replication and snapshots guarantee fast recovery; and share patterns for active/active services with duplicate suppression. 

Learn the performance techniques—pipelining, asynchronous replication, and state‑machine composition—that keep latency and jitter under control across end‑to‑end flows.
‎ 
𝗪𝗵𝗮𝘁 𝘆𝗼𝘂’𝗹𝗹 𝗹𝗲𝗮𝗿𝗻:

▪️​ The core building blocks of sequencer architectures, when to use non‑gating vs. gating vs. consensus, and how to reason about their trade‑offs.
‎ 
▪️​ How deterministic state machines and global ordering work together to guarantee correctness across distributed components.
‎ 
▪️​ Practical snapshotting strategies (and where to store them) to enable fast recovery—even when a host is lost.
‎ 
▪️​ Patterns for active/active and active/warm availability modes across gateways and engines, plus duplicate suppression on the sequencer path.
‎ 
▪️​ Performance playbook: pipelining, asynchronous replication, batching, and composing state machines to cut hop‑latency and tail jitter.
‎ 
𝗪𝗵𝗼 𝘀𝗵𝗼𝘂𝗹𝗱 𝘄𝗮𝘁𝗰𝗵:
‎ 
▪️​ Platform and trading‑system architects, heads of engineering, and senior developers designing low‑latency, highly available, and consistent trading platforms.
‎ 
By the end, you’ll have a clear mental model for designing resilient, deterministic trading systems with sequencers at the core—what to build, where to place it, and how to keep performance and correctness non‑negotiable.

𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗳𝗼𝗿 𝗼𝘂𝗿 𝘂𝗽𝗰𝗼𝗺𝗶𝗻𝗴 𝘀𝗲𝘀𝘀𝗶𝗼𝗻 𝗮𝘁: https://aeron.io/webinar

𝗟𝗲𝗮𝗿𝗻 𝗺𝗼𝗿𝗲 𝗮𝗯𝗼𝘂𝘁 𝘂𝘀:
🔗​ https://weareadaptive.com
🔗​ https://aeron.io

## Auto Summary

The webinar comes from Adaptive Financial Consulting, the trading-technology consultancy that acquired Martin Thompson and Todd Montgomery's Real Logic in 2022 and now stewards the open-source Aeron messaging stack (originally built in 2014 for CME). The sequencer designs discussed are the conceptual foundation of Adaptive's newly announced Aeron Sequencer, a replicated-state-machine platform with a globally ordered, highly available message log built on the same Raft-based consensus ideas as Aeron Cluster. Paul Weiss is one of Adaptive's CTO-level engineers; the patterns presented generalize the firm's Hydra Platform experience building bespoke exchange and broker-dealer systems.

