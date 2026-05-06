# MARL Research Summary

This is the living research summary for the MARL simulation project. It turns papers in the workspace into project decisions, simulation milestones, and follow-up questions. Add new paper notes with the template in `docs/paper_note_template.md`, then fold durable implications back into this file and `docs/simulation_design_brief.md`.

## Current Reading Set

| Source | Topic | Current Use |
| --- | --- | --- |
| `2110.02793v2.pdf` | Multi-Agent Constrained Policy Optimisation, Gu et al., 2022 | Anchor paper for safe MARL constraints, cost tracking, and constrained baselines. |
| `MARL-Papers/2510.08529v2.pdf` | CoMAS: Co-Evolving Multi-Agent Systems via Interaction Rewards, Xue et al., ICLR 2026 | Anchor paper for LLM-agent interaction rewards, reward hacking risks, and heterogeneous agent groups. |
| `MARL-Papers/README.md` | Awesome-list style MARL index | Backlog for future papers across frameworks, LLMs, robotics, safety, coordination, and communication. |

## Working Thesis

The simulation scaffold should treat MARL as a joint-behavior problem, not just a collection of independent learners. The first useful version should expose:

- Reward and cost side by side.
- Per-agent behavior and joint outcomes side by side.
- Baseline policies and safety-aware variants side by side.
- Interaction traces when agents communicate, judge, or shape each other's rewards.

That makes the project extensible in two directions: classic safe MARL environments and LLM-agent experiments where interaction itself becomes part of the reward signal.

## Paper Findings

### MACPO: Safe MARL Needs Joint Safety

The MACPO paper frames safe MARL as a constrained Markov game. Its central point is that an agent can be locally safe while the joint behavior of multiple agents is unsafe. This matters for robotics, autonomous driving, and any system where agent interactions can create hazards.

The paper proposes two safety-aware model-free MARL algorithms:

- MACPO, which extends constrained policy optimization to multi-agent trust-region updates.
- MAPPO-Lagrangian, which adds Lagrangian safety penalties to a MAPPO-style clipped policy update.

The theoretical claim is strong: under the paper's assumptions, safe multi-agent policy iteration gives monotonic reward improvement and constraint satisfaction at every iteration.

Experimentally, both methods satisfy safety constraints much better than IPPO, MAPPO, and HAPPO on Safe Multi-Agent MuJoCo and Safe Multi-Agent Robosuite. HAPPO can still achieve higher reward, but it violates safety constraints, so the tradeoff is explicit: best raw reward is not necessarily deployable behavior.

### MACPO: Benchmarking Safety Is Part of the Contribution

The paper introduces two benchmark suites:

- SMAMuJoCo, safety-aware multi-agent MuJoCo tasks.
- SMARobosuite, safety-aware multi-agent Robosuite tasks.

These extend continuous-control MARL tasks by adding unsafe regions, obstacles, and cost constraints. For this project, that suggests the first evaluation harness should track both return and violation cost, and should report constraint violation as a first-class result rather than an auxiliary metric.

### CoMAS: Interaction Can Become Reward

CoMAS shifts MARL toward LLM-based agents. Its key idea is that agents can improve through multi-agent interaction without external reward signals. Instead of relying only on a rule verifier, reward model, confidence score, semantic entropy, or majority-vote pseudo-label, CoMAS derives rewards from discussion dynamics.

The framework has agents propose solutions, evaluate others, and score outputs. An LLM-as-judge mechanism converts interaction traces into rewards, and each agent is optimized with RL.

Across math, coding, and science benchmarks, CoMAS generally improves over untrained agents and is often state of the art against the selected baselines. The gains are sometimes modest, but repeated-seed results make the improvements more useful than one-off demonstrations.

### CoMAS: Reward Design Is Fragile

CoMAS ablations show that the interaction reward structure is important. Removing evaluation can make agents become increasingly strict judges. Removing scoring can lead to reward hacking, where agents support everything and drive reward toward the maximum.

For this project, any agent-generated reward should be instrumented for collusion, overly harsh judging, degenerate agreement, and divergence between interaction reward and task performance.

### CoMAS: More and More Diverse Agents Help

CoMAS reports positive scaling with agent count and diversity. Four-agent settings tend to beat smaller groups in several setups, and heterogeneous agents often outperform homogeneous ones.

The implication is that multi-agent benefit is not just duplication. Diversity of policies, roles, prompts, models, or observation access can improve group-level learning.

## Safe MARL Implications

- Define safety as an explicit cost signal with thresholds, not only as negative reward.
- Track per-agent costs, joint cost, and constraint violation frequency.
- Keep unconstrained baselines in the experiment matrix so reward-safety tradeoffs remain visible.
- Prefer environments with interpretable hazards early: collisions, unsafe zones, congestion, energy budget overruns, blocked rescue paths, or resource depletion.
- Separate training reward from reporting metrics so a high-return policy cannot hide unsafe behavior.
- Add safety curves over time, not just final averages, because transient unsafe exploration matters in constrained settings.

## LLM-Agent Reward Implications

- Preserve interaction traces as data: proposal, critique, vote, score, revision, and final answer/action.
- Treat agent-generated rewards as untrusted measurements that require audits.
- Track agreement rate, judge entropy, score inflation, score collapse, and reward-task correlation.
- Compare homogeneous groups against heterogeneous groups before assuming more agents are useful.
- Add anti-collusion checks when agents score each other or negotiate reward.
- Keep a non-interaction baseline so gains from discussion are not confused with gains from more inference compute.

## Candidate Simulation Milestones

1. **Single-machine scaffold:** run a tiny grid or continuous toy environment with two to four agents, deterministic seeds, and episode logs.
2. **Baseline MARL loop:** compare independent learners against a shared/cooperative baseline with common reward and per-agent observations.
3. **Safety layer:** add hazards, cost budgets, and violation reports without changing the core environment API.
4. **Constrained baseline:** add a simple Lagrangian or penalty-based constrained learner to make reward-cost tradeoffs visible.
5. **Interaction logging:** record agent communication, votes, or coordination messages as structured traces.
6. **LLM-agent prototype:** run a small non-physical task where agents propose, critique, and score decisions; start with frozen agents before training.
7. **Heterogeneity sweep:** compare identical agents with role-diverse or model-diverse agents.
8. **Research dashboard:** summarize return, safety, coordination, and reward-quality metrics across seeds and experiment configs.

## Metrics to Track

| Metric Family | Metrics | Why It Matters |
| --- | --- | --- |
| Reward | episode return, per-agent return, team return, reward variance | Measures task success and exposes instability across agents. |
| Safety | total cost, per-agent cost, cost rate, constraint violation rate, worst-episode cost | Distinguishes deployable policies from high-reward unsafe policies. |
| Coordination | collision rate, resource conflicts, joint action entropy, role utilization, communication count | Shows whether agents are learning useful joint behavior. |
| Robustness | seed variance, policy performance under perturbed hazards, held-out scenario return/cost | Prevents overfitting to one layout or interaction pattern. |
| LLM interaction | agreement rate, judge entropy, score inflation, score-task correlation, critique diversity | Detects reward hacking and low-value consensus. |
| Efficiency | sample steps, wall time, tokens, judge calls, environment steps per improvement | Keeps experiments comparable when agents or judges add compute. |

## Open Questions

- What should the first simulation domain be: grid-world safety, traffic-like routing, pursuit/evasion, resource allocation, or a small robotics-inspired continuous task?
- Should the initial constrained baseline use a simple penalty, a Lagrangian multiplier, or a closer MAPPO-Lagrangian analogue?
- How much LLM-agent work should happen inside the same simulation harness versus in a parallel text-task harness?
- Which papers from the `MARL-Papers/README.md` index should be promoted next: MAPPO, HAPPO/HATRPO, QMIX, communication, or autonomous driving safety?

## Maintenance Notes

- Add detailed notes for each new paper using `docs/paper_note_template.md`.
- Keep this file short enough to scan; move implementation-facing detail to `docs/simulation_design_brief.md`.
- When a paper changes a milestone, metric, or risk, update the relevant section here and cite the paper in the current reading set.
