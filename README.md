# Optimistic Concurrency Control
Transactions executed with optimistic concurrency control are divided into
three phases:

1. a __read phase__ during which a transaction reads and writes values to a
   local cache,
2. a __validation phase__ during which a transaction checks to see if its
   execution is consistent with a serialization of concurrently executing
   transactions, and
3. a __write phase__ during which a transaction copies its cached writes into
   the database (provided it passed validation).

A transaction is assigned a timestamp when it enters its validation phase. The
logic to validate transaction `j` is as follows:

- for all transactions `i` < `j`:
    - if the write set of `i` overlaps the read set of `j`:
        - transaction `i` must finish its write phase before transaction `j`
          starts its read phase
    - elif the write set of `i` overlaps the write set of `j`:
        - transaction `i` must finish its write phase before transaction `j`
          starts its write phase
    - else:
        - the two transactions can overlap arbitrarily

This repo includes a toy implementation of the OCC algorithms presented in [1].

- \[1]: Kung, Hsiang-Tsung, and John T. Robinson. "On optimistic methods for
  concurrency control." _ACM Transactions on Database Systems (TODS)_ 6.2
  (1981): 213-226.
