# Deep Research

Source: https://github.com/Weizhena/Deep-Research-skills (MIT, LICENSE kept beside this file). Inspired by RhinoInsight (arXiv:2511.18743). Upstream Claude Code skills are preserved verbatim under `references/upstream/` and the web-search agent plus its modules under `references/`. This file adapts that workflow to Muse tools. Use the English upstream wording for prompts where it says a prompt must be reproduced strictly.

Use this workflow for thesis (skripsi) work first: literature reviews and tinjauan pustaka, paper and benchmark surveys, theory and method comparison, research-gap mapping, and any systematic topic investigation. It also fits technical, market, and due-diligence research.

- Run research in two controlled phases with the user in the loop: outline first, deep investigation second, report last. Never jump straight to deep research without a confirmed outline.

- Keep every research run in its own folder `~/workspace/research/<topic_slug>/` unless the user names another location, with `outline.yaml`, `fields.yaml`, `results/` for per-item JSON, and `report.md` as the final deliverable.

## Tool mapping from upstream

- Replace upstream `AskUserQuestion` with a direct question in chat, and use `muse.create_options` when the choice is bounded, such as time range or batch size.

- Replace upstream `WebSearch` and the `web-search-agent` Task with `browser.search` for discovery and `subagent.spawn` for parallel per-item investigation. Give each subagent the exact prompt template from the phase below, the fields file path, and its output JSON path.

- Replace upstream `~/.claude/skills/research/validate_json.py` with `~/workspace/custom-skills/deep_research/validate_json.py`. It needs PyYAML, installed with `pip install pyyaml` or `pip3 install --user --break-system-packages pyyaml`.

- Read the matching search strategy module in `references/web-search-modules/` before searching. For a thesis, `academic-papers.md` is mandatory. Add `general-web.md` for context and official sources, and the technical modules only when the topic needs them.

## Phase 1: research, build the outline

- Generate an initial framework from your own knowledge first: the main research items in the domain and a suggested field framework grouped by category. For a thesis, items are usually papers, theories, methods, datasets, benchmarks, or prior studies (penelitian terdahulu), and fields cover identity, method, sample or data, findings, limitations, and relevance to the user's research question.

- Show that framework to the user and ask what to add or remove and whether the field framework fits. Do not proceed on an unconfirmed framework.

- Ask for the time range, such as the last 5 years for a thesis literature review, since 2020, or unlimited, then launch one web-search subagent in the background to supplement the framework. Reproduce this prompt strictly, replacing only the variables in braces: Research topic {topic}, current date {YYYY-MM-DD}, the existing framework, and goals to verify missing items, supplement items found within {time_range}, and suggest new fields, returning supplementary items, recommended supplementary fields, and sources as structured text without writing files.

- Ask whether the user already has a field definition file, such as a supervisor requirement, a journal template, or variables from their proposal. Merge it when they provide one.

- Write two separate files. Write `outline.yaml` with the topic, the items list, and execution config covering batch_size, items_per_agent, and output_dir defaulting to `./results`, confirming batch_size and items_per_agent with the user. Write `fields.yaml` in the exact shape the validator accepts: a top-level `fields:` mapping of category to a list of field dicts each with `name`, `description`, and `detail_level`, plus a top-level `uncertain:` list. Use detail levels brief, moderate, and detailed.

- Show both files to the user for confirmation before Phase 2.

## Phase 1b: extend the outline

- To add items, locate the run's `outline.yaml`, ask the user for specific items and whether to also launch a web search for more, then append without duplicates and show the updated outline for confirmation before saving.

- To add fields, locate the run's `fields.yaml`, take new fields from the user's input or from a web search for common fields in the domain, then ask the user to confirm each field, its category, and its detail_level before appending and saving.

## Phase 2: research-deep, investigate every item

- Locate `outline.yaml`, read the items and execution config, and check `results/` first. Skip items whose JSON already exists and validates, so an interrupted run resumes instead of restarting.

- Work batch by batch using batch_size and items_per_agent from the outline, and get the user's approval before starting the next batch. Launch one subagent per agent slot in parallel.

- Give each subagent this prompt strictly, replacing only the variables in braces: research {item_related_info} and output structured JSON to {output_path}, reading {fields_path} for all field definitions, marking uncertain values with [uncertain], adding an `uncertain` array listing every uncertain field name, writing all field values in the language the user chose for the run, then running `python ~/workspace/custom-skills/deep_research/validate_json.py -f {fields_path} -j {output_path}` and finishing only after validation passes.

- Build each output path by slugifying the item name: replace spaces with underscores and remove special characters, then save as `{output_dir}/{item_slug}.json`.

- For a thesis, require every item JSON to carry full citation data as fields, such as authors, year, title, venue or journal, DOI or stable URL, so the report can become a bibliography. Never invent a citation, DOI, statistic, or finding. Mark anything unverified as [uncertain].

- Report progress after each batch: how many items are complete, which failed or carry uncertain marks, and where the outputs live.

## Phase 3: research-report, compile the report

- Locate the run, read all result JSON files, and scan for short summary fields worth showing in the table of contents, such as year, method, sample size, score, or citation count. Ask the user which of those fields to display beside each item name.

- Generate `generate_report.py` inside the run folder following the upstream `research-report` skill in `references/upstream/research-report/SKILL.md`, including its JSON structure compatibility, category mapping, complex value formatting, extra-field collection, and uncertain-value skipping rules. Cover every field value, skip values containing [uncertain] and fields listed in `uncertain`, and build a table of contents with anchor links plus the user-selected summary fields.

- Run the script to produce `report.md`, then check the report covers every item and every defined field before delivering it. For a thesis, also surface a synthesis the raw report does not give: agreements and contradictions across studies, the research gap, and which items best support each chapter or sub-bab, clearly separated from the sourced data.

## Academic integrity for thesis use

- Treat the report as research material for the user to read, verify, and rewrite in their own words, not as finished thesis text to submit as-is.

- Keep sources traceable end to end: every claim in a summary traces to an item JSON, and every item JSON traces to real sources found in search.

- Flag weak sources, such as blogs cited for academic claims, predatory-looking journals, or undated pages, instead of presenting all sources as equal.
