# English AI-Pattern Removal (merged from `humanizer` skill)

Based on Wikipedia's "Signs of AI writing" guide (WikiProject AI Cleanup) + blader/humanizer v2.5.1 (MIT). Use for English text: blog posts, essays, PR descriptions, docs, memos, emails, tweets, resumes. Same class as the Chinese patterns in SKILL.md — apply the same process (identify → rewrite → preserve meaning → add soul → final anti-AI pass).

## Voice calibration (when user provides a writing sample)

1. Read the sample first: sentence-length patterns, word-choice level, paragraph openings, punctuation habits (dashes, parentheticals, semicolons), recurring phrases, transition style.
2. Match the sample's voice in the rewrite — if they write short sentences, don't produce long ones; if they say "stuff", don't upgrade to "elements".
3. No sample → default: natural, varied, opinionated.

## Adding soul (the other half of the job)

- Have opinions: report facts, then react to them.
- Vary rhythm: short punchy sentences mixed with long ones.
- Acknowledge complexity and mixed feelings.
- Use "I" when it fits; be specific about feelings, not generic ("there's something unsettling about agents churning at 3am" beats "this is concerning").
- Let some mess in: tangents, asides, half-formed thoughts.
- Sterile/voiceless writing is as obvious as slop: no opinions, uniform sentences, press-release tone = still AI.

## The 34 patterns (condensed)

### Content patterns
1. **Undue emphasis on significance/legacy/trends** — stands/serves as, testament, vital/significant/crucial/pivotal, underscores/highlights, broader movement, evolving landscape, indelible mark. Strip the "marking a pivotal moment" framing; state what it actually is.
2. **Undue notability/media claims** — "cited in NYT/BBC", "active social media presence". Replace with specific citations ("In a 2024 NYT interview she argued...").
3. **Superficial -ing analyses** — highlighting..., ensuring..., reflecting..., showcasing..., fostering..., encompassing... Delete the participle tack-ons; state the fact.
4. **Promotional language** — boasts, vibrant, rich (figurative), profound, nestled, in the heart of, groundbreaking, renowned, breathtaking, must-visit, stunning.
5. **Vague attributions / weasel words** — "Industry reports", "Observers have cited", "Experts argue". Attribute to a specific source or drop.
6. **Formulaic "Challenges and Future Prospects" sections** — "Despite its... faces several challenges... Despite these challenges...". Replace with concrete specifics.

### Language & grammar patterns
7. **Overused AI vocabulary** — Actually, Additionally, align with, crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight (verb), interplay, intricate, key (adjective), landscape (abstract), pivotal, showcase, tapestry, testament, underscore, valuable, vibrant + marketing clichés (at the end of the day, when it comes to, in a world where, moving forward, circle back, deep dive, game-changer, double down, navigate, lean into, unpack).
8. **Copula avoidance** — serves as/stands as/marks/represents/boasts/features instead of is/has.
9. **Negative parallelisms & tailing negations** — "Not only... but...", "It's not just X; it's Y", clipped "no guessing" fragments.
10. **Rule of three overuse** — forced triads ("innovation, inspiration, and industry insights").
11. **Elegant variation / synonym cycling** — protagonist/hero/main character/central figure; say the same word twice.
12. **False ranges** — "from X to Y" where X and Y aren't on a meaningful scale.
13. **Passive voice & subjectless fragments** — "No configuration file needed", "results are preserved automatically" → "You do not need...", "the system preserves...".

### Style patterns
14. **Em dash overuse** — most can become commas, periods, or parentheses.
15. **Overuse of boldface** — mechanical emphasis on key terms.
16. **Inline-header vertical lists** — "**UX:** ..." bullets; rewrite as prose.
17. **Title case in headings** — "Strategic Negotiations And Global Partnerships" → sentence case.
18. **Emojis** in headings/bullets — remove unless the brand uses them.
19. **Curly quotation marks** — prefer straight quotes.

### Communication patterns
20. **Chatbot artifacts** — "I hope this helps!", "Of course!", "Certainly!", "Would you like...", "let me know".
21. **Knowledge-cutoff disclaimers** — "as of [date]", "up to my last training update", "while specific details are limited...".
22. **Sycophancy** — "Great question! You're absolutely right...".

### Filler & hedging
23. **Filler phrases** — "In order to"→"To", "Due to the fact that"→"Because", "At this point in time"→"Now", "has the ability to"→"can", "It is important to note that"→delete.
24. **Excessive hedging** — "could potentially possibly be argued... might" → "may".
25. **Generic positive conclusions** — "The future looks bright... exciting times lie ahead".
26. **Hyphenated pair overuse** — third-party, cross-functional, data-driven, high-quality, decision-making; humans hyphenate inconsistently.
27. **Persuasive authority tropes** — "The real question is", "at its core", "what really matters", "fundamentally", "the heart of the matter".
28. **Signposting** — "Let's dive in", "here's what you need to know", "without further ado".
29. **Fragmented headers** — heading followed by a one-line restatement of itself.

### Rhythm & rhetoric
30. **Forced metaphors** — strained/mixed metaphors, figurative substitution where a plain word is clearer, metaphor explained right after use. Cut it, say the literal thing.
31. **Dramatic fragmentation / punchy kickers** — two-word subjectless sentences, staccato "X. And Y. And Z.", mic-drop closing lines ("the catalog, honestly priced").
32. **Rhetorical questions answered immediately** — "What makes an API good? It comes down to..." State the point directly.
33. **Sentence-opener tics** — "So...", "Look,", habitual And/But, "I think"/"I believe" for facts, adverb openers (Interestingly/Importantly/Notably/Crucially).
34. **Reassurance kickers** — "And that's okay.", "There's nothing wrong with that.", "you're not alone".

## Process

1. Read the input (read_file if it's a file). 2. Identify every pattern instance. 3. Rewrite. 4. Ensure: sounds natural aloud, varied sentence structure, specific details over vague claims, right tone, simple is/are/has where appropriate. 5. Draft. 6. Ask "What makes this obviously AI generated?" — answer with remaining tells. 7. "Now make it not obviously AI generated." 8. Final version. 9. For files: apply with patch (targeted) or write_file (full rewrite) and show what changed.