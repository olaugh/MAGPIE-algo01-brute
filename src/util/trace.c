#include "trace.h"

#include "io_util.h"
#include "string_util.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#ifdef __APPLE__
#include <sys/time.h>
#elif defined(__linux__)
#include <time.h>
#endif

// Global trace file handles
FILE *g_movegen_trace_file = NULL;
FILE *g_word_lookup_trace_file = NULL;

// Word lookup statistics
static uint64_t g_word_lookup_search_count = 0;
static uint64_t g_word_lookup_comparison_count = 0;
static uint64_t g_last_stats_print_count = 0;

// Movegen tile placement tracking
static int g_tile_log_frequency = 0; // 0 = log every placement
static uint64_t g_tile_placement_count = 0;
static uint64_t g_tile_last_log_count = 0;
static uint64_t g_cross_set_check_count = 0;
static char g_current_tiles[BOARD_DIM]; // Current tiles in the row
// Letter counts per square: [square_index][letter 'A'-'z']
// We use 'A'-'z' range to cover uppercase A-Z and lowercase a-z
#define LETTER_RANGE 58  // 'z' - 'A' + 1
static int g_letter_counts[BOARD_DIM][LETTER_RANGE];

// Get wall clock nanosecond timestamp
uint64_t trace_get_timestamp_ns(void) {
#ifdef __APPLE__
  struct timeval tv;
  gettimeofday(&tv, NULL);
  return (uint64_t)tv.tv_sec * 1000000000ULL + (uint64_t)tv.tv_usec * 1000ULL;
#elif defined(__linux__)
  struct timespec ts;
  clock_gettime(CLOCK_REALTIME, &ts);
  return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
#else
  // Fallback: no timestamp support
  return 0;
#endif
}

void trace_init(const char *movegen_path, const char *word_lookup_path,
                int tile_log_frequency) {
  // Close any existing trace files first
  trace_close();

  // Set tile log frequency
  g_tile_log_frequency = tile_log_frequency;

  // Open movegen trace file if path provided
  if (!is_string_empty_or_null(movegen_path)) {
    g_movegen_trace_file = fopen(movegen_path, "we");
    if (!g_movegen_trace_file) {
      log_fatal("Failed to open movegen trace file: %s", movegen_path);
    }
    // Use line buffering for better real-time viewing
    // Ignore setvbuf return value - failure is non-critical
    (void)setvbuf(g_movegen_trace_file, NULL, _IOLBF, 0);

    // Initialize tile placement tracking
    trace_movegen_reset_tile_stats();
  }

  // Open word lookup trace file if path provided
  if (!is_string_empty_or_null(word_lookup_path)) {
    g_word_lookup_trace_file = fopen(word_lookup_path, "we");
    if (!g_word_lookup_trace_file) {
      log_fatal("Failed to open word lookup trace file: %s", word_lookup_path);
    }
    // Use line buffering for better real-time viewing
    // Ignore setvbuf return value - failure is non-critical
    (void)setvbuf(g_word_lookup_trace_file, NULL, _IOLBF, 0);
  }
}

void trace_close(void) {
  // Print final stats if word lookup tracing was enabled
  if (g_word_lookup_trace_file && g_word_lookup_search_count > 0) {
    uint64_t ts_ns = trace_get_timestamp_ns();
    (void)fprintf(g_word_lookup_trace_file,
                  "{\"timestamp_ns\":%llu,\"type\":\"final_stats\","
                  "\"total_searches\":%llu,\"total_comparisons\":%llu,"
                  "\"avg_comparisons_per_search\":%.2f}\n",
                  (unsigned long long)ts_ns,
                  (unsigned long long)g_word_lookup_search_count,
                  (unsigned long long)g_word_lookup_comparison_count,
                  (double)g_word_lookup_comparison_count /
                      (double)g_word_lookup_search_count);
  }

  if (g_movegen_trace_file) {
    // Ignore fclose return value - we're cleaning up anyway
    (void)fclose(g_movegen_trace_file);
    g_movegen_trace_file = NULL;
  }
  if (g_word_lookup_trace_file) {
    // Ignore fclose return value - we're cleaning up anyway
    (void)fclose(g_word_lookup_trace_file);
    g_word_lookup_trace_file = NULL;
  }

  // Reset counters
  g_word_lookup_search_count = 0;
  g_word_lookup_comparison_count = 0;
  g_last_stats_print_count = 0;
}

bool trace_movegen_enabled(void) { return g_movegen_trace_file != NULL; }

bool trace_word_lookup_enabled(void) {
  return g_word_lookup_trace_file != NULL;
}

void trace_word_lookup_increment_search(void) { g_word_lookup_search_count++; }

void trace_word_lookup_increment_comparison(void) {
  g_word_lookup_comparison_count++;
}

void trace_word_lookup_print_stats_if_needed(void) {
  if (!g_word_lookup_trace_file) {
    return;
  }

  // Print stats every 1000 searches
  if (g_word_lookup_search_count - g_last_stats_print_count >= 1000) {
    uint64_t ts_ns = trace_get_timestamp_ns();
    uint64_t searches_since_last =
        g_word_lookup_search_count - g_last_stats_print_count;
    (void)fprintf(g_word_lookup_trace_file,
                  "{\"timestamp_ns\":%llu,\"type\":\"stats\","
                  "\"total_searches\":%llu,\"total_comparisons\":%llu,"
                  "\"searches_since_last\":%llu,"
                  "\"avg_comparisons_per_search\":%.2f}\n",
                  (unsigned long long)ts_ns,
                  (unsigned long long)g_word_lookup_search_count,
                  (unsigned long long)g_word_lookup_comparison_count,
                  (unsigned long long)searches_since_last,
                  (double)g_word_lookup_comparison_count /
                      (double)g_word_lookup_search_count);
    g_last_stats_print_count = g_word_lookup_search_count;
  }
}

// Movegen tile placement tracking
void trace_movegen_set_tile_log_frequency(int frequency) {
  g_tile_log_frequency = frequency;
}

void trace_movegen_increment_cross_set_check(void) {
  g_cross_set_check_count++;
}

void trace_movegen_reset_tile_stats(void) {
  g_tile_placement_count = 0;
  g_tile_last_log_count = 0;
  g_cross_set_check_count = 0;
  for (int i = 0; i < BOARD_DIM; i++) {
    g_current_tiles[i] = '.';
    for (int j = 0; j < LETTER_RANGE; j++) {
      g_letter_counts[i][j] = 0;
    }
  }
}

void trace_movegen_record_tile_placement(int row, int col, char tile_char) {
  (void)row; // Row is just for logging, not tracked in arrays
  if (col >= 0 && col < BOARD_DIM) {
    g_current_tiles[col] = tile_char;
    // Track which letter was placed in this square
    if (tile_char >= 'A' && tile_char <= 'z') {
      int letter_idx = tile_char - 'A';
      if (letter_idx >= 0 && letter_idx < LETTER_RANGE) {
        g_letter_counts[col][letter_idx]++;
      }
    }
  }
  g_tile_placement_count++;
}

void trace_movegen_record_tile_unplacement(int row, int col) {
  (void)row; // Row is just for logging, not tracked in arrays
  if (col >= 0 && col < BOARD_DIM) {
    g_current_tiles[col] = '.';
  }
}

// Helper function to output tile statistics
static void trace_movegen_output_tile_stats(void) {
  uint64_t ts_ns = trace_get_timestamp_ns();

  // First output a summary showing current state
  char current_state_str[BOARD_DIM + 1];
  for (int i = 0; i < BOARD_DIM; i++) {
    current_state_str[i] = g_current_tiles[i];
  }
  current_state_str[BOARD_DIM] = '\0';

  (void)fprintf(g_movegen_trace_file,
                "{\"timestamp_ns\":%llu,\"type\":\"tile_snapshot\","
                "\"placement_id\":%llu,\"cross_set_checks\":%llu,"
                "\"current_state\":\"%s\"}\n",
                (unsigned long long)ts_ns,
                (unsigned long long)g_tile_placement_count,
                (unsigned long long)g_cross_set_check_count, current_state_str);

  // Output one line per square showing letter distribution
  for (int square = 0; square < BOARD_DIM; square++) {
    // Build letter counts JSON object
    char letter_counts_str[1024]; // Enough for all letter counts
    int pos = 0;
    pos += snprintf(letter_counts_str + pos, sizeof(letter_counts_str) - pos,
                    "{");

    bool first = true;
    for (int letter_idx = 0; letter_idx < LETTER_RANGE; letter_idx++) {
      int count = g_letter_counts[square][letter_idx];
      if (count > 0) {
        char letter = 'A' + letter_idx;
        if (!first) {
          pos += snprintf(letter_counts_str + pos,
                          sizeof(letter_counts_str) - pos, ",");
        }
        pos += snprintf(letter_counts_str + pos,
                        sizeof(letter_counts_str) - pos, "\"%c\":%d", letter,
                        count);
        first = false;
      }
    }
    pos +=
        snprintf(letter_counts_str + pos, sizeof(letter_counts_str) - pos, "}");

    (void)fprintf(
        g_movegen_trace_file,
        "{\"timestamp_ns\":%llu,\"type\":\"square_letter_counts\","
        "\"placement_id\":%llu,\"square\":%d,\"current_tile\":\"%c\","
        "\"cross_set_checks\":%llu,\"letter_counts\":%s}\n",
        (unsigned long long)ts_ns, (unsigned long long)g_tile_placement_count,
        square, g_current_tiles[square],
        (unsigned long long)g_cross_set_check_count, letter_counts_str);
  }

  g_tile_last_log_count = g_tile_placement_count;
}

void trace_movegen_print_tile_stats_if_needed(void) {
  if (!g_movegen_trace_file) {
    return;
  }

  // If frequency is -1, skip frequency-based logging (only log at anchor end)
  if (g_tile_log_frequency == -1) {
    return;
  }

  // If frequency is 0, log every placement. Otherwise log every N placements
  bool should_log = (g_tile_log_frequency == 0) ||
                    (g_tile_placement_count - g_tile_last_log_count >=
                     (uint64_t)g_tile_log_frequency);

  if (should_log) {
    trace_movegen_output_tile_stats();
  }
}

void trace_movegen_print_tile_stats_for_anchor_end(void) {
  if (!g_movegen_trace_file) {
    return;
  }

  // Only output if we're in per-anchor mode (-1) or if there's been any activity
  if (g_tile_log_frequency == -1 ||
      g_tile_placement_count > g_tile_last_log_count) {
    trace_movegen_output_tile_stats();
  }
}
