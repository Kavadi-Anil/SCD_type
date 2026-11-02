# SCD Type 4: Separate History Table

> SQL dialect used in these notes: **SQL Server** (2022+ for `IS DISTINCT FROM`; older-version fallbacks are given in [section 10](#10-sql-server-notes)).

---

## 1. Quick recap: what is an SCD?

A **dimension** table holds descriptive context (customer, store, product). Its attributes change **slowly and unpredictably**: a customer changes city, a risk rating goes up, a tier is upgraded.

A **Slowly Changing Dimension (SCD)** strategy answers one question:

> **When a descriptive attribute changes, what do we do with the OLD value?**

| Type  | What happens on change                       | History kept?               |
|-------|----------------------------------------------|-----------------------------|
| 0     | Never change the value                       | Original only               |
| 1     | Overwrite the old value                      | None                        |
| 2     | Add a new row (with start/end dates)         | Full, in the same table     |
| 3     | Keep current + previous value in columns     | One step back               |
| **4** | **Current table + separate history table**   | **Full, in a separate table** |
| 5     | Type 4 mini-dimension + Type 1 "current" pointer | Full + current shortcut |
| 6     | Types 1 + 2 + 3 combined                     | Full + current + previous   |

👉 For the full basics (fact vs dimension, natural vs surrogate key, MERGE, `IS DISTINCT FROM`), see [scd_type_3.md](scd_type_3.md).

---

## 2. What is SCD Type 4?

> **Keep history in a separate table.**
> - **Current table**: one row per entity, always the latest values (small and fast for everyday queries)
> - **History table**: every old version of the row, with the dates it was valid
>
> When something changes, **copy the old row into history first, then overwrite the current table.**

```
                 change arrives
                      │
      ┌───────────────┴────────────────┐
      ▼ (1) archive old version        ▼ (2) overwrite
┌──────────────────────┐        ┌──────────────────────┐
│ dim_customer_history │        │ dim_customer         │
│ every old version    │        │ latest version only  │
│ valid_from, valid_to │        │ eff_from             │
└──────────────────────┘        └──────────────────────┘
```

### How it compares to Types 2 and 3

| Compared with | Difference                                                                 |
|---------------|-----------------------------------------------------------------------------|
| **Type 3**    | History is **unlimited**, not just one previous value                      |
| **Type 2**    | The **main table doesn't grow** with old versions; history lives elsewhere |

### ⚠️ "Type 4" has two meanings (interview favourite)

| Meaning | Where it comes from | What it is |
|---------|---------------------|-----------|
| **History table** | Common usage in most data engineering teams today | Current table + separate history table (this file's main topic) |
| **Mini-dimension** | Ralph Kimball's original definition | Rapidly changing attributes (age band, income band) split into their own small dimension table ([section 6](#6-kimballs-meaning-the-mini-dimension)) |

If an interviewer asks about Type 4, it's worth saying: *"Do you mean the history-table pattern or Kimball's mini-dimension?"* Kimball's **Type 5** is built on the mini-dimension meaning, so you'll need it in the next lesson.

---

## 3. Example 1 (Basic): Customer city and tier

`city` and `tier` are tracked. Every change creates a history row.

### Run 1: Source (`stg_customer`), 2026-01-01

| cust_id | name  | city      | tier   |
|---------|-------|-----------|--------|
| C01     | Ravi  | Bengaluru | Silver |
| C02     | Priya | Chennai   | Gold   |
| C03     | Arjun | Pune      | Bronze |

**Current table after Run 1 (`dim_customer`)**

| cust_id | name  | city      | tier   | eff_from   |
|---------|-------|-----------|--------|------------|
| C01     | Ravi  | Bengaluru | Silver | 2026-01-01 |
| C02     | Priya | Chennai   | Gold   | 2026-01-01 |
| C03     | Arjun | Pune      | Bronze | 2026-01-01 |

**History table after Run 1 (`dim_customer_history`)**: empty, because nothing has changed yet.

### Run 2: Source, 2026-06-01

| cust_id | name  | city          | tier         |
|---------|-------|---------------|--------------|
| C01     | Ravi  | **Hyderabad** | Silver       |
| C02     | Priya | Chennai       | **Platinum** |
| C03     | Arjun | Pune          | Bronze       |
| C04     | Kavya | Mumbai        | Silver       |

**Current table after Run 2**

| cust_id | name  | city      | tier     | eff_from   |
|---------|-------|-----------|----------|------------|
| C01     | Ravi  | Hyderabad | Silver   | 2026-06-01 |
| C02     | Priya | Chennai   | Platinum | 2026-06-01 |
| C03     | Arjun | Pune      | Bronze   | 2026-01-01 |
| C04     | Kavya | Mumbai    | Silver   | 2026-06-01 |

**History table after Run 2**

| cust_id | name  | city      | tier   | valid_from | valid_to   |
|---------|-------|-----------|--------|------------|------------|
| C01     | Ravi  | Bengaluru | Silver | 2026-01-01 | 2026-06-01 |
| C02     | Priya | Chennai   | Gold   | 2026-01-01 | 2026-06-01 |

### Run 3: Source, 2026-10-12

| cust_id | name  | city      | tier     |
|---------|-------|-----------|----------|
| C01     | Ravi  | **Delhi** | **Gold** |
| C02     | Priya | Chennai   | Platinum |
| C03     | Arjun | Pune      | Bronze   |
| C04     | Kavya | Mumbai    | Silver   |

**Current table after Run 3**

| cust_id | name  | city    | tier     | eff_from   |
|---------|-------|---------|----------|------------|
| C01     | Ravi  | Delhi   | Gold     | 2026-10-12 |
| C02     | Priya | Chennai | Platinum | 2026-06-01 |
| C03     | Arjun | Pune    | Bronze   | 2026-01-01 |
| C04     | Kavya | Mumbai  | Silver   | 2026-06-01 |

**History table after Run 3**

| cust_id | name  | city      | tier   | valid_from | valid_to   |
|---------|-------|-----------|--------|------------|------------|
| C01     | Ravi  | Bengaluru | Silver | 2026-01-01 | 2026-06-01 |
| C02     | Priya | Chennai   | Gold   | 2026-01-01 | 2026-06-01 |
| C01     | Ravi  | Hyderabad | Silver | 2026-06-01 | 2026-10-12 |

> 💡 **Compare with Type 3:** there, Ravi's first city (Bengaluru) was lost after his second move. In Type 4, **both Bengaluru and Hyderabad are kept** in the history table.

> 📅 `valid_to` is **exclusive**: "valid up to, but **not including**, this date." So a lookup for date `d` uses `valid_from <= d AND d < valid_to`.

### SQL code

```sql
DECLARE @load_date DATE = '2026-06-01';
SET XACT_ABORT ON;          -- any error rolls back the whole transaction

BEGIN TRAN;

-- Step 1: ARCHIVE the old version of changed rows into history
INSERT INTO dbo.dim_customer_history (cust_id, name, city, tier, valid_from, valid_to)
SELECT t.cust_id, t.name, t.city, t.tier, t.eff_from, @load_date
FROM   dbo.dim_customer t
JOIN   dbo.stg_customer s ON t.cust_id = s.cust_id
WHERE  t.city IS DISTINCT FROM s.city
   OR  t.tier IS DISTINCT FROM s.tier;

-- Step 2: OVERWRITE the current table and insert new customers
MERGE dbo.dim_customer WITH (HOLDLOCK) AS t
USING dbo.stg_customer AS s
   ON t.cust_id = s.cust_id

WHEN MATCHED AND (   t.city IS DISTINCT FROM s.city
                  OR t.tier IS DISTINCT FROM s.tier ) THEN
  UPDATE SET t.city     = s.city,
             t.tier     = s.tier,
             t.eff_from = @load_date

WHEN NOT MATCHED BY TARGET THEN
  INSERT (cust_id, name, city, tier, eff_from)
  VALUES (s.cust_id, s.name, s.city, s.tier, @load_date);

COMMIT;
```

### Rules to remember

1. **Archive first, then update.** If you update first, the old values are gone before you can save them.
2. **One transaction.** If Step 2 fails after Step 1 succeeded, a rerun would archive the same rows **again** (duplicate history). The transaction makes both steps succeed or fail together.
3. **The same change check in both steps.** The `WHERE` in Step 1 and the `AND (...)` in Step 2 must be identical, so that **exactly the rows archived are the rows updated**.
4. **Rerun-safe.** After a successful run, current = source, so neither step finds a difference and nothing happens.

> ⚠️ **Gap in this basic version:** `name` is neither in the change check nor in `SET`, so a name change is **silently ignored**. In a real design you decide explicitly for every column: tracked (creates history) or untracked (Type 1 overwrite). Example 2 shows how to handle both.

---

## 4. Example 2 (Real-world, 3+ years level): Bank customer risk profile

### Business scenario

Compliance auditors at a bank regularly ask:

> *"What was this customer's **risk rating on the day this transaction happened**?"*

That needs **full history**. Daily operations (fraud checks, mobile app screens, dashboards) only need the **current** profile, and they must be **fast**.
→ A **lean current table** plus a **full history table**. This is a textbook Type 4 use case.

### Column design

| Column        | Treatment                   | Why |
|---------------|-----------------------------|-----|
| `segment`     | **Tracked** (creates history) | Regulatory reporting by segment |
| `risk_rating` | **Tracked**                 | Audit: risk at transaction time |
| `kyc_status`  | **Tracked**                 | Audit: was KYC complete at the time? |
| `email`       | Untracked (Type 1 overwrite) | Business doesn't need old emails |
| `last_login`  | Untracked (Type 1 overwrite) | Changes **almost daily**. If tracked, the history table would explode with useless rows. **A very common mistake.** |

### What makes this "real-world"

The source (`stg_customer`) is a **CDC feed**:
- it sends **only changed records**
- it can send the **same customer more than once** per batch
- it marks deletes with `op_type = 'D'` (and the other columns are NULL on delete rows)

### Table design (DDL)

```sql
CREATE TABLE dbo.stg_customer (
    cust_id      VARCHAR(10)  NOT NULL,
    segment      VARCHAR(20)  NULL,
    risk_rating  VARCHAR(10)  NULL,
    kyc_status   VARCHAR(20)  NULL,
    email        VARCHAR(100) NULL,
    last_login   DATE         NULL,
    op_type      CHAR(1)      NOT NULL,   -- I = insert, U = update, D = delete
    op_ts        DATETIME2    NOT NULL,   -- full timestamp, not just a time
    batch_date   DATE         NOT NULL
);

CREATE TABLE dbo.dim_customer (                  -- CURRENT table
    customer_key  INT IDENTITY(1,1) PRIMARY KEY,  -- surrogate key, used by facts
    cust_id       VARCHAR(10)  NOT NULL UNIQUE,   -- natural key
    segment       VARCHAR(20)  NULL,
    risk_rating   VARCHAR(10)  NULL,
    kyc_status    VARCHAR(20)  NULL,
    email         VARCHAR(100) NULL,
    last_login    DATE         NULL,
    tracked_hash  VARBINARY(32) NOT NULL,         -- hash of tracked columns
    eff_from      DATE         NOT NULL,          -- when current TRACKED values started
    is_active     CHAR(1)      NOT NULL DEFAULT 'Y',
    inserted_at   DATETIME2    NOT NULL,
    updated_at    DATETIME2    NOT NULL
);

CREATE TABLE dbo.dim_customer_history (          -- HISTORY table
    hist_id       BIGINT IDENTITY(1,1) PRIMARY KEY,
    customer_key  INT          NOT NULL,
    cust_id       VARCHAR(10)  NOT NULL,
    segment       VARCHAR(20)  NULL,
    risk_rating   VARCHAR(10)  NULL,
    kyc_status    VARCHAR(20)  NULL,
    valid_from    DATE         NOT NULL,
    valid_to      DATE         NOT NULL,          -- exclusive
    change_type   VARCHAR(10)  NOT NULL,          -- why this version ended: UPDATE / DELETE
    batch_date    DATE         NOT NULL           -- which load created this row
);

CREATE INDEX ix_hist_lookup
    ON dbo.dim_customer_history (customer_key, valid_from, valid_to);
```

> The history table stores **only tracked columns**. Untracked columns (`email`, `last_login`) have no history by design.

### Run 1: Source, batch 2026-04-01

| cust_id | segment | risk_rating | kyc_status | email       | last_login | op_type | op_ts            |
|---------|---------|-------------|------------|-------------|------------|---------|------------------|
| C01     | Retail  | Low         | Verified   | ravi@x.com  | 2026-03-31 | I       | 2026-04-01 09:00 |
| C02     | Premium | Low         | Verified   | priya@x.com | 2026-03-30 | I       | 2026-04-01 09:00 |
| C03     | Retail  | Medium      | Pending    | arjun@x.com | 2026-03-31 | I       | 2026-04-01 09:00 |

**Current table after Run 1** (`tracked_hash`, `inserted_at`, `updated_at` not shown)

| customer_key | cust_id | segment | risk_rating | kyc_status | email       | last_login | eff_from   | is_active |
|--------------|---------|---------|-------------|------------|-------------|------------|------------|-----------|
| 1            | C01     | Retail  | Low         | Verified   | ravi@x.com  | 2026-03-31 | 2026-04-01 | Y         |
| 2            | C02     | Premium | Low         | Verified   | priya@x.com | 2026-03-30 | 2026-04-01 | Y         |
| 3            | C03     | Retail  | Medium      | Pending    | arjun@x.com | 2026-03-31 | 2026-04-01 | Y         |

**History table after Run 1:** empty.

### Run 2: Source, batch 2026-07-01

| cust_id | segment | risk_rating | kyc_status | email             | last_login | op_type | op_ts            |
|---------|---------|-------------|------------|-------------------|------------|---------|------------------|
| C01     | Retail  | Medium      | Verified   | ravi@x.com        | 2026-06-30 | U       | 2026-07-01 09:00 |
| C01     | Retail  | **High**    | Verified   | ravi@x.com        | 2026-06-30 | U       | 2026-07-01 14:00 |
| C02     | Premium | Low         | Verified   | **priya.s@x.com** | 2026-06-29 | U       | 2026-07-01 09:00 |
| C03     | Retail  | Medium      | Pending    | arjun@x.com       | **2026-06-30** | U   | 2026-07-01 09:00 |
| C04     | NRI     | Low         | Verified   | kavya@x.com       | 2026-06-30 | I       | 2026-07-01 09:00 |

What's going on:

| Customer | Situation | Result |
|----------|-----------|--------|
| C01 | Appears **twice**: risk → Medium at 09:00, → High at 14:00 | Latest (High) wins, **1 history row** |
| C02 | Only `email` changed (untracked) | Current updated, **no history row** |
| C03 | Only `last_login` changed (untracked) | Current updated, **no history row** |
| C04 | New customer | Inserted |

**Current table after Run 2**

| customer_key | cust_id | segment | risk_rating | kyc_status | email         | last_login | eff_from   | is_active |
|--------------|---------|---------|-------------|------------|---------------|------------|------------|-----------|
| 1            | C01     | Retail  | High        | Verified   | ravi@x.com    | 2026-06-30 | 2026-07-01 | Y         |
| 2            | C02     | Premium | Low         | Verified   | priya.s@x.com | 2026-06-29 | 2026-04-01 | Y         |
| 3            | C03     | Retail  | Medium      | Pending    | arjun@x.com   | 2026-06-30 | 2026-04-01 | Y         |
| 4            | C04     | NRI     | Low         | Verified   | kavya@x.com   | 2026-06-30 | 2026-07-01 | Y         |

> C02 and C03 were updated, but their `eff_from` **didn't move**, because none of their tracked values changed. `eff_from` means "when the current tracked version started", not "when the row was last touched" (that's `updated_at`).

**History table after Run 2**

| hist_id | customer_key | cust_id | segment | risk_rating | kyc_status | valid_from | valid_to   | change_type |
|---------|--------------|---------|---------|-------------|------------|------------|------------|-------------|
| 1       | 1            | C01     | Retail  | Low         | Verified   | 2026-04-01 | 2026-07-01 | UPDATE      |

> Only **one** history row, even though four customers were touched.

### Run 3: Source, batch 2026-10-12

| cust_id | segment     | risk_rating | kyc_status   | email      | last_login | op_type | op_ts            |
|---------|-------------|-------------|--------------|------------|------------|---------|------------------|
| C01     | **Premium** | High        | Verified     | ravi@x.com | 2026-10-11 | U       | 2026-10-12 09:00 |
| C02     | NULL        | NULL        | NULL         | NULL       | NULL       | **D**   | 2026-10-12 09:00 |
| C03     | Retail      | Medium      | **Verified** | arjun@x.com| 2026-10-11 | U       | 2026-10-12 09:00 |

What's going on:

| Customer | Situation |
|----------|-----------|
| C01 | Upgraded to Premium |
| C02 | Account closed (delete). Note that all columns are NULL on the delete row. |
| C03 | KYC completed |
| C04 | **Not in the feed.** In CDC, *missing does not mean deleted*; it just means no change. C04 must be left alone. |

**Current table after Run 3**

| customer_key | cust_id | segment | risk_rating | kyc_status | email         | last_login | eff_from   | is_active |
|--------------|---------|---------|-------------|------------|---------------|------------|------------|-----------|
| 1            | C01     | Premium | High        | Verified   | ravi@x.com    | 2026-10-11 | 2026-10-12 | Y         |
| 2            | C02     | Premium | Low         | Verified   | priya.s@x.com | 2026-06-29 | 2026-10-12 | **N**     |
| 3            | C03     | Retail  | Medium      | Verified   | arjun@x.com   | 2026-10-11 | 2026-10-12 | Y         |
| 4            | C04     | NRI     | Low         | Verified   | kavya@x.com   | 2026-06-30 | 2026-07-01 | Y         |

> C02 is **soft-deleted** (`is_active = 'N'`) rather than physically removed, so old fact rows pointing to `customer_key = 2` still join correctly. Its last known values are kept, **not** overwritten with the NULLs from the delete row.

**History table after Run 3**

| hist_id | customer_key | cust_id | segment | risk_rating | kyc_status | valid_from | valid_to   | change_type |
|---------|--------------|---------|---------|-------------|------------|------------|------------|-------------|
| 1       | 1            | C01     | Retail  | Low         | Verified   | 2026-04-01 | 2026-07-01 | UPDATE      |
| 2       | 1            | C01     | Retail  | High        | Verified   | 2026-07-01 | 2026-10-12 | UPDATE      |
| 3       | 2            | C02     | Premium | Low         | Verified   | 2026-04-01 | 2026-10-12 | DELETE      |
| 4       | 3            | C03     | Retail  | Medium      | Pending    | 2026-04-01 | 2026-10-12 | UPDATE      |

> `change_type` records **why the version ended**. Row 3 says: "C02 was Premium/Low/Verified from 04-01 until the account was closed on 10-12."

### SQL code (full load script)

```sql
DECLARE @load_date DATE = '2026-10-12';
SET XACT_ABORT ON;

------------------------------------------------------------------
-- Step 0: Deduplicate the batch ONCE and compute the tracked hash
--         (materialised so every later step sees the same data)
------------------------------------------------------------------
DROP TABLE IF EXISTS #src;

SELECT cust_id, segment, risk_rating, kyc_status, email, last_login, op_type,
       HASHBYTES('SHA2_256',
                 CONCAT(ISNULL(segment,     '~'), '|',
                        ISNULL(risk_rating, '~'), '|',
                        ISNULL(kyc_status,  '~'))) AS row_hash
INTO   #src
FROM (
    SELECT s.*,
           ROW_NUMBER() OVER (PARTITION BY s.cust_id ORDER BY s.op_ts DESC) AS rn
    FROM   dbo.stg_customer s
    WHERE  s.batch_date = @load_date
) x
WHERE rn = 1;

BEGIN TRAN;

------------------------------------------------------------------
-- Step 1: ARCHIVE the old version (tracked change OR delete)
------------------------------------------------------------------
INSERT INTO dbo.dim_customer_history
       (customer_key, cust_id, segment, risk_rating, kyc_status,
        valid_from, valid_to, change_type, batch_date)
SELECT t.customer_key, t.cust_id, t.segment, t.risk_rating, t.kyc_status,
       t.eff_from, @load_date,
       CASE WHEN s.op_type = 'D' THEN 'DELETE' ELSE 'UPDATE' END,
       @load_date
FROM   dbo.dim_customer t
JOIN   #src s ON s.cust_id = t.cust_id
WHERE  t.is_active = 'Y'
  AND (   s.op_type = 'D'                     -- delete
       OR t.tracked_hash <> s.row_hash );     -- tracked column changed

------------------------------------------------------------------
-- Step 2: SOFT DELETE (handled separately: delete rows are all NULL)
------------------------------------------------------------------
UPDATE t
SET    t.is_active  = 'N',
       t.eff_from   = @load_date,
       t.updated_at = SYSDATETIME()
FROM   dbo.dim_customer t
JOIN   #src s ON s.cust_id = t.cust_id
WHERE  s.op_type   = 'D'
  AND  t.is_active = 'Y';

------------------------------------------------------------------
-- Step 3: UPSERT inserts / updates (tracked + untracked columns)
------------------------------------------------------------------
MERGE dbo.dim_customer WITH (HOLDLOCK) AS t
USING (SELECT * FROM #src WHERE op_type <> 'D') AS s
   ON t.cust_id = s.cust_id

WHEN MATCHED AND (   t.is_active    = 'N'                       -- reactivation
                  OR t.tracked_hash <> s.row_hash               -- tracked change
                  OR t.email      IS DISTINCT FROM s.email      -- untracked change
                  OR t.last_login IS DISTINCT FROM s.last_login ) THEN
  UPDATE SET
    t.segment      = s.segment,
    t.risk_rating  = s.risk_rating,
    t.kyc_status   = s.kyc_status,
    t.email        = s.email,
    t.last_login   = s.last_login,
    -- move eff_from ONLY when a new tracked version starts
    t.eff_from     = CASE WHEN t.is_active = 'N' OR t.tracked_hash <> s.row_hash
                          THEN @load_date ELSE t.eff_from END,
    t.tracked_hash = s.row_hash,
    t.is_active    = 'Y',
    t.updated_at   = SYSDATETIME()

WHEN NOT MATCHED BY TARGET THEN
  INSERT (cust_id, segment, risk_rating, kyc_status, email, last_login,
          tracked_hash, eff_from, is_active, inserted_at, updated_at)
  VALUES (s.cust_id, s.segment, s.risk_rating, s.kyc_status, s.email, s.last_login,
          s.row_hash, @load_date, 'Y', SYSDATETIME(), SYSDATETIME());

COMMIT;
```

> In SQL Server, the right-hand side of every `SET` uses the **old** row values. So `t.is_active = 'N'` inside the `eff_from` CASE sees the value *before* it is set to `'Y'`.

### What makes this production-grade

#### 1. Deduplicate once (`ROW_NUMBER` into `#src`)
CDC can send several records per key per batch. A MERGE fails if two source rows match one target row (*"The MERGE statement attempted to UPDATE or DELETE the same row more than once"*). The deduplicated batch is stored in `#src` **once**, so the archive step and the update step see **exactly the same data**.

#### 2. Hash-based change detection
Instead of comparing every tracked column one by one, compare **one hash**:

```sql
HASHBYTES('SHA2_256', CONCAT(ISNULL(segment,'~'), '|', ISNULL(risk_rating,'~'), '|', ISNULL(kyc_status,'~')))
```

| Why hash?                                    | Detail |
|----------------------------------------------|--------|
| Scales                                       | 30 tracked columns = still one comparison |
| NULL-safe automatically                      | `ISNULL` makes sure the hash is never NULL, so plain `<>` is safe |
| Stored in the current table                  | `tracked_hash` is calculated once at load, not on every run |

⚠️ **Hash pitfalls:**

| Pitfall | Example | Fix |
|---------|---------|-----|
| No delimiter | `'ab' + 'c'` = `'a' + 'bc'` → same hash | Always put `'|'` between columns |
| `CONCAT_WS` skips NULLs | `CONCAT_WS('|','A',NULL,'B')` = `CONCAT_WS('|','A','B',NULL)` = `'A|B'` | Wrap each column in `ISNULL(col,'~')` |
| Untracked columns in the hash | `last_login` in the hash → history row every day | Hash **tracked columns only** |
| Case / spaces | SQL Server `=` is usually case-insensitive, but hashes are not: `'Low'` ≠ `'low'` | Standardise (`UPPER`, `TRIM`) before hashing, or accept it as a change |
| Column order changed | Different order → every row looks changed | Fix the order; treat a hash-definition change as a planned re-baseline |

#### 3. Tracked vs untracked columns
- A **tracked** change → history row and new `eff_from`.
- An **untracked** change → current row overwritten only (Type 1). `eff_from` stays the same.

This is what keeps the history table meaningful and small.

#### 4. Deletes handled separately
A delete row has **NULLs** in every column. If it went through normal change detection, it would look like "everything changed to NULL" and **overwrite the current row with NULLs**. That's why deletes have their own step (Step 2) and are excluded from the MERGE.

#### 5. Missing ≠ deleted
With CDC, a key that's **absent** from the batch just means "no change". Never use `WHEN NOT MATCHED BY SOURCE THEN DELETE` with a CDC feed, because it would wipe out every customer who didn't change today. (That clause is only valid for **full snapshot** feeds.)

#### 6. Soft delete (`is_active`)
Fact rows point at `customer_key`. Physically deleting the dimension row breaks those joins, so mark it inactive instead.

#### 7. Rerun safety (idempotency)
If the whole script runs again for the same batch:

| Step | Why nothing happens on rerun |
|------|------------------------------|
| 1. Archive | Hashes now match; deleted rows are already `is_active = 'N'` |
| 2. Soft delete | `WHERE t.is_active = 'Y'` finds nothing |
| 3. MERGE | No column differs |

If the job **fails midway**, `SET XACT_ABORT ON` + the transaction roll back Steps 1–3 together, so you never get "archived but not updated".

#### 8. `@load_date`, not `GETDATE()`
Backfills and late reruns must stamp the **batch's** date, not today's date.

### Point-in-time queries: answering the auditor

History is split across two tables, so build **one view of all versions**:

```sql
CREATE VIEW dbo.vw_customer_versions AS
SELECT customer_key, cust_id, segment, risk_rating, kyc_status,
       valid_from, valid_to, change_type AS version_end_reason
FROM   dbo.dim_customer_history
UNION ALL
SELECT customer_key, cust_id, segment, risk_rating, kyc_status,
       eff_from, CAST('9999-12-31' AS DATE), NULL          -- current version is open-ended
FROM   dbo.dim_customer
WHERE  is_active = 'Y';                                    -- closed accounts have no current version
```

#### Query 1: "What was the risk rating at the time of each transaction?"

`fact_transaction` (sample)

| txn_id | customer_key | txn_date   | amount   |
|--------|--------------|------------|----------|
| T1     | 1            | 2026-05-15 | 50,000   |
| T2     | 1            | 2026-07-01 | 9,00,000 |
| T3     | 1            | 2026-09-20 | 2,00,000 |
| T4     | 1            | 2026-10-15 | 75,000   |
| T5     | 3            | 2026-08-10 | 30,000   |

```sql
SELECT f.txn_id, f.txn_date, v.cust_id, v.segment, v.risk_rating, v.kyc_status
FROM   dbo.fact_transaction f
JOIN   dbo.vw_customer_versions v
  ON   v.customer_key = f.customer_key
 AND   f.txn_date >= v.valid_from
 AND   f.txn_date <  v.valid_to;          -- exclusive end
```

| txn_id | txn_date   | cust_id | segment | risk_rating | kyc_status | Comes from |
|--------|------------|---------|---------|-------------|------------|------------|
| T1     | 2026-05-15 | C01     | Retail  | Low         | Verified   | history row 1 |
| T2     | 2026-07-01 | C01     | Retail  | High        | Verified   | history row 2 |
| T3     | 2026-09-20 | C01     | Retail  | High        | Verified   | history row 2 |
| T4     | 2026-10-15 | C01     | Premium | High        | Verified   | current table |
| T5     | 2026-08-10 | C03     | Retail  | Medium      | **Pending**| history row 4 |

> 🔎 T5 is the kind of finding auditors look for: a ₹30,000 transaction while **KYC was still Pending**.

> ⚠️ **Date-grain caveat for T2:** the risk actually became High at **14:00** on 07-01. With date-level validity, a transaction at 10:00 that day also shows "High", even though the risk was **Medium** at that moment. If that matters, see [section 5](#5-strict-audit-mode-keep-every-intermediate-version).

#### Query 2: "Show me every customer's profile as it was on 2026-08-01"

```sql
DECLARE @as_of DATE = '2026-08-01';

SELECT cust_id, segment, risk_rating, kyc_status
FROM   dbo.vw_customer_versions
WHERE  @as_of >= valid_from
  AND  @as_of <  valid_to;
```

| cust_id | segment | risk_rating | kyc_status |
|---------|---------|-------------|------------|
| C01     | Retail  | High        | Verified   |
| C02     | Premium | Low         | Verified   |
| C03     | Retail  | Medium      | Pending    |
| C04     | NRI     | Low         | Verified   |

> C02 appears because on 2026-08-01 the account was still open (history row 3). On any date **after** 2026-10-12 it would not appear at all.

### Bonus Run 4: Reactivation (C02 reopens), batch 2027-01-15

| cust_id | segment | risk_rating | kyc_status | email         | last_login | op_type | op_ts            |
|---------|---------|-------------|------------|---------------|------------|---------|------------------|
| C02     | Retail  | Medium      | Pending    | priya.s@x.com | 2027-01-15 | I       | 2027-01-15 10:00 |

What the script does:
- **Step 1** doesn't archive (`t.is_active = 'N'`). The closed period has no version, and that's correct.
- **Step 3** matches on `cust_id`, sees `is_active = 'N'`, overwrites the values, sets `is_active = 'Y'` and `eff_from = 2027-01-15`, and **keeps `customer_key = 2`**.

C02's timeline in `vw_customer_versions`:

| valid_from | valid_to   | segment | risk_rating | kyc_status | Meaning |
|------------|------------|---------|-------------|------------|---------|
| 2026-04-01 | 2026-10-12 | Premium | Low         | Verified   | Open (history, ended by DELETE) |
| *(gap)*    |            |         |             |            | Account closed: no rows returned for these dates |
| 2027-01-15 | 9999-12-31 | Retail  | Medium      | Pending    | Reopened (current) |

---

## 5. Strict audit mode: keep every intermediate version

In Example 2, C01 went **Low → Medium (09:00) → High (14:00)** in one batch. Deduplication kept only High, so **Medium never reached history**.

For most analytics that's fine. For a **bank auditor**, those 5 hours at "Medium" might legally matter. Here are both approaches:

| Approach | What's kept | Validity grain | Use when |
|----------|-------------|----------------|----------|
| **Latest wins** (Example 2) | Last state per batch | `DATE` | Analytics, daily reporting |
| **Every version** (this section) | Every distinct tracked state | `DATETIME2` (`op_ts`) | Regulatory audit, fraud investigation |

### Changes needed for strict mode

- `valid_from` / `valid_to` / `eff_from` become **`DATETIME2`**, taken from **`op_ts`** instead of `@load_date`.
- Process **all** CDC events in the batch, ordered by `op_ts`, instead of only the latest.
- Skip events where tracked columns **didn't change** compared with the previous event (e.g. a `last_login`-only update).

### Expected result for C01 after Run 2 (strict mode)

**History**

| customer_key | cust_id | risk_rating | valid_from       | valid_to         | change_type |
|--------------|---------|-------------|------------------|------------------|-------------|
| 1            | C01     | Low         | 2026-04-01 09:00 | 2026-07-01 09:00 | UPDATE      |
| 1            | C01     | **Medium**  | 2026-07-01 09:00 | 2026-07-01 14:00 | UPDATE      |

**Current**

| customer_key | cust_id | risk_rating | eff_from         |
|--------------|---------|-------------|------------------|
| 1            | C01     | High        | 2026-07-01 14:00 |

### SQL pattern: build a version chain with `LAG` / `LEAD`

The trick is to treat the **existing current row** as the first "event", then put the batch's events after it in time order.

```sql
DECLARE @load_date DATE = '2026-07-01';
DROP TABLE IF EXISTS #versions;

WITH events AS (
    -- (a) the version that is current BEFORE this batch
    SELECT t.customer_key, t.cust_id, t.segment, t.risk_rating, t.kyc_status,
           t.eff_from AS ver_from,            -- DATETIME2 in strict mode
           t.tracked_hash AS row_hash,
           1 AS is_existing
    FROM   dbo.dim_customer t
    WHERE  t.is_active = 'Y'
      AND  EXISTS (SELECT 1 FROM dbo.stg_customer s
                   WHERE s.cust_id = t.cust_id
                     AND s.batch_date = @load_date AND s.op_type = 'U')

    UNION ALL

    -- (b) every update event in this batch
    SELECT t.customer_key, s.cust_id, s.segment, s.risk_rating, s.kyc_status,
           s.op_ts,
           HASHBYTES('SHA2_256', CONCAT(ISNULL(s.segment,'~'), '|',
                                        ISNULL(s.risk_rating,'~'), '|',
                                        ISNULL(s.kyc_status,'~'))),
           0
    FROM   dbo.stg_customer s
    JOIN   dbo.dim_customer t ON t.cust_id = s.cust_id AND t.is_active = 'Y'
    WHERE  s.batch_date = @load_date AND s.op_type = 'U'
),
changes AS (
    -- compare each event with the one before it
    SELECT e.*,
           LAG(row_hash) OVER (PARTITION BY cust_id
                               ORDER BY ver_from, is_existing DESC) AS prev_hash
    FROM   events e
),
versions AS (
    -- keep only real tracked changes, then find where each version ends
    SELECT c.*,
           LEAD(ver_from) OVER (PARTITION BY cust_id ORDER BY ver_from) AS ver_to
    FROM   changes c
    WHERE  prev_hash IS NULL OR prev_hash <> row_hash
)
SELECT * INTO #versions FROM versions;

BEGIN TRAN;

-- every version that has a successor goes to history
-- (this includes the old current row AND the intermediate states)
INSERT INTO dbo.dim_customer_history
       (customer_key, cust_id, segment, risk_rating, kyc_status,
        valid_from, valid_to, change_type, batch_date)
SELECT customer_key, cust_id, segment, risk_rating, kyc_status,
       ver_from, ver_to, 'UPDATE', @load_date
FROM   #versions
WHERE  ver_to IS NOT NULL;

-- the newest version becomes the current row (only if it is a NEW version)
UPDATE t
SET    t.segment      = v.segment,
       t.risk_rating  = v.risk_rating,
       t.kyc_status   = v.kyc_status,
       t.tracked_hash = v.row_hash,
       t.eff_from     = v.ver_from,
       t.updated_at   = SYSDATETIME()
FROM   dbo.dim_customer t
JOIN   #versions v ON v.customer_key = t.customer_key
WHERE  v.ver_to IS NULL
  AND  v.is_existing = 0;

-- then: untracked columns, deletes and new customers exactly as in Example 2
COMMIT;
```

How it works for C01 in Run 2:

| Event | ver_from | risk | prev_hash same? | Kept? | ver_to | Goes to |
|-------|----------|------|-----------------|-------|--------|---------|
| existing row | 2026-04-01 09:00 | Low | – (first) | ✅ | 2026-07-01 09:00 | History |
| CDC event 1 | 2026-07-01 09:00 | Medium | No | ✅ | 2026-07-01 14:00 | History |
| CDC event 2 | 2026-07-01 14:00 | High | No | ✅ | NULL | Current |

For C03 (only `last_login` changed), the CDC event has the **same hash** as the existing row, so it is filtered out. Only the existing row remains, with `ver_to = NULL`, so nothing is archived. ✅

> **Trade-off:** strict mode needs timestamp-grain validity everywhere, a bigger history table, and more complex SQL. Choose it only when the business or regulator actually needs intra-day accuracy.

---

## 6. Kimball's meaning: the mini-dimension

### The problem it solves

A customer dimension has **50 million rows**. Some attributes change **often**: age band, income band, credit score band. With Type 2, every change would add a row, and the table would explode. With Type 1, you'd lose history.

### The idea

> Move the rapidly changing attributes into their **own small dimension**, called the **mini-dimension**, and put its key **directly on the fact table**.

Because the mini-dimension stores **bands** (not raw values), it holds only the **combinations**: e.g. 6 age bands × 5 income bands × 4 credit bands = **120 rows**, no matter how many customers there are.

```
                 ┌────────────────────┐
                 │ dim_customer       │  stable attributes (name, city)
                 │ customer_key (PK)  │
                 └─────────▲──────────┘
                           │
┌──────────────────────────┴───────────────────────┐
│ fact_sales: sale_id, customer_key, profile_key, amount │
└──────────────────────────┬───────────────────────┘
                           │
                 ┌─────────▼──────────┐
                 │ dim_customer_profile│  mini-dimension (~120 rows)
                 │ profile_key (PK)    │  age_band, income_band, credit_band
                 └────────────────────┘
```

### Sample tables

**`dim_customer`** (stable, rarely changes)

| customer_key | cust_id | name | city      |
|--------------|---------|------|-----------|
| 1            | C01     | Ravi | Bengaluru |

**`dim_customer_profile`** (mini-dimension, all band combinations pre-loaded)

| profile_key | age_band | income_band | credit_band |
|-------------|----------|-------------|-------------|
| 1           | 25-34    | 5-10L       | Good        |
| 2           | 25-34    | 10-20L      | Good        |
| 3           | 25-34    | 10-20L      | Excellent   |
| …           | …        | …           | …           |

Ravi's profile over the year: Jan **5-10L / Good** → May income rises to **10-20L** → Sept credit improves to **Excellent**.

**`fact_sales`**: each sale captures the profile **at the time of the sale**

| sale_id | sale_date  | customer_key | profile_key | amount |
|---------|------------|--------------|-------------|--------|
| S1      | 2026-02-10 | 1            | 1           | 5,000  |
| S2      | 2026-06-15 | 1            | 2           | 12,000 |
| S3      | 2026-09-25 | 1            | 3           | 20,000 |

> `dim_customer` **never changed**. The history lives in the **fact table**, through `profile_key`.

### Fact load: look up the profile key at load time

```sql
INSERT INTO dbo.fact_sales (sale_id, sale_date, customer_key, profile_key, amount)
SELECT s.sale_id, s.sale_date, c.customer_key, p.profile_key, s.amount
FROM   dbo.stg_sales s
JOIN   dbo.dim_customer         c  ON c.cust_id = s.cust_id
JOIN   dbo.stg_customer_profile sp ON sp.cust_id = s.cust_id     -- today's banded profile
JOIN   dbo.dim_customer_profile p
  ON   p.age_band    = sp.age_band
 AND   p.income_band = sp.income_band
 AND   p.credit_band = sp.credit_band;
```

### Report: sales by income band (as it was at the time of sale)

```sql
SELECT p.income_band, SUM(f.amount) AS sales
FROM   dbo.fact_sales f
JOIN   dbo.dim_customer_profile p ON p.profile_key = f.profile_key
GROUP  BY p.income_band;
```

| income_band | sales  |
|-------------|--------|
| 5-10L       | 5,000  |
| 10-20L      | 32,000 |

### Limitation → leads to Type 5

From `dim_customer` alone, you **can't see Ravi's current profile**. You'd have to find his latest fact row, and a customer with no recent sales has no answer at all.
**SCD Type 5** fixes this by adding the **current** `profile_key` to `dim_customer` as a **Type 1** column (an "outrigger"). That's the next lesson.

---

## 7. Type 4 vs Types 1, 2 and 3

| Aspect                     | Type 1        | Type 2                     | Type 3                    | Type 4 (history table)            |
|----------------------------|---------------|----------------------------|---------------------------|-----------------------------------|
| On change                  | Overwrite     | New row in same table      | Shift to "prev" column    | Copy old row to history, overwrite current |
| Where history lives        | Nowhere       | Same table                 | Extra columns             | **Separate table**                |
| How much history           | None          | Full                       | Usually one step back     | Full                              |
| Main table size            | 1 row/entity  | Grows with every change    | 1 row/entity              | **1 row/entity**                  |
| Current-value queries      | Simple, fast  | Need `is_current` filter   | Simple, fast              | **Simple, fast**                  |
| Historical queries         | Impossible    | One table, date join       | Only previous value       | `UNION` of two tables + date join |
| Load complexity            | Low           | Medium                     | Low–medium                | Medium (two tables, one transaction) |

---

## 8. Pros, cons, and when to use it

| ✅ Pros                                                   | ❌ Cons                                                   |
|-----------------------------------------------------------|-----------------------------------------------------------|
| Current table stays small and fast                        | Two tables to keep in sync, so a transaction is needed    |
| Unlimited history                                         | Historical queries need a `UNION` view + date-range join  |
| Everyday users never see history complexity               | Archive and update must use identical change logic        |
| History table can be stored/partitioned/archived separately | Easy to bloat history by tracking noisy columns         |
| Surrogate key stays stable                                | Facts join to the current row by default, so point-in-time needs extra work |

### Use Type 4 when

- **Most queries need only current values** (apps, APIs, operational dashboards), **and**
- **Full history is still required** for audit, compliance, or occasional analysis, **and/or**
- The dimension is **large** and attributes **change often**, so Type 2 would bloat the main table.

### Avoid Type 4 when

- Most reports need **historical attribution** (sales by the region *at that time*). Type 2 makes that a simple join.
- Nobody needs history → use Type 1.
- Only "old vs new" comparison is needed → use Type 3.

---

## 9. Real-world applications

1. **Banking / fintech KYC & risk profile**: lean current profile for fraud checks; full history for regulators.
2. **Insurance policyholder details**: current policy data for servicing; history for claims disputes ("what was the coverage on the accident date?").
3. **Telecom subscriber plans**: current plan for billing; plan history for churn and upgrade analysis.
4. **E-commerce product catalogue**: current price/description for the website; price history for analytics and price-change audits.
5. **HR employee master**: current job/grade/manager for apps; history for payroll audits and tenure analysis.
6. **Healthcare patient demographics**: current details for appointments; history for compliance.
7. **Mini-dimension (Kimball meaning)**: customer demographic bands, credit score bands, and loyalty behaviour bands on very large customer dimensions.

---

## 10. SQL Server notes

| Topic | Note |
|-------|------|
| `IS DISTINCT FROM` | Available from **SQL Server 2022**. Older versions: `ISNULL(a,'~') <> ISNULL(b,'~')`, or `EXISTS (SELECT a EXCEPT SELECT b)` (NULL-safe, a common T-SQL idiom). |
| `HASHBYTES` | Use `'SHA2_256'` (returns `VARBINARY(32)`). Avoid `MD5`/`SHA1` for new designs. Before SQL Server 2016, input was limited to 8,000 bytes. |
| `CONCAT` vs `CONCAT_WS` | `CONCAT` turns NULL into an empty string; `CONCAT_WS` **skips** NULLs entirely. Both need `ISNULL(col,'~')` for correct hashing. |
| `MERGE` limits | At most two `WHEN MATCHED` clauses, and then one must be `UPDATE` and the other `DELETE`. That's why Example 2 uses **one** UPDATE branch with `CASE` expressions. |
| `MERGE` concurrency | Use `WITH (HOLDLOCK)` on the target to avoid race conditions when two loads run together. Always end MERGE with `;`. |
| Transactions | `SET XACT_ABORT ON` makes any runtime error roll back the whole transaction. |
| `NOT MATCHED BY SOURCE` | Only for **full snapshot** feeds, **never** for CDC. |
| Temp tables | `#src` is session-scoped; materialising it ensures every step uses identical data. |

---

## 11. Production checklist for Type 4

- [ ] Decide **per column**: tracked (history) vs untracked (Type 1). Keep noisy columns like `last_login` **out** of history.
- [ ] Deduplicate the CDC batch **once** (`ROW_NUMBER() ... ORDER BY op_ts DESC`) into a temp table.
- [ ] Use a **hash of tracked columns** with delimiters and `ISNULL` on every column.
- [ ] **Archive first, then update**, inside **one transaction** with `SET XACT_ABORT ON`.
- [ ] Use **identical change logic** in the archive step and the update step.
- [ ] Handle **deletes separately**: their columns are NULL.
- [ ] **Soft delete** (`is_active = 'N'`); never physically delete rows facts depend on.
- [ ] **Missing ≠ deleted** for CDC; never use `NOT MATCHED BY SOURCE` there.
- [ ] Handle **reactivation**: same `customer_key`, new `eff_from`, no fake version for the closed period.
- [ ] Stamp dates with **`@load_date`** (or `op_ts` in strict mode), not `GETDATE()`.
- [ ] Process batches **in order**. Loading an older batch after a newer one corrupts history.
- [ ] Provide a **`vw_customer_versions`** view and index history on `(customer_key, valid_from, valid_to)`.
- [ ] Decide **latest-wins vs every-version** with the business or compliance team.
- [ ] Test: new key, no change, untracked-only change, tracked change, duplicate keys, NULL → value, delete, reactivation, full rerun, failed-midway rerun.

---

## 12. Check your understanding

**Conceptual**
1. In one sentence, what does Type 4 do when a tracked value changes?
2. Name one advantage of Type 4 over Type 2, and one over Type 3.
3. What are the **two meanings** of "Type 4"? Which one does Kimball's Type 5 build on?
4. What does it mean that `valid_to` is **exclusive**? Write the date condition for a point-in-time lookup.

**Scenario-based**
5. An e-commerce site shows current prices to millions of users per second, but finance needs every historical price for audits. Which type, and why?
6. A team tracks `last_login` as a history column. What will happen to the history table within a year?
7. A CDC batch doesn't contain customer C04. A junior engineer adds `WHEN NOT MATCHED BY SOURCE THEN UPDATE SET is_active = 'N'`. What goes wrong?

**Code-level**
8. Why must the archive step run **before** the MERGE? What is lost if the order is reversed?
9. The job crashes after Step 1 (archive) but before Step 3 (MERGE), and there is **no** transaction. What happens on rerun?
10. Why are delete rows handled in their own step instead of inside the MERGE?
11. Why is `CONCAT(segment, risk_rating, kyc_status)` (no delimiter, no `ISNULL`) a bad hash input? Give a concrete example of two different rows producing the same string.
12. In Run 2, C02's email changed. Why didn't its `eff_from` change? Which column tells you when the row was last touched?
13. Why does the `vw_customer_versions` view filter `is_active = 'Y'` on the current table?

**Design thinking**
14. A regulator asks: "What was C01's risk rating at **10:00 on 2026-07-01**?" With the latest-wins design, what answer do you give, and is it correct? What would you change?
15. In the mini-dimension pattern, how do you find a customer's **current** income band if they haven't bought anything for a year? What does that tell you about why Type 5 exists?
16. When C02 reopens their account, why do we keep `customer_key = 2` instead of creating a new key? When might a new key be the better choice?
