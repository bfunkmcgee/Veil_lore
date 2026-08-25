# SANDLINE — Canon Integration Plan
*Turning ThinShot into SANDLINE. Prepared 16 August 2026 against commit `acc516c` (89 commits) and Veil Codex canon CR3 · NF2 · GS1 · RM1–RM5.*

---

## 0. The governing rule

> **Fiction conforms to the Codex. Mechanics conform to the build.** (RM1, RM5)

Nothing in this plan changes a rule, a stat, a system, or a tuning value. Every item below is naming, framing, text, or additive systems work. If a step would alter how the game *plays*, it has been written wrong.

**Second rule, learned from the code itself.** `Unit.gd` carries this comment on the `Kind` enum:

> *"Appended last and must STAY last: saves store the raw ordinal, so inserting mid-enum would quietly turn every saved soldier into somebody else."*

Enum ordinals are persisted. **No renaming pass may reorder `Kind` or `TEAM_*`.** Identifiers may be renamed in place; ordinals may not move. Where a new kind is needed it is appended, and the save version is climbed. This single constraint shapes the whole sequence below.

---

## 1. Surface area — the good news

The non-conforming fiction is far smaller than it looks, because the codebase already separates role from identity. `Unit.kind_role_name()` is a single `match` block holding **every** faction-facing label in the game.

| Literal | scripts | README | Assessment |
|---|---|---|---|
| `Rust Choir` | 7 | 1 | Concentrated in one function |
| `Choir` | 49 | 23 | Mostly comments and briefing prose |
| `DESERT SCOUTS` | 4 | 0 | Three banners and a win state |
| `goblin` / `Goblin` | 182 | 18 | **Mostly identifiers and sprite paths — keep** |

**The `goblin` identifiers stay.** `GOBLIN_SMG`, `goblin_spawns`, `TEAM_GOBLIN`, `assets/sprites/Goblin/` — these are enum members, data keys, and file paths. Renaming them buys nothing, risks the save format, and churns 10,595 asset paths. Canon governs *what the player is told*, not what the developer types. A goblin sprite is correct: **the Thirst are goblins.** What was wrong was never the species; it was the framing of the species as a rabble.

---

## 2. Phase 1 — The rename *(one commit per step; no mechanical change)*

### 1.1 Faction labels — `Unit.kind_role_name()`

The entire faction rename is one function.

| Current | Canon | Rationale |
|---|---|---|
| `Rust Choir Chorister` | `Thirst Well-hand` | KC2 — dispossessed duneworks labour |
| `Rust Choir Raider` | `Thirst Runner` | Same tactics, no rabble framing |
| `Rust Choir Skirmisher` | `Thirst Light Runner` | Speed is kit and build, not "half-starved frame" |
| `Rust Choir Novice` | `Pressed Conscript` | Fragility is training and equipment (IA1) |
| `Rust Choir Cantor` | `Thirst Marksman` | Music naming is Crown/Veil-coded in canon |
| `Scout Team Lead` | `Kestrel Team Lead` | KC1 |
| `Scout Machinegunner` | `Kestrel Machinegunner` | KC1 |
| `Rodar Akai, Hero of the Scouts` | `Rodar Akai, Kestrel Squad` | KC1 — he is a conscript, not a hero-of |
| `Desert Scout` *(fallback)* | `Kestrel Rifleman` | KC1 |
| `Prisoner` | `Prisoner` | Correct already |

### 1.2 Banners — `Battle.gd` ×4
`DESERT SCOUTS' TURN` → `KESTREL SQUAD'S TURN` (three sites). `DESERT SCOUTS WIN` → **`CONTACT RESOLVED`** — this one is not cosmetic; see §3.3. `THE CHOIR SINGS ON` → `THE SQUAD IS GONE`.

### 1.3 Rank ladder — `Game.gd`
`Scout / Corporal / Sergeant / Staff Sergeant / Master Sergeant` → `Levy / Corporal / Sergeant / Staff Sergeant / Master Sergeant`. Rodar enters as a conscript; the bottom rung should say so.

### 1.4 Operations and missions — `Levels.gd`

| Current | Canon |
|---|---|
| `OPERATION DRY CHOIR` | `OPERATION DRY WELL` |
| `OPERATION SECOND VERSE` | `OPERATION LONG SURVEY` |
| `THE CHOIRMASTER` | `THE SURVEY CAMP` |
| `DRY WASH`, `THE SCRAPLINE`, `OUTPOST 7`, `THE LONG HAUL`, `THE CISTERN`, `THE HOLDING PENS` | **unchanged** — all canon-neutral and good |

### 1.5 Briefing and debrief prose — the real work

Seven missions × briefing + debrief + fiction. **Complete drop-in replacements are written in Appendix A.** Three substitutions run throughout:

- **Motive replaces menace.** The enemy crossed the wash because a well was capped, not because they are raiders. The Charter of Wells is the reason for every mission in Operation Dry Well.
- **The Accord replaces "command."** The squad is Crown, seconded to a Confederacy counterinsurgency, and the locals did not ask for them (KC1).
- **The trail leads to the foundry.** The depot mark "off the maps for eleven years" becomes Tarkesh Wound-steel — weapons the Crown cannot account for, arriving along routes nobody plotted (GS1, Act IV).

### 1.6 README
Rewrite §"The game" and both operation summaries. Delete the rabble paragraph entirely: *"Novices are the bottom of it — shirtless, handed whatever sidearm was left over."* Replace with materiel and politics — a pressed conscript is fragile because he was handed a bad rifle last week, and he is here because his settlement lost its water.

**Exit criterion for Phase 1:** the word *Choir* appears nowhere the player can see. Identifiers and paths untouched. Zero test failures — no rule changed.

---

## 3. Phase 2 — The Grounded Doctrine *(additive; the identity of the game)*

Ordered to exploit what already ships, and priced against the modules that now exist.

### 3.1 Named Dead — `Rules.gd` adjacent, `Battle.gd` UI
Every insurgent generates an identity at spawn: name, age, settlement, one line of provenance from the Charter grievance. Hidden during contact, revealed at after-action. **Once a name is known the interface never again says *goblins*.** Data plus a UI pass; no rule touched.

### 3.2 Surrender and rout — `Rules.gd`, `test_rules.gd`
Morale already exists. Extend it: below panic with squad firing superiority, the unit **offers surrender**; a routing unit reaching the map edge is **escaped**, not killed, and scores as resolved. Per RM5 the thresholds live in `Rules.gd` with assertions in `test_rules.gd`.

*Prerequisite for Act IV: the Spoken-For's horror is the absence of this prompt (GS1 §SS.6). It cannot land before the prompt is habitual.*

### 3.3 Split the after-action in two — `Battle.gd` *(revised per GS2)*

**Not** a rescore from kills to restraint. Two panels that are never summed:

- **THE OPERATION** — *graded*. Objective, squad intact, tempo, execution. Killing armed combatants is how this is earned, and a hard-fought firefight can be a perfect operation.
- **THE ROLL** — *reported*. Names added, civilians harmed, prisoners taken and their disposition. Never ranked, never subtracted from the grade.

The banner change in §1.2 stands, but for a narrower reason: `DESERT SCOUTS WIN` becomes `CONTACT RESOLVED` because the *victory line* should not read as a scoreline, not because winning by force is a lesser outcome.

**Implementation guardrails (GS2).** These belong in `Rules.gd` with assertions:

- Killing an armed, fighting combatant: **Standing 0, Strain 0, rating unaffected.**
- Conduct penalties apply only to chosen acts — firing on routing/surrendered/wounded, civilian casualties, destroying wells or homes or aid, refusing collection of the dead, arrests without cause.
- Accepting surrender costs the acting unit's turn and creates a prisoner obligation.
- **Alliance Strain floor per district is greater than zero and cannot be cleared by conduct.** Assert it. A player who reaches zero has found a bug in the theme.
- **Kill floor per combat mission.** At least one enemy class in every combat map cannot rout or surrender. Assert that a no-kill completion is impossible.

### 3.3b One mission where restraint is wrong
Schedule it in Operation Dry Well: hesitation costs a squadmate, the drill says shoot, and the drill is right. Josen Marr carries it (NF2 counterweight). Without this mission the systems above still read as a morality meter with extra steps.

### 3.4 Dava's Notebook — `Game.gd`, save v3
A persistent campaign document: every civilian treated, every combatant killed, cross-linked where the district connects them. The **migration ladder makes this routine** — add the payload field, write `_migrate_2_to_3`, extend `test_save_load.gd`.

### 3.5 Bystanders — reuse the prisoner plumbing
`CIVILIAN` already exists, is never shot at, and does not move until reached. A bystander is a civilian who is **not an objective** — present, in the way, and killable. This is the smallest high-impact change in the plan: the code is written, and only the mission data changes.

### 3.6 District Standing and Alliance Strain — `Game.gd`
Two campaign counters beside the campaign seed. Standing per settlement; Strain theater-wide and driven **only by Crown-attributed goblin deaths**. Sillae's cooperation degrades as Strain climbs (GS1 §SS.4), so this pairs with her arrival in Phase 3.

---

## 4. Phase 3 — The squad

Six more Kestrels. The class-tree architecture already generalises: each role is a `CLASS_PERK_RANKS` entry plus art.

| Kestrel | Route | Cost |
|---|---|---|
| Josen Marr | Existing scout kind, named | free |
| Essa Vane | Grenadier tree over the existing pooled ordnance | small |
| Sillae Vekh | Marksman variant; carries the Strain interface | medium |
| Brukk Meshan | The machinegunner, named | free |
| Halvik Dunn | Breacher — needs the gate asset (`ASSETS.md` #2) | medium + art |
| Dava Ren | Medic — `Field Dressing` perk already exists as a seed | medium + art |
| Fen Ost | Technician — anomaly readings; the Act IV hook | medium + art |

**Append new kinds; never insert.** Climb the save version each time.

---

## 5. Phase 4 — The Strange *(shortest path from the shipped game)*

Operation Long Survey already ends pointing at "the one who asked the questions, still out there, at the end of the tracks." Per **RM4** that man is the Cartographer.

1. Rename the Choirmaster bowl to **The Survey Camp** and make the antagonist the Cartographer.
2. Add **Linewalkers** — declare the player's next action aloud, and be right unless the player does something unscripted.
3. Add **Spoken-For** — morale-immune, no surrender prompt. The payoff of §3.2.
4. Wound-steel shipments become a grey-market offer the player may accept.
5. Corven Sayle's reveal; Felia's pass-through as a scripted NPC.

---

## 6. Phase 5 — Old Promise

Verse Clock, prophetic interface corruption, the Wellspring floor-map arena, breaking the Charter, and the Testimony finale. Last, because it subverts systems that must first be habitual.

---

## 7. Sequencing constraints

1. **Never reorder `Kind` or `TEAM_*`.** Append only, and climb `SAVE_VERSION`.
2. **Surrender (§3.2) ships before Spoken-For (Phase 4).**
3. **Sillae (Phase 3) ships with or before Alliance Strain (§3.6)** — a meter with no face is a number.
4. **Named Dead (§3.1) ships before the Notebook (§3.4)** — the Notebook records names.
5. **Every numeric rule lands in `Rules.gd` with an assertion** (RM5).
6. **Phase 1 must not change a single test result.** If a test moves, a rule moved, and the commit is wrong.

---

## 8. What is explicitly *not* being replaced

- The cover model, hit resolution, fire modes, magazines, overwatch, suppression, grenades — **canon defers to these** (RM1).
- Permadeath with garrison-only replacement (RM3).
- The seven shipped maps, their layouts, spawn tables, and tuning.
- The goblin sprites, the `goblin` identifiers, and the asset tree.
- `Rules.gd`, the harnesses, the save ladder, the seeding, the art pipeline.
- The Holding Pens rescue design — it is already the Grounded Doctrine, written before the doctrine reached the repo.

---

## 9. Definition of done

SANDLINE has replaced ThinShot when: no player-visible text contradicts the Codex; the enemy has names and motives; a mission can be completed without killing; the after-action counts contacts resolved; a civilian can die and the game notices; and the trail out of Operation Long Survey leads to the Cartographer.

Everything after that is Acts I–II and the horror.

---

# Appendix A — Mission text, rewritten

*Drop-in replacements for every narrative field in `Levels.gd`. Field names match the data (`fiction`, `briefing`, `orders`, `debrief`). **No objective, spawn, map, or stat changes** — the mechanical definitions are untouched, per RM1 and the Phase 1 exit criterion.*

**Three rules held throughout.** No briefing implies the killing was avoidable (GS2). No debrief grades the player. The enemy has a reason, and it is a good one.

**One reconciliation made here.** The shipped text reveals crates *"machined, not scavenged — every crate struck with the same depot mark. One of ours, taken off the maps eleven years ago."* Canon's Act IV hook is factory-new Tarkesh **Wound-steel** Mattocks that nobody shipped (GS1). These are unified rather than chosen between: the **crates** carry a Crown depot mark, and the **weapons inside them** are Tarkesh — new, unworn, from a foundry unwritten in A.V. 1983. A Crown depot struck off the maps was moving guns that should not exist. Both threads become one, and Operation Long Survey runs straight into Act IV.

---

## OPERATION DRY WELL
*(was OPERATION DRY CHOIR)*

**summary:** Push the Thirst back off the eastern wells, and find out what they are carrying.

---

### 1 · DRY WASH

**fiction**
> A dead watercourse on the Confederacy's eastern line. There has been no water in it for two hundred years, and men are dying over it this morning.

**briefing**
> The Thirst has never crossed the wash before. This morning they did — in daylight, in numbers, and they did not stop at the pumping station they passed on the way.
>
> Eleven days ago an Accord survey capped four marginal wells north of here. The Assembly filed an objection. The Thirst filed this.
>
> Rangers are stretched east and the Accord wants the crossing clear. That is the whole order, and it is yours because you are what is available.

**orders**
> CLEAR THE WASH

**debrief**
> They were not raiding.
>
> Every fighter on the wash carried the same load: crates, sorted and tallied, roped for a long carry. Nobody hauls a tally into a raid.
>
> They were moving it somewhere, and they were late. Follow the route back.

---

### 2 · THE SCRAPLINE

**fiction**
> A wire-and-scrap yard on the old freight line, where the Thirst stacks what it moves.

**briefing**
> The route ends in a yard the locals call the Scrapline: rows of crates stacked and roped, waiting on a truck that has not come.
>
> Killing carriers changes nothing. There are always more carriers — the Charter left four settlements without water and every one of them has sons. The load is what matters.
>
> There is a mast over the yard as well. It is not theirs, and while it stands, everyone within forty miles knows you are here.

**orders**
> BURN THE CACHES, DROP THE RELAY

**debrief**
> The crates were not scrap.
>
> Primers, casings, barrel stock — machined, not scavenged. And the rifles: Tarkesh Foundry Mattocks, factory-new, no wear on the rails, no dust in the actions. Bhorra proof marks.
>
> The Foundry was unwritten in eighty-three. There has not been a new Mattock in the world for three hundred and forty years, and there are eleven of them in this yard.
>
> Every crate is struck with a Crown depot mark. One of ours, taken off the maps eleven years ago.
>
> Somebody is shipping guns that do not exist through a depot that does not either.

---

### 3 · OUTPOST 7

**fiction**
> A Crown forward depot, struck off the maps eleven years ago. The Thirst lives in it now, and the squad goes in at dawn.

**briefing**
> Outpost 7 was ours. It is not on any inventory the Accord will admit to holding, and the Thirst has been eating out of it for a decade.
>
> Two ammunition stores are still standing in there. They are the reason a water dispute has rifles in it.
>
> You cannot hold the place. There are not enough of you and there never were. Blow the stores and walk the squad back out.

**orders**
> BLOW THE AMMO STORES, THEN EXTRACT

**debrief**
> The stores are gone. What was in them was not.
>
> Both were light — a third full, at most, and swept clean rather than looted. Somebody drew that stock down deliberately and moved it out ahead of you.
>
> Ranger liaison has filed the Foundry marks upward and been told the query is above the Accord. Note that and keep it out of the log.
>
> Take the squad home. This is not finished, and the Assembly of Wells has called a strike in three districts over the capping. Whatever comes next is going to happen in front of people.

---

## OPERATION LONG SURVEY
*(was OPERATION SECOND VERSE)*

**summary:** The stores were drawn down before you got there. Find out who took the rest, and where it went.

---

### 4 · THE LONG HAUL

**fiction**
> Open ground west of the wash, where a Thirst column was still walking two days after the depot burned.

**briefing**
> You were told the Thirst was finished east of the line. Here they are in daylight, walking a load west with no cover for a mile in any direction.
>
> The stores at Outpost 7 were light when you blew them. This is where the rest went, and it is still going.
>
> Burn the load.
>
> Ranger liaison has asked, on the record, that the squad account for what is in it before firing. That request is noted, and the order stands.

**orders**
> BURN THE COLUMN'S LOAD

**debrief**
> Water.
>
> Not ordnance. Drums of water, tallied and roped and hand-hauled across forty miles of nothing, and the squad put a match to all of it in a country that has been arguing about wells for three centuries.
>
> The Rangers have gone quiet. Not hostile. Quiet, which is worse, and Liaison has stopped forwarding district intelligence pending a conversation nobody has scheduled.
>
> Note also: the Thirst is not arming a war any more. It is supplying something. And whatever it is sits far enough out that a drink is worth a column.

---

### 5 · THE CISTERN

**fiction**
> A walled water point on the old survey line. The only water east for a day in either direction, and the Charter says it belongs to a family that has not drawn from it in ninety years.

**briefing**
> Every tally in the column names the same place: a cistern on the survey line, walled and held.
>
> It is the only water east of here, which is why they hold it and why you cannot go around it.
>
> Get the squad through and out the far side. Do not stop to take it — you could not hold it, and the Assembly would hear that the Crown seized a well before the sun went down.

**orders**
> BREAK THROUGH TO THE EAST

**debrief**
> Past the cistern the tracks stop scattering.
>
> Every path east of the water runs together into one, beaten flat and wide by more feet than the Thirst has ever put in one place — and it does not follow the road. It follows the old riverbed, which has been dry since before the Charter was written.
>
> Somebody is walking them along a watercourse that has no water in it.

---

### 6 · THE HOLDING PENS

**fiction**
> A wire pen behind the Thirst's line, and the reason they have been hauling water across forty miles of nothing.

**briefing**
> The water was not for them.
>
> Behind the line there is a pen, and in it are the people they have been keeping alive — Confederacy survey staff, by the tallies. Civilians. Taken, fed, and kept.
>
> That is what the column was for. Go and get them.
>
> The pen is wire. You will see them long before you reach them, and so will everyone else.

**orders**
> REACH THE PRISONERS, THEN WALK THEM OUT

**debrief**
> Surveyors. Taken off the line eleven years ago, the same season Outpost 7 came off the maps, and kept alive ever since because somebody wanted the maps in their heads.
>
> They knew every well, dump, and cistern on the survey line. That is how the Thirst found them all.
>
> They will not say his name. They say he asked about water that is not there — where it used to run, how deep, how fast, which way it turned. Eleven years of questions about dry rivers.
>
> One of them asked us, twice, what day it was, and then said she already knew.
>
> He is still out there, at the end of the tracks.

---

### 7 · THE SURVEY CAMP
*(was THE CHOIRMASTER)*

**fiction**
> Where every track east of the cistern ends: a camp laid out along a riverbed that has been dry for two hundred years, pitched as though the water were still running.

**briefing**
> The tracks end in a bowl in the rock, and the Thirst is in it — all of it, and more than you have seen in one place.
>
> They did not gather themselves. Somebody down there has been keeping them, and while he keeps them there will always be another column.
>
> Fighters in that bowl will not break. Liaison has been clear on this and so has the interrogation of the pen guards: they are not staying because they are brave. They are staying because they have been told how this ends and they believe it.
>
> No caches this time. No withdrawal.

**orders**
> END THE READING

**debrief**
> It is over, and it is quiet.
>
> The camp was not a camp. It was laid out along the bed in stages — markers at the bends, stakes at the depth changes, the whole dry course measured out and pegged as though somebody intended to fill it.
>
> The old man's papers are forty years of Confederacy survey work, annotated in a hand that gets steadier the further out it goes. The last forty pages are not survey. They are a schedule.
>
> He was not with the bodies. Nobody saw him leave.
>
> Bring the squad home. The Rangers are burying their own dead separately from ours, and did not ask whether we minded.

---

## Cross-cutting text changes

| Location | Change |
|---|---|
| `Game.gd` ranks | `Scout` → `Levy` (bottom rung only) |
| `Battle.gd` banners | `DESERT SCOUTS' TURN` → `KESTREL SQUAD'S TURN` ×3 |
| `Battle.gd` win | `DESERT SCOUTS WIN` → `CONTACT RESOLVED` |
| `Battle.gd` loss | `THE CHOIR SINGS ON` → `THE SQUAD IS GONE` |
| `Battle.gd` hero loss | `RODAR AKAI HAS FALLEN` — **keep, it is already right** |
| `Unit.kind_role_name()` | Per §1.1 table |
| Camp fixtures | "assignment post" wording → Levy replacement draft |

**Objective labels** — `CLEAR THE WASH`, `BURN THE CACHES, DROP THE RELAY`, `BLOW THE AMMO STORES, THEN EXTRACT`, `BURN THE COLUMN'S LOAD`, `BREAK THROUGH TO THE EAST`, `REACH THE PRISONERS`, `END THE READING`. Only two changed: *ammo dumps* → *ammo stores*, and *LEAVE NOBODY SINGING* → *END THE READING*.
