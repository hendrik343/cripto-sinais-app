/**
 * Função para buscar dados de gráficos do CoinGecko API
 * Suporta múltiplos idiomas para mensagens de erro
 */
async function fetchChartData(coin) {
  const COIN_MAP = {
    "shib": "shiba-inu",
    "pepe": "pepe",
    "btc": "bitcoin",
    "eth": "ethereum",
    "floki": "floki",
    "doge": "dogecoin",
    "sol": "solana"
  };

  const mappedCoin = COIN_MAP[coin] || coin;

  try {
    const res = await fetch(`https://api.coingecko.com/api/v3/coins/${mappedCoin}/market_chart?vs_currency=usd&days=30`);
    if (!res.ok) {
      throw new Error(`API returned status ${res.status}`);
    }
    const data = await res.json();
    return {
      labels: data.prices.map(item => new Date(item[0]).toLocaleDateString()),
      prices: data.prices.map(item => item[1]),
      volumes: data.total_volumes.map(item => item[1])
    };
  } catch (error) {
    console.error(`Error fetching data: ${error.message}`);
    const errorMessage = document.documentElement.lang === 'pt' 
      ? 'Erro ao carregar dados. Limite de API atingido, tente novamente em alguns minutos.' 
      : document.documentElement.lang === 'fr'
        ? 'Erreur lors du chargement des données. Limite API atteinte, réessayez dans quelques minutes.'
        : 'Error loading data. API rate limit reached, try again in a few minutes.';
    alert(errorMessage);
    return {
      labels: [],
      prices: [],
      volumes: []
    };
  }
}

/**
 * Verifica se o usuário tem acesso premium
 * Retorna uma Promise que resolve para true se o usuário é premium, false caso contrário
 */
async function checkPremiumAccess() {
  try {
    const response = await fetch('/api/check_premium');
    const data = await response.json();
    return data.premium === true;
  } catch (error) {
    console.error('Erro ao verificar acesso premium:', error);
    return false;
  }
}

/**
 * Renderiza um gráfico de preços usando Chart.js
 * 
 * @param {string} elementId - ID do elemento canvas para o gráfico
 * @param {object} chartData - Dados do gráfico (labels, prices, volumes)
 * @param {string} coinSymbol - Símbolo da moeda (ex: BTC, ETH)
 */
function renderPriceChart(elementId, chartData, coinSymbol) {
  const ctx = document.getElementById(elementId).getContext('2d');
  
  // Verifica se já existe um gráfico neste canvas e o destrói
  if (window.coinCharts && window.coinCharts[elementId]) {
    window.coinCharts[elementId].destroy();
  }
  
  // Inicializa o objeto de gráficos se ainda não existir
  if (!window.coinCharts) {
    window.coinCharts = {};
  }
  
  // Cria o novo gráfico
  window.coinCharts[elementId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: coinSymbol + ' ' + (document.documentElement.lang === 'pt' ? 'Preço' : 
                                     document.documentElement.lang === 'fr' ? 'Prix' : 'Price'),
          data: chartData.prices,
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          borderWidth: 2,
          pointRadius: 1,
          pointHoverRadius: 5,
          tension: 0.4,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#e2e8f0'
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          titleColor: '#e2e8f0',
          bodyColor: '#e2e8f0',
          borderColor: '#334155',
          borderWidth: 1
        }
      },
      scales: {
        x: {
          ticks: {
            color: '#94a3b8'
          },
          grid: {
            color: 'rgba(51, 65, 85, 0.5)'
          }
        },
        y: {
          ticks: {
            color: '#94a3b8',
            callback: function(value) {
              return '$' + value.toLocaleString();
            }
          },
          grid: {
            color: 'rgba(51, 65, 85, 0.5)'
          }
        }
      }
    }
  });
}

/**
 * Renderiza um gráfico de volume usando Chart.js
 * 
 * @param {string} elementId - ID do elemento canvas para o gráfico
 * @param {object} chartData - Dados do gráfico (labels, prices, volumes)
 * @param {string} coinSymbol - Símbolo da moeda (ex: BTC, ETH)
 */
function renderVolumeChart(elementId, chartData, coinSymbol) {
  const ctx = document.getElementById(elementId).getContext('2d');
  
  // Verifica se já existe um gráfico neste canvas e o destrói
  if (window.coinCharts && window.coinCharts[elementId]) {
    window.coinCharts[elementId].destroy();
  }
  
  // Inicializa o objeto de gráficos se ainda não existir
  if (!window.coinCharts) {
    window.coinCharts = {};
  }
  
  // Cria o novo gráfico
  window.coinCharts[elementId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: coinSymbol + ' ' + (document.documentElement.lang === 'pt' ? 'Volume' : 
                                     document.documentElement.lang === 'fr' ? 'Volume' : 'Volume'),
          data: chartData.volumes,
          backgroundColor: 'rgba(79, 70, 229, 0.7)',
          borderColor: 'rgba(79, 70, 229, 1)',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#e2e8f0'
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          titleColor: '#e2e8f0',
          bodyColor: '#e2e8f0',
          borderColor: '#334155',
          borderWidth: 1
        }
      },
      scales: {
        x: {
          ticks: {
            color: '#94a3b8'
          },
          grid: {
            color: 'rgba(51, 65, 85, 0.5)'
          }
        },
        y: {
          ticks: {
            color: '#94a3b8',
            callback: function(value) {
              return '$' + value.toLocaleString();
            }
          },
          grid: {
            color: 'rgba(51, 65, 85, 0.5)'
          }
        }
      }
    }
  });
}

/**
 * Carrega e renderiza gráficos para uma determinada moeda
 * 
 * @param {string} coin - ID da moeda (ex: bitcoin, ethereum)
 * @param {string} symbol - Símbolo da moeda (ex: BTC, ETH)
 * @param {string} priceChartId - ID do elemento canvas para o gráfico de preços
 * @param {string} volumeChartId - ID do elemento canvas para o gráfico de volume
 */
async function loadCoinCharts(coin, symbol, priceChartId, volumeChartId) {
  try {
    // Verifica se o usuário tem acesso premium
    const isPremium = await checkPremiumAccess();
    
    if (!isPremium && document.querySelector('.premium-content')) {
      // Se o usuário não tiver acesso premium e estiver em conteúdo premium,
      // redireciona para a página de preview
      window.location.href = '/premium-preview';
      return;
    }
    
    // Mostra mensagem de carregamento
    const loadingMessage = document.documentElement.lang === 'pt' 
        ? 'Carregando dados...' 
        : document.documentElement.lang === 'fr'
          ? 'Chargement des données...'
          : 'Loading data...';
    
    if (document.getElementById(priceChartId)) {
      document.getElementById(priceChartId).parentNode.innerHTML = 
        `<div class="text-center p-4"><div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2">${loadingMessage}</p></div>`;
    }
    
    // Busca os dados do gráfico
    const chartData = await fetchChartData(coin);
    
    // Renderiza os gráficos
    if (document.getElementById(priceChartId)) {
      renderPriceChart(priceChartId, chartData, symbol);
    }
    
    if (document.getElementById(volumeChartId)) {
      renderVolumeChart(volumeChartId, chartData, symbol);
    }
    
  } catch (error) {
    console.error('Erro ao carregar gráficos:', error);
    
    const errorMessage = document.documentElement.lang === 'pt' 
      ? 'Erro ao carregar gráficos. Tente novamente mais tarde.' 
      : document.documentElement.lang === 'fr'
        ? 'Erreur lors du chargement des graphiques. Veuillez réessayer plus tard.'
        : 'Error loading charts. Please try again later.';
    
    if (document.getElementById(priceChartId)) {
      document.getElementById(priceChartId).parentNode.innerHTML = 
        `<div class="alert alert-danger">${errorMessage}</div>`;
    }
  }
}