
#include <vector>
#include <unordered_map>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <chrono>


int main(int argc, char** argv) {

  std::chrono::system_clock::time_point t1;
  std::chrono::system_clock::time_point t2;
  float elapsed_seconds;
 
  if (argc != 2) {
    exit(EXIT_FAILURE);
  }

  std::string stop_chars = " \n";
  
  // convert to string
  t1 = std::chrono::system_clock::now();
  std::ifstream t(argv[1]);
  std::stringstream buffer;
  buffer << t.rdbuf();
  std::string text = buffer.str();
  t2 = std::chrono::system_clock::now();
  elapsed_seconds = std::chrono::duration<float>(t2 - t1).count();
  std::cout << elapsed_seconds << std::endl;

  // split
  t1 = std::chrono::system_clock::now();
  std::vector<std::string> words;
  std::string cur_word = "";
  for (size_t i = 0; i < text.length(); ++i) {
    bool break_word = false;
    for (size_t j = 0; j < stop_chars.length(); ++j) {
      if (text[i] == stop_chars[j]) {
        break_word = true;
      }
    }
    if (break_word) {
      words.push_back(cur_word);
      cur_word = "";
    } else {
      cur_word += text[i];
    }
  }
  t2 = std::chrono::system_clock::now();
  elapsed_seconds = std::chrono::duration<float>(t2 - t1).count();
  std::cout << elapsed_seconds << std::endl;

  // build hash map
  t1 = std::chrono::system_clock::now();
  std::unordered_map<std::string, int> counts;
  for (auto& word : words) {
    auto it = counts.find(word);
    if (it != counts.end()) {
      ++(it->second);
    } else {
      counts[word] = 0;
    }
  }
  t2 = std::chrono::system_clock::now();
  elapsed_seconds = std::chrono::duration<float>(t2 - t1).count();
  std::cout << elapsed_seconds << std::endl;

  // print checks
  std::cout << counts.size() << std::endl;
  size_t word_checksum = 0;
  for (auto& iter : counts) {
    word_checksum += iter.second;
  }
  std::cout << word_checksum << std::endl;
}

