// Monitor de Criptomoedas - JavaScript Principal

// Armazena os dados de preços atuais
let currentPrices = {};
let cryptoList = [];
let alertThreshold = 3.0;
const maxAlerts = 10;
let alertsShown = 0;

// Inicializa quando o DOM estiver totalmente carregado
document.addEventListener('DOMContentLoaded', function() {
    // Configura o tempo inicial
    updateTimestamp();
    
    // Carrega a lista de criptomoedas
    loadCryptocurrencies();
    
    // Configura os manipuladores de eventos
    if (document.getElementById('refresh-btn')) {
        document.getElementById('refresh-btn').addEventListener('click', loadAlerts);
    }
    
    // Inicia atualizações regulares
    setInterval(updatePrices, 30000); // Atualiza a cada 30 segundos
    setInterval(updateTimestamp, 10000); // Atualiza o timestamp a cada 10 segundos
    setInterval(loadAlerts, 120000); // Atualiza alertas a cada 2 minutos

    // Carrega os alertas iniciais
    loadAlerts();
});

// Load list of monitored cryptocurrencies
function loadCryptocurrencies() {
    fetch('/api/cryptocurrencies')
        .then(response => response.json())
        .then(data => {
            cryptoList = data;
            // Não precisamos mais atualizar o crypto-count, pois o elemento não existe mais no HTML
            
            // Load initial price data
            updatePrices();
        })
        .catch(error => {
            console.error('Error loading cryptocurrency list:', error);
            // Silenciando o erro para evitar mensagens desnecessárias ao usuário
        });
}

// Update cryptocurrency prices
function updatePrices() {
    fetch('/api/prices/current')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Store previous prices for comparison
            const previousPrices = {...currentPrices};
            currentPrices = data;
            
            // Update the table
            updatePriceTable(previousPrices);
            
            // Update timestamp
            updateTimestamp();
            
            // Clear any previous error messages
            const errorElem = document.querySelector('.api-error-alert');
            if (errorElem) {
                errorElem.remove();
            }
        })
        .catch(error => {
            console.error('Error updating prices:', error);
            // Silenciando o erro para não confundir o usuário
        });
}

// Update the price table with current data
function updatePriceTable(previousPrices) {
    const tableBody = document.querySelector('#crypto-table tbody');
    
    // Clear placeholder if present
    const placeholder = document.querySelector('.placeholder-row');
    if (placeholder) {
        tableBody.innerHTML = '';
    }
    
    // If no data, show message
    if (Object.keys(currentPrices).length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-6 text-gray-400">Nenhum dado de preço disponível ainda.</td>
            </tr>
        `;
        return;
    }
    
    // Sort cryptocurrencies by symbol
    const symbols = Object.keys(currentPrices).sort();
    
    symbols.forEach(symbol => {
        const crypto = currentPrices[symbol];
        const previousPrice = previousPrices[symbol] ? previousPrices[symbol].price : null;
        let changeClass = '';
        let changeHtml = '';
        
        // Calculate and format change if previous price exists
        if (previousPrice !== null) {
            const percentChange = ((crypto.price - previousPrice) / previousPrice) * 100;
            changeClass = percentChange > 0 ? 'price-up' : percentChange < 0 ? 'price-down' : '';
            const changeIcon = percentChange > 0 ? '▲' : percentChange < 0 ? '▼' : '';
            
            changeHtml = `<span class="${changeClass}">${changeIcon} ${Math.abs(percentChange).toFixed(2)}%</span>`;
            
            // Create alert for significant changes
            if (Math.abs(percentChange) >= alertThreshold) {
                createAlert(symbol, crypto.price, previousPrice, percentChange);
            }
        } else {
            changeHtml = '<span class="text-gray-400">-</span>';
        }
        
        // Format timestamp
        const timestamp = new Date(crypto.timestamp);
        const formattedTime = timestamp.toLocaleTimeString('pt-PT');
        
        // Check if row for this symbol already exists
        const existingRow = document.getElementById(`row-${symbol}`);
        
        // Generate recommendation HTML if available
        let recommendationHtml = '';
        if (crypto.recommendation) {
            const recClass = crypto.recommendation === 'COMPRA' ? 'price-up' : 'price-down';
            const recIcon = crypto.recommendation === 'COMPRA' ? '✅' : '⚠️';
            recommendationHtml = `<span class="${recClass} font-bold">${recIcon} ${crypto.recommendation}</span>`;
        } else {
            recommendationHtml = '<span class="text-gray-400">-</span>';
        }
        
        if (existingRow) {
            // Update existing row
            existingRow.innerHTML = `
                <td class="py-2 border-b border-gray-700">${symbol}</td>
                <td class="py-2 border-b border-gray-700">${crypto.formatted_price}</td>
                <td class="py-2 border-b border-gray-700">${changeHtml}</td>
                <td class="py-2 border-b border-gray-700">${recommendationHtml}</td>
                <td class="py-2 border-b border-gray-700">${formattedTime}</td>
            `;
            
            // Add animation class temporarily to highlight the update
            existingRow.classList.add('bg-gray-700');
            setTimeout(() => existingRow.classList.remove('bg-gray-700'), 1000);
        } else {
            // Create new row
            const newRow = document.createElement('tr');
            newRow.id = `row-${symbol}`;
            newRow.className = 'hover:bg-gray-700';
            newRow.innerHTML = `
                <td class="py-2 border-b border-gray-700">${symbol}</td>
                <td class="py-2 border-b border-gray-700">${crypto.formatted_price}</td>
                <td class="py-2 border-b border-gray-700">${changeHtml}</td>
                <td class="py-2 border-b border-gray-700">${recommendationHtml}</td>
                <td class="py-2 border-b border-gray-700">${formattedTime}</td>
            `;
            tableBody.appendChild(newRow);
        }
    });
}

// Create an alert card for significant price changes
function createAlert(symbol, currentPrice, previousPrice, percentChange) {
    const alertsContainer = document.getElementById('alerts-container');
    const noAlertsMessage = document.getElementById('no-alerts-message');
    
    // Hide "no alerts" message if it's visible
    if (noAlertsMessage) {
        noAlertsMessage.style.display = 'none';
    }
    
    // Determine alert styling based on price direction
    const isPriceUp = percentChange > 0;
    const alertClass = isPriceUp ? 'price-up' : 'price-down';
    const icon = isPriceUp ? 'ph-arrow-up' : 'ph-arrow-down';
    const recommendation = isPriceUp ? 'COMPRA ✅' : 'VENDA ⚠️';
    
    // Create alert card
    const alertCard = document.createElement('div');
    alertCard.className = `bg-gray-700 p-4 rounded-lg mb-3 border-l-4 ${isPriceUp ? 'border-green-500' : 'border-red-500'}`;
    alertCard.innerHTML = `
        <div class="flex justify-between items-center mb-2">
            <div class="flex items-center">
                <span class="font-bold text-lg mr-2">${symbol}</span>
                <i class="ph ${icon} ${alertClass}"></i>
            </div>
            <span class="text-gray-400 text-sm">${new Date().toLocaleTimeString('pt-PT')}</span>
        </div>
        <div class="grid grid-cols-2 gap-2 text-sm">
            <div>Atual: <span class="${alertClass} font-medium">${formatPrice(currentPrice)}</span></div>
            <div>Anterior: <span class="text-gray-300">${formatPrice(previousPrice)}</span></div>
            <div>Variação: <span class="${alertClass} font-medium">${percentChange.toFixed(2)}%</span></div>
            <div>Sinal: <span class="${alertClass} font-bold">${recommendation}</span></div>
        </div>
    `;
    
    // Add to the beginning of the alerts container
    alertsContainer.insertBefore(alertCard, alertsContainer.firstChild);
    
    // Limit number of alerts shown
    alertsShown++;
    if (alertsShown > maxAlerts) {
        const alerts = alertsContainer.querySelectorAll('div[class*="bg-gray-700"]');
        if (alerts.length > maxAlerts) {
            alerts[alerts.length - 1].remove();
        }
    }
}

// Format price with appropriate decimal places
function formatPrice(price) {
    if (price < 0.01) {
        return `$${price.toFixed(8)}`;
    } else if (price < 1) {
        return `$${price.toFixed(6)}`;
    } else if (price < 1000) {
        return `$${price.toFixed(4)}`;
    } else {
        return `$${price.toFixed(2)}`;
    }
}

// Update the "last updated" timestamp
function updateTimestamp() {
    const now = new Date();
    document.getElementById('last-updated').textContent = now.toLocaleTimeString('pt-PT');
}

// Função para carregar alertas e recomendações
function loadAlerts() {
    fetch('/alerts')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('alert-body') || document.querySelector('#crypto-table tbody');
            const now = new Date();
            document.getElementById('last-updated').textContent = now.toLocaleTimeString('pt-PT');

            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center py-6 text-gray-400">Nenhum alerta por enquanto. As recomendações aparecerão aqui assim que forem geradas.</td></tr>';
                return;
            }

            tbody.innerHTML = data.map(row => `
                <tr class="border-b border-gray-700 hover:bg-gray-700">
                <td class="py-2">${row.symbol}</td>
                <td class="py-2">$${parseFloat(row.price).toFixed(5)}</td>
                <td class="py-2">${row.change}</td>
                <td class="py-2">${row.tendencia}</td>
                <td class="py-2">${row.acao}</td>
                <td class="py-2">${row.time}</td>
                </tr>
            `).join('');
            
            // Atualiza o timestamp
            updateTimestamp();
        })
        .catch(() => {
            // Silenciando o erro para não confundir o usuário
            console.log("Recarregando dados em segundo plano...");
        });
}

// Display error message
function showErrorMessage(message) {
    // Remove any existing error messages
    const existingErrors = document.querySelectorAll('.api-error-alert');
    existingErrors.forEach(el => el.remove());
    
    // Create new error message
    const alertDiv = document.createElement('div');
    alertDiv.className = 'api-error-alert flex items-center justify-between';
    alertDiv.innerHTML = `
        <div class="flex items-center">
            <i class="ph ph-warning-circle text-red-400 mr-2"></i>
            ${message}
        </div>
        <button class="text-white hover:text-gray-200" onclick="this.parentElement.remove()">
            <i class="ph ph-x"></i>
        </button>
    `;
    
    // Insert at the top of the container
    const container = document.querySelector('.max-w-6xl');
    container.insertBefore(alertDiv, container.firstChild);
}