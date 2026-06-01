---
source: https://www.youtube.com/watch?v=zi0rHwfiX1Q
type: video
file: "[[John Hughes - Testing the Hard Stuff and Staying Sane.mkv]]"
tags:
  - property-based-testing
  - quickcheck
  - erlang
  - functional-programming
  - state-machine-testing
  - concurrency
  - automotive-software
---


## Auto Summary

John Hughes co-invented QuickCheck with Koen Claessen at Chalmers University in 1999 and founded Quviq AB to build the commercial Erlang version that drives the examples here. The war stories are real industrial engagements: the CAN-stack and dispenser bugs come from Quviq's AUTOSAR acceptance-testing project for Volvo Cars (20,000 lines of QuickCheck against a million lines of C across six suppliers, surfacing roughly 200 defects, 100 of them in the standard itself), and the parallel race-condition example traces a notorious bug in Erlang's dets storage layer that had plagued Klarna's production systems for years. A written version appears as "Experiences with QuickCheck: Testing the Hard Stuff and Staying Sane" in the 2016 Festschrift A List of Successes That Can Change the World.

