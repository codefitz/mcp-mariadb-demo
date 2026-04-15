# Query patterns

## List Red Hat hosts
```sql
SELECT HOSTNAME
FROM ASSET_HOST
WHERE OS LIKE '%Red Hat%';
```

## Distinct Red Hat values across OS fields
```sql
SELECT DISTINCT OS
FROM ASSET_HOST
WHERE OS LIKE '%RED%HAT%'
   OR OS_TYPE LIKE '%RED%HAT%'
   OR OS_VENDOR LIKE '%RED%HAT%';
```

## Get software for a named host using trusted relationship path
```sql
SELECT si.*
FROM ASSET_SOFTWAREINSTANCE si
JOIN ASSET_SOFTWAREINSTANCE_RELATIONSHIP sir
  ON sir.CHILD_ID = si.ID
WHERE sir.PARENT_KIND = 'Host'
  AND sir.CHILD_KIND = 'SoftwareInstance'
  AND sir.PARENT_ID = (
      SELECT ah.ID
      FROM ASSET_HOST ah
      WHERE ah.NAME = 'ldn-t4dpr-02'
  );
```

## List software types by host using trusted join
```sql
SELECT
    h.NAME AS host_name,
    si.TYPE AS software_type
FROM ASSET_HOST h
JOIN ASSET_SOFTWAREINSTANCE_RELATIONSHIP r
  ON h.GUID = r.PARENT_GUID
 AND r.PARENT_KIND = 'Host'
 AND r.CHILD_KIND = 'SoftwareInstance'
JOIN ASSET_SOFTWAREINSTANCE si
  ON r.CHILD_ID = si.ID;
```

## Count software per host with environment
```sql
WITH software_counts AS (
    SELECT
        PARENT_GUID,
        COUNT(*) AS software_count
    FROM ASSET_SOFTWAREINSTANCE_RELATIONSHIP
    WHERE PARENT_KIND = 'Host'
      AND CHILD_KIND = 'SoftwareInstance'
    GROUP BY PARENT_GUID
)
SELECT
    h.NAME,
    COALESCE(sc.software_count, 0) AS software_count,
    ue.NAME AS environment_name
FROM ASSET_HOST h
LEFT JOIN software_counts sc
       ON h.GUID = sc.PARENT_GUID
LEFT JOIN UMAP_CI ci
       ON h.GUID = ci.ASSET_GUID
LEFT JOIN UMAP_ENVIRONMENT ue
       ON ci.ENVIRONMENT_ID = ue.ID
ORDER BY software_count DESC;
```

## Approximate software count by host using RUNNING_ON fallback
```sql
WITH software_counts AS (
    SELECT
        RUNNING_ON AS host_shortname,
        COUNT(*) AS software_count
    FROM ASSET_SOFTWAREINSTANCE
    GROUP BY RUNNING_ON
)
SELECT
    h.NAME,
    h.HOSTNAME,
    COALESCE(sc.software_count, 0) AS software_count,
    ue.NAME AS environment_name
FROM ASSET_HOST h
LEFT JOIN software_counts sc
       ON h.HOSTNAME = sc.host_shortname
LEFT JOIN UMAP_CI ci
       ON h.GUID = ci.ASSET_GUID
LEFT JOIN UMAP_ENVIRONMENT ue
       ON ci.ENVIRONMENT_ID = ue.ID;
```

## Exploration query for all asset tables
```sql
SHOW TABLES LIKE 'ASSET\_%';
```

## Exploration query for relationship table indexes
```sql
SHOW INDEXES FROM ASSET_SOFTWAREINSTANCE_RELATIONSHIP;
```
