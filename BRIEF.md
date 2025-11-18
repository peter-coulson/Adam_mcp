# Project Brief

## Overview

Build a minimal MCP server that exposes a small set of CAD actions ("tools") for a CAD program of your choice (Fusion 360, Onshape, FreeCAD, SolidWorks, Rhino/Grasshopper).

## What to Build

Implement a lightweight MCP server that:

1. Registers a handful of tools that feel natural for the chosen CAD
   - Keep it minimal: we prefer 3–5 great tools over 12 half-baked ones.
2. Handles arguments & validation.
3. Can run locally.
4. Demonstrates a minimal flow
   - Create a rounded box: sketch rectangle → extrude → fillet edges.

## Deliverables

- README.md with setup, run instructions, and a quick start example.
- Server code (any language is fine; TypeScript/Python are great).
- Short demo (optional but helpful): a 1–3 minute screen recording showing the tools being called and the CAD responding.
- Notes.md with:
  - Design decisions and tradeoffs.
  - What you'd do next with more time.
  - Any limitations or known issues.
