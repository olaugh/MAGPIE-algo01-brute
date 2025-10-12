#include "trace.h"

#include "io_util.h"
#include "string_util.h"
#include <stdio.h>
#include <stdlib.h>

// Global trace file handles
FILE *g_movegen_trace_file = NULL;
FILE *g_word_lookup_trace_file = NULL;

void trace_init(const char *movegen_path, const char *word_lookup_path) {
  // Close any existing trace files first
  trace_close();

  // Open movegen trace file if path provided
  if (!is_string_empty_or_null(movegen_path)) {
    g_movegen_trace_file = fopen(movegen_path, "we");
    if (!g_movegen_trace_file) {
      log_fatal("Failed to open movegen trace file: %s", movegen_path);
    }
    // Use line buffering for better real-time viewing
    // Ignore setvbuf return value - failure is non-critical
    (void)setvbuf(g_movegen_trace_file, NULL, _IOLBF, 0);
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
}

bool trace_movegen_enabled(void) { return g_movegen_trace_file != NULL; }

bool trace_word_lookup_enabled(void) {
  return g_word_lookup_trace_file != NULL;
}
