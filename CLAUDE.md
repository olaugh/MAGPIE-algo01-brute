# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**This is a fork of MAGPIE** for educational and video production purposes.

MAGPIE (Macondo Accordant Game Program and Inference Engine) is a high-performance crossword game playing and analysis program written in C. It supports static move generation, Monte Carlo simulation, exhaustive inferences, autoplay, superleave generation, and exhaustive endgame solving. It uses the KWG (GADDAG-like) and KLV (leave value) data structures originally developed in wolges.

### Fork Purpose: Scrabble Algorithm Visualization for YouTube

This fork demonstrates the evolution from naive to state-of-the-art Scrabble move generation through ~10-20 incremental optimizations:

1. **Starting point**: Extremely naive/brute-force move finding (linear word list scanning)
2. **Incremental improvements**: Each optimization is implemented as a discrete step
3. **End goal**: Reach MAGPIE's production-quality move generation with shadow playing and WMP

**Video Production Workflow**:
- Use `bin/magpie autoplay` with `-printboards true -pretty true` to generate game visualizations
- Process autoplay output (board diagrams + CGP strings) into video frames
- Each video illustrates specific algorithmic improvements and their performance impact

The fork maintains compatibility with upstream MAGPIE data structures and formats while adding instrumentation, alternate move generation paths (e.g., `-luwords`, `-lswords`), and enhanced debugging output for educational content creation.

## Build System

The project uses Make with multiple build flavors controlled by the `BUILD` variable:

- **dev** (default): Development build with sanitizers (`-fsanitize=address,undefined,pointer-compare,pointer-subtract,leak`)
- **thread**: Thread sanitizer build (`-fsanitize=thread`)
- **release**: Optimized build (`-O3 -flto -march=native -DNDEBUG`)
- **vlg**: Valgrind-compatible build (no sanitizers)
- **cov**: Coverage build (`--coverage`)

### Common Build Commands

```bash
# Build main executable and tests (dev build)
make all

# Build release version
make magpie BUILD=release

# Build tests
make magpie_test

# Build with thread sanitizer
make magpie BUILD=thread

# Clean build artifacts
make clean
```

**Note**: You may see the warning `ld: warning: search path 'lib' not found` during linking. This is harmless and can be ignored.

### Configurable Board Dimensions

The board dimensions and rack size can be configured at compile time:

```bash
make magpie BOARD_DIM=15 RACK_SIZE=7    # Standard (default)
make magpie BOARD_DIM=21 RACK_SIZE=7    # Super variant
```

The default is `BOARD_DIM=15` and `RACK_SIZE=7`.

### Running Tests

```bash
# Run all unit tests (standard board)
./bin/magpie_test

# Run specific test
./bin/magpie_test <test_name>
```

Tests are located in `test/` and follow the pattern `*_test.c` and `*_test.h`.

### Data Files

Required lexicon and leave value data must be downloaded before running:

```bash
./download_data.sh        # Download KWG and KLV files
./convert_lexica.sh       # Convert text lexicons to KWG format
```

Data is stored in `data/` and `testdata/` directories.

## Code Architecture

### Directory Structure

- **src/compat/**: Platform compatibility layer (endianness, threading, malloc)
- **src/def/**: Type definitions and enums (suffixed with `_defs.h`)
- **src/ent/**: Core entity data structures (Board, Game, Player, Rack, KWG, KLV, WMP)
- **src/impl/**: Algorithm implementations (move_gen, simmer, inference, autoplay, endgame)
- **src/str/**: String formatting and parsing utilities
- **src/util/**: General utilities (string_util, io_util, math_util, fileproxy)
- **cmd/**: Command-line entry point
- **test/**: Unit tests

### Key Data Structures

#### KWG (GADDAG)
The KWG (originally from wolges) is a GADDAG-like structure for fast word lookups. Each node is a 32-bit packed integer containing:
- Tile/letter information
- Arc index (pointer to children)
- Flags for end-of-list and accepting state

See `src/ent/kwg.h` and https://github.com/andy-k/wolges/blob/main/details.txt

#### KLV (Leave Values)
The KLV structure stores pre-calculated leave values for rack evaluations. It includes:
- A KWG structure for leaves
- Word counts per node
- Float values for each leave

See `src/ent/klv.h`

#### WMP (Word Map)
Word map structure for fast move generation on positions with many tiles on the board. Includes linear and hash-based lookups.

See `src/ent/wmp.h` and `src/impl/wmp_move_gen.h`

#### Game State
The `Game` structure (src/ent/game.h) is the central state container:
- Contains `Board`, `Bag`, two `Player` objects, and `LetterDistribution`
- Supports backup/restore for move search
- Tracks game variant, bingo bonus, consecutive scoreless turns

#### Board Representation
The `Board` (src/ent/board.h) maintains four sub-boards:
- One pair for each direction (horizontal/vertical)
- One pair for each cross index
- Each square contains: letter, cross sets, anchor status, bonus square info

#### Move Generation
Move generation (src/impl/move_gen.h) uses:
- Shadow playing for pruning unpromising moves early
- Anchor-based generation with left/right extensions
- Cross-set pre-computation for fast validation
- WMP-based generation for late-game positions with many tiles

#### PlayersData
The `PlayersData` structure manages per-player data:
- KWG (lexicon), KLV (leaves), WMP (wordmap)
- Move sorting and recording types
- Supports shared or per-player lexicons

### Move Generation Flow

1. **Load position** (gen_load_position): Initialize board state, rack, cross sets
2. **Shadow playing** (gen_shadow): Pre-compute highest possible scores per anchor
3. **Recursive generation**: For each anchor, generate valid plays using KWG traversal
4. **Recording**: Moves are recorded based on sort type (equity/score) and record type (best/all)

### Move Generation Implementation Notes

**Shadow Playing and Extension Sets**
- Shadow playing (src/impl/move_gen.c:2301) calculates highest possible scores per anchor by simulating plays
- Relies on KWG `left_extension_set` and `right_extension_set` for pruning
- If implementing non-KWG move generation (e.g., word list validation), shadow playing must be bypassed
- Without valid extension sets, `shadow_start()` exits early (line 2027), causing anchors to not be added to the heap

**Anchor Continuation and Incomplete Racks**
- When continuing through an anchor in `go_on()`, the code checks `anchor_right_extension_set & rack_cross_set` (line ~823-824 in standard recursive_gen)
- This optimization prevents exploration when the rack can't possibly form valid continuations
- **Critical edge case**: With incomplete racks (< RACK_SIZE tiles), playthrough moves where `tiles_played=0` at the anchor rely entirely on this extension set check
- If implementing alternative move generation without extension sets, this check must be removed or bypassed
- Example failure: With rack "L" and existing "A" on board, move "AL" fails if the extension set check prevents continuation past the anchor

**Board Orientation and Transposition**
- Vertical moves (dir=1) use transposed board coordinates
- `board_copy_row_cache()` handles the transposition automatically
- When dir=1, "row" refers to the original column, "col" refers to the original row
- Anchor detection and cross-set calculation work the same for both orientations after transposition

**Testing Move Generation Changes**
- Always test with **incomplete racks** (1-3 tiles) as well as full racks (7 tiles)
- Test both empty boards and complex endgame positions
- Compare output against KWG-based generation using identical CGP positions
- Use `-lswords true` or `-luwords true` flags to test alternative generation paths
- Pay special attention to playthrough scenarios where tiles must be placed adjacent to existing tiles

### Simulation and Inference

- **Simulation** (src/impl/simmer.h): Monte Carlo tree search with configurable plies and stopping conditions
- **Inference** (src/impl/inference.h): Exhaustive rack inference based on opponent moves
- **Autoplay** (src/impl/autoplay.h): Self-play with game pairs and double-sided tile drawing to reduce variance

### Equity System

Equity values are stored as fixed-point integers (scaled by 1000 via `EQUITY_RESOLUTION`) throughout the codebase. Use `equity_to_double()` and `double_to_equity()` for conversions (src/ent/equity.h). See the "Score/Equity Format" section below for details.

## Code Quality Tools

### Static Analysis

```bash
./cppcheck.sh         # Run cppcheck
./tidy.sh             # Run clang-tidy (requires clang-tidy-18)
python3 format.py     # Check clang-format (requires clang-format-20)
python3 find_circ_deps.py  # Check for circular dependencies
```

### Code Formatting

**Important**: Before committing code, always check and fix formatting with clang-format-20:

```bash
python3 format.py     # Check formatting issues
clang-format-20 -i <file>  # Format specific file in-place
```

The project uses clang-format-20 for consistent code style. All code must be formatted before committing to pass CI checks.

**Best Practice for Claude Code**: After writing or modifying C code, run `python3 format.py` to check for formatting issues. Common formatting issues include:
- Line length violations (>80 characters)
- Function parameter alignment
- Binary operator placement (operators at end of line vs beginning)
- Indentation of continued expressions

If `format.py` shows differences, apply the formatting changes immediately before committing. This prevents CI failures and reduces noise in pull requests.

**Tip**: Look for patterns like:
```c
// Often needs reformatting:
int result = some_long_function_name(argument1, argument2,
    argument3);  // Wrong alignment

// Correct after clang-format:
int result =
    some_long_function_name(argument1, argument2, argument3);
```

### Static Analysis (clang-tidy)

**Important**: Anticipate and fix common clang-tidy warnings before committing:

**1. Missing Headers (misc-include-cleaner)**
- Always `#include <stdio.h>` when using FILE, fopen, fclose, fprintf, setvbuf
- Check that all used types/functions have their headers directly included
- Don't rely on transitive includes

**2. Ignored Return Values (cert-err33-c)**
- Functions like `fprintf`, `fclose`, `setvbuf` have return values that must be handled
- If the return value is truly non-critical, cast to void: `(void)fprintf(...)`
- Add a comment explaining why it's safe to ignore: `// Ignore fprintf return - trace logging is non-critical`

**3. File Descriptor Flags (android-cloexec-fopen)**
- Use `fopen(path, "we")` instead of `fopen(path, "w")` to set O_CLOEXEC
- The 'e' flag prevents file descriptors leaking to child processes

**Common Pattern for Trace/Debug Logging:**
```c
// Correct: cast to void and explain why
// Ignore fprintf return value - trace logging is non-critical
(void)fprintf(trace_file, "{\"type\":\"event\",\"value\":%d}\n", value);

// Correct: use 'e' flag for O_CLOEXEC
FILE *f = fopen(path, "we");
if (!f) {
  log_fatal("Failed to open file: %s", path);
}

// Ignore setvbuf return - line buffering failure is non-critical
(void)setvbuf(f, NULL, _IOLBF, 0);
```

### CI Pipeline

GitHub Actions runs:
- cppcheck static analysis
- clang-tidy static analysis (see above for common issues)
- clang-format verification (see Code Formatting section)
- Circular dependency check
- Unit tests (standard and super board)

All checks must pass before merging.

## Common Development Patterns

### Error Handling
Use `ErrorStack` for propagating errors. Check with `error_stack_is_empty()` after operations that may fail.

### Memory Management
- Use `malloc_or_die()`, `calloc_or_die()` for allocations that must succeed
- All major structures have `*_create()` and `*_destroy()` functions
- Game state supports `game_backup()` / `game_unplay_last_move()` for search

### String Utilities
- Use `string_duplicate()` for safe string copying
- `split_string_by_*()` functions for parsing

### File I/O
- `fileproxy.h` provides platform-independent file operations
- `data_filepaths.h` manages data file locations
- Use `stream_from_filename()` with ErrorStack for safe file opening

## Testing Conventions

- Test files follow `*_test.c` / `*_test.h` naming
- Use `test_util.h` for common test utilities
- Tests include both unit tests and integration tests (e.g., autoplay_test, endgame_test)
- Test constants defined in `test_constants.h`

## Performance Considerations

- Move generation is highly optimized with shadow playing and cross-set pruning
- Use release build for performance testing: `make magpie BUILD=release`
- Board dimension affects performance significantly; most operations are O(BOARD_DIM²)
- KWG lookups are cache-friendly with prefetching hints

## UCGI Mode

MAGPIE supports UCGI (Universal Crossword Game Interface) mode for asynchronous command processing:

```bash
./bin/magpie set -mode ucgi
```

In UCGI mode, commands run asynchronously in the background, and the `stop` command halts ongoing operations.

## CGP Format

Crossword Game Position (CGP) format specifies a game state:

```
cgp <board> <racks> <scores> <consecutive_zeros>
```

Example empty board:
```
cgp 15/15/15/15/15/15/15/15/15/15/15/15/15/15/15 / 0/0 0
```

See src/impl/cgp.h for parsing and src/str/game_string.h for formatting.

### CGP Output in Board Displays

For debugging convenience, CGP representations are automatically included when displaying boards:

- **`show` command**: Displays the board with CGP at the bottom
- **`autoplay` with `-printboards true`**: Each board snapshot includes a CGP line

This allows you to easily copy/paste the exact game state to reproduce positions for debugging or testing.

Example output from autoplay with `-pretty true -printboards true`:
```
=== Game Pair 1, Game 1, Turn 5 ===
[board diagram]

CGP: 15/15/15/7STEARIN/15/15/15/15/15/15/15/15/15/15/15 ABCDEFG/XYZ 42/35 0 lex CSW21; ld english;
```

## Testing Move Generation with the Binary

You can test move generation interactively using the `magpie` binary with CGP positions. This is useful for verifying move generation behavior and debugging specific scenarios.

### Basic Usage

```bash
./bin/magpie <<'EOF'
cgp 15/15/15/15/15/15/15/15/15/15/15/15/15/15/15 AAAAAAA/ 0/0 0 -lex CSW21 -ld english -s1 score -s2 score
gen -numplays 5
EOF
```

This command:
1. Loads an empty board with rack AAAAAAA
2. Sets the lexicon to CSW21 and letter distribution to English
3. Sets move sort type to `score` for both players
4. Generates up to 5 moves

### Testing Linear/Brute-Force Move Generation

This fork includes naive/brute-force move generation implementations for educational comparison and benchmarking:

```bash
./bin/magpie <<'EOF'
cgp 15/15/15/15/15/15/15/15/15/15/15/15/15/15/15 AEINRST/ 0/0 0 -lex CSW21 -ld english -luwords true -s1 score -s2 score
gen -numplays 10
EOF
```

**Move Generation Options** (for comparing algorithm approaches):
- **`-luwords true`**: Linear unsorted word list (O(n) lookup per check) - most naive
- **`-lswords true`**: Linear sorted word list (O(log n) binary search) - first optimization
- **WMP**: Word map enabled by default when available - optimized for late-game positions
- **KWG/GADDAG**: Default recursive generation - production SOTA algorithm

**Precedence order** (src/impl/move_gen.c:2183-2200):
1. Wordsmog mode (if enabled)
2. WMP (takes precedence over linear methods for equivalence testing)
3. Linear word lists (sorted_words or unsorted_words)
4. KWG recursive generation (default)

These options allow side-by-side performance comparisons to illustrate algorithmic improvements for video content.

### Common Options

- **-lex <lexicon>**: Specify lexicon (CSW21, NWL23, etc.)
- **-ld <distribution>**: Letter distribution (english, catalan, etc.)
- **-s1 <sort>**, **-s2 <sort>**: Move sort type for each player (`equity` or `score`)
- **-r1 <record>**, **-r2 <record>**: Move record type for each player (`best` or `all`)
- **-luwords <bool>**: Enable linear unsorted word list (O(n) lookup - very slow)
- **-lswords <bool>**: Enable linear sorted word list (O(log n) binary search - has known bugs on complex boards)
- **-numplays <n>**: Maximum number of moves to generate

### Score/Equity Format

Equity values are stored internally as fixed-point integers scaled by 1000 (`EQUITY_RESOLUTION = 1000` in src/def/equity_defs.h), but **displayed to users as decimal numbers**:

- **Internal**: `4000` (raw integer)
- **User output**: `4.000` (via `equity_to_double()` or `string_builder_add_equity()`)
- **Example**: A 54-point play (with 50-point bingo bonus) is stored as `54000` but displayed as `54.000`

Use conversion functions from src/ent/equity.h:
- `equity_to_double()` - convert to double for display/calculations
- `double_to_equity()` - convert from double to internal representation
- `equity_to_int()` - convert to integer (only if value is a whole number)

Recent debug code may occasionally display raw scaled integers for internal diagnostics, but all standard user-facing output uses the conversion functions to show proper decimal values.

### Example Positions

Empty board with common rack:
```bash
cgp 15/15/15/15/15/15/15/15/15/15/15/15/15/15/15 AEINRST/ 0/0 0 -lex CSW21 -ld english
```

Mid-game position:
```bash
cgp 4AUREOLED3/11O3/11Z3/10FY3/10A4/10C4/10I4/7THANX3/10GUV2/15/15/15/15/15/15 AHMPRTU/ 177/44 0 -lex CSW21 -ld english
```

### Testing Positions from Autoplay Output

When running `autoplay` with `-printboards true`, each board display includes a CGP line. You can copy this CGP to reproduce and debug specific positions:

**Step 1: Run autoplay and capture output**
```bash
./bin/magpie autoplay games 2 -gp true -seed 1337 -lex CSW21 -lswords true -threads 1 -printboards true > output.txt
```

**Step 2: Find a problematic position in the output**
```
=== Game Pair 2, Game 2, Turn 31 ===
   A B C D E F G H I J K L M N O   -> Player 1                 II        370
   ... [board diagram] ...

CGP: 1hEDONIC3MILT/VETO2SHUNTED2/1WANE2APO1HERB/3GERM6YA/3SNEE2GO1FUD/5WE1FANGA2/3QIS1TABOURS1/2LI2VAX2NOIR/13TE/10OYEZ1/10R4/6PAlUDIC2/7LIROT3/4JAKE7/15 L/II 495/370 0 lex CSW21; ld english;
```

**Step 3: Test the position with gen command**

Copy the CGP string and test move generation:
```bash
./bin/magpie << 'EOF'
cgp 1hEDONIC3MILT/VETO2SHUNTED2/1WANE2APO1HERB/3GERM6YA/3SNEE2GO1FUD/5WE1FANGA2/3QIS1TABOURS1/2LI2VAX2NOIR/13TE/10OYEZ1/10R4/6PAlUDIC2/7LIROT3/4JAKE7/15 L/II 495/370 0 -lex CSW21 -ld english -s1 score -s2 score
gen -numplays 10
EOF
```

**Step 4: Compare different move generation strategies**
```bash
# Test with default KWG (should work)
./bin/magpie << 'EOF'
cgp [paste CGP here] -lex CSW21 -ld english -s1 score -s2 score
gen -numplays 10
EOF

# Test with sorted words (has known bug - only works on empty boards)
./bin/magpie << 'EOF'
cgp [paste CGP here] -lex CSW21 -ld english -s1 score -s2 score -lswords true
gen -numplays 10
EOF
```

This workflow allows you to:
- Isolate specific problematic positions from autoplay
- Compare move generation across different algorithms
- Debug why certain positions aren't finding moves
- Verify algorithm equivalence

### Debugging Tips

- Add printf statements in move_gen.c to trace execution
- Use `lldb ./bin/magpie` to debug interactively
- Check cross-set generation with print statements in game_gen_classic_cross_set()
- Verify anchor placement with debug output in board_update_all_anchors()
