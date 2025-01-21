async function readExcelFile() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];

  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = function (e) {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: "array" });
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
        const jsonData = XLSX.utils.sheet_to_json(firstSheet);
        resolve(jsonData);
      } catch (error) {
        reject(error);
      }
    };

    reader.onerror = function (error) {
      reject(error);
    };

    reader.readAsArrayBuffer(file);
  });
}

async function predict() {
  try {
    const fileInput = document.getElementById("fileInput");
    if (!fileInput || !fileInput.files || !fileInput.files[0]) {
      throw new Error("請選擇檔案");
    }

    const predictButton = document.getElementById("predictButton");
    predictButton.disabled = true;
    predictButton.textContent = "預測中...";

    const selectedFeatures = Array.from(
      document.querySelectorAll('input[name="features[]"]:checked')
    ).map((cb) => cb.value);

    if (selectedFeatures.length === 0) {
      throw new Error("請至少選擇一個特徵");
    }

    const testData = await readExcelFile();
    const parkType = document.querySelector(
      'input[name="parkType"]:checked'
    ).value;

    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        testData: testData,
        selectedFeatures: selectedFeatures,
        parkType: parkType,
      }),
    });

    const results = await response.json();

    if (!response.ok) {
      throw new Error(results.error || "預測失敗");
    }

    displayResults(results);
  } catch (error) {
    console.error("Error:", error);
    const container = document.getElementById("resultContainer");
    container.innerHTML = `<div class="error-message">錯誤：${error.message}</div>`;
  } finally {
    const predictButton = document.getElementById("predictButton");
    predictButton.disabled = false;
    predictButton.textContent = "開始預測";
  }
}

function displayResults(results) {
  const container = document.getElementById("resultContainer");
  container.innerHTML = "";

  // 創建結果表格
  const table = document.createElement("table");
  table.className = "result-table";

  // 添加表頭
  const thead = document.createElement("thead");
  thead.innerHTML = `
        <tr>
            <th>園區名稱</th>
            <th>適配度分數</th>
        </tr>
    `;
  table.appendChild(thead);

  // 添加表格內容
  const tbody = document.createElement("tbody");

  // 確保 results 中的數據存在且格式正確
  if (
    results.suitability_scores &&
    results.park_names &&
    Array.isArray(results.suitability_scores) &&
    Array.isArray(results.park_names)
  ) {
    results.suitability_scores.forEach((score, index) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td>${results.park_names[index] || `Sample_${index}`}</td>
                <td>${
                  typeof score === "number" ? score.toFixed(2) : "0.00"
                }</td>
            `;
      tbody.appendChild(row);
    });
  }

  table.appendChild(tbody);
  container.appendChild(table);
}
