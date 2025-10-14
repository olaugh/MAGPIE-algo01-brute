#!/bin/bash

# Play a full game with seed 1337 and capture movegen traces with heatmaps
echo "=========================================="
echo "Per-Anchor Mode (recommended for videos)"
echo "=========================================="
echo "Playing full game with seed 1337..."
echo "This will generate movegen_peranchor.jsonl with one heatmap per anchor"
echo ""

./bin/magpie <<'EOF'
autoplay games 1 -seed 1337 -lex CSW24 -ld english -s1 score -s2 score -lswords true -threads 1 -tracemovegen movegen_peranchor.jsonl -tilelogfreq -1
EOF

echo ""
echo "=== Per-Anchor Trace Stats ==="
echo "File size:"
ls -lh movegen_peranchor.jsonl

echo ""
echo "Total lines:"
wc -l movegen_peranchor.jsonl

echo ""
echo "Event type breakdown:"
echo "  position_loaded:"
grep -c '"type":"position_loaded"' movegen_peranchor.jsonl
echo "  tile_snapshot:"
grep -c '"type":"tile_snapshot"' movegen_peranchor.jsonl
echo "  square_letter_counts:"
grep -c '"type":"square_letter_counts"' movegen_peranchor.jsonl
echo "  move_found:"
grep -c '"type":"move_found"' movegen_peranchor.jsonl

echo ""
echo "=========================================="
echo "Frequency Mode (for detailed analysis)"
echo "=========================================="
echo "Playing full game with seed 1337..."
echo "This will generate movegen_freq.jsonl with tile placement heatmaps (frequency 50)"
echo ""

./bin/magpie <<'EOF'
autoplay games 1 -seed 1337 -lex CSW24 -ld english -s1 score -s2 score -lswords true -threads 1 -tracemovegen movegen_freq.jsonl -tilelogfreq 50
EOF

echo ""
echo "=== Frequency-Based Trace Stats ==="
echo "File size:"
ls -lh movegen_freq.jsonl

echo ""
echo "Total lines:"
wc -l movegen_freq.jsonl

echo ""
echo "=== Sample Events (Per-Anchor) ==="
echo ""
echo "Sample CGP (first position):"
grep '"type":"position_loaded"' movegen_peranchor.jsonl | head -1

echo ""
echo "Sample tile snapshot (showing current state):"
grep '"type":"tile_snapshot"' movegen_peranchor.jsonl | head -1

echo ""
echo "Sample square letter counts (first 3 non-empty):"
grep '"type":"square_letter_counts"' movegen_peranchor.jsonl | grep -v '"letter_counts":{}' | head -3

echo ""
echo "Sample move found (first 3 moves):"
grep '"type":"move_found"' movegen_peranchor.jsonl | head -3
