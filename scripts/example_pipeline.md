# Example pipeline

## Input
A user asks a business question, for example:
- list hosts with their software
- which hosts run SQL Server in production
- list Red Hat hosts and their network interfaces

## Stage 1: retrieval
Retrieve relevant chunks from:
- core entities
- relationship map
- query patterns
- SQL generation policy
- generated schema catalog

## Stage 2: relationship planning
Ask the model to produce an internal plan containing:
- user intent
- candidate tables
- trusted join path
- fallback join path
- required filters
- join confidence

## Stage 3: SQL generation
Generate read-only SQL only after the join plan is complete.

## Stage 4: validation
Before execution, validate:
- every referenced table exists
- every referenced column exists
- discriminator filters are present where needed
- heuristic joins are marked low confidence internally

## Stage 5: execution
Run SQL through MCP.

## Stage 6: retry logic
If execution fails:
- inspect live schema again
- prefer narrower exploration queries
- do not invent a new join based only on a plausible column name
