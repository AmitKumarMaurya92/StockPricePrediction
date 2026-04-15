let currentChartData = null;

document.getElementById('predict-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const symbol = document.getElementById('symbol').value;
    const market = document.getElementById('market').value;
    const interval = document.getElementById('interval').value;
    const btn = document.getElementById('predict-btn');
    const loading = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const placeholder = document.getElementById('placeholder');
    const errorDiv = document.getElementById('error-message');
    
    errorDiv.classList.add('hidden');
    resultDiv.classList.add('hidden');
    if (placeholder) placeholder.classList.remove('hidden');
    
    btn.disabled = true;
    loading.classList.remove('hidden');
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, market, interval })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update UI blocks
            document.getElementById('res-symbol').textContent = `${data.symbol} - ${data.company_name}`;
            document.getElementById('res-logo').textContent = data.symbol.substring(0, 3);
            
            // Format Predicted Price
            document.getElementById('res-predicted-price').textContent = `${data.currency_symbol}${data.prediction.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            
            // Format Change UI text
            const isPositive = data.change >= 0;
            const changeStr = isPositive 
                ? `▲ +${data.change.toFixed(2)} (+${data.percent_change.toFixed(2)}%)`
                : `▼ ${data.change.toFixed(2)} (${data.percent_change.toFixed(2)}%)`;
                
            const changeNode = document.getElementById('res-change');
            changeNode.textContent = changeStr;
            changeNode.className = isPositive ? 'price-change text-green' : 'price-change text-red';
            
            // Set Trading Recommendation Signal
            const recNode = document.getElementById('res-recommendation');
            recNode.textContent = data.recommendation;
            
            if (data.recommendation.includes('BUY')) {
                recNode.style.backgroundColor = 'rgba(16, 185, 129, 0.2)';
                recNode.style.color = '#10b981';
                recNode.style.border = '1px solid rgba(16, 185, 129, 0.3)';
            } else if (data.recommendation.includes('SELL')) {
                recNode.style.backgroundColor = 'rgba(239, 68, 68, 0.2)';
                recNode.style.color = '#ef4444';
                recNode.style.border = '1px solid rgba(239, 68, 68, 0.3)';
            } else {
                recNode.style.backgroundColor = 'rgba(251, 191, 36, 0.2)';
                recNode.style.color = '#fbbf24'; // Yellow
                recNode.style.border = '1px solid rgba(251, 191, 36, 0.3)';
            }
            
            // Set Target and Stop Loss
            document.getElementById('setup-action').textContent = `(${data.recommendation})`;
            document.getElementById('target-price').textContent = `${data.currency_symbol}${data.target_price.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            document.getElementById('stop-loss').textContent = `${data.currency_symbol}${data.stop_loss.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            
            // Bottom stats formatting
            document.getElementById('stat-open').textContent = `${data.currency_symbol}${data.last_open.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            document.getElementById('stat-high').textContent = `${data.currency_symbol}${data.last_high.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            document.getElementById('stat-low').textContent = `${data.currency_symbol}${data.last_low.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            
            // Cache the data and draw chart
            currentChartData = data;
            renderDynamicChart(data);
            
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

// Re-render chart freely when user dynamically switches the dropdown
document.getElementById('chart-type').addEventListener('change', () => {
    if (currentChartData) {
        renderDynamicChart(currentChartData);
    }
});

function renderDynamicChart(data) {
    const dates = data.historical_dates;
    const chartType = document.getElementById('chart-type').value;
    
    // Calculate the predicted next date for overlay
    const lastDate = new Date(dates[dates.length - 1]);
    const nextDay = new Date(lastDate);
    nextDay.setDate(nextDay.getDate() + 1);
    const predictedDateStr = nextDay.toISOString().split('T')[0];

    // Variable representation based on dropdown selection
    let trace1;
    if (chartType === 'candlestick') {
        trace1 = {
            x: dates,
            open: data.historical_open,
            high: data.historical_high,
            low: data.historical_low,
            close: data.historical_close,
            type: 'candlestick',
            name: data.symbol,
            increasing: { line: { color: '#10b981' } }, // Green
            decreasing: { line: { color: '#ef4444' } }  // Red
        };
    } else if (chartType === 'line') {
        trace1 = {
            x: dates,
            y: data.historical_close,
            type: 'scatter',
            mode: 'lines',
            fill: 'tozeroy', // Creates an aesthetic area chart
            fillcolor: 'rgba(56, 189, 248, 0.1)',
            name: 'Close Price',
            line: { color: '#38bdf8', width: 3 }
        };
    } else if (chartType === 'bar') {
        trace1 = {
            x: dates,
            y: data.historical_close,
            type: 'bar',
            name: 'Close Price',
            marker: { color: '#818cf8', opacity: 0.8 }
        };
    }

    // The prediction node
    const trace2 = {
        x: [predictedDateStr],
        y: [data.prediction],
        type: 'scatter',
        mode: 'markers+lines',
        name: 'Forecast Output',
        marker: { color: '#f97316', size: 10, symbol: 'star' }
    };
    
    const layout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#94a3b8', family: 'Inter' },
        margin: { t: 20, r: 20, b: 40, l: 40 },
        xaxis: {
            showgrid: true,
            gridcolor: 'rgba(255, 255, 255, 0.05)',
            rangeslider: { visible: false } // Hide ugly native rangeslider
        },
        yaxis: {
            tickprefix: data.currency_symbol,
            showgrid: true,
            gridcolor: 'rgba(255, 255, 255, 0.05)'
        },
        showlegend: false
    };

    const config = { responsive: true, displayModeBar: false };
    Plotly.newPlot('chart-container', [trace1, trace2], layout, config);
}
