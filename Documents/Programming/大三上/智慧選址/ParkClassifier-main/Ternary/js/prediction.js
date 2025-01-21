async function readExcelFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, {type: 'array'});
                const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                const jsonData = XLSX.utils.sheet_to_json(firstSheet);
                resolve(jsonData);
            } catch (error) {
                reject(error);
            }
        };
        
        reader.onerror = function(error) {
            reject(error);
        };
        
        reader.readAsArrayBuffer(file);
    });
}

function displayResults(results) {
    const container = document.getElementById('resultContainer');
    container.innerHTML = '';
    
    const table = document.createElement('table');
    table.className = 'prediction-table';
    
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['園區名稱', '園區類別', '預測機率', '預測結果'].forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    const tbody = document.createElement('tbody');
    results.forEach(result => {
        const row = document.createElement('tr');
        
        // 園區名稱
        const nameCell = document.createElement('td');
        nameCell.textContent = result.園區名稱;
        row.appendChild(nameCell);
        
        // 預測類別
        const classCell = document.createElement('td');
        classCell.textContent = result.園區類別;
        row.appendChild(classCell);
        
        // 預測機率
        const probCell = document.createElement('td');
        const probabilities = Object.entries(result.預測機率)
            .sort((a, b) => b[1] - a[1])
            .map(([category, prob]) => `${category}: ${prob.toFixed(2)}%`)
            .join('<br>');
        probCell.innerHTML = probabilities;
        row.appendChild(probCell);
        
        // 預測結果
        const resultCell = document.createElement('td');
        const highestProb = Object.entries(result.預測機率)
            .reduce((a, b) => a[1] > b[1] ? a : b);
        resultCell.textContent = `${highestProb[0]} (${highestProb[1].toFixed(2)}%)`;
        resultCell.style.color = '#2196f3';
        resultCell.style.fontWeight = 'bold';
        row.appendChild(resultCell);
        
        tbody.appendChild(row);
    });
    table.appendChild(tbody);
    container.appendChild(table);
}

function handleError(error) {
    console.error('Error:', error);
    const container = document.getElementById('resultContainer');
    container.innerHTML = `
        <div class="error-message">
            發生錯誤：${error.message || '未知錯誤'}
        </div>
    `;
}

async function predict() {
    try {
        const fileInput = document.getElementById('fileInput');
        if (!fileInput || !fileInput.files || !fileInput.files[0]) {
            throw new Error('請選擇檔案');
        }

        const predictButton = document.getElementById('predictButton');
        predictButton.disabled = true;
        predictButton.textContent = '預測中...';

        const selectedFeatures = Array.from(
            document.querySelectorAll('input[name="features[]"]:checked')
        ).map(cb => cb.value);

        if (selectedFeatures.length === 0) {
            throw new Error('請至少選擇一個特徵');
        }

        const testData = await readExcelFile();
        const modelType = document.querySelector('input[name="model"]:checked').value;

        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                testData: testData,
                selectedFeatures: selectedFeatures,
                modelType: modelType
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            throw new Error(data.error || '預測失敗');
        }
    } catch (error) {
        handleError(error);
    } finally {
        const predictButton = document.getElementById('predictButton');
        predictButton.disabled = false;
        predictButton.textContent = '開始預測';
    }
}