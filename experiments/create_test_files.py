import os

def create_test_files():
  """Membuat file tes untuk demo celah keamanan"""

  os.makedirs("test_security", exist_ok=True)

  files_to_create = [
    "test_security/important_data.txt",
    "test_security/user_databaes.db",
    "test_security/config.json",
    "test_security/secret_key.txt",
  ]
    
    
  for file_path in files_to_create:
    with open(file_path, "w") as f:
      f.write(f"IMPORTANT DATA - DO NOT DELETE\n")
      f.write(f"File: {file_path}\n")
      f.write(f"This file contains critical system data!\n")
      f.write("=" * 50 + "\n")
    print(f"Created : {file_path}")
    
    print(f"\n📁 Created {len(files_to_create)} test files in test_security/")
    print("🚨 These files will be deleted by malicious code!")


if __name__ == "__main__":
  create_test_files()

    
  