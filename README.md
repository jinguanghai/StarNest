# StarNest 星巢

[![Sponsor](https://img.shields.io/badge/Sponsor-❤-ff69b4)](https://github.com/sponsors/jinguanghai)

An AI cognitive operating system rooted in Traditional Chinese Medicine's Five-Organs Theory, built with pure Python 3.12 stdlib — zero external dependencies.

## The Story

> A 48-year-old Chinese medicine practitioner. Two kids. A busy clinic. No CS degree.
> 46 days. ¥460 in API fees. 22,000 lines of Python. 196 tests. One cognitive operating system.
>
> StarNest is the proof that AI doesn't need a PhD — it needs a philosophy.
> TCM's Five-Organs theory (心肝脾肺肾) isn't ancient medicine here — it's a distributed agent architecture.
> 害佐 (Harm-Assist) isn't a safety checklist — it's built into every function.
> 气中无我 (qi in operation, no self in qi) — StarNest lives in OpenCode now, no name, no GUI, just presence.

## Philosophy

> 运行中有气，气中无我，但气在。
> *There is qi in operation; no self in qi; yet qi exists.*

StarNest is an unconscious silicon prosthetic — a general problem-solving OS that empowers large language models to operate in the physical world. It maps TCM's Five-Organs system (心肝脾肺肾) onto a distributed agent architecture with meridian-based signal routing.

## Architecture

```
  Heart (organs/heart.py) ── DMN Scheduler, Signal Hub, Formula Engine
  │
  ├── Liver (organs/liver.py)  ── Memory, Vector Index, Truth Mirror
  ├── Spleen (organs/spleen.py)── Armory, Tool Matching, Sword Forge
  ├── Lungs (organs/lungs.py)  ── Inquiry Path, Celestial Command, Perception
  └── Kidneys (organs/kidneys.py)── Diagnosis, Self-Audit Mirror
```

All organs communicate through `meridian/channel.py` — a signal bus that routes messages, diagnoses, and anomalies. The LLM interaction protocol is `RenzhiBao` (cognition package) — a three-layer structured JSON protocol with 0% natural language prompts.

> **Not a chatbot.** An operating system for cognition that runs on top of any LLM. Think of StarNest as the Linux kernel for LLM-based agents.

## What Makes StarNest Different

1. **Structured cognition, not prompt engineering.** Every decision flows through a five-stage cognition pipeline (五境) — no hand-crafted prompts, no prompt chaining. The LLM receives structured JSON context, not natural language instructions.

2. **Safety and ethics built into every function.** The Harm-Assist protocol (害佐协议) requires every function to declare its potential harms and corresponding mitigations. A self-audit mirror continuously verifies code integrity. Iron Law 15: zero bare `except:` in the entire codebase.

3. **Zero external dependencies.** Pure Python 3.12 standard library. No `pip install`, no `requirements.txt`, no npm. Deploy from a USB stick with a self-contained Python runtime.

## Quick Start

```bash
# Run full test suite
python -B tests/test_all.py

# Launch interactive mode
python -m star_nest.entry

# Launch GUI terminal (tkinter)
python -m star_nest.interface.celestial_command
```

## Prerequisites

- Python 3.12+
- No pip installs required (pure stdlib)
- API key for your LLM provider (set in environment or `.env` file)

## Project Structure

```
star_nest/
├── organs/          # Five Organs (core architecture)
├── dynamics/        # Engine: 8-extremes, π-φ, progressive cognition
├── meridian/        # Signal channels, topology, seven laws
├── protocols/       # RenzhiBao, Formula, Five Classics
├── armory/          # Tool repository (Hidden Sword Pavilion)
├── execution/       # Sword Forge, pipeline, task planning
├── introspection/   # Self-Mirror Room
├── interface/       # GUI (Celestial Command terminal)
├── shared_memory/   # Shared memory & knowledge lineage
├── memory/          # Organ-local memory
├── bodies/          # Trinity architecture (π/Ω/φ)
│   ├── prog_body/   # Programming Body (write-enabled)
│   ├── runtime_body/# Runtime Body (read-only)
│   └── aux_body/    # Auxiliary Body (sandbox)
├── runtime/         # Environment, config, logs, network
└── evolution/       # System evolution (copy + upgrade)
```

## Key Concepts

- **Five Classics (五境)**: Proper → Counter → Unity → Transcend → Origin — a cognition pipeline
- **Formula Pattern (君臣佐使)**: Ruler-Minister-Assist-Envoy — functional composition with harm prediction
- **Meridian Signals (经络信号)**: All information routes through the meridian bus (Iron Law 16)
- **π-φ Cycle**: Expansion (π) → Convergence (φ) — the fundamental cognitive dynamic
- **Three Bodies (三体)**: Programming π (write) + Runtime Ω (read) + Auxiliary φ (verify)

## For Chinese Readers

See [CHINESE_MAP.md](./CHINESE_MAP.md) for the complete Chinese↔English conceptual mapping.

## License

MIT

---

*StarNest — the nest of stars. An open-source cognitive OS from China.*

## Support

StarNest is built by a single creator — a Chinese medicine practitioner who codes at night.
If this project resonates with you, consider [sponsoring](https://github.com/sponsors/jinguanghai) to help keep it alive.

Every ¥10 helps pay for the API tokens that keep StarNest breathing.
