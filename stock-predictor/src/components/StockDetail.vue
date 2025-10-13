<template>
  <div
    class="h-screen w-screen flex flex-col overflow-hidden font-sans relative"
    :class="theme === 'dark' ? 'bg-background-dark text-text-primary' : 'bg-gray-100 text-gray-800'"
  >
    <!-- FINAL "STARFIELD" BACKGROUND -->
    <div id="star-background">
      <div id="stars1"></div>
      <div id="stars2"></div>
      <div id="stars3"></div>
    </div>


    <!-- "GLASS" HEADER BAR -->
    <header class="w-full flex justify-between items-center border-b px-4 h-14 flex-shrink-0 z-20 backdrop-blur-lg" :class="theme === 'dark' ? 'border-gray-800/50 bg-background-dark/50' : 'border-gray-200/50 bg-white/50'">
        <button @click="$router.push('/dashboard')" class="flex items-center gap-2 text-text-secondary hover:text-text-primary transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
            Dashboard
        </button>
        <div v-if="stock" class="flex items-center gap-4 text-right">
             <div 
                class="flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold"
                :class="marketStatus.class"
              >
                <div class="h-2 w-2 rounded-full" :class="marketStatus.dotClass"></div>
                <span>{{ marketStatus.text }}</span>
              </div>
        </div>
    </header>

    <!-- LOADING STATE -->
    <div v-if="!stock" class="flex-1 flex flex-col items-center justify-center relative z-10">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
      <p class="mt-4 text-lg text-text-secondary">Loading Terminal...</p>
    </div>
    
    <!-- MAIN GRID -->
    <main v-else class="flex-1 grid grid-cols-1 lg:grid-cols-4 xl:grid-cols-5 overflow-hidden relative z-10">
      
      <!-- MAIN PANEL -->
      <div class="lg:col-span-3 xl:col-span-4 h-full flex flex-col p-4 sm:p-6">
        
        <div class="flex-shrink-0 mb-6">
            <h1 class="text-5xl sm:text-7xl font-bold tracking-tighter">{{ stock.name }}</h1>
            <p class="text-xl sm:text-2xl text-text-secondary mt-1 font-mono">{{ stock.symbol }}</p>
        </div>
        
        <!-- Price & Prediction Header -->
        <div class="flex-shrink-0 mb-6 flex items-end justify-between">
            <div>
                <p class="text-7xl sm:text-8xl font-bold font-mono tracking-tight">₹{{ stock.current.toFixed(2) }}</p>
                <p class="text-2xl font-semibold mt-1" :class="stock.change >= 0 ? 'text-accent' : 'text-red-500'">
                    {{ stock.change >= 0 ? '▲' : '▼' }} {{ Math.abs(stock.change).toFixed(2) }}%
                </p>
            </div>
            <!-- LIVE PREDICTION DISPLAY -->
            <div class="text-right pb-2" v-if="isMarketOpen">
                <p class="text-text-secondary text-sm mb-1">AI Prediction (5 min)</p>
                 <p v-if="livePrediction" :class="livePredictionStatus.class" class="text-3xl font-mono font-bold transition-colors duration-300">
                    ₹{{ livePrediction.toFixed(2) }}
                </p>
                <p v-else class="text-gray-500 animate-pulse text-xl">Calculating...</p>
            </div>
        </div>

        <!-- Chart Container -->
        <div class="flex-1 min-h-0 w-full relative">
            <canvas id="stockChart"></canvas>
        </div>
      </div>

      <!-- SIDEBAR -->
      <aside class="lg:col-span-1 xl:col-span-1 border-l flex flex-col z-20 backdrop-blur-lg" :class="theme === 'dark' ? 'border-gray-800/50 bg-background-sidebar/50' : 'border-gray-200/50 bg-white/50'">
        <h2 class="text-lg font-semibold p-4 border-b flex-shrink-0" :class="theme === 'dark' ? 'border-gray-800/80' : 'border-gray-200/80'">
            Analysis & Data
        </h2>
        <div class="overflow-y-auto flex-1">
            <!-- Daily Forecast (Only shows when market is closed) -->
            <div class="data-module" v-if="!isMarketOpen">
              <h3 class="module-title">AI Forecast</h3>
              <div class="text-center py-4">
                <p class="text-text-secondary text-sm mb-2">Outlook (Next Trading Day)</p>
                <div class="text-3xl font-bold h-10">
                    <p v-if="dailyPrediction" class="text-cyan-400">{{ dailyPrediction }}</p>
                    <p v-else class="text-gray-500 animate-pulse text-xl">Not Calculated</p>
                </div>
              </div>
            </div>
            <!-- Performance Module -->
            <div class="data-module">
              <h3 class="module-title">Performance</h3>
              <div class="module-content">
                  <div class="data-row group"><span>Day's High</span><span class="font-mono">₹{{ stock.dayHigh.toFixed(2) }}</span></div>
                  <div class="data-row group"><span>Day's Low</span><span class="font-mono">₹{{ stock.dayLow.toFixed(2) }}</span></div>
                  <div class="data-row group"><span>Prev. Close</span><span class="font-mono">₹{{ stock.previousClose.toFixed(2) }}</span></div>
              </div>
            </div>
            <!-- Key Info Module -->
            <div class="data-module">
              <h3 class="module-title">Key Information</h3>
              <div class="module-content">
                  <div class="data-row group"><span>Market Cap</span><span>{{ stock.marketCap ? formatMarketCap(stock.marketCap) : 'N/A' }}</span></div>
                  <div class="data-row group"><span>Sector</span><span class="text-right truncate">{{ stock.sector || 'N/A' }}</span></div>
                  <div class="data-row group"><span>Exchange</span><span>{{ stock.symbol.includes('.NS') ? 'NSE' : 'BSE' }}</span></div>
              </div>
            </div>
            <!-- About Module -->
            <div class="data-module">
              <h3 class="module-title">About {{ stock.name.split(' ')[0] }}</h3>
               <p class="text-text-secondary text-sm leading-relaxed max-h-48 overflow-y-auto pr-2 module-scroll">
                    {{ stock.summary || 'No company summary available.' }}
                </p>
            </div>
        </div>
      </aside>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue";
import Chart from "chart.js/auto";
import annotationPlugin from 'chartjs-plugin-annotation';
import axios from "axios";
import { useRoute } from "vue-router";

Chart.register(annotationPlugin);

const theme = ref('dark'); const route = useRoute(); const symbol = route.params.symbol; const stock = ref(null); const isMarketOpen = ref(false); const livePrediction = ref(null); const dailyPrediction = ref(null); const priceStreamStatus = ref('disconnected'); let chartInstance = null; let priceEventSource = null; let predictionEventSource = null;

const livePredictionStatus = computed(() => { if (!livePrediction.value || !stock.value) return { class: 'text-gray-500' }; if (livePrediction.value > stock.value.current) return { class: 'text-accent' }; if (livePrediction.value < stock.value.current) return { class: 'text-red-500' }; return { class: 'text-gray-400' }; });
const marketStatus = computed(() => { if (!isMarketOpen.value) return { class: 'bg-gray-500/10 text-gray-400', dotClass: 'bg-gray-500', text: 'Market Closed' }; switch (priceStreamStatus.value) { case 'connected': return { class: 'bg-accent/10 text-accent', dotClass: 'bg-accent animate-pulse', text: 'Live' }; case 'error': return { class: 'bg-yellow-500/10 text-yellow-400', dotClass: 'bg-yellow-500', text: 'Error' }; default: return { class: 'bg-blue-500/10 text-blue-400', dotClass: 'bg-blue-500 animate-pulse', text: 'Connecting...' }; } });

const checkIfMarketIsOpen = () => { const now = new Date(); const utcDay = now.getUTCDay(); const utcHours = now.getUTCHours(); const utcMinutes = now.getUTCMinutes(); const marketOpenUTC = 3 * 60 + 45; const marketCloseUTC = 10 * 60; if (utcDay > 0 && utcDay < 6) { const currentTimeInMinutes = utcHours * 60 + utcMinutes; return currentTimeInMinutes >= marketOpenUTC && currentTimeInMinutes <= marketCloseUTC; } return false; };
const fetchStock = async () => { isMarketOpen.value = checkIfMarketIsOpen(); const endpoint = isMarketOpen.value ? `/stock/${symbol}` : `/stock_history/${symbol}`; try { const res = await axios.get(`http://127.0.0.1:5000${endpoint}`); stock.value = res.data; await nextTick(); drawChart(res.data.intraday_trend); if (isMarketOpen.value) { startPriceStream(symbol); startLivePredictionStream(symbol); } else { fetchDailyPrediction(symbol); } } catch (error) { console.error(`Failed to fetch from ${endpoint}:`, error); stock.value = { name: "Data not available", symbol: symbol, current: 0, change: 0, dayHigh: 0, dayLow: 0, previousClose: 0, summary: "Could not load profile." }; } };
const fetchDailyPrediction = async (symbol) => { try { const res = await axios.get(`http://127.0.0.1:5000/prediction/daily/${symbol}`); dailyPrediction.value = res.data.outlook; } catch(error) { console.error("Could not fetch daily prediction:", error); } };

const startPriceStream = (symbol) => {
    if (priceEventSource) priceEventSource.close();
    priceEventSource = new EventSource(`http://127.0.0.1:5000/stream/${symbol}`);
    priceStreamStatus.value = 'connecting';
    priceEventSource.onopen = () => { priceStreamStatus.value = 'connected'; };
    priceEventSource.onerror = () => { priceStreamStatus.value = 'error'; };

    priceEventSource.onmessage = (event) => {
        if (!stock.value || !chartInstance) return;
        const data = JSON.parse(event.data);
        const newTime = new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        stock.value.current = data.price;
        stock.value.change = ((data.price - stock.value.previousClose) / stock.value.previousClose) * 100;
        stock.value.updated = newTime;

        const labelIndex = chartInstance.data.labels.indexOf(newTime);
        if (labelIndex !== -1) {
            chartInstance.data.datasets[0].data[labelIndex] = data.price;
            chartInstance.data.datasets[1].data[labelIndex] = data.price;
        }
        
        // Use the default animation by calling update() without arguments
        chartInstance.update();
    };
};
const startLivePredictionStream = (symbol) => { if (predictionEventSource) predictionEventSource.close(); predictionEventSource = new EventSource(`http://127.0.0.1:5000/stream/prediction/${symbol}`); predictionEventSource.onmessage = (event) => { const data = JSON.parse(event.data); if (data && data.prediction) { livePrediction.value = data.prediction; } }; };

// --- CHART & UTILITIES (with Interactive Updates) ---
const generateTimeLabels = () => {
    const labels = [];
    let hour = 9, minute = 15;
    while (hour < 15 || (hour === 15 && minute <= 30)) {
        labels.push(`${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`);
        minute += 5;
        if (minute >= 60) { minute -= 60; hour += 1; }
    }
    return labels;
};

const drawChart = (data) => {
  if (!data) return;
  const ctx = document.getElementById("stockChart");
  if (!ctx) return;
  if (chartInstance) chartInstance.destroy();
  
  const fullTimelineLabels = generateTimeLabels();
  const dataMap = new Map(data.map(d => [d.time || d.date, d.price]));
  const prices = fullTimelineLabels.map(label => dataMap.get(label) || null);
  
  const isUp = stock.value.change >= 0;
  const glowColor = isUp ? 'rgba(45, 212, 191, 1)' : 'rgba(248, 113, 113, 1)';
  const backgroundColor = isUp ? 'rgba(45, 212, 191, 0.1)' : 'rgba(248, 113, 113, 0.1)';

  chartInstance = new Chart(ctx, { 
    type: 'line', 
    data: { 
      labels: fullTimelineLabels, 
      datasets: [
        { label: 'Price', data: prices, borderColor: glowColor, borderWidth: 2, fill: false, tension: 0.1, pointRadius: 0, shadowOffsetX: 0, shadowOffsetY: 0, shadowBlur: 10, shadowColor: glowColor },
        { label: 'Fill', data: prices, borderColor: 'transparent', backgroundColor: backgroundColor, fill: true, tension: 0.1, borderWidth: 0, pointRadius: 0, pointHitRadius: 0 }
      ] 
    }, 
    options: { 
        responsive: true, 
        maintainAspectRatio: false,
        animation: { duration: 800, easing: 'easeOutQuart' },
        interaction: { mode: 'index', intersect: false, axis: 'x' },
        plugins: { 
            legend: { display: false },
            tooltip: { 
                enabled: true, mode: 'index', intersect: false, position: 'nearest',
                backgroundColor: 'rgba(0, 0, 0, 0.8)', titleFont: { size: 14, weight: 'bold' },
                bodyFont: { size: 12 }, padding: 10,
                filter: (item) => item.datasetIndex === 0 && item.raw !== null,
                callbacks: { title: (c) => c[0].label, label: (c) => `Price: ₹${c.parsed.y.toFixed(2)}` } 
            },
            annotation: {
                annotations: {
                    previousCloseLine: {
                        type: 'line', yMin: stock.value.previousClose, yMax: stock.value.previousClose,
                        borderColor: 'rgba(156, 163, 175, 0.4)', borderWidth: 1.5, borderDash: [6, 6],
                        label: {
                            content: 'Prev. Close', position: 'start',
                            backgroundColor: 'rgba(156, 163, 175, 0.1)', color: 'rgba(209, 213, 219, 0.7)',
                            font: { size: 10 }, padding: 4, yAdjust: -10, enabled: true
                        }
                    }
                }
            }
        }, 
        scales: { 
            x: { ticks: { color: "#9CA3AF", maxRotation: 0, autoSkip: true, maxTicksLimit: 12 }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }, 
            y: { position: 'right', ticks: { color: "#9CA3AF" }, grid: { color: 'rgba(255, 255, 255, 0.05)' } } 
        } 
    } 
  });
};

const formatMarketCap = (cap) => { if (cap >= 1e12) return `₹${(cap / 1e12).toFixed(2)}T`; if (cap >= 1e9) return `₹${(cap / 1e9).toFixed(2)}B`; return `₹${(cap / 1e6).toFixed(2)}M`; };

// --- LIFECYCLE HOOKS ---
onMounted(() => {
    fetchStock();
    axios.post(`http://127.0.0.1:5000/predict/start/${symbol}`);
    axios.post(`http://127.0.0.1:5000/train/on_demand/${symbol}`);
});

onUnmounted(() => {
    if (priceEventSource) priceEventSource.close();
    if (predictionEventSource) predictionEventSource.close();
    if (chartInstance) chartInstance.destroy();
    axios.post(`http://127.0.0.1:5000/predict/stop/${symbol}`);
});
</script>

<style>
/* Base Styles & Color Variables */
:root { --background-dark: #0A0E13; --background-sidebar: #07090D; --text-primary: #E5E7EB; --text-secondary: #9CA3AF; --accent: #2DD4BF; --red: #F87171; }
.font-sans { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
.font-mono { font-family: 'Menlo', 'Consolas', 'Monaco', 'Liberation Mono', 'Lucida Console', monospace; }
.bg-background-dark { background-color: var(--background-dark); } .bg-background-sidebar { background-color: var(--background-sidebar); } .text-text-primary { color: var(--text-primary); } .text-text-secondary { color: var(--text-secondary); } .text-accent { color: var(--accent); } .text-red-500 { color: var(--red); } .border-accent { border-color: var(--accent); }

/* Sidebar Module Styles */
.data-module { @apply p-4 border-b border-gray-800/80; }
.module-title { @apply text-sm font-semibold text-text-secondary mb-3 uppercase tracking-wider; }
.module-content { @apply space-y-2 text-sm; }
.data-row { @apply flex justify-between items-center; }
.data-row span:first-child { @apply text-text-secondary; }
.module-scroll::-webkit-scrollbar { width: 4px; }
.module-scroll::-webkit-scrollbar-track { background: transparent; }
.module-scroll::-webkit-scrollbar-thumb { @apply bg-gray-700 rounded-full; }

/* FINAL "STARFIELD" BACKGROUND */
@keyframes animStar { from { transform: translateY(0px); } to { transform: translateY(-2000px); } }
#star-background { position: fixed; top: 0; left: 0; width: 100%; height: 2000px; z-index: -1; }
#stars1, #stars2, #stars3 { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: transparent; }
#stars1 { background-image: radial-gradient(.5px .5px at 10vw 20vh, white, transparent), radial-gradient(.5px .5px at 40vw 50vh, white, transparent), radial-gradient(1px 1px at 90vw 30vh, white, transparent); animation: animStar 70s linear infinite; }
#stars2 { background-image: radial-gradient(.5px .5px at 30vw 80vh, white, transparent), radial-gradient(1px 1px at 60vw 10vh, white, transparent), radial-gradient(.5px .5px at 80vw 90vh, white, transparent); animation: animStar 120s linear infinite; }
#stars3 { background-image: radial-gradient(.5px .5px at 5vw 95vh, white, transparent), radial-gradient(1px 1px at 50vw 5vh, white, transparent), radial-gradient(.5px .5px at 70vw 60vh, white, transparent); animation: animStar 180s linear infinite; }
</style>