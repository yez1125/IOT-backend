// 讀取 Excel 檔案
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

        // 驗證是否包含「園區名稱」
        if (!jsonData.length || !jsonData[0]["園區名稱"]) {
          reject(new Error("Excel 檔案缺少必要的欄位：園區名稱"));
        }

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

// 提交預測請求
async function predict() {
  try {
    const fileInput = document.getElementById("fileInput");
    if (!fileInput || !fileInput.files || !fileInput.files[0]) {
      throw new Error("請選擇檔案");
    }

    const predictButton = document.getElementById("predictButton");
    predictButton.disabled = true;
    predictButton.textContent = "預測中...";

    const testData = await readExcelFile();

    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        testData: testData,
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

// 顯示結果
function displayResults(results) {
  const container = document.getElementById("resultContainer");
  container.innerHTML = "";

  const table = document.createElement("table");
  table.className = "prediction-table";

  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  [
    "園區名稱",
    "距離 (愈近代表愈相似)",
    "分數 (愈高代表愈相似)",
    "距離等級 (愈高代表愈相似)",
  ].forEach((header) => {
    const th = document.createElement("th");
    th.textContent = header;
    th.style.position = "sticky";
    th.style.top = "0";
    th.style.backgroundColor = "#f5f7fa";
    th.style.zIndex = "1000";
    th.style.borderBottom = "2px solid #ddd";
    th.style.padding = "12px 15px";
    th.style.textAlign = "left";
    th.style.fontWeight = "bold";
    th.style.fontSize = "14px";

    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  results.forEach((result, index) => {
    const row = document.createElement("tr");
    row.style.backgroundColor = index % 2 === 0 ? "#fafafa" : "white";

    // 園區名稱
    const nameCell = document.createElement("td");
    nameCell.textContent = result.index;
    nameCell.style.fontWeight = "bold";
    row.appendChild(nameCell);

    // 預測類別
    //const categoryCell = document.createElement("td");
    //categoryCell.textContent = result.predicted_category;
    //categoryCell.style.fontWeight = "bold";
    //categoryCell.style.color = "#2196f3";
    //row.appendChild(categoryCell);

    // 距離
    const distanceCell = document.createElement("td");
    distanceCell.innerHTML = Object.entries(result.distances)
      .map(([key, value]) => `${key}: ${value.toFixed(4)}`)
      .join("<br>");
    row.appendChild(distanceCell);

    // 分數
    const scoreCell = document.createElement("td");
    scoreCell.innerHTML = Object.entries(result.scores)
      .map(([key, value]) => `${key}: ${value.toFixed(4)}`)
      .join("<br>");
    row.appendChild(scoreCell);

    // 距離等級
    const distanceLevelCell = document.createElement("td");
    distanceLevelCell.innerHTML = Object.entries(result.levels)
      .map(([key, value]) => `${key}: ${value}`)
      .join("<br>");
    row.appendChild(distanceLevelCell);

    tbody.appendChild(row);
  });

  table.appendChild(tbody);
  container.appendChild(table);
}

// 啟用提交按鈕
document.getElementById("fileInput").addEventListener("change", function () {
  const file = this.files[0];
  const predictButton = document.getElementById("predictButton");

  if (file) {
    predictButton.disabled = false;
    predictButton.textContent = "開始預測";
  } else {
    predictButton.disabled = true;
    predictButton.textContent = "請選擇檔案";
  }
});
