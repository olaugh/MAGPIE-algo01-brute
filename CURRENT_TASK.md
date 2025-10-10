# Current Task: Naive Recursive Move Generation with Binary Search

## Status: ✅ COMPLETE

## Summary

Successfully implemented naive recursive move generation that:
1. **Places tiles indiscriminately** without KWG prefix filtering
2. **Validates words** using binary or linear search against word lists
3. **Works with incomplete racks** (fewer than RACK_SIZE tiles)
4. **Supports both orientations** (horizontal and vertical)
5. **Matches KWG output** for all tested positions

## Implementation

### Files Modified
- `src/impl/move_gen.c` - Added three new functions:
  - `naive_recursive_gen()` (line ~666)
  - `naive_go_on()` (line ~779)
  - `naive_check_word_and_record()` (line ~737)

### Key Design Decisions

1. **No Extension Sets**: Unlike `recursive_gen`, we don't use `left_extension_set` or `right_extension_set` for filtering. We place tiles indiscriminately based only on cross-checks.

2. **Shadow Playing Bypass**: For word lists, we skip shadow playing entirely and add all anchors directly to the heap with `EQUITY_MAX_VALUE`.

3. **Anchor Continuation**: Removed the `anchor_right_extension_set` check that was preventing continuation through anchors with incomplete racks.

### Function Flow

```
shadow_by_orientation()
  └─> For each anchor (when using word lists):
        Add directly to anchor_heap (no shadow play)

gen_record_scoring_plays()
  └─> For each anchor from heap:
        naive_recursive_gen(col, ...)
          ├─> If square has letter: playthrough via naive_go_on()
          └─> If square empty: try each rack letter
                └─> naive_go_on(col, letter, ...)
                      ├─> Update strip, score, cross-scores
                      ├─> Check if word complete: naive_check_word_and_record()
                      │     ├─> Build word from strip (unblank letters)
                      │     ├─> Binary/linear search in word list
                      │     └─> If found: record_tile_placement_move()
                      ├─> Continue left: naive_recursive_gen(col-1, ...)
                      └─> Continue right: naive_recursive_gen(col+1, ...)
```

## Bugs Fixed

### Bug #1: Vertical Moves Not Generated
**Problem**: Vertical anchors were being detected but not added to the anchor heap.
**Root Cause**: Shadow playing uses KWG `anchor_left_extension_set` and `anchor_right_extension_set`, which are not valid for word list generation. With extension sets of 0, `shadow_start()` would exit early without setting `max_tiles_to_play`, causing `shadow_play_for_anchor()` to return without adding the anchor.
**Solution**: When using word lists, bypass shadow playing entirely in `shadow_by_orientation()`. Add all anchors directly to the heap with `EQUITY_MAX_VALUE`.

### Bug #2: Incomplete Rack Playthrough Failure
**Problem**: With a single-tile rack (e.g., just 'L'), moves like f14.AL failed where 'A' exists on the board and 'L' must be placed after it.
**Root Cause**: In `naive_go_on()` at line ~823, the condition to continue right through the anchor was:
```c
if ((gen->tiles_played != 0) ||
    (gen->anchor_right_extension_set & gen->rack_cross_set) != 0)
```
When playing through the anchor tile (tiles_played=0), it relied on `anchor_right_extension_set` which is a KWG-specific optimization not applicable to naive generation.
**Solution**: For naive generation, always allow continuing through the anchor (removed the extension set check).

## Testing Results

### Empty Board (2-tile rack)
```bash
cgp 15/.../15 AT/ 0/0 0 -lswords true
```
✅ Finds: 8g.AT, 8g.TA, 8h.AT, 8h.TA (4 moves + exchanges + pass)

### Complex Board (1-tile rack)
```bash
cgp 1hEDONIC3MILT/.../15 L/II 495/370 0 -lswords true
```
✅ Finds: f13.LA, f14.AL (matches KWG exactly)

## Key Insights

1. **Incomplete Racks Are the Edge Case**: The bugs only manifested with racks having fewer than RACK_SIZE (7) tiles. Full racks masked the extension set filtering issues.

2. **Extension Sets Are KWG-Specific**: The `left_extension_set` and `right_extension_set` are optimizations for KWG-based generation. They don't apply to naive generation with word lists.

3. **Shadow Playing Requires KWG**: Shadow playing calculates highest possible scores by simulating plays using the KWG. Without a valid KWG, shadow playing fails or produces incorrect results.

## Usage

```bash
# Naive generation with sorted word list (binary search)
./bin/magpie << 'EOF'
cgp <board> <racks> <scores> 0 -lex CSW21 -ld english -lswords true
gen -numplays 10
EOF

# Naive generation with unsorted word list (linear search)
./bin/magpie << 'EOF'
cgp <board> <racks> <scores> 0 -lex CSW21 -ld english -luwords true
gen -numplays 10
EOF
```

## Code Locations

- Naive generation entry: `src/impl/move_gen.c:2370` (in `gen_record_scoring_plays`)
- Main recursive function: `src/impl/move_gen.c:666` (`naive_recursive_gen`)
- Word validation: `src/impl/move_gen.c:737` (`naive_check_word_and_record`)
- Continuation logic: `src/impl/move_gen.c:779` (`naive_go_on`)
- Shadow bypass: `src/impl/move_gen.c:2135` (`shadow_by_orientation`)
- Anchor continuation fix: `src/impl/move_gen.c:836-843` (removed extension set check)

## Next Steps

This implementation is complete and ready for:
1. Performance benchmarking vs KWG generation
2. Integration into autoplay for algorithm comparison videos
3. Further optimizations (e.g., caching, pruning) as separate incremental steps
