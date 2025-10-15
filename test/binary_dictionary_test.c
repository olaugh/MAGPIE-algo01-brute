#include "binary_dictionary_test.h"

#include "../src/ent/dictionary_word.h"
#include "../src/ent/letter_distribution.h"
#include "../src/ent/players_data.h"
#include "../src/impl/config.h"
#include "../src/util/string_util.h"
#include "test_util.h"
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>

static DictionaryWord create_word_from_string(const LetterDistribution *ld,
                                              const char *human_readable_word) {
  DictionaryWord word;
  int length = (int)string_length(human_readable_word);
  ld_str_to_mls(ld, human_readable_word, false, word.word, length);
  word.length = (uint8_t)length;
  return word;
}

void word_lookup_binary_search(void) {
  // Create Config with CSW21 dictionary and enable loading sorted words
  // This will load words from KWG (which outputs in sorted order)
  // and sort them explicitly
  Config *config = config_create_or_die("set -lex CSW21 -lswords true");

  const LetterDistribution *ld = config_get_ld(config);
  const PlayersData *players_data = config_get_players_data(config);

  // Get the sorted word list from players data
  const DictionaryWordList *word_list =
      players_data_get_sorted_words(players_data, 0);

  // Verify the list is actually sorted
  assert(dictionary_word_list_is_sorted(word_list) == true);

  // Create test words
  DictionaryWord brute = create_word_from_string(ld, "BRUTE");
  DictionaryWord aa = create_word_from_string(ld, "AA");
  DictionaryWord zzzs = create_word_from_string(ld, "ZZZS");
  DictionaryWord olaugh = create_word_from_string(ld, "OLAUGH");

  // Perform checks with binary search
  assert(dictionary_word_list_contains_word_binary_search(word_list, &brute) ==
         true);
  assert(dictionary_word_list_contains_word_binary_search(word_list, &aa) ==
         true);
  assert(dictionary_word_list_contains_word_binary_search(word_list, &zzzs) ==
         true);
  assert(dictionary_word_list_contains_word_binary_search(word_list, &olaugh) ==
         false);

  // Cleanup
  config_destroy(config);
}
