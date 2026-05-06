# Paper Note Template

Use this template for each new paper before merging durable findings into `paper_findings.md` or `docs/simulation_design_brief.md`.

## Metadata

- **Title:**
- **Authors:**
- **Year / venue:**
- **Local file or link:**
- **Primary category:** safe MARL, coordination, communication, LLM agents, robotics, value decomposition, policy gradient, benchmark, other
- **Read date:**
- **Status:** skimmed, partially read, fully read, implemented

## One-Sentence Takeaway

Write the shortest useful claim this paper adds to the project.

## Problem

What MARL problem does the paper address? Note the environment assumptions, observability assumptions, safety constraints, reward structure, and agent relationship.

## Method

Summarize the method in project terms:

- What is learned?
- What is centralized versus decentralized?
- What information is shared between agents?
- How are rewards, costs, constraints, or interaction signals handled?
- What baselines does the paper compare against?

## Results

Capture the findings that should influence this project:

- Best-performing settings:
- Failure cases or limitations:
- Sensitivity to agent count, heterogeneity, reward design, or environment:
- Reported metrics:
- Benchmarks or tasks:

## Simulation Implications

Translate the paper into concrete project changes:

- Environment feature to add:
- Baseline to add:
- Metric to track:
- Experiment to run:
- Logging needed:
- Risk or guardrail:

## Safety Implications

If relevant, identify:

- Cost signal:
- Constraint threshold:
- Joint safety failure mode:
- Per-agent safety failure mode:
- Reward-safety tradeoff:

## LLM-Agent Implications

If relevant, identify:

- Interaction trace type:
- Reward source:
- Judge or evaluator:
- Reward hacking risk:
- Diversity or role implication:
- External validation signal:

## Open Questions

- What is still unclear after reading?
- What would need to be reproduced before trusting the claim?
- Which follow-up paper should be read next?

## Action Items

- [ ] Add/update research summary.
- [ ] Add/update simulation design brief.
- [ ] Add/update experiment backlog.
- [ ] Add/update metrics list.
- [ ] Create implementation issue or task.
