# ThinShot → SANDLINE — Repository Assessment & Conversion Roadmap
*Revision 2 — reassessed 16 August 2026 at commit `acc516c` (89 commits) against Veil Codex canon CR3 · narrative NF2 · engineering EN2.2 · GS1 · RM1*

> **Revision note.** Revision 1 assessed commit `5549959` (50 commits). Thirty-nine commits have landed since, and they invalidate two of that revision's conclusions. Civilians on the battlefield — called there "the single hardest Grounded Doctrine requirement" — **are built and shipping**. Rodar Akai **is already the player character**. Phase 2 is materially cheaper than estimated, and Phase 1 is partly done. Superseded claims are marked below.

---

## 1. Verdict (revised)

The project has grown from 7,466 to **10,485 lines** and from 50 to **89 commits**, and the growth is not content padding — it is *engineering discipline*. In two weeks the repo acquired:

- **`Rules.gd`** — the combat arithmetic lifted out of the controller into a static, testable module, explicitly so that "the percentage on screen and the percentage rolled" cannot drift apart.
- **Three test harnesses** — `test_rules.gd`, `test_progression.gd`, `test_save_load.gd` — carrying roughly **208 assertions**, plus `check_cover_rules.gd`, which sweeps every shipped map against the cover model on a bare `Board.new()` with no scene tree.
- **A versioned save system** with a migration ladder, that refuses to overwrite a file it cannot read.
- **Deterministic seeding** — a campaign seed, a derived `battle_seed()`, and a separate RNG stream for the hit roll, with retries deliberately reseeded.
- **An asset pipeline** — a validated PixelLab floor pipeline, `TileCatalog.gd`, `FloorLayer.gd`, board transitions, roads, painted zones, and two Python validators.

**This repository now has the same engineering posture as the Codex itself: one source of truth for the rules, and a harness that proves it.** That is the single most important fact in this revision, because every Grounded Doctrine system in Phase 2 is arithmetic — and arithmetic now has a home and a test suite to land in.

The Revision 1 precedence ruling (**RM1**) stands and is reinforced: *mechanics follow the build, fiction follows the Codex.*

---

## 2. What changed since Revision 1

### 2.1 Canon adoption has already begun

**Rodar Akai is in the game.** Seventy-four references. He is a distinct unit kind (`HERO`), ships with his own sprite set, arrives at the accuracy cap, carries his own four-tier perk tree, and — significantly — **his death ends the mission**: `RODAR AKAI HAS FALLEN`. The repo independently arrived at "Rodar is the campaign."

*Supersedes Revision 1 §3.1, which listed "Team Lead → Rodar Akai" as pending work.*

### 2.2 Civilians are built — the hardest requirement, shipped

**`THE HOLDING PENS`** adds a `rescue` objective kind and non-combatant prisoners: they walk at move 4, carry no weapon, are cut loose by any soldier who ends a move beside them (no button, no action cost), and must then be **walked out**. `living_soldiers()` deliberately excludes them, and a prisoner left standing alone is explicitly *not a squad*.

This is the mechanical spine of every remaining Grounded Doctrine system. Escortable non-combatants who can die and whose survival is the objective — that was the expensive part, and it is done.

*Supersedes Revision 1 §4 item 3 ("Civilians on the battlefield — M") and §2.3's note that the civilian art was unused.*

### 2.3 The story converged on canon by itself

The Holding Pens debrief: *"Surveyors. Taken off the line eleven years ago, when Outpost 7 came off the maps, and kept alive ever since because somebody down there wanted the maps in their heads… And they say the one who asked the questions is still out there, at the end of the tracks."*

Canon's Riverspoken are led by **the Cartographer** — the Confederacy's former survey-master, who mapped the dead watercourses for forty years, walked into the deep desert with his instruments, and came back speaking (KC2). The repo, with no knowledge of that ruling, wrote an antagonist at the end of the tracks who collects surveyors for the maps in their heads.

**These are the same character.** Operation Second Verse is already walking toward the Riverspoken. This is the strongest available bridge from the shipped game into Act IV, and it requires almost no retrofitting.

### 2.4 Progression deepened

Four flat perks became **24 across three class trees** (Scout, Machinegunner, Hero), four ranks of two choices each — including `Inspiration`, a hero aura, and `Executioner`, a flanking damage bonus, both already priced into `Rules.gd`.

### 2.5 Content and craft

Seven missions (was six). Operation Second Verse now runs on the **salt** biome, so the biome plumbing is live rather than notional. Enemy AI now reads *the same* cover the rules apply — an AI/rules parity fix of exactly the kind the Codex harness exists to catch.

---

## 3. What still conflicts with canon

Unchanged from Revision 1, and now the **only** substantial blocker:

**The Goblin Rust Choir.** Choristers, Raiders, Skirmishers, Novices, a Cantor, and an "armed rabble" framing in which Novices are *"shirtless, handed whatever sidearm was left over, and pushed out front as a screen."* This violates TR2, KC2, and Book X.1 for the reasons IA1 gave: a people rendered as a creature type. The rename table in Revision 1 §3.1 stands — **the Thirst**, well-hands, runners, pressed conscripts, a Thirst marksman. Sprites are retained; only the fiction changes.

Also outstanding: the player faction is still **Desert Scouts** (canon: Kestrel Squad, Accord Ranger Program), and the win banner still reads `DESERT SCOUTS WIN`.

Still absent: Named Dead, the Notebook, District Standing, Alliance Strain, surrender and rout, and the remaining five squad members.

---

## 4. Roadmap (revised)

### Phase 0 — Ground truth *(unchanged; still first)*
Play all seven missions. Then rewrite Annex VIII.2 to describe the build that exists — move-once/shoot-once, adjacency cover, magazines and fire modes, `Rules.gd` constants — rather than the unbuilt AP/D20 spec.

### Phase 1 — The rename *(partly done)*
Rodar has landed. Remaining: Rust Choir → the Thirst, Desert Scouts → Kestrel Squad, the win/loss banners, and the briefing and debrief rewrite against KC1/KC2. Re-point the depot-mark trail at the Tarkesh ghost foundry. **Low risk, unblocks everything, and after it the repo is SANDLINE.**

### Phase 2 — The Grounded Doctrine *(cheaper than estimated)*
Order revised to exploit what now exists:

1. **Named Dead** — generated identity per insurgent, revealed at after-action; the interface stops saying *goblins* once a name is known. Pure data plus a UI pass.
2. **Surrender and rout** — extend the existing morale model; a routed unit reaching the edge is *escaped*, not killed. `Rules.gd` is the natural home.
3. **Re-score the after-action** from kills to **contacts resolved**.
4. **The Notebook** — a persistent document; the save system's migration ladder makes adding a payload field routine rather than risky.
5. **Civilians beyond prisoners** — reuse the rescue plumbing for bystanders who are present rather than objectives.
6. **District Standing** and **Alliance Strain** — campaign-level counters in `Game.gd`, alongside the campaign seed.

Every item lands in a module with a test harness in front of it.

### Phase 3 — Squad and structure
Sillae, Dava, Fen, Halvik, Essa, Josen. The class-tree architecture already generalises — each new role is a tree plus art. Bond conversations reuse the camp walkaround. Acts I–II as new operations.

### Phase 4 — The Strange *(shortest path from the shipped game)*
**Start from the Holding Pens thread.** The surveyor-collector at the end of the tracks becomes the Cartographer; the Choirmaster bowl becomes a Riverspoken working. Add Linewalkers who declare your next action and Spoken-For with no surrender prompt — the latter being the horror payoff of Phase 2 step 2, which is why surrender must ship first.

### Phase 5 — Old Promise
Verse Clock, prophetic interface corruption, the Wellspring, breaking the Charter, Testimony.

---

## 5. Rulings

- **RM1** *(stands)* — mechanics follow the build; fiction, naming, factions, and doctrine follow the Codex.
- **RM2** *(stands, now the sole blocker)* — the Rust Choir is struck and reframed as the Thirst.
- **RM3** *(stands)* — permadeath with garrison-only replacement is canonical.
- **RM4** *(new)* — **the Cartographer is canonically the surveyor-collector of Operation Second Verse.** The repo's independent invention is adopted rather than overwritten: the man at the end of the tracks who keeps surveyors alive for the maps in their heads is the Confederacy's former survey-master, and Operation Second Verse is SANDLINE's on-ramp to Act IV.
- **RM5** *(new)* — **`Rules.gd` is the canonical home of combat arithmetic.** Any Grounded Doctrine mechanic expressible as a number belongs there, with an assertion in `test_rules.gd`. The Codex will not respecify in prose what the module already states in code.

---

## 6. The sentence, revised

Revision 1 said the repo had solved the hard problem of a tactics game that feels good to play, and had not made the player feel bad about winning. That still holds — but the gap has narrowed from a chasm to a rename and six counters. **The prisoners were the hard part, and they are already walking out.**
