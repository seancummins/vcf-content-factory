"""Offline, conservative LU-designator analysis; no network or file access."""
from __future__ import annotations

import hashlib
import re


class IdentityError(ValueError):
    pass


def _is_integer(value):
    # pyVmomi byte/long are int subclasses; bool is not a storage integer.
    return isinstance(value, int) and not isinstance(value, bool)


def fingerprint(value):
    return hashlib.sha256(str(value).encode()).hexdigest()[:16]


def naa(value, prefix):
    if not isinstance(value, str) or not re.fullmatch(re.escape(prefix) + r"[0-9a-fA-F]+", value, re.I):
        raise IdentityError("INVALID_NAA_REPRESENTATION")
    payload = value[len(prefix):].lower()
    if not ((len(payload) == 16 and payload[0] == "5") or (len(payload) == 32 and payload[0] == "6")):
        raise IdentityError("UNSUPPORTED_NAA_FORMAT")
    return payload


def reference(value):
    if not isinstance(value, dict) or set(value) != {"naa"}:
        raise IdentityError("INVALID_STORAGE_REFERENCE")
    return naa(value["naa"], "0x")


def descriptor(item):
    """Recognize only complete binary LU-associated NAA5/6 page83 descriptors.

    namespaceId is deliberately not interpreted as the designator type. The
    VMware namespace labels the representation; the header independently proves
    association/type. Page80/payload-only/unknown encodings are never inferred.
    """
    result = {"format": "unrecognized", "status": "unsupported", "namespace": "other"}
    if not isinstance(item, dict):
        return result, None
    namespace = item.get("namespace")
    if isinstance(namespace, str) and namespace.lower() in {"naa", "eui", "t10", "unknown"}:
        result["namespace"] = namespace.lower()
    namespace_id = item.get("namespaceId")
    result["namespace_id_valid"] = _is_integer(namespace_id) and -128 <= namespace_id <= 255
    if not result["namespace_id_valid"]:
        result["status"] = "namespace_id_missing_or_invalid"
        return result, None
    data = item.get("data")
    if not isinstance(data, list) or not all(_is_integer(x) and -128 <= x <= 255 for x in data):
        result["status"] = "invalid_bytes"
        return result, None
    raw = bytes(x & 255 for x in data)
    result["byte_count"] = len(raw)
    result["data_fp"] = fingerprint(raw.hex())
    if result["namespace"] != "naa":
        return result, None
    if len(raw) < 4:
        result["status"] = "missing_descriptor_header"
        return result, None
    result.update({"association": (raw[1] >> 4) & 3, "code_set": raw[0] & 15,
                   "designator_type": raw[1] & 15, "declared_length": raw[3]})
    if raw[2] != 0 or raw[1] & 0x40 or (raw[1] & 0x80) or raw[0] & 0xf0:
        result["status"] = "unsupported_header_bits"
    elif len(raw) != 4 + raw[3]:
        result["status"] = "invalid_declared_length"
    elif result["code_set"] != 1 or result["designator_type"] != 3:
        result["status"] = "unsupported_designator"
    else:
        try:
            payload = naa("naa." + raw[4:].hex(), "naa.")
        except IdentityError:
            result["status"] = "unsupported_naa_format"
        else:
            result.update({"format": "page83_header_and_payload", "status": "valid_lu_naa",
                           "naa_format": "naa" + payload[0], "payload_fp": fingerprint(payload)})
            if result["association"] in {1, 2}:
                result["status"] = "not_logical_unit"
                return result, None
            if result["association"] != 0:
                result["status"] = "reserved_association"
                return result, None
            return result, payload
    return result, None


def analyze(source, expected):
    """Return sanitized report and private full identity evidence separately."""
    expected_text = expected.get("naa") if isinstance(expected, dict) else None
    expected = reference(expected)
    if not isinstance(source, dict) or not isinstance(source.get("lun_uuid"), str) or not source["lun_uuid"]:
        raise IdentityError("INVALID_BACKING_UUID")
    timestamp = source.get("observed_at_epoch_ms")
    if timestamp is not None and (type(timestamp) is not int or timestamp <= 0):
        raise IdentityError("INVALID_OBSERVATION_TIME")
    observations = source.get("lun_observations")
    if not isinstance(observations, list) or not observations:
        raise IdentityError("MISSING_HOST_OBSERVATIONS")
    reports, tokens, seen = [], [], set()
    consensus = {field: set() for field in ("vendor", "model", "lunType", "deviceType", "capacity")}
    blocked = False
    for observation in observations:
        if not isinstance(observation, dict):
            raise IdentityError("INVALID_HOST_OBSERVATIONS")
        host = observation.get("host_moid")
        if not isinstance(host, str) or not host or host in seen:
            raise IdentityError("INVALID_HOST_OBSERVATIONS")
        seen.add(host)
        method = observation.get("join_method")
        method = method if method in {"exact_backing_uuid", "exact_canonical_candidate"} else "unrecognized"
        report = {"host_fp": fingerprint(host), "join_method": method,
                  "status": "blocked"}
        lun = observation.get("lun")
        if not isinstance(lun, dict) or report["join_method"] not in {"exact_backing_uuid", "exact_canonical_candidate"}:
            report["reason"] = "lun_missing_ambiguous_or_unreadable"
            blocked = True
            reports.append(report)
            continue
        if not isinstance(lun.get("uuid"), str) or not lun["uuid"]:
            raise IdentityError("MISSING_OBSERVED_LUN_UUID")
        if method == "exact_backing_uuid" and lun["uuid"] != source["lun_uuid"]:
            raise IdentityError("CONTRADICTORY_UUID_JOIN")
        description_invalid = False
        for field in ("vendor", "model", "lunType", "deviceType"):
            value = lun.get(field)
            if value is not None:
                if not isinstance(value, str) or not value:
                    description_invalid = True
                else:
                    consensus[field].add(value)
        capacity = lun.get("capacity")
        capacity_valid = False
        if capacity is not None:
            if (isinstance(capacity, dict) and set(capacity) == {"block", "blockSize"}
                    and all(_is_integer(capacity[k]) and capacity[k] > 0 for k in capacity)
                    and capacity["block"] * capacity["blockSize"] <= 2**63 - 1):
                capacity_valid = True
                consensus["capacity"].add(capacity["block"] * capacity["blockSize"])
            else:
                description_invalid = True
        try:
            canonical = naa(lun.get("canonicalName"), "naa.")
        except IdentityError:
            canonical = None
        items = [lun["durableName"]] if lun.get("durableName") is not None else []
        alternates = lun.get("alternateName")
        if not isinstance(alternates, list):
            raise IdentityError("INCOMPLETE_ALTERNATE_NAMES")
        items += alternates
        decoded = [descriptor(item) for item in items]
        for index, (detail, _) in enumerate(decoded):
            detail["source_field"] = "durableName" if index == 0 and lun.get("durableName") is not None else "alternateName"
        raw_descriptors = lun.get("descriptor")
        if not isinstance(raw_descriptors, list) or any(not isinstance(d, dict) for d in raw_descriptors):
            raise IdentityError("INCOMPLETE_DESCRIPTOR_IDS")
        valid = {token for _, token in decoded if token is not None}
        # Unknown alternate representations are retained but cannot supply proof.
        # Complete port/target designators are legitimate but never LU identity.
        # Malformed NAA claims remain unresolved rather than silently skipped.
        conflicting = any(detail["namespace"] == "naa" and detail["status"] not in {"valid_lu_naa", "not_logical_unit"}
                          for detail, _ in decoded)
        report.update({"descriptors": [detail for detail, _ in decoded],
                       "canonical_supported": canonical is not None,
                       "canonical_equals_reference": canonical == expected,
                       "distinct_lu_designators": len(valid),
                       "uuid_fp": fingerprint(lun.get("uuid")),
                       "uuid_equals_backing": lun.get("uuid") == source.get("lun_uuid"),
                       "opaque_uuid_equals_reference_text": lun["uuid"] == expected_text,
                       "opaque_uuid_equals_canonical_text": lun["uuid"] == lun.get("canonicalName"),
                       "descriptor_id_count": len(raw_descriptors),
                       "descriptor_id_exact_canonical_count": sum(d.get("id") == lun.get("canonicalName") for d in raw_descriptors),
                       "descriptor_id_exact_reference_text_count": sum(d.get("id") == expected_text for d in raw_descriptors),
                       "capacity_dimensions_valid": capacity_valid,
                       "descriptive_values_valid": not description_invalid,
                       "descriptive_properties_available": {name: lun.get(name) is not None for name in
                           ("vendor", "model", "revision", "displayName", "serialNumber", "lunType", "deviceType", "localDisk", "capacity")}})
        if canonical is not None and valid == {canonical} and canonical == expected and not conflicting and not description_invalid:
            report["status"] = "qualified_observation"
            tokens.append(canonical)
        else:
            blocked = True
            report["reason"] = "missing_conflicting_or_unproven_lu_identity"
        reports.append(report)
    current = [r for r, o in zip(reports, observations) if o.get("host_moid") == source.get("host_moid")]
    if len(current) != 1 or current[0]["join_method"] != "exact_backing_uuid" or not current[0].get("uuid_equals_backing"):
        blocked = True
    conflicts = [field for field, values in consensus.items() if len(values) > 1]
    if conflicts:
        blocked = True
    qualified = not blocked and len(tokens) == len(observations) and len(set(tokens)) == 1
    return {"mode": "lun-identity", "qualification": "CONDITIONALLY QUALIFIED" if qualified else "BLOCKED",
            "observed_at_epoch_ms": timestamp,
            "source_rdm_count": 1, "observed_host_count": len(observations), "hosts": reports,
            "cross_host_equivalence": "observed" if qualified and len(tokens) >= 2 else "not_established",
            "cross_vcenter_equivalence": "not_tested", "temporal_stability": "not_tested",
            "conflicting_descriptive_fields": conflicts,
            "storage_reference": "operator_supplied_not_independently_acquired",
            "candidate_key": {"identity_scheme": "naa", "payload_fp": fingerprint(tokens[0])} if qualified else None}, source
