---
source: https://www.youtube.com/watch?v=139UPjoq7Kw
type: video
file: "[[Horace He- Building Machine Learning Systems for a Trillion Trillion Floating Point Operations.webm]]"
tags:
  - machine-learning
  - pytorch
  - compilers
  - gpu-computing
  - distributed-training
  - horace-he
  - jane-street
---

## Description

Over the last 10 years we've seen Machine Learning consume everything, from the tech industry to the Nobel Prize, and yes, even the ML acronym. This rise in ML has also come along with an unprecedented buildout of infra, with Llama 3 now reaching 4e25 floating point operations, or 40 yottaflops, or 40 trillion trillion floating point operations.

To build these ML models, you need ML systems, like PyTorch. In this talk, Horace will (attempt to) answer: 
- How have ML systems evolved over time to meet the training needs of ML models? How does building ML systems differ from regular systems?
- How do we get the most out of a single GPU? What's the point of compilers if we're just training a single model?
- And what is the right way to think about scaling to 10s of thousands of GPUs?

## Auto Summary

Horace He is a former Meta/PyTorch engineer known for creating torch.compile and FlexAttention, now at Thinking Machines. This talk, delivered as a Jane Street tech talk in December 2024, traces the evolution of ML frameworks from declarative graph-based systems to PyTorch's imperative model and covers single-GPU compiler optimizations and the challenges of distributed training across tens of thousands of GPUs.

