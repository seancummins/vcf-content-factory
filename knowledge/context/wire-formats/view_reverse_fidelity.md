# View reverse fidelity (DEF-019)

Date: 2026-10-16. Scope: offline reverse conversion within the existing view
model. This evidence uses public `VMWARE` kinds and explicitly synthetic fixture
keys/values. It does not recover the historical private four-view extract, prove
live platform acceptance, or claim that every forward-model or PAK-origin view
has a lossless reverse representation.

## Supported contract

Both dictionary parsers (`extractor._parse_view_def_element` and
`reverse_local._parse_view_xml_to_dict`) and the dataclass parser
`dashboards.reverse.parse_view_xml_element` use one shared fidelity decoder.
Their existing callers include the exported content-ZIP parser, local XML map
builder, public `parse_view_from_content_xml`, and `vcfcf_*` compatibility
aliases. Both dictionary YAML writers emit the existing `subject.filter` key;
when `subjects` supplies several kinds, `subject` contains only the view-wide
filter. No top-level YAML `subject_filter` key is introduced.

The decoder preserves the following supported semantics:

- Subject filters: ordered OR groups of ordered AND conditions, condition and
  selector fields, string/integer/finite-float values, and optional `transform`
  and boolean `businessHours`. Optional absence remains distinct from explicit
  `businessHours=false`. String values such as `"true"` and `"false"` remain
  strings. `metricValue.isStringMetric` must agree with the value's type.
- The current model has one view-wide filter. Every `SubjectType`, including
  descendant/self entries for every kind, must have the same representable
  filter, or all must omit it. Mixed filtered/unfiltered entries and differing
  filters fail. Some owning-SubjectType injection paths can produce such mixed
  entries; they are outside this supported reverse contract.
- Ordinary and instanced column property/string flags are independent. A
  property can have `isProperty=true` and `isStringAttribute=false`. False flags
  use existing model defaults; no property is inferred from its key/name.
- One instanced-group driver with `attributeKey="Instance Name"` and a nonempty
  `instanceGroupName`, followed by colon-instance members. Driver show/summary
  flags survive. Member keys split only at the first colon and the first pipe
  after it; later colon/pipe segments remain in the suffix, preserving keys
  such as `diskspace:262|snapshot:snapshot-1|used` exactly. The existing model
  regenerates the member attribute from these components.
- The member wire shape carries no separate binding to a driver. More than one
  driver, a colon-instance member before the driver, or malformed driver/member
  fields are rejected rather than assigned an invented group. A colon-bearing
  ordinary column in a view without a group remains ordinary.
- The supported member fixture retains CURRENT, MAX,
  TRANSFORM_EXPRESSION plus its expression, TIMESTAMP, subject binding, unit,
  color bounds and column order. This change restores expression fields in
  both dictionary reverse routes as part of group reconstruction.
- One `summaryInfos` footer row with existing SUM/AVG/MIN/MAX/COUNT aggregation,
  custom/default label and ordered column indexes. Explicit `[0]`, `[]`, and
  all columns remain distinct. Missing summary means no footer. An existing
  summary row must carry `displayName`, `aggregation`, and an explicit
  `attributeIndexes` list; missing-field wire semantics are not inferred. The
  renderer already writes all three fields for `summary: true`.

## Strict errors

Unsupported filter payloads raise fixed, value-free `ValueError` messages. This
includes duplicate JSON keys, nonfinite numbers (including overflow), malformed
or empty groups, missing/unknown fields, unsupported enums/types, bare boolean
values, and conflicting `isStringMetric` flags. Validation exception payloads
are not propagated as message text or chained causes.

Critical column fidelity properties must be scalar and unique. A present
missing-value/list-valued flag, invalid boolean token, or activated driver with
no valid attribute key fails. Summary structure is checked directly: one
Property/List/Item/Value row, only supported row properties, unique scalar
properties, and a direct index list of in-range integer items. Empty malformed
summary blocks, unknown scalar/list fields, duplicate rows/properties and
nested/invalid index items fail.

These strict fidelity errors deliberately propagate from the public dataclass
APIs, despite their legacy WARN/None behavior for other unrecognised shapes.
The extraction/local-map callers finish parsing before writing view YAML. They
therefore stop instead of writing an apparently valid view with a broader
resource selection or lost group/summary semantics. Existing warning behavior
for unrelated unsupported shapes is otherwise unchanged.

## Reproduction and evidence

`tests/fixtures/view_reverse_fidelity_ordinary.xml`, `..._filtered.xml`, and
`..._instanced.xml` were generated once with the existing YAML loader and
renderer, then retained as XML regression inputs. Tests parse the real XML
through all three routes, write existing-schema YAML, reload it with
`load_view`, and compare the rendered XML bytes. The dataclass route also
renders the directly parsed model. UUIDs, kind and column order, default
behavior, and selected semantics are asserted independently of byte equality.
No source XML cache or blind XML passthrough is used.

Before the source correction, the initial matrix recorded **120 failures and
3 passes** (ordinary cases passed; filter/group/summary fidelity failed). The
completed matrix has **264 passes**. Four existing loader warnings report that
the dataclass route retains the default 24-hour window implicitly for aggregate
members; the selected canonical fixture still renders byte-identically. No
forward renderer, loader, template, packaging or product-model change was needed.

Run the durable offline launcher (it denies credential/environment-file access,
networking and repository writes from tests):

```sh
.venv/bin/python -B tests/offline/run.py --test tests/test_view_reverse_fidelity.py
```

The new matrix plus related filter, group, multi-subject/binding, local reverse
and time-segment tests passed **388 tests** (10 recorded warnings, including
the four above, existing aggregation warnings, and one existing UTC API
DeprecationWarning):

```sh
.venv/bin/python -B tests/offline/run.py \
  --test tests/test_view_reverse_fidelity.py \
  --test tests/test_view_multi_subject_column_binding.py \
  --test tests/test_view_subject_filter.py \
  --test tests/test_view_instanced_group_columns.py \
  --test tests/test_view_multi_subject.py \
  --test tests/test_reverse_local.py \
  --test tests/test_view_time_segment_column.py
```

Implementation references: existing `SubjectFilterCondition`,
`InstancedGroupSpec`, and `SummaryRow` in `src/vcfcf_core/dashboards/loader.py`;
`_xml_instanced_group_item` and `_render_summary_infos` in
`src/vcfcf_core/dashboards/render.py`; prior column wire documentation in
[view_column_wire_format.md](view_column_wire_format.md). Existing model and
renderer comments cite the read-only vendor reference provenance. This fix adds
synthetic coverage of that current contract; it does not invent vendor behavior.
