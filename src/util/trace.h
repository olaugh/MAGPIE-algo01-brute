#ifndef TRACE_H
#define TRACE_H

#include <stdbool.h>
#include <stdio.h>

// Global trace file handles
extern FILE *g_movegen_trace_file;
extern FILE *g_word_lookup_trace_file;

// Initialize trace files from file paths
void trace_init(const char *movegen_path, const char *word_lookup_path);

// Close and flush trace files
void trace_close(void);

// Check if tracing is enabled for each category
bool trace_movegen_enabled(void);
bool trace_word_lookup_enabled(void);

#endif // TRACE_H
