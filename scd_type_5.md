# SCD Type 5: Mini-Dimension + Type 1 "Current Profile" Pointer

> SQL dialect used in these notes: **SQL Server** (same as [scd_type_4.md](scd_type_4.md)).
> Prerequisite: the **mini-dimension** section in [scd_type_4.md, section 6](scd_type_4.md#6-kimballs-meaning-the-mini-dimension).

---

## 1. Quick recap: where Type 5 fits

| Type  | What happens on change                                  | History kept?              |
|-------|---------------------------------------------------------|----------------------------|
| 0     | Never change the value                                  | Original only              |
| 1     | Overwrite the old value                                 | None                       |
| 2     | Add a new row (with start/end dates)                    | Full, in the same table    |
| 3     | Keep current + previous value in columns                | One step back              |
| 4     | Separate history table, **or** Kimball's mini-dimension | Full                       |
| **5** | **Mini-dimension (4) + current profile key on the base dimension (1)** | **Full (via facts) + current (via dimension)** |
| 6     | Types 1 + 2 + 3 combined                                | Full + current + previous  |

> **Why "5"?** Because **4 + 1 = 5**: Kimball's Type 4 mini-dimension plus a Type 1 overwrite column.
> ⚠️ Type 5 builds on the **mini-dimension** meaning of Type 4, **not** the "history table" meaning.

---

## 2. What is SCD Type 5?

### The problem with the Type 4 mini-dimension

In the mini-dimension pattern, rapidly changing attributes (income band, credit band) live in a small separate table, and the **fact table** stores which profile applied at the time of each sale.

That gives you perfect **history**, but there's a gap:

> ❓ *"What is Ravi's **current** income band?"*

With only Type 4, you'd have to find Ravi's **latest sale** and read its `profile_key`. And if a customer hasn't bought anything recently, **there is no answer at all**.

### The Type 5 solution

> **Add a `current_profile_key` column to the base customer dimension and overwrite it (Type 1) whenever the customer's profile changes.**

Now there are **two paths** to the profile:

```
                     ┌──────────────────────────────┐
                     │ dim_customer (base dimension)│
                     │ cust_key, cust_id, name,     │
                     │ current_profile_key ─────────┼──────┐  PATH 2: CURRENT profile
                     └──────────────▲───────────────┘      │  (Type 1, overwritten)
                                    │ cust_key             │
┌───────────────────────────────────┴───────────────┐      ▼
│ fact_sales                                        │   ┌────────────────────────┐
│ sale_date, cust_key, profile_key, amount ─────────┼──►│ dim_profile            │
└───────────────────────────────────────────────────┘   │ (mini-dimension)       │
              PATH 1: profile AT TIME OF SALE           │ profile_key,           │
              (frozen in the fact row, never changes)   │ income_band,           │
                                                        │ credit_band            │
                                                        └────────────────────────┘
```

| Question | Path | Join |
|----------|------|------|
| "Sales by income band **at the time of sale**" | Path 1 | `fact_sales.profile_key → dim_profile` |
| "Sales by customer's **current** income band" | Path 2 | `fact_sales.cust_key → dim_customer.current_profile_key → dim_profile` |
| "How many customers are **currently** in 20L+?" | Path 2 | `dim_customer.current_profile_key → dim_profile` (**no facts needed**) |

### Why not just use Type 2 on the customer dimension?

| With Type 2 on `dim_customer` | With Type 5 |
|-------------------------------|-------------|
| Every band change adds a **new customer row** | Customer row count **never grows** from band changes |
| 50M customers × frequent band changes = **hundreds of millions of rows** | 50M customer rows + a mini-dimension of **only band combinations** (often < 1,000 rows) |
| `cust_key` changes per version, so it's hard to count "unique customers" | One `cust_key` per customer, forever |

---

## 3. The three tables

**`dim_customer`** (base dimension): `cust_key`, `cust_id`, `name`, `current_profile_key`

**`dim_profile`** (mini-dimension): `profile_key`, `income_band`, `credit_band`

**`fact_sales`**: `sale_date`, `cust_key`, `profile_key`, `amount`

| Table          | Role                                                        | How it changes                                        |
|----------------|-------------------------------------------------------------|-------------------------------------------------------|
| `dim_profile`  | Mini-dimension: each **band combination** stored **once**   | New combinations are **added**; nothing is ever updated |
| `dim_customer` | One row per customer + `current_profile_key`                | `current_profile_key` is **overwritten** (Type 1)     |
| `fact_sales`   | One row per sale, with the profile **at the time of sale**  | New rows **added**; old rows **never touched**        |

> 💡 In real projects the mini-dimension usually holds more bands (e.g. `age_band`, `income_band`, `credit_band`), and the base dimension holds stable attributes (e.g. `city`). This example keeps two bands so the runs are easy to follow.

> 📝 `profile_key` is an `INT IDENTITY` in the database. It is shown as **P1, P2, P3** in these notes for readability.

---

## 4. Worked example: two runs

### RUN 1: January

**Input 1: Customer feed (`stg_customer`)**

| cust_id | name  | income_band | credit_band |
|---------|-------|-------------|-------------|
| C01     | Ravi  | 5-10L       | Good        |
| C02     | Priya | 20L+        | Excellent   |
| C03     | Arjun | 5-10L       | Good        |

**Input 2: Sales feed (`stg_orders`)**

| sale_date  | cust_id | amount |
|------------|---------|--------|
| 2026-01-20 | C01     | 2,000  |
| 2026-01-22 | C02     | 5,000  |
| 2026-01-25 | C03     | 1,500  |

**`dim_profile` after Run 1**

| profile_key | income_band | credit_band |
|-------------|-------------|-------------|
| P1          | 5-10L       | Good        |
| P2          | 20L+        | Excellent   |

> Three customers, but only **two combinations**. Ravi and Arjun **share P1**.

**`dim_customer` after Run 1**

| cust_key | cust_id | name  | current_profile_key |
|----------|---------|-------|---------------------|
| 1        | C01     | Ravi  | P1                  |
| 2        | C02     | Priya | P2                  |
| 3        | C03     | Arjun | P1                  |

**`fact_sales` after Run 1**

Each sale picks up the customer's `current_profile_key` **at load time** and stores it **permanently**.

| sale_date  | cust_key  | profile_key | amount |
|------------|-----------|-------------|--------|
| 2026-01-20 | 1 (Ravi)  | P1          | 2,000  |
| 2026-01-22 | 2 (Priya) | P2          | 5,000  |
| 2026-01-25 | 3 (Arjun) | P1          | 1,500  |

---

### RUN 2: June

**Input 1: Customer feed (`stg_customer`)**

| cust_id | name  | income_band | credit_band   |
|---------|-------|-------------|---------------|
| C01     | Ravi  | **10-20L**  | **Excellent** |
| C02     | Priya | 20L+        | Excellent     |
| C03     | Arjun | 5-10L       | Good          |
| C04     | Kavya | 20L+        | Excellent     |

> Ravi got a raise **and** better credit. Kavya is a new customer.

**Input 2: Sales feed (`stg_orders`)**

| sale_date  | cust_id | amount |
|------------|---------|--------|
| 2026-06-05 | C01     | 3,000  |
| 2026-06-07 | C04     | 4,000  |

**`dim_profile` after Run 2**

| profile_key | income_band | credit_band |
|-------------|-------------|-------------|
| P1          | 5-10L       | Good        |
| P2          | 20L+        | Excellent   |
| P3          | 10-20L      | Excellent   |

What happened:
- Ravi's new combination **didn't exist yet**, so **P3 was added**.
- Kavya's combination **already exists (P2)**, so nothing new is added for her.
- **P1 stays** even though Ravi left it, because Arjun and old sales still use it. Mini-dimension rows are **never deleted or updated**.

**`dim_customer` after Run 2**

| cust_key | cust_id | name  | current_profile_key |
|----------|---------|-------|---------------------|
| 1        | C01     | Ravi  | **P3** ← was P1     |
| 2        | C02     | Priya | P2                  |
| 3        | C03     | Arjun | P1                  |
| 4        | C04     | Kavya | P2                  |

What happened: Ravi **still has one row**. Only his pointer was **overwritten** from P1 to P3 (Type 1). Kavya was inserted.

**`fact_sales` after Run 2**

| sale_date  | cust_key  | profile_key | amount |                     |
|------------|-----------|-------------|--------|---------------------|
| 2026-01-20 | 1 (Ravi)  | **P1**      | 2,000  | old row, unchanged  |
| 2026-01-22 | 2 (Priya) | P2          | 5,000  | old row, unchanged  |
| 2026-01-25 | 3 (Arjun) | P1          | 1,500  | old row, unchanged  |
| 2026-06-05 | 1 (Ravi)  | **P3**      | 3,000  | new                 |
| 2026-06-07 | 4 (Kavya) | P2          | 4,000  | new                 |

> 🔑 **The key insight:** Ravi's January sale still says **P1** and his June sale says **P3**. The fact table holds the **history**; `dim_customer` holds the **current** state. Neither one has to grow to support the other.

---

## 5. SQL code

### 5.1 Table design (DDL)

```sql
CREATE TABLE dbo.dim_profile (                        -- mini-dimension
    profile_key   INT IDENTITY(1,1) PRIMARY KEY,
    income_band   VARCHAR(20) NOT NULL,
    credit_band   VARCHAR(20) NOT NULL,
    CONSTRAINT uq_profile UNIQUE (income_band, credit_band)   -- each combination once
);

CREATE TABLE dbo.dim_customer (                       -- base dimension
    cust_key             INT IDENTITY(1,1) PRIMARY KEY,
    cust_id              VARCHAR(10)  NOT NULL UNIQUE,
    name                 VARCHAR(100) NOT NULL,
    current_profile_key  INT NOT NULL
        REFERENCES dbo.dim_profile (profile_key),     -- Type 1 outrigger
    updated_at           DATETIME2    NOT NULL
);

CREATE TABLE dbo.fact_sales (
    sale_id      BIGINT IDENTITY(1,1) PRIMARY KEY,
    sale_date    DATE          NOT NULL,
    cust_key     INT           NOT NULL REFERENCES dbo.dim_customer (cust_key),
    profile_key  INT           NOT NULL REFERENCES dbo.dim_profile (profile_key),  -- frozen at load
    amount       DECIMAL(12,2) NOT NULL
);
```

> The `UNIQUE (income_band, credit_band)` constraint guarantees that a combination can never be stored twice, even if the load logic has a bug.

### 5.2 Load script (runs once per batch)

**The order matters:** profiles → customers → facts. The fact load reads `current_profile_key`, so the customer pointer must already be up to date for this batch.

```sql
SET XACT_ABORT ON;      -- any error rolls back everything
BEGIN TRAN;

------------------------------------------------------------------
-- Step 1: Add NEW band combinations to the mini-dimension
--         (insert-only; existing rows are never updated or deleted)
------------------------------------------------------------------
INSERT INTO dbo.dim_profile (income_band, credit_band)
SELECT DISTINCT s.income_band, s.credit_band
FROM   dbo.stg_customer s
WHERE  NOT EXISTS (SELECT 1
                   FROM   dbo.dim_profile p
                   WHERE  p.income_band = s.income_band
                     AND  p.credit_band = s.credit_band);

------------------------------------------------------------------
-- Step 2: Upsert customers and OVERWRITE current_profile_key (Type 1)
------------------------------------------------------------------
MERGE dbo.dim_customer WITH (HOLDLOCK) AS t
USING (
    SELECT s.cust_id, s.name, p.profile_key
    FROM   dbo.stg_customer s
    JOIN   dbo.dim_profile  p
      ON   p.income_band = s.income_band
     AND   p.credit_band = s.credit_band
) AS s
   ON t.cust_id = s.cust_id

WHEN MATCHED AND (   t.current_profile_key <> s.profile_key
                  OR t.name IS DISTINCT FROM s.name ) THEN
  UPDATE SET t.current_profile_key = s.profile_key,     -- overwrite pointer
             t.name                = s.name,
             t.updated_at          = SYSDATETIME()

WHEN NOT MATCHED BY TARGET THEN
  INSERT (cust_id, name, current_profile_key, updated_at)
  VALUES (s.cust_id, s.name, s.profile_key, SYSDATETIME());

------------------------------------------------------------------
-- Step 3: Load facts, freezing the profile that is current RIGHT NOW
------------------------------------------------------------------
INSERT INTO dbo.fact_sales (sale_date, cust_key, profile_key, amount)
SELECT o.sale_date,
       c.cust_key,
       c.current_profile_key,       -- snapshot of the profile at load time
       o.amount
FROM   dbo.stg_orders   o
JOIN   dbo.dim_customer c ON c.cust_id = o.cust_id;

COMMIT;
```

### How each step behaves in Run 2

| Step | Ravi (C01) | Kavya (C04) | Arjun / Priya |
|------|------------|-------------|---------------|
| 1. Profiles | `10-20L / Excellent` not found → **P3 inserted** | `20L+ / Excellent` found (P2) → nothing | Found → nothing |
| 2. Customers | Matched, P1 ≠ P3 → **pointer overwritten to P3** | Not matched → **inserted with P2** | Matched, no change → untouched |
| 3. Facts | June sale gets **P3** | June sale gets **P2** | No sales this run |

> ⚠️ If you ran Step 3 **before** Step 2, Ravi's June sale would wrongly get **P1** (his January profile).

### 5.3 Views for BI users

Kimball recommends exposing the current profile through a **view with renamed columns**, so report users never confuse "current band" with "band at time of sale".

```sql
-- Customer with CURRENT profile (Path 2)
CREATE VIEW dbo.vw_customer AS
SELECT c.cust_key,
       c.cust_id,
       c.name,
       p.income_band AS current_income_band,
       p.credit_band AS current_credit_band
FROM   dbo.dim_customer c
JOIN   dbo.dim_profile  p ON p.profile_key = c.current_profile_key;

-- Profile AT TIME OF SALE (Path 1)
CREATE VIEW dbo.vw_sale_profile AS
SELECT profile_key,
       income_band AS sale_income_band,
       credit_band AS sale_credit_band
FROM   dbo.dim_profile;
```

> Same physical table (`dim_profile`), two **roles**: "current profile" and "profile at time of sale". This is called a **role-playing** dimension.

---

## 6. The reports (after Run 2)

### Report 1: Sales by income band **at the time of sale** (Path 1)

```sql
SELECT sp.sale_income_band, SUM(f.amount) AS sales
FROM   dbo.fact_sales      f
JOIN   dbo.vw_sale_profile sp ON sp.profile_key = f.profile_key
GROUP  BY sp.sale_income_band;
```

| sale_income_band | sales  | Made up of                               |
|------------------|--------|------------------------------------------|
| 5-10L            | 3,500  | Ravi Jan 2,000 + Arjun Jan 1,500         |
| 10-20L           | 3,000  | Ravi Jun 3,000                           |
| 20L+             | 9,000  | Priya Jan 5,000 + Kavya Jun 4,000        |

> Ravi's January sale counts under **5-10L**, because that was his band **when he bought**. ✅ Historically accurate.

### Report 2: Sales by the customer's **current** income band (Path 2)

```sql
SELECT c.current_income_band, SUM(f.amount) AS sales
FROM   dbo.fact_sales  f
JOIN   dbo.vw_customer c ON c.cust_key = f.cust_key
GROUP  BY c.current_income_band;
```

| current_income_band | sales  | Made up of                                   |
|---------------------|--------|----------------------------------------------|
| 5-10L               | 1,500  | Arjun                                        |
| 10-20L              | 5,000  | Ravi Jan 2,000 + Ravi Jun 3,000 (he is 10-20L **now**) |
| 20L+                | 9,000  | Priya + Kavya                                |

> Same data, different question: *"How much have the customers who are **now** 10-20L spent in total?"* Useful for targeting, e.g. "our upgraded customers have spent ₹5,000 so far."

### Report 3: Customers by current band, **no facts needed**

```sql
SELECT current_income_band, current_credit_band, COUNT(*) AS customers
FROM   dbo.vw_customer
GROUP  BY current_income_band, current_credit_band;
```

| current_income_band | current_credit_band | customers |
|---------------------|---------------------|-----------|
| 5-10L               | Good                | 1 (Arjun) |
| 10-20L              | Excellent           | 1 (Ravi)  |
| 20L+                | Excellent           | 2 (Priya, Kavya) |

> 💡 **This is the query Type 4 alone could not answer.** A customer with zero sales still has a current profile.

### Report 4: Then vs now for each sale

```sql
SELECT c.name, f.sale_date, f.amount,
       sp.sale_income_band,
       c.current_income_band
FROM   dbo.fact_sales      f
JOIN   dbo.vw_customer     c  ON c.cust_key     = f.cust_key
JOIN   dbo.vw_sale_profile sp ON sp.profile_key = f.profile_key
ORDER  BY c.name, f.sale_date;
```

| name  | sale_date  | amount | sale_income_band | current_income_band |
|-------|------------|--------|------------------|---------------------|
| Arjun | 2026-01-25 | 1,500  | 5-10L            | 5-10L               |
| Kavya | 2026-06-07 | 4,000  | 20L+             | 20L+                |
| Priya | 2026-01-22 | 5,000  | 20L+             | 20L+                |
| Ravi  | 2026-01-20 | 2,000  | **5-10L**        | **10-20L**          |
| Ravi  | 2026-06-05 | 3,000  | 10-20L           | 10-20L              |

> Both paths in one query: the **history** and the **current** state side by side.

---

## 7. Production considerations

| Concern | What can go wrong | How to handle it |
|---------|-------------------|------------------|
| **Load order** | Facts loaded before customers get the **old** profile | Always run profiles → customers → facts in one job |
| **NULL bands** | A customer with an unknown income band doesn't match any profile and is **silently dropped** by the `JOIN` | Map NULLs to `'Unknown'` with `ISNULL(income_band,'Unknown')` in Steps 1 and 2, so an "Unknown" profile is created like any other |
| **Late-arriving facts** | A January sale arriving in June would get Ravi's **June** profile (P3) | For late facts, look up the profile from a customer-profile history (or the source's effective dates), not from `current_profile_key` |
| **Late-arriving customer** | A sale for a customer not yet in `dim_customer` is dropped by the inner join | Insert an "inferred member" row, or use an Unknown customer (`cust_key = -1`) and fix it later |
| **Duplicate source rows** | Two rows for C01 in one batch → MERGE error "attempted to UPDATE the same row more than once" | Deduplicate `stg_customer` with `ROW_NUMBER()` first (see [scd_type_4.md](scd_type_4.md)) |
| **Rerun of the fact load** | Re-running Step 3 **duplicates** sales | Add an `order_id` and insert only `WHERE NOT EXISTS (SELECT 1 FROM fact_sales f WHERE f.order_id = o.order_id)` |
| **Raw values instead of bands** | Storing exact income (e.g. 7,43,000) makes the mini-dimension as big as the customer table | Always **band** the values before loading |
| **Too many band columns** | 10 bands × 10 values each = 10 billion possible combinations | Keep mini-dimensions to a few low-cardinality bands; split into two mini-dimensions if needed |
| **Confusing the two paths** | Analysts join `fact.profile_key` when they meant "current", or the other way round | Expose them as views with clearly renamed columns (`sale_*` vs `current_*`) |

---

## 8. Type 5 vs Type 4 vs Type 2

| Aspect                              | Type 2 on customer           | Type 4 mini-dimension         | **Type 5**                              |
|-------------------------------------|------------------------------|-------------------------------|-----------------------------------------|
| Customer rows per customer          | Many (one per version)       | One                           | **One**                                 |
| History of bands                    | In the customer dimension    | In the fact table             | **In the fact table**                   |
| Current band without facts          | Yes (`is_current` row)       | ❌ No                          | ✅ **Yes** (`current_profile_key`)       |
| Band at time of sale                | Yes                          | Yes                           | **Yes**                                 |
| Size impact of frequent band changes | Huge                        | Tiny                          | **Tiny**                                |
| Customers with no recent facts      | Fine                         | Profile unknown               | **Fine**                                |
| Complexity                          | Medium                       | Medium                        | Medium (+ one Type 1 column)            |

---

## 9. Pros and cons

| ✅ Pros                                                       | ❌ Cons                                                     |
|---------------------------------------------------------------|-------------------------------------------------------------|
| Answers both "at time of sale" and "current" questions        | Two join paths, so users need training or clear views       |
| Base dimension stays one row per customer                     | History of profile changes **between** sales isn't recorded |
| Mini-dimension stays tiny (combinations only)                 | Only works for **banded**, low-cardinality attributes       |
| Current profile is available even for customers with no facts | Load order and late-arriving facts need care                |
| Fact rows are never updated (insert-only)                     | Less widely known; requires explanation in design reviews   |

> ⚠️ **Important limitation:** if Ravi's band changed in March and again in April and he bought nothing in between, the March band is **never recorded anywhere**. Type 5 records the profile only **at the moments facts happen**, plus the current one. If you need every profile change, add a profile history table (Type 4 history meaning) or use Type 2.

---

## 10. Real-world applications

1. **Retail / e-commerce customer demographics**: age band, income band and loyalty band at purchase time vs today.
2. **Banking**: credit score band and balance band at loan application vs current, for risk portfolio reporting.
3. **Telecom**: usage band (data GB/month) and ARPU band at recharge time vs current, for plan targeting.
4. **Insurance**: risk band at policy purchase vs current, for renewal pricing.
5. **Marketing segmentation (RFM)**: recency/frequency/monetary segment at campaign time vs now, for campaign effectiveness.
6. **HR analytics**: performance band and salary band at promotion time vs current.

---

## 11. Check your understanding

**Conceptual**
1. Why is it called Type **5**? Which two types does it combine?
2. Which meaning of Type 4 does Type 5 build on: the history table or the mini-dimension?
3. In Type 5, where does the **history** of a customer's profile live, and where does the **current** profile live?
4. Why is `dim_profile` never updated or deleted from, only inserted into?

**Using the worked example**
5. After Run 2, why does P1 still exist even though Ravi moved to P3?
6. Kavya is new in Run 2. Why wasn't a new profile row created for her?
7. In Report 1, Ravi's January sale counts under 5-10L, but in Report 2 it counts under 10-20L. Explain why both are "correct".
8. Arjun buys nothing in Run 3, but his income band changes to 10-20L. Which tables change, and how?

**Code-level**
9. What goes wrong if Step 3 (fact load) runs **before** Step 2 (customer MERGE)?
10. A customer arrives with `income_band = NULL`. What happens in the current script, and how would you fix it?
11. Why does `dim_profile` have a `UNIQUE (income_band, credit_band)` constraint even though the load uses `NOT EXISTS`?
12. A January sale for Ravi arrives late, in the June batch. Which `profile_key` does the current script give it? Is that correct?

**Design thinking**
13. Ravi's band changes in March and again in April, and he buys nothing in between. Can Type 5 tell you his March band? What would you add if the business needs it?
14. A team wants to put exact `annual_income` (not a band) in the mini-dimension. What would you tell them?
15. When would you choose plain Type 2 on the customer dimension instead of Type 5?
