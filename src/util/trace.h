#ifndef TRACE_H
#define TRACE_H

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

// Global trace file handles
extern FILE *g_movegen_trace_file;
extern FILE *g_word_lookup_trace_file;

// Initialize trace files from file paths
void trace_init(const char *movegen_path, const char *word_lookup_path,
                int tile_log_frequency);

// Close and flush trace files
void trace_close(void);

// Check if tracing is enabled for each category
bool trace_movegen_enabled(void);
bool trace_word_lookup_enabled(void);

// Get nanosecond timestamp (relative to trace start)
uint64_t trace_get_timestamp_ns(void);

// Word lookup statistics tracking
void trace_word_lookup_increment_search(void);
void trace_word_lookup_increment_comparison(void);
void trace_word_lookup_print_stats_if_needed(void);

// Movegen tile placement tracking
void trace_movegen_set_tile_log_frequency(int frequency);
void trace_movegen_increment_cross_set_check(void);
void trace_movegen_record_tile_placement(int row, int col, char tile_char);
void trace_movegen_record_tile_unplacement(int row, int col);
void trace_movegen_print_tile_stats_if_needed(void);
void trace_movegen_print_tile_stats_for_anchor_end(void);
void trace_movegen_reset_tile_stats(void);

#endif // TRACE_H
