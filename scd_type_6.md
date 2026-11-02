# SCD Type 6: Hybrid (Type 1 + Type 2 + Type 3)

> SQL dialect used in these notes: **SQL Server** (2022+ for `IS DISTINCT FROM`; see [scd_type_4.md, SQL Server notes](scd_type_4.md#10-sql-server-notes) for older-version fallbacks).
> Earlier lessons: [Type 3](scd_type_3.md) · [Type 4](scd_type_4.md) · [Type 5](scd_type_5.md)

---

## 1. Quick recap: where Type 6 fits

| Type  | What happens on change                                  | History kept?              |
|-------|---------------------------------------------------------|----------------------------|
| 0     | Never change the value                                  | Original only              |
| 1     | Overwrite the old value                                 | None                       |
| 2     | Add a new row (with start/end dates)                    | Full, in the same table    |
| 3     | Keep current + previous value in columns                | One step back              |
| 4     | Separate history table, or Kimball's mini-dimension     | Full                       |
| 5     | Mini-dimension + Type 1 current-profile pointer         | Full (via facts) + current |
| **6** | **Type 2 rows + historical & current columns, current overwritten on all rows** | **Full + current on every row** |

> **Why "6"?** Because **1 + 2 + 3 = 6**. It is the most popular hybrid type in real projects, because it gives you **full history** and the **current value on every row**.

---

## 2. What is SCD Type 6?

### Step 1: The problem with plain Type 2

In Type 2, every change creates a new row. Ravi moves Bengaluru → Hyderabad → Delhi:

| cust_key | cust_id | name | city      | start_date | end_date   | is_current |
|----------|---------|------|-----------|------------|------------|------------|
| 1        | C01     | Ravi | Bengaluru | 2026-01-01 | 2026-05-31 | N          |
| 3        | C01     | Ravi | Hyderabad | 2026-06-01 | 2026-10-18 | N          |
| 5        | C01     | Ravi | Delhi     | 2026-10-19 | 9999-12-31 | Y          |

✅ History is perfect: each sale points to the row that was valid when it happened, so a January sale shows "Bengaluru".

❌ But if the business asks:

> *"Show all of Ravi's sales under his **current** city."*

the old rows **don't know** he's now in Delhi. You need an extra **self-join** to find his `is_current = 'Y'` row:

```sql
-- Plain Type 2: "as it is now" needs a self-join
SELECT cur.city AS current_city, SUM(f.amount) AS sales
FROM   fact_sales   f
JOIN   dim_customer d   ON d.cust_key  = f.cust_key           -- version at time of sale
JOIN   dim_customer cur ON cur.cust_id = d.cust_id            -- same customer...
                       AND cur.is_current = 'Y'               -- ...current version
GROUP  BY cur.city;
```

Analysts find this annoying and **often get it wrong** (forgetting `is_current`, joining on the wrong key, double counting).

### Step 2: The Type 6 fix

Keep Type 2 rows, but store **two columns** for the attribute:

| Column            | Meaning                                    | Changes?                                           |
|-------------------|--------------------------------------------|----------------------------------------------------|
| `historical_city` | The city **during that version**           | **Never** changes once written                     |
| `current_city`    | The city **today**                         | **Overwritten on ALL rows** of the customer whenever they move |

### Where each type comes in

| Piece                                                       | Type       |
|-------------------------------------------------------------|------------|
| New row for each change, with dates and a current flag      | **Type 2** |
| Two columns for the same attribute (historical + current)   | **Type 3** |
| `current_city` overwritten on **every** row of that customer | **Type 1** |

```
Ravi moves Hyderabad → Delhi

  cust_key 1  historical: Bengaluru   current: Hyderabad ─┐
  cust_key 3  historical: Hyderabad   current: Hyderabad ─┼─► Type 1: overwrite ALL to "Delhi"
                                      (expire: end_date, N)  ◄── Type 2: close the open row
  cust_key 5  historical: Delhi       current: Delhi      ◄── Type 2: insert new version
```

---

## 3. Worked example: three runs

### Run 1: Source (`stg_customer`), 2026-01-01

| cust_id | name  | city      |
|---------|-------|-----------|
| C01     | Ravi  | Bengaluru |
| C02     | Priya | Chennai   |

**Target after Run 1 (`dim_customer`)**

| cust_key | cust_id | name  | historical_city | current_city | start_date | end_date   | is_current |
|----------|---------|-------|-----------------|--------------|------------|------------|------------|
| 1        | C01     | Ravi  | Bengaluru       | Bengaluru    | 2026-01-01 | 9999-12-31 | Y          |
| 2        | C02     | Priya | Chennai         | Chennai      | 2026-01-01 | 9999-12-31 | Y          |

> For a brand-new customer, `historical_city = current_city`.

### Run 2: Source, 2026-06-01

| cust_id | name  | city          |
|---------|-------|---------------|
| C01     | Ravi  | **Hyderabad** |
| C02     | Priya | Chennai       |
| C03     | Arjun | Pune          |

**Target after Run 2**

| cust_key | cust_id | name  | historical_city | current_city  | start_date | end_date       | is_current |
|----------|---------|-------|-----------------|---------------|------------|----------------|------------|
| 1        | C01     | Ravi  | Bengaluru       | **Hyderabad** | 2026-01-01 | **2026-05-31** | **N**      |
| 2        | C02     | Priya | Chennai         | Chennai       | 2026-01-01 | 9999-12-31     | Y          |
| 3        | C01     | Ravi  | Hyderabad       | Hyderabad     | 2026-06-01 | 9999-12-31     | Y          |
| 4        | C03     | Arjun | Pune            | Pune          | 2026-06-01 | 9999-12-31     | Y          |

What happened to Ravi:
- **Row 1 was expired** (Type 2): `end_date` set, `is_current = 'N'`.
- **Row 1's `current_city` was overwritten** to Hyderabad (Type 1), but its `historical_city` **still says Bengaluru**.
- **Row 3 was inserted** as his new current version (Type 2).

### Run 3: Source, 2026-10-19

| cust_id | name  | city      |
|---------|-------|-----------|
| C01     | Ravi  | **Delhi** |
| C02     | Priya | Chennai   |
| C03     | Arjun | Pune      |

**Target after Run 3**

| cust_key | cust_id | name  | historical_city | current_city | start_date | end_date       | is_current |
|----------|---------|-------|-----------------|--------------|------------|----------------|------------|
| 1        | C01     | Ravi  | Bengaluru       | **Delhi**    | 2026-01-01 | 2026-05-31     | N          |
| 2        | C02     | Priya | Chennai         | Chennai      | 2026-01-01 | 9999-12-31     | Y          |
| 3        | C01     | Ravi  | Hyderabad       | **Delhi**    | 2026-06-01 | **2026-10-18** | **N**      |
| 4        | C03     | Arjun | Pune            | Pune         | 2026-06-01 | 9999-12-31     | Y          |
| 5        | C01     | Ravi  | Delhi           | Delhi        | 2026-10-19 | 9999-12-31     | Y          |

> All three of Ravi's rows now say `current_city = Delhi`, while each row's `historical_city` still shows **where he was during that period**.

> 📅 In this design `end_date` is **inclusive** (the last day the version was valid): new `start_date` = old `end_date` + 1 day. Lookups therefore use `BETWEEN start_date AND end_date`. (The Type 4 notes used an *exclusive* `valid_to`. Both are fine, but **pick one convention per warehouse** and never mix them.)

---

## 4. How the fact table uses it

Each sale points to the `cust_key` that was **valid on the sale date** (normal Type 2 behaviour).

**`fact_sales`**

| sale_date  | cust_key                     | amount |
|------------|------------------------------|--------|
| 2026-01-20 | 1 (Ravi, Bengaluru version)  | 2,000  |
| 2026-08-10 | 3 (Ravi, Hyderabad version)  | 3,000  |
| 2026-10-25 | 5 (Ravi, Delhi version)      | 1,500  |

### Fact load: look up the version valid on the sale date

```sql
INSERT INTO dbo.fact_sales (sale_date, cust_key, amount)
SELECT o.sale_date,
       d.cust_key,
       o.amount
FROM   dbo.stg_orders   o
JOIN   dbo.dim_customer d
  ON   d.cust_id = o.cust_id
 AND   o.sale_date BETWEEN d.start_date AND d.end_date;   -- version valid that day
```

> 💡 Because the lookup uses the **sale date** (not "current row"), a **late-arriving** sale (e.g. an August sale loaded in October) still gets the correct Hyderabad version, `cust_key = 3`. This is an advantage over the Type 5 load, which froze whatever profile was current at load time.

### Report 1: "As it was" (sales by city at the time of sale)

```sql
SELECT d.historical_city, SUM(f.amount) AS sales
FROM   dbo.fact_sales   f
JOIN   dbo.dim_customer d ON d.cust_key = f.cust_key
GROUP  BY d.historical_city;
```

| historical_city | sales |
|-----------------|-------|
| Bengaluru       | 2,000 |
| Hyderabad       | 3,000 |
| Delhi           | 1,500 |

### Report 2: "As it is now" (all sales by the customer's current city)

```sql
SELECT d.current_city, SUM(f.amount) AS sales
FROM   dbo.fact_sales   f
JOIN   dbo.dim_customer d ON d.cust_key = f.cust_key
GROUP  BY d.current_city;
```

| current_city | sales |
|--------------|-------|
| Delhi        | 6,500 |

> 🔑 **Same join, just a different column. No self-join needed.** That's the whole point of Type 6.

### Report 3: Both at once ("where did today's Delhi revenue come from?")

```sql
SELECT d.current_city, d.historical_city, SUM(f.amount) AS sales
FROM   dbo.fact_sales   f
JOIN   dbo.dim_customer d ON d.cust_key = f.cust_key
GROUP  BY d.current_city, d.historical_city;
```

| current_city | historical_city | sales |
|--------------|-----------------|-------|
| Delhi        | Bengaluru       | 2,000 |
| Delhi        | Hyderabad       | 3,000 |
| Delhi        | Delhi           | 1,500 |

> This is the **Type 3 "old vs new"** idea, but with **full** history instead of just one step back.

### Report 4: Current customer list (dimension only)

```sql
SELECT cust_id, name, current_city
FROM   dbo.dim_customer
WHERE  is_current = 'Y';
```

| cust_id | name  | current_city |
|---------|-------|--------------|
| C01     | Ravi  | Delhi        |
| C02     | Priya | Chennai      |
| C03     | Arjun | Pune         |

> ⚠️ When querying the **dimension alone**, always filter `is_current = 'Y'`, or Ravi is counted **three times**.

---

## 5. SQL code (basic version)

Type 6 needs **three things** per changed customer:

1. **Overwrite** `current_city` on **all** their rows (Type 1)
2. **Expire** their current row (Type 2)
3. **Insert** a new current row (Type 2)

All inside **one transaction**.

### Table design (DDL)

```sql
CREATE TABLE dbo.dim_customer (
    cust_key         INT IDENTITY(1,1) PRIMARY KEY,   -- surrogate key, one per VERSION
    cust_id          VARCHAR(10)  NOT NULL,           -- natural key, many rows per customer
    name             VARCHAR(100) NOT NULL,
    historical_city  VARCHAR(50)  NULL,               -- Type 2: frozen per version
    current_city     VARCHAR(50)  NULL,               -- Type 1: overwritten on all rows
    start_date       DATE         NOT NULL,
    end_date         DATE         NOT NULL,           -- inclusive; 9999-12-31 = open
    is_current       CHAR(1)      NOT NULL,
    updated_at       DATETIME2    NOT NULL DEFAULT SYSDATETIME()
);

-- Guarantee: at most ONE current row per customer (SQL Server filtered unique index)
CREATE UNIQUE INDEX ux_dim_customer_one_current
    ON dbo.dim_customer (cust_id) WHERE is_current = 'Y';

-- Fast fact lookups and fast "update all rows of this customer"
CREATE INDEX ix_dim_customer_lookup
    ON dbo.dim_customer (cust_id, start_date, end_date);
```

> The **filtered unique index** is a cheap safety net. If a bug ever tries to create a second `is_current = 'Y'` row for a customer, the load **fails** instead of silently corrupting the data.

### Load script

```sql
DECLARE @load_date DATE = '2026-10-19';
SET XACT_ABORT ON;

BEGIN TRAN;

------------------------------------------------------------------
-- Step 0: find customers whose city changed
--         (compare with the CURRENT row's historical_city)
------------------------------------------------------------------
DROP TABLE IF EXISTS #chg;

SELECT s.cust_id, s.name, s.city
INTO   #chg
FROM   dbo.stg_customer s
JOIN   dbo.dim_customer t
  ON   t.cust_id    = s.cust_id
 AND   t.is_current = 'Y'
WHERE  t.historical_city IS DISTINCT FROM s.city;

------------------------------------------------------------------
-- Step 1: Type 1 overwrite on ALL rows + expire the open row (Type 2)
------------------------------------------------------------------
UPDATE t
SET    t.current_city = c.city,                                   -- Type 1: every row
       t.end_date     = CASE WHEN t.is_current = 'Y'
                             THEN DATEADD(DAY, -1, @load_date)
                             ELSE t.end_date END,                 -- only the open row
       t.is_current   = 'N',
       t.updated_at   = SYSDATETIME()
FROM   dbo.dim_customer t
JOIN   #chg c ON c.cust_id = t.cust_id;

------------------------------------------------------------------
-- Step 2: insert new current rows (changed + brand-new customers)
------------------------------------------------------------------
INSERT INTO dbo.dim_customer
       (cust_id, name, historical_city, current_city, start_date, end_date, is_current)
SELECT cust_id, name, city, city, @load_date, '9999-12-31', 'Y'
FROM   #chg
UNION ALL
SELECT s.cust_id, s.name, s.city, s.city, @load_date, '9999-12-31', 'Y'
FROM   dbo.stg_customer s
WHERE  NOT EXISTS (SELECT 1 FROM dbo.dim_customer t WHERE t.cust_id = s.cust_id);

COMMIT;
```

### How each step behaves in Run 3

| Step | Ravi (C01) | Priya (C02), Arjun (C03) |
|------|------------|--------------------------|
| 0. Find changes | Current row says Hyderabad, source says Delhi → **in `#chg`** | No change → not in `#chg` |
| 1. Overwrite + expire | Rows 1 & 3: `current_city = Delhi`; row 3 also gets `end_date = 2026-10-18`, `is_current = 'N'` | Untouched |
| 2. Insert | Row 5 inserted: Delhi / Delhi / open | Already exist → not inserted |

### Notes on the code

- **Step 0 must run before Step 1.** After Step 1, Ravi has **no** `is_current = 'Y'` row to compare against, so the change could no longer be detected.
- **One source row updates many target rows** (all of Ravi's versions). That is allowed. What's *not* allowed (in `MERGE`) is **several source rows matching one target row**, which is why production code deduplicates the source first.
- Setting `is_current = 'N'` on **all** of Ravi's rows is safe: the old ones were already `'N'`.
- `cust_key` is an `IDENTITY` column, so it isn't in the INSERT list.
- In SQL Server, an `UPDATE ... FROM ... JOIN` is simpler than a `MERGE` here. A `MERGE` with only a `WHEN MATCHED` branch does the same job.

---

## 6. Production-grade version

The basic script is correct for clean data. Real feeds add problems.

| Problem | Fix in the script below |
|---------|-------------------------|
| Same customer appears **twice** in one batch | Deduplicate with `ROW_NUMBER()` into `#src` |
| `city` can be **NULL** | `IS DISTINCT FROM` everywhere |
| **Name** corrections should not create a new version | Treat `name` as **pure Type 1**: overwrite on all rows, no new row |
| Job **rerun** after success or failure | Change detection + transaction make it idempotent |
| Backfills | `@load_date` (batch date), never `GETDATE()` |

### Run 4: Source, batch 2027-01-15 (messy CDC feed)

| cust_id | name           | city           | op_ts            |
|---------|----------------|----------------|------------------|
| C01     | **Ravi Kumar** | Delhi          | 2027-01-15 09:00 |
| C02     | Priya          | Chennai        | 2027-01-15 09:00 |
| C02     | Priya          | **Coimbatore** | 2027-01-15 15:00 |
| C03     | Arjun          | Pune           | 2027-01-15 09:00 |

What's going on:

| Customer | Situation | Expected result |
|----------|-----------|-----------------|
| C01 | **Name corrected** (Type 1), city unchanged | Name overwritten on **all 3 rows**, **no new version** |
| C02 | Appears **twice**; the latest (15:00) says Coimbatore | Dedup → Coimbatore wins → **new version** |
| C03 | No change | Untouched |

**Target after Run 4**

| cust_key | cust_id | name           | historical_city | current_city   | start_date | end_date       | is_current |
|----------|---------|----------------|-----------------|----------------|------------|----------------|------------|
| 1        | C01     | **Ravi Kumar** | Bengaluru       | Delhi          | 2026-01-01 | 2026-05-31     | N          |
| 2        | C02     | Priya          | Chennai         | **Coimbatore** | 2026-01-01 | **2027-01-14** | **N**      |
| 3        | C01     | **Ravi Kumar** | Hyderabad       | Delhi          | 2026-06-01 | 2026-10-18     | N          |
| 4        | C03     | Arjun          | Pune            | Pune           | 2026-06-01 | 9999-12-31     | Y          |
| 5        | C01     | **Ravi Kumar** | Delhi           | Delhi          | 2026-10-19 | 9999-12-31     | Y          |
| 6        | C02     | Priya          | Coimbatore      | Coimbatore     | 2027-01-15 | 9999-12-31     | Y          |

> Ravi still has **3 rows**: a name correction is not a new version. Priya got her **second** version.

### Production load script

```sql
DECLARE @load_date DATE = '2027-01-15';
DECLARE @end_date  DATE = DATEADD(DAY, -1, @load_date);
SET XACT_ABORT ON;

------------------------------------------------------------------
-- Step 0a: deduplicate the batch (latest record per customer wins)
------------------------------------------------------------------
DROP TABLE IF EXISTS #src;

SELECT cust_id, name, city
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
-- Step 0b: customers whose TYPE 2/6 attribute (city) changed
------------------------------------------------------------------
DROP TABLE IF EXISTS #chg;

SELECT s.cust_id, s.name, s.city
INTO   #chg
FROM   #src s
JOIN   dbo.dim_customer t
  ON   t.cust_id    = s.cust_id
 AND   t.is_current = 'Y'
WHERE  t.historical_city IS DISTINCT FROM s.city;

------------------------------------------------------------------
-- Step 1: TYPE 1 overwrite on ALL rows
--         current_city (Type 6 part) + name (pure Type 1)
------------------------------------------------------------------
UPDATE t
SET    t.current_city = s.city,
       t.name         = s.name,
       t.updated_at   = SYSDATETIME()
FROM   dbo.dim_customer t
JOIN   #src s ON s.cust_id = t.cust_id
WHERE  t.current_city IS DISTINCT FROM s.city
   OR  t.name         IS DISTINCT FROM s.name;

------------------------------------------------------------------
-- Step 2: TYPE 2 expire the open row of changed customers
------------------------------------------------------------------
UPDATE t
SET    t.end_date   = @end_date,
       t.is_current = 'N',
       t.updated_at = SYSDATETIME()
FROM   dbo.dim_customer t
JOIN   #chg c ON c.cust_id = t.cust_id
WHERE  t.is_current = 'Y';

------------------------------------------------------------------
-- Step 3: TYPE 2 insert new versions + brand-new customers
------------------------------------------------------------------
INSERT INTO dbo.dim_customer
       (cust_id, name, historical_city, current_city, start_date, end_date, is_current)
SELECT cust_id, name, city, city, @load_date, '9999-12-31', 'Y'
FROM   #chg
UNION ALL
SELECT s.cust_id, s.name, s.city, s.city, @load_date, '9999-12-31', 'Y'
FROM   #src s
WHERE  NOT EXISTS (SELECT 1 FROM dbo.dim_customer t WHERE t.cust_id = s.cust_id);

COMMIT;
```

### Why this is rerun-safe (idempotent)

If the script runs again for 2027-01-15 after succeeding:

| Step | Why nothing happens on rerun |
|------|------------------------------|
| 0b   | Current rows already match the source, so `#chg` is empty |
| 1    | `current_city` and `name` already equal the source |
| 2    | `#chg` is empty |
| 3    | `#chg` is empty; all customers already exist |

If it **fails midway**, `SET XACT_ABORT ON` rolls back Steps 0b–3 together.

### Tricky case: two different values for the same `@load_date`

If a batch is **reloaded with corrected data** for the same date (e.g. Priya's city fixed from Coimbatore to Madurai on 2027-01-15), the script would expire row 6, whose `start_date = 2027-01-15`, with `end_date = 2027-01-14`. That gives `end_date < start_date`, an invalid version.

**Fix:** if the current row's `start_date = @load_date`, **update it in place** instead of creating a new version:

```sql
-- before Steps 1-3: same-day correction → overwrite the version created today
UPDATE t
SET    t.historical_city = c.city,
       t.current_city    = c.city,
       t.updated_at      = SYSDATETIME()
FROM   dbo.dim_customer t
JOIN   #chg c ON c.cust_id = t.cust_id
WHERE  t.is_current = 'Y'
  AND  t.start_date = @load_date;

-- ...then remove those customers from #chg so Steps 2-3 skip them,
-- but still run Step 1 for their older rows' current_city.
```

---

## 7. Design alternatives you should know

### 7.1 Computing `current_city` in a view instead of storing it

Instead of overwriting every row, **derive** the current value at query time:

```sql
CREATE VIEW dbo.vw_customer_t6 AS
SELECT d.cust_key, d.cust_id, d.name, d.historical_city,
       cur.historical_city AS current_city,
       d.start_date, d.end_date, d.is_current
FROM   dbo.dim_customer d
JOIN   dbo.dim_customer cur
  ON   cur.cust_id    = d.cust_id
 AND   cur.is_current = 'Y';
```

| | Stored `current_city` (true Type 6) | View-based |
|---|---|---|
| Load cost | Updates **every** row of a changed customer | Only Type 2 load |
| Query cost | Simple, fast | Self-join hidden in the view |
| Columnar warehouses (Snowflake, Databricks) | Many row rewrites = expensive | Usually cheaper |

> Many modern teams store `current_*` columns only for a few heavily used attributes and use views for the rest.

### 7.2 Type 7 (bonus, for interviews)

Kimball's **Type 7** puts **both** a surrogate key (`cust_key`, the version) **and** the durable natural key (`cust_id`) on the **fact** table. Facts join on `cust_key` to the Type 2 dimension for "as it was", and on `cust_id` to a **current-rows-only view** for "as it is now". You get the same result as Type 6, without overwriting historical rows.

---

## 8. Quick comparison

| Type   | Full history?   | Current value on old rows? | Table size | Load complexity |
|--------|-----------------|----------------------------|------------|-----------------|
| Type 1 | No              | Yes (only one row)         | Small      | Low             |
| Type 2 | Yes             | No (needs self-join)       | Grows      | Medium          |
| Type 3 | One step back   | Yes                        | Small      | Low–medium      |
| Type 4 | Yes (separate table) | Current table only    | Small + history table | Medium |
| Type 5 | Via facts       | Yes (pointer on base dim)  | Small      | Medium          |
| **Type 6** | **Yes**     | **Yes**                    | **Grows**  | **High** (update all rows + expire + insert) |

---

## 9. Pros, cons, and when to use it

| ✅ Pros                                                         | ❌ Cons                                                              |
|-----------------------------------------------------------------|----------------------------------------------------------------------|
| "As it was" **and** "as it is now" from the **same join**       | Every change **updates all rows** of that customer, which is expensive for long histories |
| No self-joins for analysts                                      | Most complex load of all the SCD types                              |
| Full history (unlike Type 3)                                    | Table grows like Type 2                                              |
| Late-arriving facts still map to the correct version            | Historical rows are rewritten (Type 1 part), which can surprise auditors who expect history to be untouched |
| Very popular, well understood in industry                       | Must filter `is_current = 'Y'` when querying the dimension alone      |

### Use Type 6 when

- The business wants **both** "as it was" and "as it is now" reporting on the **same** dimension, e.g. sales by a customer's region **at the time of sale** and by their **current** region.
- Analysts use BI tools that can't easily express self-joins.
- The attribute changes **rarely** enough that rewriting all of a customer's rows is affordable.

### Avoid Type 6 when

- Only one of the two views is needed → use Type 1 or Type 2.
- The attribute changes **very often** → too many row rewrites; consider Type 5 (mini-dimension) or a view-based approach.
- Regulators require historical rows to be **immutable** → use Type 2 + a view (or Type 7).

---

## 10. Real-world applications

1. **Sales territory reporting**: revenue by rep's territory at the time of the deal vs current territory (for commission vs planning).
2. **Customer region / segment**: "as it was" for financial reporting, "as it is now" for marketing targeting.
3. **Product category re-organisation**: historical sales under the old and new category, with full history (Type 3 only keeps one step).
4. **Employee department / cost centre**: headcount cost at the time vs rolled up under today's org structure.
5. **Store / branch hierarchy**: branch performance by the region at the time and by today's region after a realignment.
6. **Healthcare provider network**: claims by the provider's network at service date vs current network.

---

## 11. Production checklist for Type 6

- [ ] Decide per column: **Type 1** (overwrite all rows), **Type 2** (new version), **Type 6** (historical + current pair).
- [ ] Deduplicate the source per natural key before change detection.
- [ ] Detect changes against the **current row's `historical_*`** column, **before** expiring anything.
- [ ] Use `IS DISTINCT FROM` (NULL-safe) everywhere.
- [ ] Overwrite `current_*` on **all** rows, expire the open row, insert the new version, all in **one transaction**.
- [ ] Filtered unique index: **one** `is_current = 'Y'` row per natural key.
- [ ] Pick **one** end-date convention (inclusive `BETWEEN` or exclusive `<`) for the whole warehouse.
- [ ] Use `@load_date` for `start_date` / `end_date`, never `GETDATE()`.
- [ ] Handle **same-day corrections** (don't create `end_date < start_date`).
- [ ] Fact load uses the **sale date** to find the version (`BETWEEN start_date AND end_date`).
- [ ] Index `(cust_id, start_date, end_date)` for fact lookups and all-rows updates.
- [ ] Test: new customer, no change, Type 1-only change, city change, two changes over time, duplicate source rows, NULL → value, full rerun, failed-midway rerun, same-day reload.

---

## 12. Choosing the right SCD type (the whole series)

```
Does the business need the OLD value at all?
├── No ─────────────────────────────────────────────► Type 1 (overwrite)
│        (and the value must never change?) ────────► Type 0 (retain original)
└── Yes
    ├── Only the previous value, for an old-vs-new comparison? ─► Type 3
    ├── Full history needed
    │   ├── Most queries need only CURRENT values,
    │   │   history mainly for audit?  ─────────────► Type 4 (history table)
    │   ├── Attributes change OFTEN and are bandable
    │   │   (age / income / credit band)? ─────────► Type 4 mini-dimension
    │   │        └── also need current band without facts? ─► Type 5
    │   ├── Need "as it was" only ───────────────────► Type 2
    │   └── Need "as it was" AND "as it is now"
    │       on the same join ───────────────────────► Type 6
    │            (rows must stay immutable?) ───────► Type 7 / Type 2 + view
```

---

## 13. Check your understanding

**Conceptual**
1. Why is it called Type **6**? Which part of the design comes from Type 1, which from Type 2, and which from Type 3?
2. What is the difference between `historical_city` and `current_city`? Which one ever changes after it's written?
3. What problem in plain Type 2 does Type 6 solve? Write the self-join that Type 2 would need.

**Using the worked example**
4. After Run 3, Ravi has three rows. What are their `current_city` values, and why are they all the same?
5. In Report 1 the totals are split across three cities; in Report 2 they're all under Delhi. Explain why both are correct.
6. A query `SELECT COUNT(*) FROM dim_customer WHERE current_city = 'Delhi'` returns 3. Why, and how do you fix it?

**Code-level**
7. Why must Step 0 (finding changes) run **before** Step 1 (expiring rows)?
8. In Step 1, one row in `#chg` updates **several** rows in `dim_customer`. Why is that OK, and what situation would **not** be OK?
9. Why does the production script compare against `historical_city` of the current row, and not `current_city`?
10. Ravi's name is corrected to "Ravi Kumar". Why does that **not** create a new version in the production script?
11. What does the filtered unique index `WHERE is_current = 'Y'` protect against?
12. A batch for 2027-01-15 is reloaded with a different city for Priya. What goes wrong with the basic script, and how do you fix it?

**Design thinking**
13. A customer has 200 versions, and their city changes again. What does the Type 1 part of the load cost, and what alternatives exist?
14. An auditor says: "Historical rows must never be modified." Can you still give analysts "as it is now" reporting? How?
15. Your business wants "sales by region at time of sale" only. Would you recommend Type 6? Why or why not?
16. Compare Type 5 and Type 6: both give "history + current". When would you choose each?
