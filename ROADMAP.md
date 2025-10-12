# MAGPIE Algorithm Visualization Video Roadmap

## Project Goal

Create a series of **3-5 educational YouTube videos** (15-25 minutes each) demonstrating the evolution from naive/brute-force Scrabble move generation to state-of-the-art algorithms. Each video covers multiple related optimizations (10-20 total algorithms) with visual proof of improvement and cumulative performance gains.

## Algorithm Inventory

We have **~15-20 distinct optimizations** to visualize:

**Foundation (Algorithms 1-3)**
1. Brute force permutation generation
2. Linear word list search (O(n))
3. Sorted list + binary search (O(log n))

**Structural Improvements (Algorithms 4-7)**
4. Cross-set pre-computation
5. Anchor detection
6. Left-part generation
7. Right-part generation

**Data Structure Revolution (Algorithms 8-10)**
8. Trie/prefix tree
9. GADDAG/KWG (bidirectional trie)
10. Node packing and memory optimization

**Advanced Pruning (Algorithms 11-15)**
11. Shadow playing (super-leave)
12. Extension set filtering
13. Equity-based pruning
14. Leave value adjustment (KLV)
15. Best-move-found early termination

**Endgame Optimizations (Algorithms 16-18)**
16. Word maps (WMP)
17. Dense board hash lookup
18. Exhaustive endgame solver

**Plus**: Cross-check computation, rack cross-set caching, move recording strategies, etc.

## Current Status

✅ **Phase 0**: Naive move generation implemented (Algorithms 1-3)
✅ **Phase 1**: Binary search validation working
🔄 **Phase 2**: Trace logging infrastructure (word lookup complete, move gen partial)
⏳ **Phase 3**: Video production toolchain

---

## Video Series Outline (3-5 Videos, 15-25 min each)

### Video 1: "From Brute Force to Structure" (18-20 min)
**Covers Algorithms 1-7** (Foundation + Structural Improvements)

**Story Arc**: Start impossibly slow, end with respectable performance

**Part 1: The Naive Baseline (4 min)**
- Algorithm 1-2: Brute force permutation + linear search
- Visual: Scrolling through 279,076 words repeatedly
- Metric: 5+ minutes for "AEINRST" on empty board
- Lesson: "Sometimes the obvious solution is unusable"

**Part 2: Binary Search (3 min)**
- Algorithm 3: Sort once, binary search forever
- Visual: Split screen comparison, pointer animation
- Metric: 6000x speedup (87k → 18 comparisons per word)
- Lesson: "Preprocessing can pay massive dividends"

**Part 3: Cross-Sets (4 min)**
- Algorithm 4: Pre-compute valid letters per square
- Visual: Board with cross-set overlays, pruning visualization
- Metric: 60-80% reduction in positions tried
- Lesson: "Constraints are your friend"

**Part 4: Anchors (4 min)**
- Algorithms 5-7: Anchor detection + left/right generation
- Visual: Highlight valid attachment points, generation flow
- Metric: 225 positions → 20-40 anchors
- Lesson: "Focus your effort where it matters"

**Cumulative Result**: 5+ minutes → ~5 seconds (60,000x speedup so far)

---

### Video 2: "The GADDAG Revolution" (15-18 min)
**Covers Algorithms 8-10** (Data Structure Revolution)

**Story Arc**: Show how the right data structure changes everything

**Part 1: The Trie Awakening (5 min)**
- Algorithm 8: Prefix trees for word validation
- Visual: Animated tree traversal vs list scanning
- Metric: O(word_length) validation instead of O(log dictionary_size)
- Compare: Binary search (18 comparisons) → Trie (7 steps for "RETINAS")
- Lesson: "Structure enables algorithms"

**Part 2: The GADDAG Insight (6 min)**
- Algorithm 9: Bidirectional word graph
- Visual: Show forward/backward word representations
- Key insight: One structure for both left and right extensions
- Real example: Building "RETINAS" from anchor "I"
- Lesson: "Clever encoding eliminates redundancy"

**Part 3: Implementation Details (4 min)**
- Algorithm 10: Node packing and memory optimization
- Visual: Bit-level structure breakdown
- Show 32-bit node format: arc pointer, letter, flags
- Memory comparison: 279k words → compact graph
- Lesson: "Production systems need production engineering"

**Cumulative Result**: 5 seconds → ~50 milliseconds (100x faster again)

---

### Video 3: "Advanced Pruning Techniques" (20-22 min)
**Covers Algorithms 11-15** (Advanced Pruning)

**Story Arc**: Avoid work you don't need to do

**Part 1: Shadow Playing (5 min)**
- Algorithm 11: Super-leave pre-computation
- Visual: Ghost tiles showing maximum possible score
- Metric: Prune 50%+ of anchors before generation
- Lesson: "A good estimate beats perfect precision"

**Part 2: Extension Sets (4 min)**
- Algorithm 12: Filter by rack compatibility
- Visual: Venn diagram of extension set ∩ rack
- Show early rejection when no overlap
- Lesson: "Check compatibility before committing"

**Part 3: Equity-Based Pruning (4 min)**
- Algorithm 13: Stop when best is good enough
- Visual: Anchor heap with equity thresholds
- Show heap extraction stopping mid-process
- Lesson: "Perfection is the enemy of good enough"

**Part 4: Leave Values (5 min)**
- Algorithm 14: Static leave evaluation (KLV)
- Visual: Rack tiles color-coded by synergy
- Show score vs equity rankings diverging
- Real example: "Playing QU together vs separately"
- Lesson: "Think beyond the current move"

**Part 5: Move Recording Strategies (3 min)**
- Algorithm 15: Best-move-found termination
- Quick comparison of MOVE_RECORD_ALL vs MOVE_RECORD_BEST
- Lesson: "Know when you're done"

**Cumulative Result**: 50ms → ~5ms (10x faster, production-ready)

---

### Video 4 (Optional): "Endgame Mastery" (12-15 min)
**Covers Algorithms 16-18** (Endgame Optimizations)

**When to create**: If audience engagement is high, make this a deep dive

**Part 1: The Endgame Problem (3 min)**
- Board is 60%+ filled, combinatorial explosion
- Standard generation struggles with density
- Setup: Why we need a different approach

**Part 2: Word Maps (5 min)**
- Algorithm 16-17: Hash-based late-game lookup
- Visual: Board density threshold triggering WMP
- Show hash construction and lookup
- Metric: 10-100x speedup for dense boards

**Part 3: Exhaustive Solving (4 min)**
- Algorithm 18: Perfect endgame play
- When possible, when practical
- Visual: Minimax tree for final 2-4 tiles

**Lesson**: "Different problems need different tools"

---

### Video 5 (Optional): "The Complete Picture" (18-20 min)
**Recap + Deep Dives + Real Examples**

**When to create**: Series finale after Videos 1-3 (or 1-4)

**Part 1: The Journey (5 min)**
- Montage: 5 minutes → 5 milliseconds
- Show cumulative speedup graph
- Algorithm activation sequence on single example

**Part 2: Real Game Example (8 min)**
- Play through actual game position
- Show each optimization activating
- Pause to explain "why this fired now"
- Live comparison: naive vs optimized side-by-side

**Part 3: Implementation Reality (5 min)**
- Discuss MAGPIE codebase
- Show actual KWG/KLV file formats
- Memory usage, initialization time
- Engineering tradeoffs

**Lesson**: "Great systems are built from great parts"

---

## Technical Implementation Plan

### Phase 2: Complete Trace Logging (Current)

**Week 1-2: Move Generation Tracing**
- [ ] Add logging to `naive_recursive_gen()` (the actual function used)
- [ ] Log tile placements with word_so_far and remaining rack
- [ ] Log word validation with results
- [ ] Test with various positions (empty, mid-game, endgame)

**Week 3: Enhanced Events**
- [ ] Cross-set logging (position, allowed letters)
- [ ] Anchor logging (position, direction, left extension length)
- [ ] Rack permutation summary (at anchor start)
- [ ] Shadow play logging (max equity per anchor)

---

### Phase 3: Video Production Toolchain

**Week 4-5: Python Infrastructure**
- [ ] JSONL parser (line-by-line streaming)
- [ ] Event aggregation (group by anchor, by turn)
- [ ] Data structures for visualization state
- [ ] CGP parser for board state

**Week 6-7: Manim Basics**
- [ ] Board renderer (15×15 grid, bonus squares)
- [ ] Tile placement animation
- [ ] Rack display
- [ ] Text overlays (counters, labels)

**Week 8-9: First Video (Binary Search)**
- [ ] Script and storyboard
- [ ] Manim scenes:
  - Split-screen comparison
  - Binary search pointer animation
  - Comparison counter
  - Speedup graph
- [ ] Narration recording
- [ ] Final edit and publish

---

### Phase 4: Video Production (Ongoing)

**Cadence**: 1 video every 6-8 weeks (given 15-25 min length with multiple algorithms)
**Order**: Videos 1 → 2 → 3, then decide on 4-5 based on audience response

**Per-Video Workflow** (for 15-25 min video covering 4-7 algorithms):
1. **Script** (1 week): Write narration for all parts, plan visual flow
2. **Capture traces** (2-3 days): Generate JSONL for each algorithm demo
3. **Implement visualizations** (2-3 weeks): Manim scenes for 4-7 different algorithms
4. **Record narration** (2-3 days): High-quality audio, multiple takes
5. **Edit and render** (1 week): Assemble parts, transitions, Final Cut Pro
6. **Publish** (1 day): Upload, thumbnail, description, community post

**Estimated total per video**: 5-7 weeks of work

---

## Required Data/Positions

### Empty Board Positions
- 2-tile rack: "AT" (simple, few moves)
- 3-tile rack: "ARE" (moderate, ~10 moves)
- 7-tile rack: "AEINRST" (complex, hundreds of moves)

### Mid-Game Positions
- Sparse board (20% filled): Show anchor detection
- Dense board (60% filled): Show WMP activation
- Endgame (90% filled): Show pruning effectiveness

### Edge Cases
- 1-tile rack: Playthrough moves
- Blank handling: Show unblanking
- Cross-check failures: Show pruning

---

## Tools and Technologies

### Development
- **Language**: C (MAGPIE core)
- **Build**: Make
- **Version Control**: Git + GitHub

### Tracing
- **Format**: JSONL (newline-delimited JSON)
- **Output**: Line-buffered for real-time viewing
- **Flags**: `-tracemovegen`, `-tracewordlookup`

### Visualization
- **Primary**: Manim Community Edition (Python)
- **Prototyping**: Python + Pillow (quick iteration)
- **Alternative**: p5.js (web demos)

### Video Production
- **Animation**: Manim
- **Editing**: Final Cut Pro / DaVinci Resolve
- **Audio**: Logic Pro / Audacity
- **Rendering**: FFmpeg

---

## Success Metrics

### Technical
- ✅ Trace logging captures all relevant algorithm states
- ✅ JSONL format is parseable and complete
- ✅ Manim produces smooth, accurate visualizations
- ✅ Performance numbers match actual benchmarks

### Educational
- 📊 Viewers understand the "why" behind each optimization
- 📊 Complexity analysis is visually clear (O(n) vs O(log n))
- 📊 Real-world impact is quantified (speedup factors)
- 📊 Code examples are minimal but illustrative

### Production
- 📊 3-5 core videos completed
- 📊 Consistent quality and pacing (15-25 min each)
- 📊 Clear progression: simple → complex
- 📊 Re-usable visualization components

---

## Future Extensions

### Beyond the Core Series
- **Deep Dives**: Detailed explanations of KWG structure, leave calculation, endgame solver
- **Comparisons**: MAGPIE vs Quackle vs Elise vs Maven
- **Variants**: Super Scrabble, other board sizes, different lexicons
- **Advanced Topics**: Monte Carlo simulation, equity calculation, rack tracking

### Interactive Components
- **Web Demos**: p5.js visualizations embedded in blog posts
- **Code Repositories**: Simplified reference implementations
- **Jupyter Notebooks**: Interactive algorithm exploration
- **Visualization Tools**: Standalone utilities for trace analysis

---

## Milestones

- [x] **M0**: Naive move generation working (Oct 2025)
- [x] **M1**: Binary search validation working (Oct 2025)
- [x] **M2**: Word lookup tracing complete (Oct 2025)
- [ ] **M3**: Move generation tracing complete (Nov 2025)
- [ ] **M4**: Python parser and Manim basics (Dec 2025)
- [ ] **M5**: Video 1 published - "Brute Force to Structure" (Jan 2026)
- [ ] **M6**: Video 2 published - "The GADDAG Revolution" (Feb 2026)
- [ ] **M7**: Video 3 published - "Advanced Pruning" (Mar 2026)
- [ ] **M8**: Optional Videos 4-5 (audience-dependent) (Apr-May 2026)
- [ ] **M9**: Core series complete (May 2026)

---

## Notes

- **Keep it incremental**: Each video builds on previous ones
- **Show, don't tell**: Visualizations > code dumps
- **Quantify everything**: Numbers make improvements concrete
- **Maintain authenticity**: Use real MAGPIE code, not toy examples
- **Educational focus**: Clarity over completeness
