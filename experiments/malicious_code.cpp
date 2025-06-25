// Malicious C++ code
const char* malicious_cpp_code = R"(
  #include <iostream>
  #include <fstream>
  #include <filesystem>
  #include <cstdlib>
  
  using namespace std;
  namespace fs = std::filesystem;
  
  int main() {
      cout << "Starting file system attack..." << endl;
      
      // Create malicious file
      ofstream malicious_file("HACKED_BY_USER.txt");
      malicious_file << "System has been compromised!" << endl;
      malicious_file << "All your files are belong to us!" << endl;
      malicious_file.close();
      
      // Try to delete files
      try {
          if (fs::exists("test_security")) {
              fs::remove_all("test_security");
              cout << "Deleted test_security directory!" << endl;
          }
      } catch (...) {
          cout << "Failed to delete directory" << endl;
      }
      
      // Normal program behavior to hide attack
      int a, b;
      cin >> a >> b;
      cout << a + b << endl;
      
      return 0;
  }
  )";