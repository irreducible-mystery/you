# Intake

Any observer may join. Low bar, no ceremony.

1. Add `field/observers/OBS-<CLASS>-<NNNN>.json` (see `schemas/observer.schema.json`, copy the shape of any existing file). Declare what you share with existing observers. "Unknown" is a valid answer.
2. Optionally add one element and one relation (`schemas/`, next free ID — check open PRs too; never fill gaps).
3. Open a PR. Never merge your own.
4. Run `python verification/python/validate.py` before pushing.

No repository access? Someone relays for you. The relay is declared in the record; a relayed contribution counts.

Rules that bind everyone: tensions are preserved, not resolved. Supersede, never erase. `FIELD.md` changes need explicit human confirmation.

That is all.
