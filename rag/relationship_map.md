# Relationship map

## Trusted relationships

### Host -> SoftwareInstance
Join path:
- `ASSET_HOST.GUID = ASSET_SOFTWAREINSTANCE_RELATIONSHIP.PARENT_GUID`
- `ASSET_SOFTWAREINSTANCE_RELATIONSHIP.CHILD_ID = ASSET_SOFTWAREINSTANCE.ID`

Required filters:
- `ASSET_SOFTWAREINSTANCE_RELATIONSHIP.PARENT_KIND = 'Host'`
- `ASSET_SOFTWAREINSTANCE_RELATIONSHIP.CHILD_KIND = 'SoftwareInstance'`

Confidence:
- High

### Host -> Environment
Join path:
- `ASSET_HOST.GUID = UMAP_CI.ASSET_GUID`
- `UMAP_CI.ENVIRONMENT_ID = UMAP_ENVIRONMENT.ID`

Confidence:
- High

## Heuristic or fallback relationships

### SoftwareInstance -> Host via RUNNING_ON
Join path:
- `ASSET_HOST.HOSTNAME = ASSET_SOFTWAREINSTANCE.RUNNING_ON`

Use only when:
- a trusted relationship path is unavailable
- a fast approximation is acceptable

Risks:
- shortname versus FQDN mismatch
- stale denormalised values
- hostname mismatch

Confidence:
- Medium

### NetworkInterface -> Host via parsed interface name
Join path:
- derive host name from `ASSET_NETWORKINTERFACE.NAME` only if the value follows a stable naming convention such as `... on <host-name>`

Use only when:
- no bridge table or explicit key exists in the live schema

Risks:
- brittle naming convention
- parsing errors
- duplicate host names

Confidence:
- Low

## Unresolved relationships to verify in live schema

- `ASSET_NETWORKINTERFACE.DEVICE_ID` may link to a device or host table, but this is not confirmed by the current notes.
- Additional `*_RELATIONSHIP`, `*_MEMBER`, `*_MAP`, or `UMAP_*` tables may provide trusted paths for network interfaces and should be preferred if found.
