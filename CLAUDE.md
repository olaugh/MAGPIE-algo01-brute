# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MAGPIE (Macondo Accordant Game Program and Inference Engine) is a high-performance crossword game playing and analysis program written in C. It supports static move generation, Monte Carlo simulation, exhaustive inferences, autoplay, superleave generation, and exhaustive endgame solving. It uses the KWG (GADDAG-like) and KLV (leave value) data structures originally developed in wolges.

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
./run u

# Run all unit tests (21x21 super board)
./run u 21

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

### Simulation and Inference

- **Simulation** (src/impl/simmer.h): Monte Carlo tree search with configurable plies and stopping conditions
- **Inference** (src/impl/inference.h): Exhaustive rack inference based on opponent moves
- **Autoplay** (src/impl/autoplay.h): Self-play with game pairs and double-sided tile drawing to reduce variance

### Equity System

Equity values are stored as fixed-point integers (scaled by 100) throughout the codebase. Use `equity_to_double()` and `double_to_equity()` for conversions (src/ent/equity.h).

## Code Quality Tools

### Static Analysis

```bash
./cppcheck.sh         # Run cppcheck
./tidy.sh             # Run clang-tidy (requires clang-tidy-18)
python3 format.py     # Check clang-format (requires clang-format-20)
python3 find_circ_deps.py  # Check for circular dependencies
```

### CI Pipeline

GitHub Actions runs:
- cppcheck static analysis
- clang-tidy static analysis
- clang-format verification
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
