document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("file");
  const fileNameDisplay = document.getElementById("fileName");
  const predictButton = document.getElementById("predictButton");

  // 文件選擇事件
  fileInput.addEventListener("change", (event) => {
    const fileName = event.target.files[0]?.name || "尚未選擇檔案";
    fileNameDisplay.textContent = fileName;
    predictButton.disabled = !event.target.files[0];
  });

  // 提交按鈕事件
  predictButton.addEventListener("click", async () => {
    const fileInput = document.getElementById("file");
    const file = fileInput.files[0];

    if (!file) {
      alert("請選擇檔案");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:5002/predict", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("伺服器錯誤，請稍後再試");
      }

      const results = await response.json();
      if (results.error) {
        throw new Error(results.error);
      }

      // 调用 displayResults 函数显示结果
      displayResults(results);
    } catch (error) {
      console.error("上傳失敗：", error);
      alert(error.message);
    }
  });
});
