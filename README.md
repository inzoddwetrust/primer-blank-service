# primer-blank-service

The deploy machine's test service: the shape of a co-located service of the
Primer protocol, small enough for tier 3 of `pridem` to install beside
`primer-blank` on every run. Not a template for teams.

What it shows the machine:

- **seams to its product** (protocol 4, form B; contract 3 rule 21) --
  `SERVICE_API_URL` (`address`), `SERVICE_TOKEN` (`minted`) and
  `SERVICE_KEY` (`derived`: `python -m app.derive service-key`, an HMAC of the
  token, the same for the same token);
- **a seam from its product** -- `PRODUCT_WEBHOOK_URL`;
- **the product's data** (form D) -- `profile`, checked by
  `python -m app.profile <dir>`: accepted when it holds a file `ok`;
- **`/health` and `/ready`** of protocol 9 through `primer_report`, a byte-for-
  byte copy of `primer-blank/backend/primer_report` that CI compares with the
  blank's; no database, so `alembic_head` is `null`. `seams` reports what came,
  and the one check, `config`, is red when a value is missing or the key is not
  the token's.

Released by tags `vX.Y.Z` only (contract 3 rule 3); a tag, once out, is never
moved.

## Checks

CI (`.github/workflows/ci.yml`): ruff, mypy, pytest; the image built as the
machine builds it, `derive` and `validate` run in it as the machine runs them;
`primer.yaml` through the loader of `pridem` and `pridem check` at the pinned
machine; images pinned by tag and digest; the `primer_report` copy. Each check
that can be red runs its `--selftest` first.
