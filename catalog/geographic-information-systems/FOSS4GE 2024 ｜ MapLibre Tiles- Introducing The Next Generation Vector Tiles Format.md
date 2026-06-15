---
source: https://www.youtube.com/watch?v=YHcoAFcsES0
type: video
file: "[[FOSS4GE 2024 ｜ MapLibre Tiles- Introducing The Next Generation Vector Tiles Format.mkv]]"
tags:
  - vector-tiles
  - openstreetmap
  - data-compression
  - columnar-storage
  - web-mapping
  - open-source
  - conference-talk
---

## Description

This talk introduces a new vector tiles format called MapLibre Tiles (MLT), which offers a significant tile size reduction and accelerated decoding performance compared to the de-facto standard Mapbox Vector Tiles (MVT). MLT also adds support for missing features like nested properties, linear referencing and M-values. The design of MLT is influenced by the latest research results on big data analytics formats and adapted for the map visualization use case. 

Our evaluation against MVT on a OpenMapTiles schema based tileset shows a reduction in tile size of nearly up to 80% with even faster decoding times. Moreover, on a already highly optimized Bing Maps tileset, MLT achieves reductions of up to 40% in size. Based on these results, Microsoft generously donated to MapLibre to integrate MLT into the mapping stack.

Additionally, we will explore how next-generation map rendering libraries can leverage SIMD and WebGPU compute shaders for processing to fully  utilize the potential of MLT.




Markus Tremmel

https://talks.osgeo.org/foss4g-europe-2024/talk/QC8L7A/

Room: LAStools (327) @ 03.07.2024 10:30:00

#foss4ge2024
#GeneralTrack
#StateOfSoftware

## Auto Summary

Speaker Markus Tremmel (Rohde & Schwarz) invented the MLT format; the FOSS4G Europe 2024 talk was delivered in the StateOfSoftware/General track at the Tartu conference. MLT grew out of a four-week proof-of-concept commissioned by Microsoft and executed by Stamen with Dane Springmeyer, and its core innovation is a column-oriented (Decomposition Storage Model) layout borrowed from analytics formats like Parquet, replacing MVT's row-oriented design to enable column-specific compression and vectorized decoding. The work was later formalized in a 2025 ACM SIGSPATIAL paper by Tremmel and Roland Zink, and MLT shipped in MapLibre GL JS and MapLibre Native in early 2026.

