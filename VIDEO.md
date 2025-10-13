# Video Production Guide

This document outlines technical specifications and best practices for creating educational videos about MAGPIE's algorithm optimizations for YouTube.

## YouTube Upload Specifications

### Recommended Video Format

**Container Format**: MP4 (MPEG-4 Part 14)
- Most compatible with YouTube's processing pipeline
- Fast upload and processing times
- Good balance of quality and file size

**Video Codec**: H.264 (AVC)
- Industry standard, universally supported
- YouTube recommendation for best quality
- Alternative: H.265 (HEVC) for smaller files, but less compatible

**Audio Codec**: AAC-LC (Advanced Audio Coding)
- Stereo or mono
- Sample rate: 48kHz (preferred) or 44.1kHz
- Bitrate: 128 kbps (mono) or 384 kbps (stereo)

### Resolution and Frame Rate

**Resolution Options** (16:9 aspect ratio):
- **1080p (1920×1080)** - Recommended for algorithm visualizations
- 1440p (2560×1440) - Optional for extra clarity on complex diagrams
- 4K (3840×2160) - Overkill for code/algorithm content, huge file sizes

**Frame Rate**:
- **30fps** - Standard for educational content, smooth enough for animations
- 60fps - Only needed if showing rapid real-time interactions (probably not necessary)

**Bitrate** (for H.264 @ 1080p30):
- **8-12 Mbps** - Good quality for screen captures and animations
- 15-20 Mbps - High quality if lots of fine detail (code, small text)

### Color Space

- **Color Space**: sRGB (standard RGB)
- **Color Primaries**: BT.709
- **Pixel Format**: YUV 4:2:0 (yuv420p)

### File Size Limits

- **Maximum file size**: 256 GB
- **Maximum length**: 12 hours
- For our 15-25 minute videos at 1080p30/10Mbps: ~1.5 GB per video (well within limits)

## FFmpeg Export Command

Here's a recommended FFmpeg command for exporting final videos:

```bash
ffmpeg -i input.mov \
  -c:v libx264 \
  -preset slow \
  -crf 18 \
  -pix_fmt yuv420p \
  -profile:v high \
  -level 4.2 \
  -movflags +faststart \
  -c:a aac \
  -b:a 192k \
  -ar 48000 \
  output.mp4
```

**Explanation**:
- `-c:v libx264`: Use H.264 video codec
- `-preset slow`: Better compression (slower encoding, smaller file)
- `-crf 18`: Constant Rate Factor - visually lossless quality (18-23 is good range)
- `-pix_fmt yuv420p`: Compatible pixel format
- `-profile:v high -level 4.2`: High profile for better compression, Level 4.2 for 1080p
- `-movflags +faststart`: Enable streaming (video starts playing before full download)
- `-c:a aac`: AAC audio codec
- `-b:a 192k`: Audio bitrate
- `-ar 48000`: 48kHz audio sample rate

## Manim Rendering Settings

When rendering animations with Manim, use these settings:

```python
# In scene file or command line
manim -pqh scene.py SceneName  # High quality (1080p)
manim --format=mp4 --media_dir ./output scene.py SceneName
```

**Manim config.cfg settings**:
```ini
[CLI]
resolution = 1920,1080
frame_rate = 30
pixel_format = rgba
codec_name = libx264
video_codec = h264
```

## Text and Code Readability

### Font Sizes (for 1080p)

**On-screen text**:
- **Titles/Headings**: 48-72pt
- **Body text**: 32-40pt
- **Code**: 28-36pt (monospace: Fira Code, JetBrains Mono, or SF Mono)
- **Small labels/annotations**: 24-28pt

**Test on mobile**: YouTube mobile app is common viewing platform - test that text is readable on a phone screen.

### Code Display Best Practices

- **Syntax highlighting**: Use consistent color scheme (e.g., Monokai, Dracula, or GitHub Dark)
- **Line length**: Keep code lines under 60 characters to avoid horizontal scrolling in frame
- **Line spacing**: 1.3-1.5x for readability
- **Highlight changes**: Use yellow background or arrows to draw attention to specific lines

## Video Structure Template

For each 15-25 minute algorithm video:

### Opening (30-60 seconds)
- Title card with video number and algorithm name
- Brief hook: "In this video, we'll speed up move generation by 100x"

### Introduction (1-2 minutes)
- Current state: performance baseline
- Problem: what's slow and why
- Solution preview: what optimization we'll implement

---

## First Video Structure (20 minutes)

### Detailed Breakdown with Hook Strategy

**0:00-0:10 - Title Screen (10 seconds)**
```
Bold title card: "I Made a Scrabble AI 60,000x Faster"
Subtitle: "Part 1: From Brute Force to Binary Search"
```

**0:10-0:45 - Hook: Show the Payoff IMMEDIATELY (35 seconds)**

This is the most critical part of the video. Show the extreme result before explaining anything.

**Script example:**
```
"Watch this."

[Split screen appears]
Left: "Naive Implementation" - running timer visible
Right: "Optimized" - running timer visible

[Both start running]
Left: 0:03... 0:05... 0:10... 0:30... 1:00... (keeps counting)
Right: DONE in 0.05 seconds ✓

"Same word list. Same board. Same tiles."
"60,000 times faster."
[Brief pause for impact]
"Here's how I did it."
```

**Why this works:**
- Visual proof in first 30 seconds (YouTube retention critical)
- Creates curiosity: "How is that possible?"
- Establishes stakes: the naive version is painfully slow
- Promises value: you'll learn the technique

**What NOT to do in the hook:**
- ❌ "In this video, I'm going to show you..." (boring)
- ❌ Long intro about yourself/project (nobody cares yet)
- ❌ "Before we start, let me explain Scrabble rules..." (context comes later)
- ❌ Slow build-up without payoff preview (viewers leave)

**0:45-3:00 - The Problem Setup (~2 minutes)**
- "I'm building a Scrabble AI from scratch..."
- Show empty board, explain the challenge
- "Here's the naive approach: generate every possible tile arrangement..."
- Visualize brute force with animation
- "Then check each one against 279,000 valid words..."
- Show scrolling through word list (emphasize the tedium)
- **First benchmark result**: "5 minutes 23 seconds. Completely unusable."

**3:00-8:30 - Optimization #1: Binary Search (~5.5 minutes)**

*Part A: The Insight (1 minute)*
- "The problem: checking words linearly, one by one"
- Show visual of scanning sequentially
- "But if we sort the word list once..."
- "We can use binary search"

*Part B: Algorithm Explanation (2 minutes)*
- Animated binary search visualization
- Show the halving process with pointer movements
- Comparison counter: 279,076 → 18 comparisons
- Math: O(n) vs O(log n) with actual numbers

*Part C: Implementation (1.5 minutes)*
- Quick code walkthrough (key parts only)
- Highlight comparison function
- Show sort call and binary search loop

*Part D: Results - FIRST PAYOFF (1 minute)*
- **"Let's run it..."**
- Show terminal with timing
- **Reveal: 87 seconds** (down from 5+ minutes)
- "3.7x faster already, but we can do better"
- Celebration music sting/visual effect

**8:30-15:00 - Optimization #2 & #3: Structural Improvements (~6.5 minutes)**

*Teaser*: "Binary search helped, but we're still doing too much work..."

*Part A: Cross-Sets (2 minutes)*
- Show board with existing tiles
- "Not every square can accept every letter"
- Visualize cross-checks with overlays
- Show pruning in action

*Part B: Anchor Detection (2 minutes)*
- "We don't need to try all 225 board positions"
- Highlight valid anchor points
- Show reduction: 225 → ~40 positions

*Part C: Combined Results - SECOND PAYOFF (1.5 minutes)*
- **"Now let's see the difference..."**
- Run the optimized version
- **Reveal: 5 seconds** (down from 87 seconds)
- "17x faster than binary search alone"
- "60,000x faster than where we started"

*Part D: Why It Matters (1 minute)*
- "5 seconds is playable. 5 minutes is not."
- Side-by-side comparison montage
- Graph showing cumulative speedups

**15:00-18:30 - The Bigger Picture (~3.5 minutes)**

*Part A: What We Learned (1.5 minutes)*
- Recap three key ideas:
  1. Binary search beats linear search
  2. Pre-compute constraints (cross-sets)
  3. Focus work on productive areas (anchors)

*Part B: What's Next (1 minute)*
- Tease next optimization (GADDAG/Trie)
- "5 seconds → 50 milliseconds"
- "Another 100x speedup"
- Quick flash of trie diagram

*Part C: The Journey Ahead (1 minute)*
- Show roadmap with 15-20 optimizations
- "From 5 minutes to 5 milliseconds"
- "Million-fold improvement"

**18:30-20:00 - Call to Action (~1.5 minutes)**
- Subscribe for part 2
- GitHub link
- Credits and technical notes

---

## Pacing Principles

**Never go more than 5 minutes without a concrete payoff:**
- 0:30 - Hook payoff (see the 60,000x result)
- 8:30 - First optimization payoff (binary search results)
- 15:00 - Final payoff (combined 60,000x speedup)

**Visual variety every 20-30 seconds:**
- Switch between code, animations, board views, terminal output

**Music cues:**
- Upbeat during explanations
- Tension building during benchmark runs
- Celebration sting at reveals

**Breathing room:**
- After complex explanations, pause 2-3 seconds with visuals only
- Let numbers sink in (show timer for 2-3 seconds after reveal)

### Deep Dive (10-18 minutes)
- Algorithm explanation with visual diagrams
- Code walkthrough (highlight key sections, not full implementation)
- Visualization of algorithm in action using Manim + trace data
- Comparison: before/after with real timing data

### Results (1-2 minutes)
- Performance metrics (speedup factor, absolute times)
- Complexity analysis (O(n) → O(log n))
- When this optimization matters most

### Closing (30-60 seconds)
- Recap: what we learned
- Teaser: next video's optimization
- Call to action: like, subscribe, check GitHub repo

## Asset Organization

### Directory Structure

```
videos/
├── 01-binary-search/
│   ├── script.md              # Narration script
│   ├── manim/
│   │   ├── scenes.py          # Manim animation code
│   │   └── output/            # Rendered clips
│   ├── traces/
│   │   ├── linear.jsonl       # Trace data for linear search
│   │   └── binary.jsonl       # Trace data for binary search
│   ├── assets/
│   │   ├── diagrams/          # SVG/PNG illustrations
│   │   └── audio/             # Narration recordings
│   └── final/
│       ├── rough_cut.mp4      # Assembly edit
│       └── final.mp4          # Deliverable
├── 02-cross-sets/
│   └── ...
└── shared/
    ├── intro_template.mp4     # Reusable intro animation
    ├── outro_template.mp4     # Reusable outro with social links
    └── music/                 # Background music (if used)
```

## Workflow Summary

1. **Generate traces**: Run MAGPIE with trace logging flags
2. **Write script**: Narration and timing in Markdown
3. **Create Manim scenes**: Algorithm visualizations from trace data
4. **Record narration**: High-quality audio (ideally in quiet room with decent mic)
5. **Assemble in editor**: Combine Manim renders, code overlays, narration
6. **Export**: Use FFmpeg settings above for final MP4
7. **Upload to YouTube**: Add title, description, tags, thumbnail
8. **Publish**: Schedule or publish immediately

## Quality Checklist

Before uploading:
- [ ] Video is 1080p30, H.264/AAC in MP4 container
- [ ] All text is readable on mobile device
- [ ] Audio is clear, no background noise or clipping
- [ ] Timing: No dead air longer than 1-2 seconds
- [ ] Animations are smooth (no stuttering or dropped frames)
- [ ] Code examples compile and are accurate
- [ ] Performance numbers match actual benchmark data
- [ ] Transitions between sections are smooth
- [ ] Thumbnail is eye-catching (1280×720, text readable at small size)

## YouTube Metadata Template

**Title Format**:
`Scrabble AI #[N]: [Optimization Name] - [Result] ([Series Name])`

Example: `Scrabble AI #2: Binary Search - 100x Faster Word Lookups (MAGPIE Series)`

**Description Template**:
```
In this video, we [brief one-sentence description of optimization].

⏱️ Timestamps:
0:00 - Introduction
1:23 - The Problem
3:45 - Algorithm Explanation
8:12 - Implementation
12:34 - Results & Benchmarks
14:56 - Wrap-up

🔗 Resources:
- GitHub Repository: https://github.com/[user]/MAGPIE-algo01-brute
- ROADMAP.md: [link to roadmap]
- Trace logging code: [link to specific commit]

📊 Performance:
Before: [X] seconds per move generation
After: [Y] seconds per move generation
Speedup: [Z]x faster

🎯 Next Video: [Brief teaser of next optimization]

#scrabble #algorithms #optimization #visualization #education
```

**Tags** (max 500 characters):
`scrabble, algorithms, optimization, computer science, AI, game playing, move generation, data structures, binary search, performance, visualization, educational, programming, C programming, algorithm analysis`

## Notes

- **Music**: If using background music, ensure it's royalty-free (YouTube Audio Library, Epidemic Sound, or similar)
- **Transitions**: Keep transitions simple - crossfades and cuts are fine, avoid gimmicky effects
- **Pacing**: Algorithm content can be dense - allow pauses for viewers to process
- **Accessibility**: Consider adding captions (YouTube auto-captions are okay but manual is better)
- **Engagement**: First 10 seconds are critical for viewer retention - start with a compelling visual or statement

## References

- [YouTube Recommended Upload Encoding Settings](https://support.google.com/youtube/answer/1722171)
- [FFmpeg H.264 Encoding Guide](https://trac.ffmpeg.org/wiki/Encode/H.264)
- [Manim Documentation](https://docs.manim.community/)
