document.addEventListener('DOMContentLoaded', function() {
    // 從後端獲取特徵列表
    fetch(`${API_BASE_URL}/get_features`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error);
                return;
            }
            // 使用完整集成模型的推薦特徵進行初始化
            initializeFeatures(data.features, MODEL_FEATURES['ensemble_full']);
            setupFeatureListeners();
        })
        .catch(error => {
            console.error('Error:', error);
            handleError(error);
        });

    // 文件選擇事件
    const fileInput = document.getElementById('fileInput');
    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        const fileName = document.getElementById('fileName');
        const predictButton = document.getElementById('predictButton');
        
        if (file) {
            fileName.textContent = file.name;
            fileName.style.color = '#2196f3';
            predictButton.disabled = false;
            predictButton.classList.add('active');
        } else {
            fileName.textContent = '尚未選擇檔案';
            fileName.style.color = '#999';
            predictButton.disabled = true;
            predictButton.classList.remove('active');
        }
    });

    // 預測按鈕事件
    const predictButton = document.getElementById('predictButton');
    predictButton.addEventListener('click', predict);
});