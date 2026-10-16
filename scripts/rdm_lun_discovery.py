"""Offline-testable LUN discovery analysis. No API call occurs at import time.

Raw identities/keys stay in memory or an explicit secure handoff, never reports.
Kind-name heuristics discover candidates only; semantic bindings are explicit.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import re
from typing import Any
from urllib.parse import quote


MAX_RESOURCES = 100000
MAX_CANDIDATES = 2000


class LunDiscoveryError(RuntimeError):
    CODES = frozenset({"INVALID_BINDINGS", "INCOMPLETE_INVENTORY", "READ_FAILED",
        "CANDIDATE_LIMIT", "INCOMPLETE_PROPERTIES", "INVALID_SOURCE", "INVALID_PROFILE"})

    def __init__(self, code: str):
        self.code = code if code in self.CODES else "READ_FAILED"
        super().__init__(self.code)


def validate_bindings(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    required = {"adapter_kind", "resource_kind", "granularity", "vcenter_instance_uuid"}
    allowed = required | {"uuid", "canonical_name"}
    if (not isinstance(value, dict) or not required <= value.keys() or value.keys() - allowed
            or value.get("granularity") != "physical_lun" or not ({"uuid", "canonical_name"} & value.keys())):
        raise LunDiscoveryError("INVALID_BINDINGS")
    for key in ("adapter_kind", "resource_kind"):
        if not isinstance(value[key], str) or not value[key].strip() or len(value[key]) > 128:
            raise LunDiscoveryError("INVALID_BINDINGS")
    for key in ("uuid", "canonical_name", "vcenter_instance_uuid"):
        if key not in value:
            continue
        field = value[key]
        if (not isinstance(field, dict) or set(field) != {"source", "name"}
                or field["source"] not in ("identifier", "property")
                or not isinstance(field["name"], str) or not field["name"].strip() or len(field["name"]) > 256):
            raise LunDiscoveryError("INVALID_BINDINGS")
    configured = [(value[key]["source"], value[key]["name"]) for key in
                  ("uuid", "canonical_name", "vcenter_instance_uuid") if key in value]
    if len(configured) != len(set(configured)):
        raise LunDiscoveryError("INVALID_BINDINGS")
    return deepcopy(value)


def likely_kind(adapter: str, kind: str) -> bool:
    # These are discovery hints, NOT assertions of a native kind or field role.
    return bool(re.search(r"lun|scsi|storage|volume|disk|datastore", kind, re.I))


def key_fields(resource: Any) -> tuple[dict[str, str], bool, str | None]:
    key = resource.get("resourceKey") if isinstance(resource, dict) else None
    if not isinstance(key, dict) or not all(isinstance(key.get(k), str) and key[k].strip()
            for k in ("adapterKindKey", "resourceKindKey", "name")):
        return {}, False, "resource_key_metadata_missing"
    ids = key.get("resourceIdentifiers")
    if not isinstance(ids, list) or not ids:
        return {}, False, "resource_identifiers_missing_or_empty"
    fields = {}
    folded = set()
    for entry in ids:
        kind = entry.get("identifierType") if isinstance(entry, dict) else None
        name = kind.get("name") if isinstance(kind, dict) else None
        flag = kind.get("isPartOfUniqueness") if isinstance(kind, dict) else None
        value = entry.get("value") if isinstance(entry, dict) else None
        # ASCII names have exactly the SDK's case-insensitive duplicate semantics.
        # Non-ASCII names are not silently normalized: SDK representation unproven.
        if not isinstance(name, str) or not name.strip() or not name.isascii():
            return {}, False, "identifier_name_missing_or_sdk_comparison_unverified"
        if name.lower() in folded:
            return {}, False, "duplicate_identifier_name"
        if type(flag) is not bool:
            return {}, False, "identifier_uniqueness_missing_or_nonboolean"
        if not isinstance(value, str):
            return {}, False, "identifier_value_missing_null_or_nonstring"
        if ((not value.strip() and (flag or value != ""))
                or any(ord(c) < 32 or 127 <= ord(c) <= 159 or 0xD800 <= ord(c) <= 0xDFFF for c in name + value)):
            return {}, False, "identifier_value_blank_or_unsupported_control"
        fields[name] = value
        folded.add(name.lower())
    if not any(entry["identifierType"]["isPartOfUniqueness"] for entry in ids):
        return {}, False, "no_uniqueness_bearing_identifier"
    return fields, True, None


def properties(payload: Any, resource_id: str) -> dict[str, str | None]:
    if not isinstance(payload, dict) or payload.get("resourceId") != resource_id or not isinstance(payload.get("property"), list):
        raise LunDiscoveryError("INCOMPLETE_PROPERTIES")
    result = {}
    for item in payload["property"]:
        name = item.get("name") if isinstance(item, dict) else None
        value = item.get("value") if isinstance(item, dict) else None
        if not isinstance(name, str) or not name or name in result or (value is not None and not isinstance(value, str)):
            raise LunDiscoveryError("INCOMPLETE_PROPERTIES")
        result[name] = value
    return result


def analyze(source: dict[str, str], rows: list[dict[str, Any]], bindings: dict[str, Any] | None = None):
    """Return sanitized evidence plus a private, exact key only for one proven match."""
    bindings = validate_bindings(bindings)
    if not all(isinstance(source.get(k), str) and source[k] for k in
               ("lun_uuid", "canonical_name", "vcenter_instance_uuid")):
        raise LunDiscoveryError("INVALID_SOURCE")
    census = {}
    candidates = []
    private_candidates = []
    matched = []
    incomplete = False
    ids = set()
    for row in rows:
        resource = row.get("resource")
        key = resource.get("resourceKey") if isinstance(resource, dict) else None
        rid = resource.get("identifier") if isinstance(resource, dict) else None
        if (not isinstance(key, dict) or not all(isinstance(key.get(k), str) and key[k] for k in
                ("adapterKindKey", "resourceKindKey")) or not isinstance(rid, str) or not rid or rid in ids):
            raise LunDiscoveryError("INCOMPLETE_INVENTORY")
        ids.add(rid)
        pair = (key["adapterKindKey"], key["resourceKindKey"])
        census[pair] = census.get(pair, 0) + 1
        selected = bindings is not None and pair == (bindings["adapter_kind"], bindings["resource_kind"])
        if not likely_kind(*pair) and not selected:
            continue
        fields, representable, key_issue = key_fields(resource)
        props = row.get("properties")
        complete = isinstance(props, dict) and all(isinstance(k, str) and (v is None or isinstance(v, str)) for k, v in props.items())
        methods = []
        missing_roles = []
        conflicting_roles = []
        all_values = list(fields.values()) + (list(props.values()) if complete else [])
        if source["lun_uuid"] in all_values: methods.append("exact_uuid_value_candidate")
        if source["canonical_name"] in all_values: methods.append("exact_canonical_value_candidate")
        status = "no_identity_value_match" if not methods else "semantic_binding_required"
        confidence = "none" if not methods else "unverified_semantics"
        if not representable or not complete:
            status, confidence = "incomplete_key_or_properties", "unknown"
            incomplete = True
        elif bindings is not None and not selected and methods:
            status, confidence, incomplete = "competing_unqualified_identity_match", "unknown", True
        elif selected:
            values = {}
            for role in ("uuid", "canonical_name", "vcenter_instance_uuid"):
                if role in bindings:
                    binding = bindings[role]
                    values[role] = (fields if binding["source"] == "identifier" else props).get(binding["name"])
            if any(value is None or value == "" for value in values.values()):
                status, confidence, incomplete = "missing_bound_identity_or_scope", "unknown", True
                missing_roles = [role for role, value in values.items() if value is None or value == ""]
            else:
                identity_checks = [(role, values[role] == source["lun_uuid" if role == "uuid" else role])
                                   for role in ("uuid", "canonical_name") if role in values]
                scope_match = values["vcenter_instance_uuid"] == source["vcenter_instance_uuid"]
                methods = [role + "_exact" for role, equal in identity_checks if equal]
                if methods and not scope_match:
                    status, confidence = "scope_conflict", "none"
                    conflicting_roles = ["vcenter_instance_uuid"]
                elif methods and not all(equal for _, equal in identity_checks):
                    status, confidence, incomplete = "identity_conflict", "none", True
                    conflicting_roles = [role for role, equal in identity_checks if not equal]
                elif all(equal for _, equal in identity_checks) and scope_match:
                    status, confidence = "exact_scoped_match", "high_with_operator_bindings"
                    matched.append(resource)
                else:
                    status, confidence = "no_bound_identity_match", "none"
        candidates.append({"adapter_kind": pair[0], "resource_kind": pair[1],
            "resource_uuid_fp": hashlib.sha256(rid.encode()).hexdigest()[:16],
            "status": status, "match_methods": methods, "confidence": confidence,
            "key_preserved_in_memory": True, "sdk_key_representable": representable,
            "key_issue": key_issue, "missing_roles": missing_roles, "conflicting_roles": conflicting_roles})
        hints = []
        for location, values in (("identifier", fields), ("property", props if complete else {})):
            for name, value in values.items():
                for role, expected in (("uuid", source["lun_uuid"]), ("canonical_name", source["canonical_name"]),
                                       ("vcenter_instance_uuid", source["vcenter_instance_uuid"])):
                    if value == expected:
                        hints.append({"source": location, "name": name, "exact_value_role_hint": role})
        # Explicit secure evidence is not a selected target or semantic approval.
        # Keep all candidate keys; never retain unrelated property values/tokens.
        private_candidates.append({"resource_uuid": rid, "resourceKey": deepcopy(key),
            "property_names": list(props) if complete else [], "field_hints": hints})
    status = ("incomplete_candidate_evidence" if incomplete else "ambiguous_matches" if len(matched) > 1 else
              "unique_match" if len(matched) == 1 else "no_candidate_kinds_observed" if not candidates else
              "semantic_bindings_required" if bindings is None else "no_unique_match")
    reuse = status == "unique_match"
    private = {"resource_uuid": matched[0]["identifier"], "resourceKey": deepcopy(matched[0]["resourceKey"])} if reuse else None
    return {"schema_version": "vcfcf-rdm-lun-discovery-v1", "status": status,
        "recommendation": "REUSE" if reuse else "INSUFFICIENT EVIDENCE",
        "scope": "caller_visible_inventory_only", "semantic_bindings": "operator_supplied" if bindings else "not_supplied",
        "resource_kinds": [{"adapter_kind": a, "resource_kind": k, "count": n} for (a, k), n in sorted(census.items())],
        "candidate_count": len(candidates), "exact_scoped_match_count": len(matched), "candidates": candidates,
        "source": {"rdm_count": 1, "current_host_uuid_match": True, "canonical_identity_present": True}}, private, {
            "purpose": "unqualified_candidates_not_relationship_targets", "candidates": private_candidates}


def collect(client: Any, bindings: dict[str, Any] | None):
    rows, seen, total = [], set(), None
    candidate_count = 0
    for page in range(1000):
        response = client._request("GET", "/api/resources", params={"page": page, "pageSize": 1000}, timeout=30)
        if response.status_code != 200: raise LunDiscoveryError("READ_FAILED")
        body = response.json()
        resources = body.get("resourceList") if isinstance(body, dict) else None
        info = body.get("pageInfo") if isinstance(body, dict) else None
        count = info.get("totalCount") if isinstance(info, dict) else None
        if not isinstance(resources, list) or type(count) is not int or count < 0 or (total is not None and total != count):
            raise LunDiscoveryError("INCOMPLETE_INVENTORY")
        total = count
        if total > MAX_RESOURCES: raise LunDiscoveryError("INCOMPLETE_INVENTORY")
        for resource in resources:
            key = resource.get("resourceKey") if isinstance(resource, dict) else None
            rid = resource.get("identifier") if isinstance(resource, dict) else None
            if (not isinstance(key, dict) or not all(isinstance(key.get(k), str) and key[k] for k in
                    ("adapterKindKey", "resourceKindKey")) or not isinstance(rid, str) or not rid or rid in seen):
                raise LunDiscoveryError("INCOMPLETE_INVENTORY")
            seen.add(rid)
            row = {"resource": resource}
            pair = (key["adapterKindKey"], key["resourceKindKey"])
            if likely_kind(*pair) or (bindings and pair == (bindings["adapter_kind"], bindings["resource_kind"])):
                candidate_count += 1
                if candidate_count > MAX_CANDIDATES: raise LunDiscoveryError("CANDIDATE_LIMIT")
                encoded_id = quote(rid, safe="")
                detail = client._request("GET", f"/api/resources/{encoded_id}", timeout=30)
                prop = client._request("GET", f"/api/resources/{encoded_id}/properties", timeout=30)
                if detail.status_code != 200 or prop.status_code != 200: raise LunDiscoveryError("READ_FAILED")
                full = detail.json()
                if (not isinstance(full, dict) or full.get("identifier") != rid
                        or not isinstance(full.get("resourceKey"), dict)
                        or any(full["resourceKey"].get(k) != key[k] for k in ("adapterKindKey", "resourceKindKey"))):
                    raise LunDiscoveryError("INCOMPLETE_INVENTORY")
                row = {"resource": full, "properties": properties(prop.json(), rid)}
            rows.append(row)
        if len(rows) == total: return rows
        if not resources or len(rows) > total: raise LunDiscoveryError("INCOMPLETE_INVENTORY")
    raise LunDiscoveryError("INCOMPLETE_INVENTORY")


def run(profile, capture_source, release_token, bindings=None):
    if profile != "devel": raise LunDiscoveryError("INVALID_PROFILE")
    bindings = validate_bindings(bindings)
    from vcfcf_common.client import VCFOpsClient
    client = VCFOpsClient.from_env(profile, default_profile="devel")
    cleanup = {"attempted": False, "status": "not_needed"}
    try:
        source = capture_source(include_lun=True)
        report, private, evidence = analyze(source, collect(client, bindings), bindings)
        report["token_cleanup"] = cleanup
        return report, private, evidence
    finally:
        release_token(client, cleanup)
