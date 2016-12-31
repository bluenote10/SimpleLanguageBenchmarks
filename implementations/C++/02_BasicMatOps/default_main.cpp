
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <chrono>
#include <cmath>


struct Matrix {
  int N;
  std::vector<double> data;

  Matrix operator+(Matrix const& that) const {
    Matrix result;
    result.N = N;
    result.data.resize(data.size());
    for (unsigned int i=0; i < data.size(); ++i) {
      result.data[i] = data[i] + that.data[i];
    }
    return result;
  }

  Matrix operator*(Matrix const& that) const {
    Matrix result;
    result.N = N;
    result.data.resize(data.size());
    for (int i=0; i < N; ++i) {
      for (int j=0; j < N; ++j) {
        double sum = 0;
        for (int k=0; k < N; ++k) {
          sum += data[i*N+k] * that.data[k*N+j];
        }
        result.data[i*N+j] = sum;
      }
    }
    return result;
  }

  double diag_sum() const {
    double sum = 0;
    for (int i=0; i < N; ++i) {
      sum += data[i*(N+1)];
    }
    return sum;
  }
};

Matrix read_csv(std::string filename) {

  std::vector<double> data;

  std::string cell;
  std::string line;

  std::ifstream filestream(filename);
  while (std::getline(filestream, line)) {
    std::stringstream linestream(line);
    while (std::getline(linestream, cell, ';')) {
      double value = std::stod(cell);
      data.push_back(value);
    }
  }

  return Matrix{(int) sqrt(data.size()), data};
}

int main(int argc, char** argv) {

  std::chrono::system_clock::time_point t1;
  std::chrono::system_clock::time_point t2;
  float elapsed_seconds;

  if (argc != 4) {
    exit(EXIT_FAILURE);
  }

  // read
  t1 = std::chrono::system_clock::now();
  Matrix m_A = read_csv(argv[2]);
  Matrix m_B = read_csv(argv[3]);
  t2 = std::chrono::system_clock::now();
  elapsed_seconds = std::chrono::duration<float>(t2 - t1).count();
  std::cout << elapsed_seconds << std::endl;

  // add
  t1 = std::chrono::system_clock::now();
  Matrix m_add = m_A + m_B;
  t2 = std::chrono::system_clock::now();
  elapsed_seconds = std::chrono::duration<float>(t2 - t1).count();
  std::cout << elapsed_seconds << std::endl;

  // multiply
  t1 = std::chrono::system_clock::now();
  Matrix m_mul = m_A * m_B;
  t2 = std::chrono::system_clock::now();
  elapsed_seconds = std::chrono::duration<float>(t2 - t1).count();
  std::cout << elapsed_seconds << std::endl;

  // print checks
  std::cout << m_add.diag_sum() << std::endl;
  std::cout << m_mul.diag_sum() << std::endl;
}

