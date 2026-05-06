# MARL Simulation Design Brief

This brief translates the current research summary into a scaffold plan for the MARL simulation. It is intentionally implementation-facing, but it does not prescribe code structure yet.

## Design Goals

- Support multiple agents with per-agent observations, actions, rewards, costs, and episode traces.
- Make joint safety visible from the first working environment.
- Keep unconstrained and constrained baselines comparable under the same logging schema.
- Preserve communication and judgment traces so LLM-agent experiments can reuse the same analysis habits.
- Prefer small deterministic experiments before scaling to richer physics or LLM judging.

## Initial Environment Shape

Start with a compact environment that can be understood from logs:

- Two to four agents.
- Shared task reward.
- Per-agent observations with optional partial observability.
- Hazards that create cost independently from reward.
- Joint failures such as collisions, blocked paths, unsafe crowding, or resource contention.
- Configurable seeds, layouts, agent counts, and safety budgets.

A grid-world rescue/routing task is a good first candidate because it can express safety constraints without requiring a physics stack. Later versions can map the same logging and metric schema onto MuJoCo-style or robotics-inspired domains.

## Agent Variants

| Variant | Purpose | Expected Learning |
| --- | --- | --- |
| Random / scripted | Smoke test and metric sanity check | Episode traces and violation counters work. |
| Independent learner | Unconstrained baseline | Local learning can produce poor joint safety. |
| Shared cooperative learner | Team-reward baseline | Shared reward improves coordination but may still violate constraints. |
| Penalty or Lagrangian learner | First constrained baseline | Cost budgets become visible in policy updates. |
| Role-diverse agents | Heterogeneity test | Different roles may improve coordination and safety. |
| LLM-guided agents | Interaction-reward prototype | Proposal, critique, and scoring traces can shape behavior. |

## Safety Model

Use separate reward and cost channels:

- `reward`: task progress, completion, efficiency, cooperation.
- `cost`: unsafe zone entry, collision, blocked teammate, wasted shared resource, excessive risk, or rule violation.
- `constraint`: budget or threshold over episode cost, rolling cost rate, or per-agent maximum.

Report safety in at least three ways: total episode cost, violation frequency, and worst-case episode cost. This keeps averages from hiding rare but severe failures.

## LLM-Agent Interaction Model

For LLM-agent experiments, do not start with training. Start with instrumentation:

- Agents propose an action, plan, or answer.
- Agents critique or evaluate other proposals.
- Agents score outputs or select a joint decision.
- A judge or rule checker produces an external reference score when available.
- The logger records the full trace and derived reward.

Reward checks should compare interaction reward with task outcome. A high interaction reward with poor task performance should be marked as reward hacking risk.

## Experiment Matrix

Early experiments should be small and repeated across seeds:

| Axis | Values |
| --- | --- |
| Agent count | 2, 3, 4 |
| Agent homogeneity | identical policy, role-diverse policy, observation-diverse policy |
| Safety budget | none, loose, strict |
| Baseline | random/scripted, independent, cooperative, constrained |
| Observability | full state, local view, delayed or noisy signal |
| Interaction | none, fixed messages, critique/vote, judge-scored interaction |

## Milestone Plan

1. **Episode logger:** produce one JSON-like record per episode with config, seed, per-agent summaries, reward, cost, and events.
2. **Toy environment:** run deterministic two-agent episodes with hazards and visible joint failures.
3. **Baseline comparison:** add random/scripted and independent policies with the same metrics.
4. **Safety reporting:** add constraint thresholds, violation summaries, and reward-cost plots or tables.
5. **Constrained learner:** add penalty or Lagrangian behavior and compare against unconstrained baselines.
6. **Interaction traces:** store messages, votes, critiques, and scores without changing core reward/cost logging.
7. **LLM-agent pilot:** evaluate whether interaction reward correlates with task success before using it for training.
8. **Paper-driven expansion:** promote one paper at a time into a concrete experiment or metric.

## Core Metrics

- Episode return and team return.
- Per-agent return and return imbalance.
- Total cost, per-agent cost, and violation rate.
- Worst-case episode cost across seeds.
- Completion rate and time to completion.
- Collision, blocking, or unsafe-zone event counts.
- Coordination measures such as joint action entropy or role utilization.
- Seed variance for return and cost.
- For LLM agents: agreement rate, judge entropy, score inflation, critique diversity, and reward-task correlation.

## Risks and Guardrails

- **Reward hides safety:** Always report reward and cost separately.
- **Local safety hides joint failures:** Track joint events, not only per-agent events.
- **Constraint methods look worse by reward alone:** Compare Pareto-style reward versus cost, not only final return.
- **LLM judges drift or collude:** Add external task checks when possible and track score inflation.
- **More agents only add compute:** Include fixed-compute or no-interaction baselines when testing agent count.
- **Milestones become too broad:** Keep each paper-driven expansion tied to one environment, one metric, or one baseline.

## Next Paper Targets

- MAPPO / PPO in cooperative games for a practical baseline.
- HAPPO / HATRPO for agent-by-agent trust-region comparison.
- QMIX for value decomposition in cooperative discrete environments.
- Safe autonomous driving or robotics papers for richer constraint examples.
- Communication papers for structured interaction logging.
