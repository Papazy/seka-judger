document.addEventListener('DOMContentLoaded', function(){

  // Inisiasi Ace Editor
  const editor = ace.edit("editor");
  editor.setTheme("ace/theme/monokai");
  editor.session.setMode("ace/mode/c_cpp");
  editor.setValue("#include <iostream> \nusing namespace std; \n\nint main(){ \n  int a,b; \n  cin >> a >> b; \n  cout << a + b << endl; \n  return 0;\n}\n\n")
  editor.setOptions({
    fontSize: "12px",
  })

  const languageSelect = document.getElementById("language");
  const testcasesContainer = document.getElementById("testcases-container");
  const addTestcaseButton = document.getElementById("add-testcase-btn");
  const resultContainer = document.getElementById("result-container");
  const runButton = document.getElementById("judge-btn");

  let testcaseCount = 0;


  // mengurutkan nomor test case
  function updateTestCaseNumbers(){
    const testCases = document.querySelectorAll(".test-case");
    testCases.forEach((testCase, index) => {
      const caseNumber = index + 1;
      const newId = `testcase-${caseNumber}`;

      // update id baru
      testCase.id = newId;

      // update judul test case
      const title = testCase.querySelector("h5");
      title.textContent = `Test Case ${caseNumber}`;

      // update id case tombol haspu
      const deleteBtn = testCase.querySelector(".delete-testcase-btn");
      deleteBtn.setAttribute("data-case-id", caseNumber);

      // update input dan output textarea id
      const inputTextarea = testCase.querySelector("textarea[id^='input-']");
      const outputTextarea = testCase.querySelector("textarea[id^='output-']");
      inputTextarea.id = `input-${caseNumber}`;
      outputTextarea.id = `output-${caseNumber}`;
    })

    // update jumlah test case
    testcaseCount = testCases.length;
  }

  // menambahkan test case baru
  function addTestCase(inputEx = "", outputEx = "") {
    if(!inputEx) inputEx = "";
    if(!outputEx) outputEx = "";
    testcaseCount++;
    const testcaseDiv = document.createElement("div");
    testcaseDiv.className = "test-case bg-gray-50 border border-gray-200 rounded-lg p-3";
    testcaseDiv.id = `testcase-${testcaseCount}`;
    testcaseDiv.innerHTML = `
      <div class="flex items-center justify-between mb-3">
        <h5 class="text-sm font-semibold text-gray-700 flex items-center">
          <i class="fas fa-flask mr-1 text-blue-400"></i>
          Test Case ${testcaseCount}
        </h5>
        <button class="delete-testcase-btn text-red-500 hover:text-red-700 hover:bg-red-50 p-1 rounded transition-colors duration-200" data-case-id="${testcaseCount}">
          <i class="fas fa-times text-xs"></i>
        </button>
      </div>
      <div class="space-y-2">
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Input</label>
          <textarea id="input-${testcaseCount}" rows="2" 
                    class="w-full text-xs p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    placeholder="Enter input data...">${inputEx}</textarea>
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Expected Output</label>
          <textarea id="output-${testcaseCount}" rows="2" 
                    class="w-full text-xs p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    placeholder="Enter expected output...">${outputEx}</textarea>
        </div>
      </div>
    `;
    testcasesContainer.appendChild(testcaseDiv);
  
    testcaseDiv.querySelector(".delete-testcase-btn").addEventListener("click", function(){
      const caseId = this.getAttribute("data-case-id")
      document.getElementById(`testcase-${caseId}`).remove();
      updateTestCaseNumbers();
    })
  }

  addTestcaseButton.addEventListener("click", function(){

    // dibungkus agar tidak mengirim event object
    addTestCase()
  });
  addTestCase("2 3", "5");

  // mengubah mode editor sesuai pilihan bahasa
  languageSelect.addEventListener("change", function(){
    if(this.value == "c" || this.value == "cpp"){
      editor.session.setMode("ace/mode/c_cpp");
    }else{
      editor.session.setMode("ace/mode/" + this.value);
    }
  })


  // fungsi mengirim data ke server

  // Fungsi untuk menampilkan loading state yang lebih menarik
function showLoadingState() {
  resultContainer.innerHTML = `
    <div class="flex flex-col items-center justify-center p-8 bg-blue-50 border border-blue-200 rounded-lg">
      <div class="relative">
        <!-- Spinner animasi -->
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-500"></div>
        <!-- Dots animasi -->
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="flex space-x-1">
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
          </div>
        </div>
      </div>
      <div class="mt-4 text-center">
        <h3 class="text-lg font-semibold text-blue-700">Judging Your Code</h3>
        <p class="text-blue-600 mt-1">Compiling and testing against test cases...</p>
        <div class="mt-2 text-sm text-blue-500">
          <span id="loading-dots">Please wait</span>
        </div>
      </div>
    </div>
  `;

  // Animasi dots loading
  let dotsCount = 0;
  const loadingInterval = setInterval(() => {
    const loadingDots = document.getElementById('loading-dots');
    if (loadingDots) {
      dotsCount = (dotsCount + 1) % 4;
      loadingDots.textContent = 'Please wait' + '.'.repeat(dotsCount);
    } else {
      clearInterval(loadingInterval);
    }
  }, 500);

  return loadingInterval;
}

// Modifikasi fungsi sendCodeToJudge
async function sendCodeToJudge(){
  const code = editor.getValue();
  const language = languageSelect.value;
  const testCases = [];

  const testCasesElements = document.querySelectorAll(".test-case");
  testCasesElements.forEach(testCase => {
    const input = testCase.querySelector("textarea[id^='input-']").value;
    const output = testCase.querySelector("textarea[id^='output-']").value;
    if(!input.trim() || !output.trim()){
      
    }else{

      testCases.push({
        input: input,
        expected_output: output
      })
    }
  })

  const payload = {
    code: code,
    language: language,
    test_cases: testCases
  }

  let loadingInterval;

  try{
    // Disable tombol run
    runButton.disabled = true;
    runButton.innerHTML = `
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
        Running...
      </div>
    `;
    runButton.classList.remove("bg-green-500", "hover:bg-gray-600");
    runButton.classList.add("bg-gray-400", "cursor-not-allowed");

    // Tampilkan loading state
    loadingInterval = showLoadingState();

    const response = await fetch("/v2/judge", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    })

    if(!response.ok){
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    console.log(result);

    // Clear loading interval
    if (loadingInterval) {
      clearInterval(loadingInterval);
    }

    // Display hasil
    displayResults(result);
    
  }catch(error){
    console.error("Error sending code to judge:", error);
    
    // Clear loading interval
    if (loadingInterval) {
      clearInterval(loadingInterval);
    }
    
    resultContainer.innerHTML = `
      <div class="text-red-600 p-4 border border-red-300 rounded bg-red-50">
        <h3 class="font-bold">Error occurred!</h3>
        <p class="mt-2">${error.message}</p>
      </div>
    `;
  } finally {
    // Kembalikan tombol run ke state normal
    runButton.disabled = false;
    runButton.textContent = "Run";
    runButton.classList.remove("bg-gray-400", "cursor-not-allowed");
    runButton.classList.add("bg-green-500", "hover:bg-gray-600");
  }
}

  runButton.addEventListener("click", sendCodeToJudge);

  // Fungsi untuk menampilkan hasil dengan format yang lebih baik
function displayResults(result) {
  if (result.status === "compile_error") {
    resultContainer.innerHTML = `
      <div class="text-red-600 p-4 border border-red-300 rounded bg-red-50">
        <h3 class="font-bold">Compile Error</h3>
        <pre class="mt-2 text-sm whitespace-pre-wrap">${result.error_message || 'Compilation failed'}</pre>
      </div>
    `;
    return;
  }

  let html = `
    <div class="results-summary p-4 border rounded mb-4">
      <h3 class="font-bold text-lg">Results Summary</h3>
      <p>Status: <span class="font-semibold">${result.status}</span></p>
      <p>Total Test Cases: <span class="font-semibold">${result.total_case}</span></p>
      <p>Passed: <span class="font-semibold text-green-600">${result.total_case_benar}</span></p>
    </div>
    <div class="test-results">
  `;

  result.results.forEach((testResult, index) => {
    const statusColor = testResult.passed ? 'text-green-600' : 'text-red-600';
    const statusBg = testResult.passed ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300';
    
    html += `
      <div class="test-result mb-3 p-3 border rounded ${statusBg}">
        <h4 class="font-semibold ${statusColor}">Test Case ${index + 1} - ${testResult.status.toUpperCase()}</h4>
        <div class="mt-2 text-sm">
          <p><strong>Input:</strong> <code>${testResult.input}</code></p>
          <p><strong>Expected:</strong> <code>${testResult.expected_output}</code></p>
          <p><strong>Actual:</strong> <code>${testResult.actual_output}</code></p>
          ${testResult.execution_time ? `<p><strong>Time:</strong> ${testResult.execution_time}ms</p>` : ''}
        </div>
      </div>
    `;
  });

  html += '</div>';
  resultContainer.innerHTML = html;
}

  

})