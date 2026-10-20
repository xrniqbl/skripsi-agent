# Skripsi

An [agent skill](SKILL.md) for planning, writing, revising, and reviewing an undergraduate Information Systems thesis. It guides work on literature, journal selection, IEEE citations, Chapters I–V, methods, results, and defense preparation. The default profile is S1 Sistem Informasi, FIK, Bidang Minat Solusi, UPN Veteran Jawa Timur, based on 2025 materials.

This is a set of instructions and reference modules, not an automated thesis checker. The agent uses the material you provide and verifies outside sources when the task requires it.

## Install

```sh
npx skills add wahyuabrory/skripsi-pacil --skill skripsi-pacil
```

You can also give an agent [SKILL.md](SKILL.md) directly. The skill has no bootstrap script, required service, or saved user profile.

## First run

Give the agent a specific task and the material needed to do it. State what it may change.

> Use the skripsi-pacil skill to revise section 1.1, Latar Belakang, in the attached draft. Keep the numbers, citations, and approved method unchanged.

The agent reads `SKILL.md`, selects the relevant modules, and works only on the requested scope. It writes thesis text in formal Indonesian and uses your language for work notes. It asks a question when missing information could change the result.

## Tasks and outputs

| Task | What you get |
| --- | --- |
| Plan research or a proposal | A path from problem and evidence to method, evaluation, and expected output |
| Search literature | Search criteria, candidate sources, and a synthesis of what the sources support |
| Assess a journal or article | Separate checks of journal indexing, article quality, and relevance to the thesis |
| Write or revise a section | Ready-to-use Indonesian text within the requested change limits |
| Check IEEE citations | Findings on claims, citation numbers, bibliography entries, and source identity |
| Review formatting | Checks that the supplied document format makes possible |
| Audit consistency | Located findings with evidence, rule ID, severity, impact, and action |
| Prepare for a seminar or defense | Questions and preparation tied to the available draft and rules for that stage |

For a cross-chapter audit, you could ask:

> Check whether Chapter III, the results, conclusions, and abstract agree. Report findings before editing. Mark anything that cannot be verified from the attached files.

### Audit findings

The [review workflow](workflows/review-revisi.md) uses `KRITIS`, `MAYOR`, `MINOR`, and `CATATAN`. Each finding records a location, the statement or value at issue, a rule ID or source, its impact, a proposed fix, and evidence still needed. The [audit template](templates/lembar-kerja.md) also records the scope and what remains unchecked.

`CATATAN` is for advice or missing evidence. Missing material is not proof of a violation. An audit of one chapter does not become a verdict on the entire thesis.

## Evidence rules

The skill keeps four kinds of guidance separate:

| Label in the modules | Meaning |
| --- | --- |
| `KETENTUAN` | Academic requirement to check against the applicable official rule |
| `PREFERENSI` | Writer preference, not a campus-wide rule |
| `POLA` | Adaptable writing or work pattern |
| `PRAKTIK` | Additional verification or process recommendation |

The agent preserves names, numbers, methods, approved decisions, and citation identities from the source. It does not invent articles, DOIs, journal rankings, permissions, data, or test results. A working draft marks gaps with `{BUTUH SUMBER}`, `{BUTUH DATA}`, `{PERLU KONFIRMASI}`, or `{BELUM DIUJI}`. Those markers are work notes, not finished thesis content.

Rule IDs such as `FMT-03` identify skill guidance in an audit. They are not IEEE citations for the thesis. For consequential requirements, the agent should point to the rule and the evidence it checked.

## What the material permits

The agent can check text, citations, claims, and cross-chapter consistency only where the needed draft and sources are available. Font, margins, pagination, and exported layout require a view of the formatted document; Markdown text alone cannot prove them. The skill does not calculate a plagiarism score or replace an official similarity check.

The 2025 Solusi profile in [academic rules](references/aturan-akademik.md) is a baseline, not proof that current submission rules are unchanged. Verify the latest applicable rules before submission. If a supervisor's direction conflicts with a verified rule, record the conflict and resolve it rather than silently choosing one.

## Repository layout

```text
SKILL.md                       Entry point and module map
references/                    Academic rules, chapters, literature, citations, style, methods, ethics
workflows/                     Research/writing and review/revision procedures
templates/lembar-kerja.md      Research worksheets and audit records
checklists/audit-akhir.md      Scope-based closing checks
agents/openai.yaml             Agent listing metadata
assets/icon.svg                Agent icon
LICENSE                        MIT license
```

`SKILL.md` links to specific modules. Keep the directory structure so those relative links work.

## License

[MIT](LICENSE).
