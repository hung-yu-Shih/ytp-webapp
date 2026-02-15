document.getElementById("sendBtn").addEventListener("click", async () => {
    const text = document.getElementById("userInput").value;
    if (!text) return alert("請輸入文字");

    // 呼叫後端 API
    const response = await fetch(`http://127.0.0.1:8000/predict?text=${encodeURIComponent(text)}`);
    const data = await response.json();

    document.getElementById("result").innerText = `AI 回傳：${data.output}`;
});
