# SCD Type 2: Complete Guide with Examples

## 1. What is SCD Type 2?

**SCD Type 2** (Slowly Changing Dimension Type 2) keeps **full history** by adding a **new row** every time a tracked value changes. The old row is **not deleted or overwritten**. It is closed off with an end date and marked as no longer current.

It is the most widely used SCD type, because it answers *"what was true at that time?"* exactly.

### Extra columns Type 2 needs

| Column | Purpose |
|---|---|
| `cust_key` | **Surrogate key**: a unique number for each *version* of the customer |
| `cust_id` | **Natural / business key**: the same for all versions of one customer |
| `start_date` | When this version became valid |
| `end_date` | When it stopped being valid (`9999-12-31` means "still valid") |
| `is_current` | `Y` for the latest version, `N` for old ones |

In this guide, both `city` and `tier` are **tracked** columns: a change in either one creates a new row.

---

## 2. Table Structures

```sql
CREATE TABLE stg_customer (
    cust_id  VARCHAR(10),
    name     VARCHAR(50),
    city     VARCHAR(50),
    tier     VARCHAR(20)
);

CREATE TABLE dim_customer (
    cust_key    INT IDENTITY PRIMARY KEY,   -- surrogate key (auto-generated)
    cust_id     VARCHAR(10),                -- natural key
    name        VARCHAR(50),
    city        VARCHAR(50),
    tier        VARCHAR(20),
    start_date  DATE,
    end_date    DATE,
    is_current  CHAR(1)
);
```

> IDENTITY syntax varies by database (e.g. `GENERATED ALWAYS AS IDENTITY` in PostgreSQL, `AUTOINCREMENT` in Snowflake).

---

## 3. Run-by-Run Example

### Run 1: 2026-01-01

**Source (`stg_customer`)**

| cust_id | name | city | tier |
|---|---|---|---|
| C01 | Ravi | Bengaluru | Silver |
| C02 | Priya | Chennai | Gold |
| C03 | Arjun | Pune | Bronze |

**Target after Run 1 (`dim_customer`)**

| cust_key | cust_id | name | city | tier | start_date | end_date | is_current |
|---|---|---|---|---|---|---|---|
| 1 | C01 | Ravi | Bengaluru | Silver | 2026-01-01 | 9999-12-31 | Y |
| 2 | C02 | Priya | Chennai | Gold | 2026-01-01 | 9999-12-31 | Y |
| 3 | C03 | Arjun | Pune | Bronze | 2026-01-01 | 9999-12-31 | Y |

All rows are new, so all are inserted as current.

---

### Run 2: 2026-06-01

**Source**

| cust_id | name | city | tier |
|---|---|---|---|
| C01 | Ravi | **Hyderabad** | Silver |
| C02 | Priya | Chennai | **Platinum** |
| C03 | Arjun | Pune | Bronze |
| C04 | Kavya | Mumbai | Silver |

- **Ravi**: city changed
- **Priya**: tier changed
- **Arjun**: no change
- **Kavya**: new customer

**Target after Run 2**

| cust_key | cust_id | name | city | tier | start_date | end_date | is_current |
|---|---|---|---|---|---|---|---|
| 1 | C01 | Ravi | Bengaluru | Silver | 2026-01-01 | **2026-05-31** | **N** |
| 2 | C02 | Priya | Chennai | Gold | 2026-01-01 | **2026-05-31** | **N** |
| 3 | C03 | Arjun | Pune | Bronze | 2026-01-01 | 9999-12-31 | Y |
| **4** | **C01** | **Ravi** | **Hyderabad** | **Silver** | **2026-06-01** | **9999-12-31** | **Y** |
| **5** | **C02** | **Priya** | **Chennai** | **Platinum** | **2026-06-01** | **9999-12-31** | **Y** |
| **6** | **C04** | **Kavya** | **Mumbai** | **Silver** | **2026-06-01** | **9999-12-31** | **Y** |

**What happened**

- **Ravi and Priya**: old row **expired** (end_date = day before the change, is_current = N), new row **inserted**.
- **Arjun**: untouched.
- **Kavya**: inserted as a new customer.
- Old rows still show the **old values** (Bengaluru, Gold). In Type 2, old versions are never overwritten.

---

### Run 3: 2026-10-25

**Source**

| cust_id | name | city | tier |
|---|---|---|---|
| C01 | Ravi | **Delhi** | **Gold** |
| C02 | Priya | Chennai | Platinum |
| C03 | Arjun | Pune | **Silver** |
| C04 | Kavya | Mumbai | Silver |
| C05 | Sneha | Kochi | Gold |

- **Ravi**: city and tier changed
- **Priya**: no change
- **Arjun**: tier changed
- **Kavya**: no change
- **Sneha**: new customer

**Target after Run 3**

| cust_key | cust_id | name | city | tier | start_date | end_date | is_current |
|---|---|---|---|---|---|---|---|
| 1 | C01 | Ravi | Bengaluru | Silver | 2026-01-01 | 2026-05-31 | N |
| 2 | C02 | Priya | Chennai | Gold | 2026-01-01 | 2026-05-31 | N |
| 3 | C03 | Arjun | Pune | Bronze | 2026-01-01 | **2026-10-24** | **N** |
| 4 | C01 | Ravi | Hyderabad | Silver | 2026-06-01 | **2026-10-24** | **N** |
| 5 | C02 | Priya | Chennai | Platinum | 2026-06-01 | 9999-12-31 | Y |
| 6 | C04 | Kavya | Mumbai | Silver | 2026-06-01 | 9999-12-31 | Y |
| **7** | **C01** | **Ravi** | **Delhi** | **Gold** | **2026-10-25** | **9999-12-31** | **Y** |
| **8** | **C03** | **Arjun** | **Pune** | **Silver** | **2026-10-25** | **9999-12-31** | **Y** |
| **9** | **C05** | **Sneha** | **Kochi** | **Gold** | **2026-10-25** | **9999-12-31** | **Y** |

Ravi now has **three rows**, one for each period. Nothing was lost.

---

## 4. MERGE Code

```sql
MERGE INTO dim_customer t
USING (
    -- Copy 1: every source row with its real key
    --   -> expires changed rows, inserts brand-new customers
    SELECT s.cust_id AS merge_key, s.*
    FROM   stg_customer s

    UNION ALL

    -- Copy 2: only CHANGED customers, with a NULL key
    --   -> NULL never matches, so this forces an INSERT of the new version
    SELECT NULL AS merge_key, s.*
    FROM   stg_customer s
    JOIN   dim_customer t
      ON   t.cust_id = s.cust_id
     AND   t.is_current = 'Y'
    WHERE  t.city IS DISTINCT FROM s.city
       OR  t.tier IS DISTINCT FROM s.tier
) s
ON  t.cust_id    = s.merge_key
AND t.is_current = 'Y'

-- Expire the old version
WHEN MATCHED AND (   t.city IS DISTINCT FROM s.city
                  OR t.tier IS DISTINCT FROM s.tier ) THEN
  UPDATE SET end_date   = :load_date - INTERVAL '1' DAY,
             is_current = 'N'

-- Insert the new version (changed customers) or first version (new customers)
WHEN NOT MATCHED THEN
  INSERT (cust_id, name, city, tier, start_date, end_date, is_current)
  VALUES (s.cust_id, s.name, s.city, s.tier, :load_date, DATE '9999-12-31', 'Y');
```

> - `:load_date` is the batch date passed in by the job (better than `CURRENT_DATE` for reruns and backfills).
> - Date subtraction syntax varies by database, e.g. `DATEADD(day, -1, :load_date)` in Snowflake or SQL Server.

---

## 5. Why `SELECT NULL AS merge_key`?

### The problem

A MERGE does **only one action per source row**:

- Row **matches** a target row -> `WHEN MATCHED` -> UPDATE
- Row **doesn't match** -> `WHEN NOT MATCHED` -> INSERT

But a changed customer needs **both**:

1. **UPDATE** the old row (set end_date, is_current = N)
2. **INSERT** a new row with the new values

So each changed customer is sent **twice**.

### How the two copies behave (Ravi in Run 2)

| merge_key | cust_id | city | ON `t.cust_id = s.merge_key` | Goes to | Action |
|---|---|---|---|---|---|
| C01 | C01 | Hyderabad | `C01 = C01` -> TRUE | WHEN MATCHED | **Expire** old Bengaluru row |
| NULL | C01 | Hyderabad | `C01 = NULL` -> UNKNOWN | WHEN NOT MATCHED | **Insert** new Hyderabad row |

**`anything = NULL` is never TRUE**, so a row with `merge_key = NULL` can never match and is guaranteed to be inserted. The INSERT uses `s.cust_id` (not `merge_key`), so the new row still gets the real `C01`.

### What goes wrong without it

| Approach | Result |
|---|---|
| Send changed customer **once** | Old row expired, new row never inserted. Customer has **no current row**. |
| Send twice with the **real key** both times | Both copies match the same target row. Most databases throw an error ("target row matched by more than one source row"). |
| Send twice, second copy with **NULL key** | One copy expires, the other inserts. Correct. |

### Which customers get the second copy

| Customer situation | Rows in USING output | Result |
|---|---|---|
| Unchanged | 1 (real key) | Nothing happens |
| New | 1 (real key) | Inserted (it doesn't match anything already) |
| Changed | **2** (real key + NULL key) | Old row expired + new row inserted |

Row count of the USING output = **source rows + changed customers**.

---

## 6. Step-by-Step Output of the USING Block (Run 3)

Assume Runs 1 and 2 are done. The target's **current rows** before Run 3 are:

| cust_key | cust_id | city | tier |
|---|---|---|---|
| 3 | C03 | Pune | Bronze |
| 4 | C01 | Hyderabad | Silver |
| 5 | C02 | Chennai | Platinum |
| 6 | C04 | Mumbai | Silver |

### 6.1 First half

```sql
SELECT s.cust_id AS merge_key, s.*
FROM   stg_customer s
```

Just the source table with an extra `merge_key` column (a copy of `cust_id`). Nothing filtered.

| merge_key | cust_id | name | city | tier |
|---|---|---|---|---|
| C01 | C01 | Ravi | Delhi | Gold |
| C02 | C02 | Priya | Chennai | Platinum |
| C03 | C03 | Arjun | Pune | Silver |
| C04 | C04 | Kavya | Mumbai | Silver |
| C05 | C05 | Sneha | Kochi | Gold |

**5 rows.**

### 6.2 Second half

```sql
SELECT NULL AS merge_key, s.*
FROM   stg_customer s
JOIN   dim_customer t
  ON   t.cust_id = s.cust_id
 AND   t.is_current = 'Y'
WHERE  t.city IS DISTINCT FROM s.city
   OR  t.tier IS DISTINCT FROM s.tier
```

**a) JOIN: each source row next to its current target row**

| s.cust_id | s.city (new) | s.tier (new) | t.city (old) | t.tier (old) |
|---|---|---|---|---|
| C01 | Delhi | Gold | Hyderabad | Silver |
| C02 | Chennai | Platinum | Chennai | Platinum |
| C03 | Pune | Silver | Pune | Bronze |
| C04 | Mumbai | Silver | Mumbai | Silver |

Sneha (C05) drops out: she has no row in the target yet.

**b) WHERE: keep only rows where something changed**

| s.cust_id | City changed? | Tier changed? | Keep? |
|---|---|---|---|
| C01 | Hyderabad -> Delhi: yes | Silver -> Gold: yes | **Yes** |
| C02 | no | no | No |
| C03 | no | Bronze -> Silver: yes | **Yes** |
| C04 | no | no | No |

**c) SELECT: output with NULL as merge_key**

| merge_key | cust_id | name | city | tier |
|---|---|---|---|---|
| NULL | C01 | Ravi | Delhi | Gold |
| NULL | C03 | Arjun | Pune | Silver |

**2 rows.** Values come from `s.*` (the source), so they carry the **new** values.

### 6.3 UNION ALL result

| merge_key | cust_id | name | city | tier | Came from |
|---|---|---|---|---|---|
| C01 | C01 | Ravi | Delhi | Gold | first half |
| C02 | C02 | Priya | Chennai | Platinum | first half |
| C03 | C03 | Arjun | Pune | Silver | first half |
| C04 | C04 | Kavya | Mumbai | Silver | first half |
| C05 | C05 | Sneha | Kochi | Gold | first half |
| NULL | C01 | Ravi | Delhi | Gold | second half |
| NULL | C03 | Arjun | Pune | Silver | second half |

**5 + 2 = 7 rows.**

### 6.4 What MERGE does with each row

| merge_key | cust_id | Finds a match? | Action |
|---|---|---|---|
| C01 | C01 | Yes, row 4 (values differ) | **Expire** row 4 |
| C02 | C02 | Yes, row 5 (values same) | Nothing |
| C03 | C03 | Yes, row 3 (values differ) | **Expire** row 3 |
| C04 | C04 | Yes, row 6 (values same) | Nothing |
| C05 | C05 | No (new customer) | **Insert** Sneha (row 9) |
| NULL | C01 | No (NULL never matches) | **Insert** Ravi Delhi/Gold (row 7) |
| NULL | C03 | No (NULL never matches) | **Insert** Arjun Silver (row 8) |

---

## 7. Why `IS DISTINCT FROM` instead of `<>`?

In SQL, NULL means "unknown". Any normal comparison with NULL returns **UNKNOWN**, and in a `WHERE` or `WHEN ... AND` condition UNKNOWN is treated like FALSE, so the row is **skipped**.

| Old (target) | New (source) | `old <> new` | `old IS DISTINCT FROM new` | Really changed? |
|---|---|---|---|---|
| Pune | Delhi | TRUE | TRUE | Yes |
| Pune | Pune | FALSE | FALSE | No |
| **NULL** | **Delhi** | **UNKNOWN -> skipped** | **TRUE** | **Yes** |
| **Pune** | **NULL** | **UNKNOWN -> skipped** | **TRUE** | **Yes** |
| NULL | NULL | UNKNOWN -> skipped | FALSE | No |

### Example of the bug

Arjun's tier is NULL in the target, and the source now says Bronze.

- With `<>`: `NULL <> 'Bronze'` -> UNKNOWN -> treated as "no change". Arjun stays NULL forever, with no error raised.
- With `IS DISTINCT FROM`: TRUE -> change detected -> old row expired, new row inserted.

The NULL-safe check is needed in **both** places in the MERGE: the WHERE that builds Copy 2, and the `WHEN MATCHED AND` condition that expires the old row.

### Alternatives if your database doesn't support it

| Option | Example | Where |
|---|---|---|
| `IS DISTINCT FROM` | `t.tier IS DISTINCT FROM s.tier` | PostgreSQL, Snowflake, BigQuery, Databricks, SQL Server 2022+ |
| Null-safe equal | `NOT (t.tier <=> s.tier)` | Databricks / Spark SQL, MySQL |
| `COALESCE` placeholder | `COALESCE(t.tier,'~') <> COALESCE(s.tier,'~')` | Almost everywhere |
| Spelled out | `t.tier <> s.tier OR (t.tier IS NULL AND s.tier IS NOT NULL) OR (t.tier IS NOT NULL AND s.tier IS NULL)` | Fully portable |

With `COALESCE`, the placeholder must never appear in real data and must match the column's data type (e.g. `DATE '1900-01-01'` for dates).

---

## 8. Simpler Alternative: Two Statements

Easier to read; wrap in a transaction so a failure can't leave customers without a current row.

```sql
BEGIN TRANSACTION;

-- 1. Expire changed rows
UPDATE dim_customer t
SET    end_date   = :load_date - INTERVAL '1' DAY,
       is_current = 'N'
FROM   stg_customer s
WHERE  t.cust_id = s.cust_id
  AND  t.is_current = 'Y'
  AND  (t.city IS DISTINCT FROM s.city OR t.tier IS DISTINCT FROM s.tier);

-- 2. Insert new versions + new customers (anyone without a current row now)
INSERT INTO dim_customer (cust_id, name, city, tier, start_date, end_date, is_current)
SELECT s.cust_id, s.name, s.city, s.tier, :load_date, DATE '9999-12-31', 'Y'
FROM   stg_customer s
WHERE  NOT EXISTS (
         SELECT 1 FROM dim_customer t
         WHERE  t.cust_id = s.cust_id AND t.is_current = 'Y' );

COMMIT;
```

The NULL-key MERGE is popular because it does the same work in **one atomic statement**.

---

## 9. How the Fact Table Uses Type 2

Each sale is linked to the version that was valid **on the sale date**:

```sql
INSERT INTO fact_sales (sale_date, cust_key, amount)
SELECT o.sale_date, d.cust_key, o.amount
FROM   stg_orders o
JOIN   dim_customer d
  ON   d.cust_id = o.cust_id
 AND   o.sale_date BETWEEN d.start_date AND d.end_date;
```

| sale_date | customer | cust_key picked | city at that time |
|---|---|---|---|
| 2026-03-10 | Ravi | 1 | Bengaluru |
| 2026-08-15 | Ravi | 4 | Hyderabad |
| 2026-10-26 | Ravi | 7 | Delhi |

Because the lookup uses the **sale date**, a late-arriving sale (e.g. a March sale loaded in November) still gets the correct version.

---

## 10. Common Queries

**Current state of all customers**

```sql
SELECT * FROM dim_customer WHERE is_current = 'Y';
```

**State as of a specific date**

```sql
SELECT * FROM dim_customer
WHERE  DATE '2026-03-15' BETWEEN start_date AND end_date;
```

Returns Ravi in Bengaluru / Silver and Priya in Chennai / Gold, as things were in March.

**Full history of one customer**

```sql
SELECT * FROM dim_customer WHERE cust_id = 'C01' ORDER BY start_date;
```

**Data quality check: exactly one current row per customer**

```sql
SELECT cust_id
FROM   dim_customer
WHERE  is_current = 'Y'
GROUP  BY cust_id
HAVING COUNT(*) > 1;     -- should return no rows
```

---

## 11. Key Points

1. **Surrogate key vs natural key.** `cust_id` identifies the customer; `cust_key` identifies the version. Fact tables store `cust_key`.
2. **Old rows are never modified** except to close them (end_date and is_current).
3. **Exactly one current row per customer.** Check it regularly.
4. **Reruns are safe.** If the same batch runs again, nothing differs from the current rows, so nothing is expired or inserted.
5. **Use NULL-safe comparisons** (`IS DISTINCT FROM` or equivalent) for change detection.
6. **Use the batch date** (`:load_date`), not `CURRENT_DATE`, so reruns and backfills get correct dates.
7. **Cost is table growth.** Every change adds a row. For attributes that change very often, consider Type 4 or Type 5 (mini-dimension).

---

## 12. Quick Comparison with Other SCD Types

| Type | How changes are handled | History |
|---|---|---|
| Type 1 | Overwrite | None |
| **Type 2** | **New row with dates and current flag** | **Full** |
| Type 3 | Previous-value column | One step back |
| Type 4 | Separate history table | Full |
| Type 5 | Mini-dimension + current-profile pointer | Full (via fact table) |
| Type 6 | Type 2 + current-value column on every row | Full + current |
