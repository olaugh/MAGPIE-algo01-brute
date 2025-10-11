# MAGPIE Algorithm Visualization Video Roadmap

## Project Goal

Create a series of 10-20 educational YouTube videos demonstrating the evolution from naive/brute-force Scrabble move generation to state-of-the-art algorithms. Each video illustrates a discrete optimization step with visual proof of improvement.

## Current Status

✅ **Phase 0**: Naive move generation implemented
✅ **Phase 1**: Binary search word validation working
🔄 **Phase 2**: Trace logging infrastructure (word lookup complete, move gen partial)
⏳ **Phase 3**: Video production toolchain

---

## Video Series Outline

### Arc 1: From Brute Force to Binary Search (Videos 1-3)

#### Video 1: "The Naive Approach - How Bad Can It Be?"
**Algorithm**: Linear word list search
**Key Metrics**:
- ~87,000 comparisons per word check (avg)
- ~5+ minutes for 7-tile rack on empty board
- O(n) complexity visualization

**Visual Elements**:
- Scrolling word list with counter
- Rack permutation tree
- Time elapsed counter ticking up

**Lesson**: "Sometimes the straightforward solution is too slow"

---

#### Video 2: "Binary Search - The First Real Optimization"
**Algorithm**: Sorted word list + binary search
**Key Metrics**:
- ~18 comparisons per word check (avg for CSW21)
- ~5 seconds for 7-tile rack on empty board
- O(log n) complexity visualization

**Visual Elements**:
- Split screen: linear on left, binary on right
- Binary search pointer animation (left/mid/right)
- Comparison counter (87k vs 18)
- Speedup: ~6000x faster

**Lesson**: "Sorting once pays dividends forever"

---

#### Video 3: "Cross-Sets - Pruning the Search Space"
**Algorithm**: Cross-set pre-computation
**Key Metrics**:
- Reduces candidate positions by 60-80%
- Eliminates invalid placements before word checks

**Visual Elements**:
- Board grid with cross-set overlays
- Red X over invalid positions
- Green highlight on valid cross-check squares
- Counter showing placements attempted vs pruned

**Lesson**: "The best work is work you never do"

---

### Arc 2: Anchor-Based Generation (Videos 4-6)

#### Video 4: "Anchors - Where Valid Moves Must Touch"
**Algorithm**: Anchor detection
**Key Metrics**:
- Reduces search space from 225 positions to 20-40 anchors
- O(n²) → O(anchors × rack_size!)

**Visual Elements**:
- Empty board: show center square anchor
- Mid-game: highlight anchors next to existing tiles
- Animation of anchor detection sweep

**Lesson**: "Structure guides search"

---

#### Video 5: "Left Extensions and Prefix Filtering"
**Algorithm**: Left-part generation with KWG prefix checks
**Key Metrics**:
- Prunes 90%+ of invalid prefixes early
- No more checking full words that can't possibly exist

**Visual Elements**:
- Word tree showing valid prefixes
- Red X when prefix fails KWG check
- Comparison: naive tries "ZZZZZZZ", smart stops at "ZZ"

**Lesson**: "Fail fast, fail early"

---

#### Video 6: "The GADDAG - Reversible Word Graphs"
**Algorithm**: KWG/GADDAG structure
**Key Metrics**:
- Single data structure for left and right extensions
- O(1) prefix validity checking
- Memory-efficient node packing

**Visual Elements**:
- Animated GADDAG traversal
- Show bidirectional word representation
- Node structure breakdown

**Lesson**: "The right data structure changes everything"

---

### Arc 3: Advanced Optimizations (Videos 7-10)

#### Video 7: "Shadow Playing - Highest Possible Score"
**Algorithm**: Shadow/super-leave pre-computation
**Key Metrics**:
- Prunes 50%+ of anchors before full generation
- Avoids work when best move is already better

**Visual Elements**:
- Ghost tiles showing maximum possible score
- Anchor pruning animation
- Comparison counter: anchors explored vs skipped

**Lesson**: "A good estimate beats perfect precision"

---

#### Video 8: "Leave Values - Planning Ahead"
**Algorithm**: Static leave evaluation (KLV)
**Key Metrics**:
- Adjusts move scores by -5 to +5 points
- Dramatically changes move ordering

**Visual Elements**:
- Rack tiles color-coded by leave value
- Side-by-side: score vs equity rankings
- Before/after move order comparison

**Lesson**: "Your tiles matter as much as your points"

---

#### Video 9: "Word Maps - Endgame Acceleration"
**Algorithm**: WMP (word map) late-game optimization
**Key Metrics**:
- 10-100x speedup when board is 60%+ filled
- Hash-based word lookup

**Visual Elements**:
- Board density threshold visualization
- WMP activation trigger
- Speedup graph over game progress

**Lesson**: "Adapt your strategy to the situation"

---

#### Video 10: "Putting It All Together - State of the Art"
**Algorithm**: Full MAGPIE move generation pipeline
**Key Metrics**:
- From 5+ minutes to 5 milliseconds
- 60,000x speedup overall

**Visual Elements**:
- Replay first video's example with all optimizations
- Show each optimization activating in sequence
- Final performance comparison table

**Lesson**: "Great performance comes from many small wins"

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

**Cadence**: 1 video every 2-3 weeks
**Order**: Follow Arc 1 → Arc 2 → Arc 3 sequence

**Per-Video Workflow**:
1. **Script** (2-3 days): Write narration, plan visuals
2. **Capture traces** (1 day): Generate JSONL with appropriate positions
3. **Implement visualizations** (5-7 days): Manim scenes specific to this video
4. **Record narration** (1 day): High-quality audio
5. **Edit and render** (2-3 days): Final Cut Pro / DaVinci Resolve
6. **Publish** (1 day): Upload, thumbnail, description, community post

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
- 📊 10-20 videos completed
- 📊 Consistent quality across series
- 📊 Clear progression of complexity
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

- [x] **M0**: Naive move generation working (Nov 2024)
- [x] **M1**: Binary search validation working (Nov 2024)
- [x] **M2**: Word lookup tracing complete (Dec 2024)
- [ ] **M3**: Move generation tracing complete (Jan 2025)
- [ ] **M4**: Python parser and Manim basics (Feb 2025)
- [ ] **M5**: First video published (Mar 2025)
- [ ] **M6**: Arc 1 complete (Videos 1-3) (May 2025)
- [ ] **M7**: Arc 2 complete (Videos 4-6) (Aug 2025)
- [ ] **M8**: Arc 3 complete (Videos 7-10) (Dec 2025)
- [ ] **M9**: Full series published (Jan 2026)

---

## Notes

- **Keep it incremental**: Each video builds on previous ones
- **Show, don't tell**: Visualizations > code dumps
- **Quantify everything**: Numbers make improvements concrete
- **Maintain authenticity**: Use real MAGPIE code, not toy examples
- **Educational focus**: Clarity over completeness
