---
name: vcfops-validation
description: Validate changed VCF Content Factory content and run the full deterministic validation gates before review, installation, or release.
---

# Validation

After a content-file edit, run
`scripts/validate-changed-content.sh <content-file>`. This is the Codex
equivalent of the Claude post-edit hook. It does not replace the full validation
chain, reviewer gate, CI, or explicit install approval. Use
`scripts/validate-changed-content.sh --all` before a review/install gate.
