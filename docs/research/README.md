# Research Tracking

This folder tracks the reading stream for the MARL task-allocation simulation.
Keep it lightweight: add a row to the matrix, create a short note from the
template when a paper becomes important, and update open research questions as
the implementation direction sharpens.

## Current Paper Themes

Known themes from the repo context and working roadmap:

- **Q-learning foundations:** tabular value learning, temporal-difference
  updates, exploration schedules, and the bridge from single-agent control to
  independent multi-agent learners.
- **Policy gradients:** direct policy optimization, stochastic policies,
  variance reduction, and the actor-critic family that underpins modern MARL
  methods.
- **DQN-style value learning:** replay buffers, target networks, discrete
  action control, and stability concerns when applied independently per agent.
- **PPO and MAPPO:** clipped policy optimization, centralized training with
  decentralized execution, shared policies, and the fit with the environment's
  `state()` interface.
- **VDN, QMIX, and QTRAN:** cooperative value decomposition methods for team
  reward settings, with attention to monotonic mixing assumptions and credit
  assignment.
- **COMA:** counterfactual baselines for multi-agent credit assignment in
  cooperative settings.
- **MADDPG-style actor-critic:** centralized critics with decentralized actors,
  especially useful when comparing discrete versus continuous control variants.
- **Communication:** learned messages, explicit coordination channels, and
  whether task allocation benefits from agent-to-agent information exchange.
- **UAV task allocation:** domain framing for multi-agent routing, assignment,
  service timing, energy constraints, partial observability, and scalability.
- **Game-theoretic MARL foundations:** Markov games, team Markov games,
  Nash-equilibrium learning, opponent adaptation, WoLF/PDWoLF, AWESOME, and
  Hyper-Q-style opponent modeling.
- **Deep MARL stability and scale:** replay stabilization, recurrent
  coordination networks, decentralized multi-task learning, partial
  observability, and mean-field approximations for many agents.
- **Safe MARL:** constrained policy optimization, bilevel/Stackelberg
  formulations, autonomous-driving safety, collision constraints, and
  constraint-aware evaluation.
- **LLM-based multi-agent systems:** LLM agent surveys, theory-of-mind
  collaboration, mutual human-AI modeling, interaction rewards, self-evolving
  agents, and LLM-assisted research workflows.

Do not invent full citations. If only a filename, keyword, or theme is known,
record that and mark the citation fields as `TBD`.

## Files

- [literature_matrix.md](literature_matrix.md): one-row-per-paper overview for
  quick sorting and gap spotting.
- [paper_note_template.md](paper_note_template.md): copy this into a new note
  when a paper deserves more detail.
- [research_questions.md](research_questions.md): working questions that connect
  literature themes to the current task-allocation environment.

## Suggested Workflow

1. Add a row to `literature_matrix.md` as soon as a new paper appears.
2. Use rough tags first, such as `value-decomposition`, `policy-gradient`, or
   `uav-task-allocation`.
3. Create a note from `paper_note_template.md` only after the paper looks useful
   for algorithm design, environment design, evaluation, or writing.
4. Move questions in `research_questions.md` from open to answered when there is
   enough evidence from papers or experiments.

## Naming Notes

Recommended note path:

```text
docs/research/notes/YYYY-short-paper-slug.md
```

Example:

```text
docs/research/notes/TBD-mappo-cooperative-baselines.md
```
