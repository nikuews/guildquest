# GuildQuest Mini-Adventure Environment (GMAE)

This repository contains an extensible CLI-first framework for two local players.

## Current Scope (Interface Branch)

This branch focuses on UI/interface flow, not full gameplay logic.

Implemented interface capabilities:
- Initialize/start a selected mini-adventure
- Accept player input actions turn-by-turn
- Advance turns/time through a shared engine loop
- Report current state through CLI rendering
- Detect completion and show end-of-adventure outcome
- Support reset-ready adventure implementations via a shared interface

Included mini-adventures:
- Relic Hunt (competitive)
- Timed Raid Window (co-op)

## Run

From repository root:

```bash
python3 -m GMAE.main
```

## Add a New Mini-Adventure

1. Create a module under `GMAE/adventures/<new_adventure>/`.
2. Implement a class that inherits `MiniAdventure` in `GMAE/adventures/base_adventure.py`.
3. Add the class to `AdventureRegistry` in `GMAE/engine/adventure_registry.py`.
4. Ensure `get_state()` returns renderer-friendly fields (title, mode, turn, actions, and optional board/objective lines).
