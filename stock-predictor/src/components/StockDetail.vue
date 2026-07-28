<template>
  <div class="page-container" :class="theme === 'light' ? 'light-mode' : 'dark-mode'">
    <header class="header">
      <button @click="$router.push('/dashboard')" class="back-btn">← Dashboard</button>
      <div style="display: flex; align-items: center; gap: 16px;">
        <button @click="toggleTheme" class="theme-toggle" :title="theme === 'dark' ? 'Switch to light' : 'Switch to dark'">
          <svg v-if="theme === 'dark'" style="width: 20px; height: 20px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="12" r="5" stroke-width="2"/><path stroke-width="2" stroke-linecap="round" d="M12 1v2m0 18v2m11-11h-2M3 12H1m16.36-7.36l-1.41 1.41M6.05 17.95l-1.41 1.41m12.72 0l-1.41-1.41M6.05 6.05L4.64 4.64"/></svg>
          <svg v-else style="width: 20px; height: 20px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
        </button>
        <div v-if="stock" class="market-indicator" :class="marketStatus.class">
          <span class="dot" :class="marketStatus.dotClass"></span>
          {{ marketStatus.text }}
        </div>
      </div>
    </header>

    <div v-if="!stock" class="loading-state">
      <div class="spinner"></div>
      <p>Loading market data…</p>
    </div>

    <main v-else class="main-content">
      <div class="chart-section">
        <div class="stock-header">
          <div class="stock-info">
            <h1 class="stock-name">{{ stock.name }}</h1>
            <span class="stock-symbol">{{ stock.symbol }}</span>
          </div>
          <div class="price-info">
            <div class="current-price">₹{{ stock.current.toFixed(2) }}</div>
            <div class="price-change" :class="stock.change >= 0 ? 'badge-positive' : 'badge-negative'">
              {{ stock.change >= 0 ? '▲' : '▼' }} {{ Math.abs(stock.change).toFixed(2) }}%
            </div>
          </div>
        </div>

        <div class="toolbar">
          <div class="segmented-control">
            <button :class="{active: chartMode === 'line'}" @click="chartMode = 'line'">Line</button>
            <button :class="{active: chartMode === 'candle'}" @click="chartMode = 'candle'">Candles</button>
          </div>
          <div class="indicator-toggles">
            <label class="toggle-label"><input v-model="indicators.bollinger" type="checkbox" /> Bollinger</label>
            <label class="toggle-label"><input v-model="indicators.rsi" type="checkbox" /> RSI</label>
            <label class="toggle-label"><input v-model="indicators.macd" type="checkbox" /> MACD</label>
          </div>
        </div>

        <div class="chart-container">
          <canvas ref="priceCanvas"></canvas>
        </div>

        <div v-if="indicators.rsi" class="indicator-container">
          <div class="indicator-header">RSI (14) <span class="indicator-meta">Overbought 70 · Oversold 30</span></div>
          <canvas ref="rsiCanvas"></canvas>
        </div>
        <div v-if="indicators.macd" class="indicator-container">
          <div class="indicator-header">MACD (12, 26, 9)</div>
          <canvas ref="macdCanvas"></canvas>
        </div>

        <div class="panel news-panel">
          <h2 class="panel-title">Latest News</h2>
          <div class="news-grid">
            <a v-for="(n, i) in stockNews" :key="i" :href="n.link" target="_blank" class="news-card">
              <div class="news-meta">{{ n.provider }} &middot; {{ new Date(n.pubDate).toLocaleDateString() }}</div>
              <h3 class="news-title">{{ n.title }}</h3>
              <p class="news-summary">{{ n.summary }}</p>
            </a>
          </div>
          <p v-if="stockNews.length === 0" class="empty-msg">No news available at the moment.</p>
        </div>
      </div>

      <div class="sidebar">
        <div v-if="isMarketOpen" class="panel">
          <h2 class="panel-title">AI Prediction (5 min)</h2>
          <div v-if="livePrediction" class="prediction-value" :class="livePredictionStatus.class">
            ₹{{ livePrediction.toFixed(2) }}
          </div>
          <div v-else class="loading-text">Calculating…</div>
        </div>
        <div v-else class="panel">
          <h2 class="panel-title">AI Forecast</h2>
          <div class="forecast-value">{{ dailyPrediction || 'Not calculated' }}</div>
        </div>

        <div class="panel">
          <h2 class="panel-title">Paper Trading</h2>
          <div class="trade-form">
            <input v-model.number="tradeQuantity" min="1" type="number" class="qty-input" aria-label="Share quantity" />
            <button @click="placePaperOrder('BUY')" class="btn-buy">Buy</button>
            <button @click="placePaperOrder('SELL')" class="btn-sell">Sell</button>
          </div>
          <p v-if="traderMessage" class="status-msg">{{ traderMessage }}</p>
        </div>

        <div class="panel">
          <h2 class="panel-title">Custom Alerts</h2>
          <button @click="enableAiAlert" class="btn-alert-ai">AI move ≥ 1.5%</button>
          <div class="alert-form">
            <select v-model="priceAlertDirection" class="alert-select">
              <option value="below">Below</option>
              <option value="above">Above</option>
            </select>
            <input v-model.number="priceAlertThreshold" type="number" min="0.01" step="0.01" placeholder="Price ₹" class="alert-input" />
            <button @click="enablePriceAlert" class="btn-alert-set">Set</button>
          </div>
        </div>

        <div class="panel">
          <h2 class="panel-title">Performance</h2>
          <div class="key-value-row">
            <span class="kv-label">Day's High</span>
            <span class="kv-value">₹{{ stock.dayHigh.toFixed(2) }}</span>
          </div>
          <div class="key-value-row">
            <span class="kv-label">Day's Low</span>
            <span class="kv-value">₹{{ stock.dayLow.toFixed(2) }}</span>
          </div>
          <div class="key-value-row">
            <span class="kv-label">Prev. Close</span>
            <span class="kv-value">₹{{ stock.previousClose.toFixed(2) }}</span>
          </div>
        </div>

        <div class="panel">
          <h2 class="panel-title">Key Information</h2>
          <div class="key-value-row">
            <span class="kv-label">Market Cap</span>
            <span class="kv-value">{{ stock.marketCap ? formatMarketCap(stock.marketCap) : 'N/A' }}</span>
          </div>
          <div class="key-value-row">
            <span class="kv-label">Sector</span>
            <span class="kv-value">{{ stock.sector || 'N/A' }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from "vue";
import Chart from "chart.js/auto";
import annotationPlugin from "chartjs-plugin-annotation";
import { CandlestickController, CandlestickElement } from "chartjs-chart-financial";
import "chartjs-adapter-date-fns";
import { useRoute } from "vue-router";
import api from "../api";
import { useTheme } from "../composables/useTheme";

Chart.register(annotationPlugin, CandlestickController, CandlestickElement);
const { theme, toggleTheme } = useTheme(); const route = useRoute(); const symbol = route.params.symbol; const stock = ref(null);
const stockNews = ref([]);
const dailyPrediction = ref(null);
const livePrediction = ref(null); const priceStreamStatus = ref("disconnected");
const chartMode = ref("line"); const indicators = reactive({ rsi: false, macd: false, bollinger: false }); const priceCanvas = ref(null); const rsiCanvas = ref(null); const macdCanvas = ref(null);
const tradeQuantity = ref(1); const priceAlertDirection = ref("below"); const priceAlertThreshold = ref(null); const traderMessage = ref("");
let priceChart; let rsiChart; let macdChart; let priceEventSource; let predictionEventSource; let candles = [];

const livePredictionStatus = computed(() => !livePrediction.value || !stock.value ? { class: "muted" } : livePrediction.value > stock.value.current ? { class: "gain" } : livePrediction.value < stock.value.current ? { class: "loss" } : { class: "muted" });
const marketStatus = computed(() => { if (!isMarketOpen.value) return { class: "closed", dotClass: "dot gray", text: "Market Closed" }; if (priceStreamStatus.value === "connected") return { class: "live", dotClass: "dot green", text: "Live" }; if (priceStreamStatus.value === "error") return { class: "warning", dotClass: "dot yellow", text: "Connection error" }; return { class: "connecting", dotClass: "dot blue", text: "Connecting…" }; });
const checkIfMarketIsOpen = () => { const now = new Date(); const day = now.getUTCDay(); const minutes = now.getUTCHours() * 60 + now.getUTCMinutes(); return day > 0 && day < 6 && minutes >= 225 && minutes <= 600; };
const closes = () => candles.map((item) => item.close);
const asPoints = (values) => values.map((value, index) => value == null ? null : ({ x: candles[index].x, y: value }));
const chartColors = computed(() => theme.value === 'dark' 
  ? { teal: "#10b981", red: "#ef4444", grid: "rgba(255, 255, 255, 0.06)", text: "#a3a3a3" }
  : { teal: "#10b981", red: "#ef4444", grid: "rgba(0, 0, 0, 0.06)", text: "#737373" });

function simpleMovingAverage(values, period) { return values.map((_, index) => index < period - 1 ? null : values.slice(index - period + 1, index + 1).reduce((total, value) => total + value, 0) / period); }
function ema(values, period) { const output = Array(values.length).fill(null); const multiplier = 2 / (period + 1); let seed = []; let previous = null; values.forEach((value, index) => { if (value == null) return; if (previous == null) { seed.push(value); if (seed.length === period) { previous = seed.reduce((sum, item) => sum + item, 0) / period; output[index] = previous; } } else { previous = (value - previous) * multiplier + previous; output[index] = previous; } }); return output; }
function rsi(values, period = 14) { const output = Array(values.length).fill(null); if (values.length <= period) return output; let gains = 0; let losses = 0; for (let index = 1; index <= period; index += 1) { const diff = values[index] - values[index - 1]; gains += Math.max(diff, 0); losses += Math.max(-diff, 0); } let averageGain = gains / period; let averageLoss = losses / period; output[period] = averageLoss === 0 ? 100 : 100 - 100 / (1 + averageGain / averageLoss); for (let index = period + 1; index < values.length; index += 1) { const diff = values[index] - values[index - 1]; averageGain = (averageGain * (period - 1) + Math.max(diff, 0)) / period; averageLoss = (averageLoss * (period - 1) + Math.max(-diff, 0)) / period; output[index] = averageLoss === 0 ? 100 : 100 - 100 / (1 + averageGain / averageLoss); } return output; }
function bollinger(values, period = 20) { const middle = simpleMovingAverage(values, period); return { middle, upper: middle.map((mean, index) => { if (mean == null) return null; const variance = values.slice(index - period + 1, index + 1).reduce((sum, value) => sum + (value - mean) ** 2, 0) / period; return mean + 2 * Math.sqrt(variance); }), lower: middle.map((mean, index) => { if (mean == null) return null; const variance = values.slice(index - period + 1, index + 1).reduce((sum, value) => sum + (value - mean) ** 2, 0) / period; return mean - 2 * Math.sqrt(variance); }) }; }
function macd(values) { const line = ema(values, 12).map((fast, index) => fast == null || ema(values, 26)[index] == null ? null : fast - ema(values, 26)[index]); const signal = ema(line, 9); return { line, signal, histogram: line.map((item, index) => item == null || signal[index] == null ? null : item - signal[index]) }; }
function commonOptions() { return { responsive: true, maintainAspectRatio: false, animation: { duration: 250 }, interaction: { mode: "index", intersect: false }, plugins: { legend: { labels: { color: chartColors.value.text, boxWidth: 12 } }, tooltip: { backgroundColor: theme.value === 'dark' ? "rgba(0, 0, 0, 0.95)" : "rgba(255, 255, 255, 0.95)", titleColor: theme.value === 'dark' ? "#f9fafb" : "#111827", bodyColor: theme.value === 'dark' ? "#d1d5db" : "#374151" } }, scales: { x: { type: "time", time: { unit: "minute", tooltipFormat: "HH:mm" }, ticks: { color: chartColors.value.text, autoSkip: true, maxTicksLimit: 10 }, grid: { color: chartColors.value.grid } }, y: { position: "right", ticks: { color: chartColors.value.text, callback: (value) => `₹${value}` }, grid: { color: chartColors.value.grid } } } }; }
function renderPriceChart() { if (!priceCanvas.value || !candles.length) return; priceChart?.destroy(); const options = commonOptions(); const data = { datasets: [] }; const volumes = candles.map((item) => item.volume || 0); const rising = stock.value.change >= 0; if (chartMode.value === "candle") { data.datasets.push({ type: "candlestick", label: "OHLC", data: candles.map(({ x, open, high, low, close }) => ({ x, o: open, h: high, l: low, c: close })), color: { up: "#2dd4bf", down: "#f87171", unchanged: "#94a3b8" }, borderColor: { up: "#2dd4bf", down: "#f87171", unchanged: "#94a3b8" }, yAxisID: "y" }); } else { data.datasets.push({ type: "line", label: "Price", data: asPoints(closes()), borderColor: rising ? chartColors.value.teal : chartColors.value.red, backgroundColor: rising ? "rgba(45,212,191,.10)" : "rgba(248,113,113,.10)", fill: true, tension: .15, pointRadius: 0, borderWidth: 2, yAxisID: "y" }); }
  if (indicators.bollinger) { const bands = bollinger(closes()); data.datasets.push({ type: "line", label: "Bollinger upper", data: asPoints(bands.upper), borderColor: "rgba(96,165,250,.8)", borderDash: [5, 4], pointRadius: 0, borderWidth: 1, yAxisID: "y" }, { type: "line", label: "Bollinger mid", data: asPoints(bands.middle), borderColor: "rgba(148,163,184,.7)", pointRadius: 0, borderWidth: 1, yAxisID: "y" }, { type: "line", label: "Bollinger lower", data: asPoints(bands.lower), borderColor: "rgba(96,165,250,.8)", borderDash: [5, 4], pointRadius: 0, borderWidth: 1, yAxisID: "y" }); }
  data.datasets.push({ type: "bar", label: "Volume", data: candles.map((item) => ({ x: item.x, y: item.volume || 0 })), yAxisID: "volume", backgroundColor: candles.map((item) => item.close >= item.open ? "rgba(45,212,191,.30)" : "rgba(248,113,113,.30)"), borderWidth: 0, barPercentage: .9, categoryPercentage: .92 });
  options.scales.volume = { display: false, position: "left", beginAtZero: true, suggestedMax: Math.max(...volumes, 1) * 4, grid: { display: false } }; options.plugins.annotation = { annotations: { previousClose: { type: "line", yMin: stock.value.previousClose, yMax: stock.value.previousClose, borderColor: "rgba(148,163,184,.55)", borderDash: [5, 4], borderWidth: 1 } } }; options.plugins.tooltip.callbacks = { label(context) { if (context.dataset.type === "candlestick") { const raw = context.raw; return `O ₹${raw.o.toFixed(2)}  H ₹${raw.h.toFixed(2)}  L ₹${raw.l.toFixed(2)}  C ₹${raw.c.toFixed(2)}`; } const val = context.parsed.y; if (context.dataset.label === "Volume") return `Volume: ${Number(val).toLocaleString("en-IN")}`; return `${context.dataset.label}: ₹${Number(val).toFixed(2)}`; } }; priceChart = new Chart(priceCanvas.value, { type: chartMode.value === "candle" ? "candlestick" : "line", data, options }); }
function renderRsi() { if (!indicators.rsi || !rsiCanvas.value) return; rsiChart?.destroy(); const options = commonOptions(); options.scales.y = { min: 0, max: 100, position: "right", ticks: { color: chartColors.value.text }, grid: { color: chartColors.value.grid } }; options.plugins.legend.display = false; options.plugins.annotation = { annotations: { high: { type: "line", yMin: 70, yMax: 70, borderColor: "rgba(248,113,113,.75)", borderDash: [5,4] }, low: { type: "line", yMin: 30, yMax: 30, borderColor: "rgba(45,212,191,.75)", borderDash: [5,4] } } }; rsiChart = new Chart(rsiCanvas.value, { type: "line", data: { datasets: [{ label: "RSI", data: asPoints(rsi(closes())), borderColor: "#a78bfa", pointRadius: 0, tension: .15, borderWidth: 1.5 }] }, options }); }
function renderMacd() { if (!indicators.macd || !macdCanvas.value) return; macdChart?.destroy(); const values = macd(closes()); const options = commonOptions(); options.scales.y.ticks.callback = (value) => value.toFixed(2); options.plugins.annotation = { annotations: { zero: { type: "line", yMin: 0, yMax: 0, borderColor: "rgba(148,163,184,.5)" } } }; macdChart = new Chart(macdCanvas.value, { type: "bar", data: { datasets: [{ type: "bar", label: "Histogram", data: asPoints(values.histogram), backgroundColor: values.histogram.map((value) => value >= 0 ? "rgba(45,212,191,.55)" : "rgba(248,113,113,.55)"), borderWidth: 0 }, { type: "line", label: "MACD", data: asPoints(values.line), borderColor: "#60a5fa", pointRadius: 0, borderWidth: 1.5 }, { type: "line", label: "Signal", data: asPoints(values.signal), borderColor: "#fbbf24", pointRadius: 0, borderWidth: 1.5 }] }, options }); }
function renderCharts() { renderPriceChart(); nextTick(() => { renderRsi(); renderMacd(); }); }
function normaliseCandle(point) { const close = Number(point.close ?? point.price); return { time: point.time || point.date, x: Date.parse(point.timestamp) || Date.now(), open: Number(point.open ?? close), high: Number(point.high ?? close), low: Number(point.low ?? close), close, volume: Number(point.volume || 0) }; }
const fetchStock = async () => {
    isMarketOpen.value = checkIfMarketIsOpen();
    const endpoint = isMarketOpen.value ? `/stock/${symbol}` : `/stock_history/${symbol}`;
    try {
      const [stockRes, dailyRes, newsRes] = await Promise.all([
        api.get(endpoint),
        api.get(`/prediction/daily/${symbol}`).catch(() => ({ data: { outlook: null } })),
        api.get(`/api/news/${symbol}`).catch(() => ({ data: [] }))
      ]);
      stock.value = stockRes.data;
      candles = (stockRes.data.intraday_trend || []).map(normaliseCandle);
      dailyPrediction.value = dailyRes.data.outlook;
      stockNews.value = newsRes.data;
      await nextTick();
      renderCharts();
      if (isMarketOpen.value) { startPriceStream(); startLivePredictionStream(); }
    } catch (error) {
      console.error("Could not load stock", error);
      stock.value = { name: "Data not available", symbol, current: 0, change: 0, dayHigh: 0, dayLow: 0, previousClose: 0, summary: "Could not load profile." };
    }
  };
function startPriceStream() { priceEventSource?.close(); priceEventSource = new EventSource(`${api.defaults.baseURL}/stream/${symbol}`); priceStreamStatus.value = "connecting"; priceEventSource.onopen = () => { priceStreamStatus.value = "connected"; }; priceEventSource.onerror = () => { priceStreamStatus.value = "error"; }; priceEventSource.onmessage = (event) => { const tick = JSON.parse(event.data); const tickDate = tick.timestamp ? new Date(tick.timestamp) : new Date(); const time = tickDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); const close = Number(tick.price); stock.value.current = close; stock.value.change = stock.value.previousClose ? ((close - stock.value.previousClose) / stock.value.previousClose) * 100 : 0; const last = candles.at(-1); if (last && last.time === time) { last.high = Math.max(last.high, close); last.low = Math.min(last.low, close); last.close = close; } else candles.push({ time, x: tickDate.getTime(), open: last?.close ?? close, high: close, low: close, close, volume: 0 }); renderCharts(); }; }
function startLivePredictionStream() { predictionEventSource?.close(); predictionEventSource = new EventSource(`${api.defaults.baseURL}/stream/prediction/${symbol}`); predictionEventSource.onmessage = (event) => { const data = JSON.parse(event.data); if (data?.prediction) livePrediction.value = data.prediction; }; }
const formatMarketCap = (cap) => cap >= 1e12 ? `₹${(cap / 1e12).toFixed(2)}T` : cap >= 1e9 ? `₹${(cap / 1e9).toFixed(2)}B` : `₹${(cap / 1e6).toFixed(2)}M`;
const placePaperOrder = async (side) => { try { const result = await api.post("/api/orders", { symbol, side, quantity: tradeQuantity.value }); traderMessage.value = `${result.data.side} filled at ₹${(result.data.price_paise / 100).toFixed(2)}.`; } catch (error) { traderMessage.value = error.response?.data?.error || "Sign in to place paper orders."; } };
const enableAiAlert = async () => { try { await api.post("/api/alerts", { symbol, kind: "ai_movement" }); traderMessage.value = "AI alert enabled."; } catch (error) { traderMessage.value = error.response?.data?.error || "Sign in to create alerts."; } };
const enablePriceAlert = async () => { try { await api.post("/api/alerts", { symbol, kind: "price", direction: priceAlertDirection.value, threshold: priceAlertThreshold.value }); traderMessage.value = "Price alert enabled."; } catch (error) { traderMessage.value = error.response?.data?.error || "Enter a valid price and sign in."; } };
watch([chartMode, theme, () => indicators.rsi, () => indicators.macd, () => indicators.bollinger], renderCharts);
onMounted(() => { fetchStock(); api.post(`/predict/start/${symbol}`); api.post(`/train/on_demand/${symbol}`); });
onUnmounted(() => { priceEventSource?.close(); predictionEventSource?.close(); priceChart?.destroy(); rsiChart?.destroy(); macdChart?.destroy(); });
</script>

<style scoped>
:root {
  --bg-color: #ffffff;
  --bg-secondary: #f9fafb;
  --border-color: #e5e7eb;
  --text-main: #111827;
  --text-muted: #6b7280;
  --primary: #000000;
  --emerald: #10b981;
  --emerald-bg: #dcfce7;
  --emerald-text: #166534;
  --red: #ef4444;
  --red-bg: #fef2f2;
  --red-text: #991b1b;
}

.dark-mode {
  --bg-color: #000000;
  --bg-secondary: #0a0a0a;
  --border-color: #1a1a1a;
  --text-main: #f9fafb;
  --text-muted: #9ca3af;
  --primary: #ffffff;
  --emerald-bg: rgba(16, 185, 129, 0.2);
  --emerald-text: #34d399;
  --red-bg: rgba(239, 68, 68, 0.2);
  --red-text: #f87171;
}

.page-container {
  min-height: 100vh;
  background-color: var(--bg-secondary);
  color: var(--text-main);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.header {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 64px;
  background-color: var(--bg-color);
  border-bottom: 1px solid var(--border-color);
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  transition: all 0.2s;
  color: var(--text-muted);
  cursor: pointer;
  background: transparent;
  border: none;
}

.theme-toggle:hover {
  background-color: var(--bg-secondary);
  color: var(--text-main);
}

.back-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  padding: 8px 0;
  transition: color 0.2s;
}

.back-btn:hover {
  color: var(--text-main);
}

.market-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
}

.market-indicator.live { color: var(--emerald-text); }

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #d1d5db;
}

.dot.green { background-color: var(--emerald); }
.dot.gray { background-color: #9ca3af; }
.dot.yellow { background-color: #f59e0b; }
.dot.blue { background-color: #3b82f6; }

.main-content {
  display: grid;
  grid-template-columns: 3fr 1fr;
  gap: 32px;
  max-width: 100%;
  margin: 0 auto;
  padding: 32px 48px;
  align-items: start;
}

.chart-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.stock-name {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 4px 0;
  letter-spacing: -0.02em;
}

.stock-symbol {
  font-size: 14px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: var(--text-muted);
}

.price-info {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.current-price {
  font-size: 32px;
  font-weight: 700;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  line-height: 1;
}

.price-change {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 600;
}

.badge-positive {
  background-color: var(--emerald-bg);
  color: var(--emerald-text);
}

.badge-negative {
  background-color: var(--red-bg);
  color: var(--red-text);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  align-items: center;
}

.segmented-control {
  display: flex;
  background-color: var(--bg-secondary);
  padding: 4px;
  border-radius: 8px;
}

.segmented-control button {
  border: none;
  background: transparent;
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.segmented-control button.active {
  background-color: var(--bg-color);
  color: var(--text-main);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.indicator-toggles {
  display: flex;
  gap: 16px;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
}

.toggle-label input {
  accent-color: var(--text-main);
}

.chart-container {
  height: 500px;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.indicator-container {
  height: 200px;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 16px 20px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.indicator-header {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}

.indicator-meta {
  font-weight: 400;
  color: var(--text-muted);
  margin-left: 8px;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.news-panel {
  margin-top: 24px;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.news-card {
  display: block;
  padding: 16px;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.2s;
}

.news-card:hover {
  background-color: var(--bg-color);
  border-color: var(--emerald);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.news-meta {
  font-size: 11px;
  font-weight: 600;
  color: var(--emerald-text);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.news-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.news-summary {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.empty-msg {
  font-size: 14px;
  color: var(--text-muted);
  font-style: italic;
}

.panel-title {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  color: var(--text-muted);
  margin: 0 0 16px 0;
}

.prediction-value, .forecast-value {
  font-size: 24px;
  font-weight: 700;
  font-family: ui-monospace, SFMono-Regular, monospace;
}

.prediction-value.gain { color: var(--emerald); }
.prediction-value.loss { color: var(--red); }
.prediction-value.muted { color: var(--text-main); }

.loading-text {
  color: var(--text-muted);
  font-size: 14px;
}

.trade-form, .alert-form {
  display: flex;
  gap: 8px;
}

.qty-input, .alert-input, .alert-select {
  flex: 1;
  min-width: 0;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  background: var(--bg-color);
  color: var(--text-main);
}

.qty-input:focus, .alert-input:focus, .alert-select:focus {
  outline: none;
  border-color: var(--text-main);
  box-shadow: 0 0 0 2px rgba(0,0,0,0.1);
}

.btn-buy, .btn-sell, .btn-alert-set, .btn-alert-ai {
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  color: #ffffff;
  transition: opacity 0.2s;
}

.btn-buy:hover, .btn-sell:hover, .btn-alert-set:hover, .btn-alert-ai:hover {
  opacity: 0.9;
}

.btn-buy { background-color: var(--emerald); }
.btn-sell { background-color: var(--red); }
.btn-alert-set { background-color: var(--primary); color: var(--bg-color); }
.btn-alert-ai { 
  background-color: var(--primary); 
  color: var(--bg-color);
  width: 100%; 
  margin-bottom: 8px;
}

.status-msg {
  margin: 12px 0 0 0;
  font-size: 13px;
  color: var(--text-muted);
}

.key-value-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--bg-secondary);
}

.key-value-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.kv-label {
  color: var(--text-muted);
  font-size: 14px;
}

.kv-value {
  font-weight: 500;
  font-size: 14px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  color: var(--text-muted);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top-color: var(--text-main);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media(max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
    padding: 20px 16px;
  }
  
  .stock-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .price-info {
    align-items: flex-start;
    text-align: left;
  }
  
  .chart-container {
    height: 400px;
  }
}
</style>
