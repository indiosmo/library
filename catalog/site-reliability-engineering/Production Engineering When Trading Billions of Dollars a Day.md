---
source: https://www.youtube.com/watch?v=zR9PpXWsKFQ
type: video
file: "[[Production Engineering When Trading Billions of Dollars a Day.webm]]"
tags:
  - jane-street
  - site-reliability-engineering
  - incident-response
  - algorithmic-trading
  - monitoring
  - lecture
  - ocaml
---

## Description

What's it like to monitor and operate software that trades billions of dollars a day on stock markets around the world?

When your software has near-unlimited access to your bank account, every single message counts. Speedy alerting and incident response have a direct and measurable impact on the P&L.

In this talk, Mark Doss, a production engineer at Jane Street, explores the day-to-day technical operations of a trading firm, with a heavy focus on what happens when things go wrong. He covers the unique features of the trading environment that make production engineering especially high-stakes, how Jane Street approaches monitoring and alerting (and why traditional SLO-based approaches often fall short), the role of defense in depth and cross-team communication, and walks through a realistic sample incident to make it all concrete.

00:00 Video starts
00:05 About Mark Doss
00:27 Intro and Talk Outline
05:29 Features of the production environment
17:07 What it means for Production Engineering at Jane Street
37:22 Sample Incident
49:26 Summary of Production Engineering at Jane Street
51:17 Q+A

## Auto Summary

Mark Doss is a production engineer at Jane Street, the quantitative proprietary trading firm known for running its trading systems in OCaml, and this is part of the firm's public Tech Talks series. Beyond the mechanics of monitoring, Doss stresses that trader-to-technologist communication is often the turning point in incidents: when systems look healthy but a trader reports market data "looks weird," that business signal resolves outages faster than telemetry alone. He also describes Jane Street's deliberately decentralized, near-zero-top-down-edict approach to alerting, its obsession with signal-to-noise ratio, and a no-BS communication culture that lets engineers flag errors without reputational cost. A talk with the same title was separately presented by another Jane Street engineer at USENIX SREcon25 Americas.

