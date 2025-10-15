# Current Task: Trace Logging for Video Visualization

## Status: ✅ Phase 1 Complete - Word Lookup Tracing Working

## Summary

Implemented JSONL trace logging infrastructure to capture internal algorithm states for educational video production. Successfully logs binary and linear search operations with detailed comparison tracking.

## What's Working

### 1. Trace Infrastructure ✅
- Created `src/util/trace.{c,h}` with global file handles
- Two independent trace streams: movegen and word lookup
- Command-line flags: `-tracemovegen <path>` and `-tracewordlookup <path>`
- Line-buffered output for real-time viewing
- Automatic open/close in `impl_move_gen()`

### 2. Word Lookup Tracing ✅
- **Binary Search**: Logs left/mid/right bounds for each comparison
- **Linear Search**: Logs index and comparison result for each word
- Both log final `search_complete` with total comparisons and outcome
- Output format: JSONL (one JSON per line)

**Example Output:**
```jsonl
{"type":"comparison","method":"binary","left":0,"mid":139538,"right":279076,"cmp_result":12}
{"type":"comparison","method":"binary","left":0,"mid":69768,"right":139537,"cmp_result":3}
{"type":"search_complete","method":"binary","found":true,"comparisons":18}
```

### 3. Move Generation Tracing (Partial) ⚠️
- Added to `exhaustive_gen_recursive()` but this function isn't used by `-lswords`/`-luwords`
- Need to add to `naive_recursive_gen()` (the actual function called with word lists)

**Implemented Events:**
- `tile_placed`: Logs tile, word_so_far, remaining_rack at each placement
- `move_found`: Logs word, position, tiles_played, leave, leave_value, best_score, best_equity

## Current Limitations

1. **Move generation trace is empty** when using `-lswords` because:
   - `naive_recursive_gen` is used (not `exhaustive_gen_recursive`)
   - Logging was added to the wrong function
   - Need to instrument `naive_recursive_gen` instead

2. **Linear search is very slow** on full racks:
   - Timeout with 7-tile rack on empty board
   - Works fine with 2-3 tile racks
   - Binary search works well for all rack sizes

## Usage

```bash
# Test with small rack and binary search (WORKS)
./bin/magpie << 'EOF'
cgp 15/15/15/15/15/15/15/15/15/15/15/15/15/15/15 ARE/ 0/0 0 \
  -lex CSW21 -ld english -lswords true -s1 score -s2 score \
  -tracemovegen movegen.jsonl -tracewordlookup wordlookup.jsonl
gen -numplays 5
EOF

# Word lookup trace will have ~600 lines showing binary searches
# Move generation trace is currently empty (needs fix)
```

## Files Modified

- `src/util/trace.{c,h}` - NEW: Trace infrastructure
- `src/impl/config.c` - Added flags and initialization
- `src/ent/dictionary_word.c` - Instrumented binary/linear search
- `src/impl/move_gen.c` - Instrumented exhaustive_gen_recursive (wrong function!)
- `.gitignore` - Added `*.jsonl`

## Next Steps

### Immediate (To Complete Phase 1)
1. **Add logging to `naive_recursive_gen()`** at line ~666 in move_gen.c
   - Log tile placements in the main loop
   - Log word validation results
   - This is the function actually called with `-lswords`/`-luwords`

### Phase 2: Enhanced Logging
2. **Add cross-set events** to show pruning
3. **Add anchor events** to show anchor detection
4. **Add rack permutation summary** at start of each anchor

### Phase 3: Video Production
5. **Write Python parser** for JSONL traces
6. **Create Manim visualizations** for:
   - Binary vs linear search comparison
   - Rack permutation exploration
   - Leave value calculations
7. **Produce first video**: "From Linear to Binary Search"

## Video Workflow

```
MAGPIE -tracemovegen → movegen.jsonl
         -tracewordlookup → wordlookup.jsonl
           ↓
Python parser (read JSONL line-by-line)
           ↓
Manim animation renderer
           ↓
MP4 video (algorithm visualization)
```

## Code Locations

- Trace infrastructure: `src/util/trace.{c,h}`
- Config integration: `src/impl/config.c:810` (trace_init call)
- Word lookup logging: `src/ent/dictionary_word.c:183-261`
- Move gen logging (needs fix): `src/impl/move_gen.c:895-994`
- **Target for next work**: `src/impl/move_gen.c:668` (`naive_recursive_gen`)

## Testing Notes

- Word lookup trace verified working with 613 lines generated
- Binary search shows proper O(log n) behavior (~18 comparisons for 279k words)
- Linear search would show O(n) behavior but too slow for full racks
- Move generation trace empty due to wrong function instrumented
