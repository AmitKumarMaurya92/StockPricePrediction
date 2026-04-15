document.getElementById('predict-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const symbol = document.getElementById('symbol').value;
    const btn = document.getElementById('predict-btn');
    const loading = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error-message');
    
    // Reset state
    errorDiv.classList.add('hidden');
    resultDiv.classList.add('hidden');
    
    // Show loading
    btn.disabled = true;
    loading.classList.remove('hidden');
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbol })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('res-symbol').textContent = data.symbol;
            document.getElementById('res-last-price').textContent = `$${data.last_price.toFixed(2)}`;
            document.getElementById('res-predicted-price').textContent = `$${data.prediction.toFixed(2)}`;
            resultDiv.classList.remove('hidden');
        } else {
            throw new Error(data.error || 'Prediction failed');
        }
    } catch (err) {
        errorDiv.textContent = err.message;
        errorDiv.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        loading.classList.add('hidden');
    }
});
