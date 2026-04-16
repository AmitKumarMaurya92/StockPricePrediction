let currentChartData = null;

// Autocomplete logic
const symbolInput = document.getElementById('symbol');
const autocompleteList = document.getElementById('autocomplete-list');
let debounceTimeout;

symbolInput.addEventListener('input', function() {
    clearTimeout(debounceTimeout);
    const query = this.value;
    
    if (!query) {
        autocompleteList.classList.add('hidden');
        autocompleteList.innerHTML = '';
        return;
    }
    
    // Check if user has probably already selected an NSE/BO ticker
    if (query.includes('.NS') || query.includes('.BO')) {
        autocompleteList.classList.add('hidden');
        return;
    }
    
    debounceTimeout = setTimeout(async () => {
        try {
            const market = document.getElementById('market').value;
            const res = await fetch(`/suggest?q=${encodeURIComponent(query)}&market=${market}`);
            const suggestions = await res.json();
            
            autocompleteList.innerHTML = '';
            if (suggestions.length > 0) {
                suggestions.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'autocomplete-item';
                    
                    const symbolSpan = document.createElement('span');
                    symbolSpan.className = 'ac-symbol';
                    symbolSpan.textContent = item.symbol; // Display symbol without suffix
                    
                    const nameSpan = document.createElement('span');
                    nameSpan.className = 'ac-name';
                    nameSpan.textContent = item.name + (item.exchange ? ` (${item.exchange})` : '');
                    
                    div.appendChild(symbolSpan);
                    div.appendChild(nameSpan);
                    
                    div.addEventListener('click', () => {
                        // We populate the input with the clean symbol (e.g. TCS instead of TCS.NS)
                        // The backend /predict logic will automatically append .NS internally!
                        symbolInput.value = item.symbol; 
                        autocompleteList.classList.add('hidden');
                        autocompleteList.innerHTML = '';
                        document.getElementById('predict-btn').focus();
                    });
                    
                    autocompleteList.appendChild(div);
                });
                autocompleteList.classList.remove('hidden');
            } else {
                autocompleteList.classList.add('hidden');
            }
        } catch (e) {
            console.error('Error fetching suggestions:', e);
        }
    }, 300);
});

// Hide autocomplete when clicking outside
document.addEventListener('click', function(e) {
    if (e.target !== symbolInput && !autocompleteList.contains(e.target)) {
        autocompleteList.classList.add('hidden');
    }
});

// Theme Toggling Logic
const themeBtn = document.getElementById('theme-toggle');
let isLightMode = localStorage.getItem('theme') === 'light';

if (isLightMode) {
    document.body.classList.add('light-theme');
}

themeBtn.addEventListener('click', () => {
    isLightMode = !isLightMode;
    if (isLightMode) {
        document.body.classList.add('light-theme');
        localStorage.setItem('theme', 'light');
    } else {
        document.body.classList.remove('light-theme');
        localStorage.setItem('theme', 'dark');
    }
    
    // Redraw chart to update grid colors
    if (currentChartData) {
        renderDynamicChart(currentChartData);
    }
});

document.getElementById('predict-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const symbol = document.getElementById('symbol').value;
    const market = document.getElementById('market').value;
    const interval = '1d'; // Default interval
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
            handleSuccessResponse(data, resultDiv);
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

// CSV Upload logic
document.getElementById('csv-upload').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
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
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/predict_file', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        if (data.success) {
            handleSuccessResponse(data, resultDiv);
        } else {
            throw new Error(data.error || 'File prediction failed');
        }
    } catch (err) {
        errorDiv.textContent = err.message;
        errorDiv.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        loading.classList.add('hidden');
        e.target.value = ''; // Reset
    }
});

function handleSuccessResponse(data, resultDiv) {
    // Update UI blocks
    document.getElementById('res-symbol').textContent = data.symbol;
    document.getElementById('res-logo').textContent = data.symbol.substring(0, 3).toUpperCase();
    
    const webBtn = document.getElementById('res-website');
    if (data.website && data.website !== '') {
        webBtn.href = data.website;
        webBtn.style.display = 'inline-block';
    } else {
        webBtn.style.display = 'none';
    }
    
    // Top header current price maps to the actual current 'last_price'
    document.getElementById('res-current-price').textContent = `${data.currency_symbol}${data.last_price.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    
    // AI Forecast box maps to the internal next-day prediction
    document.getElementById('res-predicted-price').textContent = `${data.currency_symbol}${data.prediction.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    
    // Format Change UI text
    const isPositive = data.change >= 0;
    const changeStr = isPositive 
        ? `▲ +${data.change.toFixed(2)} (+${data.percent_change.toFixed(2)}%)`
        : `▼ ${data.change.toFixed(2)} (${data.percent_change.toFixed(2)}%)`;
        
    const changeNode = document.getElementById('res-change');
    changeNode.textContent = changeStr;
    changeNode.className = isPositive ? 'price-change text-green' : 'price-change text-red';
    
    // Set Trading Recommendation Signal internally to the sidebar
    const recNode = document.getElementById('res-recommendation');
    recNode.textContent = data.recommendation + " SIGNAL";
    
    if (data.recommendation.includes('BUY')) {
        recNode.style.color = '#10b981';
    } else if (data.recommendation.includes('SELL')) {
        recNode.style.color = '#ef4444';
    } else {
        recNode.style.color = '#fbbf24'; // Yellow
    }
    
    // Set Target and Stop Loss inside the Sidebar AI panel
    document.getElementById('target-price').textContent = `${data.currency_symbol}${data.target_price.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    document.getElementById('stop-loss').textContent = `${data.currency_symbol}${data.stop_loss.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    
    // --- POPULATE FUNDAMENTALS GRID SECTION --- 
    const formatFund = (val, prefix='', suffix='') => (val !== 'N/A' && val !== null && !isNaN(val)) ? `${prefix}${val}${suffix}` : 'N/A';
    
    // Market Cap formatting
    let mcap = data.market_cap;
    if (mcap !== 'N/A' && typeof mcap === 'number') {
        if (mcap >= 1e12) mcap = (mcap / 1e12).toFixed(2) + ' Trillion';
        else if (mcap >= 1e9) mcap = (mcap / 1e9).toFixed(2) + ' Billion';
        else if (mcap >= 1e6) mcap = (mcap / 1e6).toFixed(2) + ' Million';
        else mcap = mcap.toLocaleString();
    }
    document.getElementById('val-market-cap').textContent = (mcap === 'N/A' || !mcap) ? 'N/A' : `${data.currency_symbol}${mcap}`;
    
    document.getElementById('val-pe').textContent = formatFund(data.stock_pe);
    document.getElementById('val-roce').textContent = formatFund(data.roce, '', '%');
    
    document.getElementById('val-current-price').textContent = `${data.currency_symbol}${data.last_price.toLocaleString()}`;
    document.getElementById('val-book-value').textContent = formatFund(data.book_value, data.currency_symbol);
    document.getElementById('val-roe').textContent = formatFund(data.roe, '', '%');
    
    const hlFormat = (data.fifty_two_high !== 'N/A' && data.fifty_two_low !== 'N/A') 
        ? `${data.currency_symbol}${data.fifty_two_high.toLocaleString()} / ${data.currency_symbol}${data.fifty_two_low.toLocaleString()}` 
        : 'N/A';
    document.getElementById('val-high-low').textContent = hlFormat;
    
    document.getElementById('val-dividend').textContent = formatFund(data.dividend_yield, '', '%');
    document.getElementById('val-face-value').textContent = 'N/A';
    
    document.getElementById('res-about-text').textContent = data.about_text !== 'N/A' ? data.about_text : 'Detailed company information or long business summary is fully unavailable directly from the Yahoo Finance payload for this ticker instance.';
    
    // Evaluate 'Read More' visibility
    const aboutContainer = document.getElementById('about-container');
    const readMoreBtn = document.getElementById('read-more-btn');
    
    // Reset state cleanly for new predictions
    aboutContainer.classList.add('clamped');
    readMoreBtn.textContent = 'READ MORE >';
    readMoreBtn.classList.add('hidden');
    
    setTimeout(() => {
        // Evaluate if actual text overflows the clamped clientHeight
        if (aboutContainer.scrollHeight > aboutContainer.clientHeight) {
            readMoreBtn.classList.remove('hidden');
        }
    }, 50);
    
    // Cache the data and draw chart
    currentChartData = data;
    renderDynamicChart(data);
    
    resultDiv.classList.remove('hidden');
}

// Re-render chart freely when user dynamically switches the dropdown
document.getElementById('chart-type').addEventListener('change', () => {
    if (currentChartData) {
        renderDynamicChart(currentChartData);
    }
});

function renderDynamicChart(data) {
    let dates = data.historical_dates;
    let open = data.historical_open;
    let high = data.historical_high;
    let low = data.historical_low;
    let close = data.historical_close;
    let volume = data.historical_volume;
    let dma50 = data.dma_50;
    let dma200 = data.dma_200;
    const chartType = document.getElementById('chart-type').value;
    
    // Filter by Timeframe organically locally
    if (dates.length > 0) {
        const lastDate = new Date(dates[dates.length - 1]);
        const cutoffDate = new Date(lastDate);
        
        if (typeof selectedTimeframe !== 'undefined') {
            if (selectedTimeframe === '1D') {
                cutoffDate.setDate(cutoffDate.getDate() - 1);
            } else if (selectedTimeframe === '1W') {
                cutoffDate.setDate(cutoffDate.getDate() - 7);
            } else if (selectedTimeframe === '1M') {
                cutoffDate.setMonth(cutoffDate.getMonth() - 1);
            } else if (selectedTimeframe === '6M') {
                cutoffDate.setMonth(cutoffDate.getMonth() - 6);
            } else if (selectedTimeframe === '1Y') {
                cutoffDate.setFullYear(cutoffDate.getFullYear() - 1);
            } else if (selectedTimeframe === '5Y') {
                cutoffDate.setFullYear(cutoffDate.getFullYear() - 5);
            } else {
                cutoffDate.setFullYear(1900); // MAX
            }
            
            let startIndex = 0;
            for (let i = 0; i < dates.length; i++) {
                if (new Date(dates[i]) >= cutoffDate) {
                    startIndex = i;
                    break;
                }
            }
            
            dates = dates.slice(startIndex);
            open = open.slice(startIndex);
            high = high.slice(startIndex);
            low = low.slice(startIndex);
            close = close.slice(startIndex);
            if (volume) volume = volume.slice(startIndex);
            if (dma50) dma50 = dma50.slice(startIndex);
            if (dma200) dma200 = dma200.slice(startIndex);
        }
    }
    
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
            open: open,
            high: high,
            low: low,
            close: close,
            type: 'candlestick',
            name: data.symbol,
            increasing: { line: { color: '#10b981' } }, // Green
            decreasing: { line: { color: '#ef4444' } }  // Red
        };
    } else if (chartType === 'line') {
        trace1 = {
            x: dates,
            y: close,
            type: 'scatter',
            mode: 'lines',
            name: 'Close Price',
            line: { color: '#6366f1', width: 2.5 } // Vibrant Indigo Line
        };
    } else if (chartType === 'bar') {
        trace1 = {
            x: dates,
            y: close,
            type: 'bar',
            name: 'Close Price',
            marker: { color: '#4f46e5', opacity: 1.0 } // Changed to stark dark indigo with 100% opacity for clear distinction from volume
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
    
    // 50-Day Moving Average
    const traceDMA50 = {
        x: dates,
        y: dma50 ? dma50.map(v => v === 'N/A' ? null : v) : [],
        type: 'scatter',
        mode: 'lines',
        name: '50 DMA',
        line: { color: '#f59e0b', width: 1.5 } // Orange line
    };

    // 200-Day Moving Average
    const traceDMA200 = {
        x: dates,
        y: dma200 ? dma200.map(v => v === 'N/A' ? null : v) : [],
        type: 'scatter',
        mode: 'lines',
        name: '200 DMA',
        line: { color: '#64748b', width: 1.5 } // Slate line
    };
    
    const isLight = document.body.classList.contains('light-theme');
    const gridColor = isLight ? 'rgba(0, 0, 0, 0.1)' : 'rgba(255, 255, 255, 0.05)';
    const textColor = isLight ? '#475569' : '#94a3b8';
    
    // The volume trace overlay mapped to a secondary Y-axis (y2)
    // Map volume to thousands (k) form explicitly per user request
    const volumeInK = volume ? volume.map(v => v / 1000) : [];
    const maxVolumeInK = Math.max(...(volumeInK.length ? volumeInK : [0]));
    
    const traceVolume = {
        x: dates,
        y: volumeInK,
        type: 'bar',
        name: 'Volume',
        yaxis: 'y2',
        marker: { color: isLight ? 'rgba(147, 197, 253, 0.8)' : 'rgba(96, 165, 250, 0.6)' } // Solid light blue bars matching reference
    };

    const layout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: textColor, family: 'Inter' },
        margin: { t: 20, r: 60, b: 40, l: 60 },
        bargap: 0.05, 
        barmode: 'group', // Ensures native plot overlay mapping behaves correctly for multi-bars
        xaxis: {
            showgrid: true,
            gridcolor: gridColor,
            rangeslider: { visible: false } 
        },
        yaxis: {
            title: { text: `Price on Exchange (${data.currency_symbol})`, font: { size: 10 } },
            tickprefix: data.currency_symbol,
            showgrid: true,
            gridcolor: gridColor,
            domain: [0, 1], // Full chart height for price
            side: 'right' 
        },
        yaxis2: {
            title: { text: 'Volume', font: { size: 10 } },
            showgrid: false,
            domain: [0, 1], // Full chart height for volume (creates overlap)
            overlaying: 'y', // Overlays exactly on top of yaxis
            range: [0, maxVolumeInK * 1.8], // Cap volume bars dynamically to bottom ~55% (increased from 30%)
            tickfont: { size: 10, color: textColor },
            ticksuffix: 'k',
            tickformat: ',', // Add commas for readable numbers e.g. 50,000k
            side: 'left' 
        },
        showlegend: false
    };

    const config = { responsive: true, displayModeBar: false };
    Plotly.newPlot('chart-container', [traceVolume, traceDMA50, traceDMA200, trace1, trace2], layout, config);
    
    // Resync Checkboxes state internally upon fresh redraws so traces accurately represent box states.
    const showPrice = document.getElementById('toggle-price').checked;
    const showDMA50 = document.getElementById('toggle-dma50').checked;
    const showDMA200 = document.getElementById('toggle-dma200').checked;
    const showVol = document.getElementById('toggle-volume').checked;
    
    Plotly.restyle('chart-container', {visible: showVol ? true : 'legendonly'}, [0]);
    Plotly.restyle('chart-container', {visible: showDMA50 ? true : 'legendonly'}, [1]);
    Plotly.restyle('chart-container', {visible: showDMA200 ? true : 'legendonly'}, [2]);
    Plotly.restyle('chart-container', {visible: showPrice ? true : 'legendonly'}, [3, 4]);
}

// Toggle Read More
document.addEventListener('click', function(e) {
    if (e.target && e.target.id === 'read-more-btn') {
        const container = document.getElementById('about-container');
        if (container.classList.contains('clamped')) {
            container.classList.remove('clamped');
            e.target.textContent = 'READ LESS <';
        } else {
            container.classList.add('clamped');
            e.target.textContent = 'READ MORE >';
        }
    }
});

let selectedTimeframe = '1Y';

document.querySelectorAll('.interval-btn[data-period]').forEach(btn => {
    btn.addEventListener('click', (e) => {
        // Update styling visually
        document.querySelectorAll('.interval-btn[data-period]').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        // Mutate the global filter state
        selectedTimeframe = e.target.getAttribute('data-period');
        
        // Instant visual update without reloading from API
        if (currentChartData) {
            renderDynamicChart(currentChartData);
        }
    });
});

document.getElementById('toggle-price').addEventListener('change', function(e) {
    const update = { visible: e.target.checked ? true : 'legendonly' };
    Plotly.restyle('chart-container', update, [3, 4]);
});

document.getElementById('toggle-dma50').addEventListener('change', function(e) {
    const update = { visible: e.target.checked ? true : 'legendonly' };
    Plotly.restyle('chart-container', update, [1]);
});

document.getElementById('toggle-dma200').addEventListener('change', function(e) {
    const update = { visible: e.target.checked ? true : 'legendonly' };
    Plotly.restyle('chart-container', update, [2]);
});

document.getElementById('toggle-volume').addEventListener('change', function(e) {
    const update = { visible: e.target.checked ? true : 'legendonly' };
    Plotly.restyle('chart-container', update, [0]);
});
