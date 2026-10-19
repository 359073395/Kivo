# Workflow And Rules

## Decision Stages

1. Define region, category and optional keyword/efficacy direction.
2. Acquire current platform evidence through LinkFox/TikTok import.
3. Validate links, observation time, sales, GMV, growth and data confidence.
4. Run Eagle Eye five-layer screening:
   - category/efficacy fit;
   - recent market signal;
   - competitor reproducibility;
   - content feasibility;
   - owned-business readiness when applicable.
5. Inject full data only for passed candidates.
6. Apply hard exclusions and VCP memory.
7. Calculate Prism mathematical, optimistic and pessimistic scores.
8. Run structured LLM/Furnace assessment only for rule-qualified candidates.
9. Route to high-score, scale, observation, data-completion, market opportunity, sourcing/listing or elimination.
10. Import test/advertising feedback and rescore.
11. Create rule-change proposals; activate only after approval and backtest.

## Formal High-Score Gate

A candidate cannot enter a formal plan unless all applicable gates pass:

- evidence is no more than 48 hours old;
- required market fields are complete and consistent;
- no hard exclusion is triggered;
- rule score meets the active version threshold;
- LLM output is valid structured data, above threshold and sufficiently confident;
- an owned SKU has exact identity, current price, cost/margin, inventory and store listing readiness.

LLM timeout, invalid JSON, low confidence or score conflict routes to observation/data completion.

## Memory Policy

Keep decision-useful memory:

- elimination cause;
- observation reason;
- proven store-SKU combination;
- proven script direction or creator wording;
- category experience;
- data anomaly or unreliable-source pattern.

Do not keep routine execution logs as business memory. Recent testing and rule versions take priority over old conclusions.

## Test Review

Use a stable experiment ID. Treat two-hour and 24-hour data as the same sample, with 24-hour data taking precedence. Review:

- views and retention;
- click-through rate;
- conversion rate;
- orders and GMV;
- spend and ROAS;
- store/listing readiness;
- account effect;
- script direction;
- natural versus advertising traffic.

Do not infer that a SKU failed when the store, listing, account or script is the actual bottleneck.

## Truthfulness

- Say `current imported data` when no fresh task was run.
- Preserve source URLs and observation dates.
- Distinguish confirmed facts, calculations and inference.
- Never fabricate sales, GMV, growth, inventory, profit or store links.
- Exact SKU identity overrides name similarity.

