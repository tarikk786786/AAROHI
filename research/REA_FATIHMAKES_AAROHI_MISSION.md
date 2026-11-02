# AAROHI — REA-led independent reconstruction research

## Objective
Use the official REA project (https://github.com/morluto/rea) as a local analysis instrument to investigate the publicly accessible FatihMakes projects and build an independently engineered, AAROHI-branded personal AI assistant in this repository.

This is an investigation and implementation brief, not a claim that the reference projects have already been fully reverse engineered.

## Authoritative repositories
- REA: https://github.com/morluto/rea.git
- Reference account: https://github.com/FatihMakes
- Reference repos:
  - https://github.com/FatihMakes/AI-Assistant-for-Computer
  - https://github.com/FatihMakes/AI-Assistant-1.1
  - https://github.com/FatihMakes/Jarvis-Mark-X
  - https://github.com/FatihMakes/Mark-X
  - https://github.com/FatihMakes/Mark-X.1
  - https://github.com/FatihMakes/Mark-X-TR
  - https://github.com/FatihMakes/Mark-LVI
  - https://github.com/FatihMakes/Mark-XXXIX-OR
- Target: https://github.com/tarikk786786/AAROHI
- Target branch: main
- Research branch: research/fatihmakes-rea-integration

## Current AAROHI facts verified from source
- Existing codebase is a Python/FastAPI-based Javis-derived agentic OS branded as AAROHI.
- README describes multiple model providers, voice, MCP, skills, memory, background tasks and an OpenMausBot companion.
- `main.py` imports `server.main:app`.
- `vercel.json` defines FastAPI app and CLI services.
- `AGENTS.md` identifies important invariants: internal Javis API/tool/session names must remain stable; both dashboard trees must be kept in sync; Vercel filesystem state must use /tmp; preserve host allowlist; secrets must never be committed.
- `requirements.txt` is carefully pinned; do not make casual dependency upgrades.
- Do not assume these documented features are all currently healthy. Verify them through actual tests and runtime inspection.

## Important REA operating rule
Clone REA and target projects into a separate local research workspace, not inside AAROHI's production source tree. Read REA's latest README, AGENTS.md, LICENSE, third-party notices, installation docs and MCP contracts. Install only the pinned supported Node runtime and dependencies. Verify actual CLI/MCP command names from REA's own help and generated tool catalog. Do not invent commands.

Use REA's applicable static analysis, CLI, MCP, provider and runtime observation workflows to inspect authorized local clones. Static analysis first; runtime observation only in a disposable sandbox with synthetic data. Never target private accounts, bypass login/DRM/security, exfiltrate data, or run untrusted programs against a production machine.

## Audit every reference repository
For all eight projects:
1. Clone the default branch and record repository URL, commit SHA, branch, license and last update.
2. Enumerate all files, entrypoints, manifests, dependencies and workflows.
3. Read README and all project documentation.
4. Identify UI, backend, assistant loop, model/provider calls, prompt/persona configuration, speech-to-text, text-to-speech, audio devices, GUI/event loop, computer control, OS calls, browser interactions, memory/persistence, tools, error handling and packaging.
5. Trace execution paths from user input through model/tool selection to output.
6. Use REA to analyze relevant JavaScript/Electron/native/.NET/Android/binary or runtime artifacts where actually applicable. Do not pretend REA supports a target it does not.
7. Run only safe, sandboxed public demos or tests, with synthetic prompts and dummy credentials.
8. Capture exact evidence: file path, symbol/function, line range or REA evidence/session reference, observed behavior, uncertainty and test command/result.
9. Compare versions and detect forks/duplicates using Git history, tree hashes and source diffs. Do not merge duplicate copies blindly.
10. Track every component's license and third-party notice. Reuse code only where license terms allow, preserve notices and attribution. Otherwise implement independently from documented behavior and observed interfaces.

If a repository does not have README.md or a guessed path returns 404, inspect the root tree and discover its real entrypoints. Do not treat missing README as missing repository.

## Deliverables to create under research/
- REPOSITORY_INVENTORY.md
- REPOSITORY_TREE_AND_ENTRYPOINTS.md
- LICENSE_AND_PROVENANCE.md
- PER_REPO_TECHNICAL_AUDITS/ (one audit per repository)
- REA_EVIDENCE_INDEX.md
- FEATURE_CATALOG.md
- CROSS_REPO_COMPARISON.md
- EXECUTION_AND_DATA_FLOWS.md
- SECURITY_AND_PERMISSION_REVIEW.md
- AAROHI_FEATURE_PRESERVATION_MATRIX.md
- AAROHI_TARGET_ARCHITECTURE.md
- IMPLEMENTATION_ROADMAP.md
- TEST_PLAN_AND_RESULTS.md
- KNOWN_LIMITATIONS.md

For each discovered feature record: source repository, source commit, evidence, functionality, triggering event, inputs/outputs, dependency/provider, permissions, state/persistence, errors and recovery, license status, AAROHI mapping, implementation status and tests.

## Implementation rules
1. First run baseline checks on current AAROHI and record existing failures before modifications.
2. Keep the existing AAROHI product, interface, voice/persona, model providers, brain/memory, MCP, skills, plugin/tool registry, background tasks, CLI and deployment behavior. Verify each from the source rather than relying only on README claims.
3. Preserve internal `javis_*` tool names, `JavisPet`, session keys, API paths and compatibility contracts unless a migration is proven safe and explicitly documented.
4. Do not overwrite or delete existing features, settings, user data, databases, environment variables or credentials.
5. Implement selected reference capabilities as small modules behind stable interfaces; no giant rewrite and no speculative framework additions.
6. Prefer existing AAROHI libraries and architecture. Add a dependency only with a demonstrated need and license/security review.
7. Separate domain logic, provider adapters, orchestration, runtime adapters and UI.
8. Expose capabilities accurately. Do not show fake enabled indicators or placeholder buttons.
9. Preserve security: explicit permissions for computer actions, bounded commands, filesystem allowlists, process ownership, confirmation for destructive/consequential actions, audit logs, cancellation, timeouts and cleanup.
10. Computer interaction must execute only on a trusted local/remote desktop worker. Do not try to run persistent desktop automation inside Vercel serverless functions.
11. Voice must use permission-aware microphone handling, selectable STT/TTS providers, interruption support and clear provider status.
12. Model integration must use the current AAROHI provider architecture; never hardcode keys or promise free/unlimited access without checking provider terms.
13. Keep frontend English as default and retain supported multilingual options.
14. Rebrand all user-facing UI and documentation as AAROHI while retaining legally required source notices and compatible internal interfaces.

## Required feature investigation
Prioritize these categories, but include any other real features discovered:
- Desktop GUI/assistant loop
- Voice input/STT and voice output/TTS
- Visual/avatar/animation behavior
- Prompt/persona configuration
- Model/provider selection and fallback
- Computer and OS automation
- Browser automation
- File and application operations
- Conversation state and memory
- Tools, APIs and integrations
- Scheduling/background tasks
- Settings and localization
- Installation and packaging
- Security, permissions and recovery

## Deployment and Git safety
- Inspect current Vercel configuration, project settings, build logs and deployment status before changing deployment files.
- Vercel serverless filesystem is ephemeral/read-only outside /tmp; preserve the current state directory strategy.
- Persistent agents, GUI control, audio devices and long-lived workers must be separate services where needed.
- Never commit secrets, `.env`, tokens, private keys, local user data, caches, binaries or reference repository clones.
- Work on `research/fatihmakes-rea-integration`.
- Do not force-push and do not rewrite main history.
- Run relevant unit, integration, security, type/lint and production build checks.
- Inspect the final diff and verify no existing feature was unintentionally removed.
- Create a PR to main with evidence and actual test results. Do not merge or deploy a broken/untested build.
- Verify deployment with real smoke tests; report URL and deployment identifier only when confirmed.

## Definition of done
AAROHI remains the existing product, now with selected, evidence-backed capabilities independently implemented from the reference collection. Every reused component has provenance and license clearance. Every claimed feature has a working implementation and a test or explicitly documented verification gap. The final report distinguishes source inspection, static analysis, simulated tests, real runtime tests and unverified claims.