# DEF-019 post-reboot evidence

Recorded 2026-10-16 after the operator rebooted usul. The old `/tmp` evidence
was absent. No historical log was reconstructed or counted as a new result.

- `freeze.json`: exact frozen-v2 path/checksum entries recovered from the
  trusted prior task record, then verified against all eight actual files.
- `baseline.json`: exact 23 pre-task checksum entries recovered from that
  record. Twenty unchanged current files matched; the three original core
  modules were recovered with local `git show HEAD:<path>` and matched their
  original checksums. The source correction is the only intended difference.
- `sdk-freeze.json`: six recorded build-13 path/checksum entries, all matched
  against the actual nested adapter files. No SDK library is copied here.
- `root-full.txt`: fresh completed guarded suite stdout/stderr, actual exit 0.
- `root-result.json`: its exact command, summary, log SHA-256 and observed
  execution-session provenance. The metadata is a receipt, not test output.
- `stock-validation.txt`: fresh unchanged stock wrapper under the reviewed
  native/startup guards, actual exit 0. Independent direct CLI return codes
  are required separately because the stock Python wrapper is fail-open on
  internal exceptions.
- `independent-full.txt`, `independent-validators.txt`,
  `independent-matrix.txt` and `independent-forward.txt`: fresh independent
  outputs copied byte-for-byte from their corresponding `*-independent.log`
  files. The receipt records actual process exits and raw-log hashes.
- `independent-result.json` and `integrity-independent.json`: the independent
  verdict/verification receipt and candidate/baseline/build-13 integrity result.
  The expected-failure original-source run is summarized with its raw-log hash
  in the receipt and review; its bulky tracebacks are not archived here.
- `forward.xml` and `forward-manifest.json`: actual fresh forward XML and 67
  current input hashes (26 views, 41 supermetrics). The XML digest equals the
  recorded historical output digest. The lost historical XML/input manifest
  was not recreated or compared as a surviving file.
- `documentation-baselines.json`: original documentation hashes and the local
  Git commit/branch used to recover the exact original source modules. This
  records provenance; no Git mutation was performed.

These files retain nonsecret local test/provenance evidence only. They do not
redistribute proprietary SDK JARs, recover lost historical capture data,
establish live-platform acceptance or authorize installation/publication.
The evidence directory itself grants no approval; the separate framework
review records the independent verdict.
