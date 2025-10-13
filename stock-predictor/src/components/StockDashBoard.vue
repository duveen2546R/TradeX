<template>
  <div
    class="relative min-h-screen w-full flex flex-col items-center justify-start p-4 sm:p-6 lg:p-10 transition-all duration-700 overflow-hidden"
    :class="theme === 'dark' ? 'bg-[#0b0f13] text-gray-200' : 'bg-gray-100 text-gray-900'"
  >
    <!-- Animated Gradient Background -->
    <div class="aurora-wrapper">
      <div class="aurora-blob-1"></div>
      <div class="aurora-blob-2"></div>
    </div>

    <!-- Header -->
    <header class="w-full max-w-7xl flex justify-between items-center mb-8 relative z-10">
       <h1 class="text-3xl font-bold cursor-pointer" @click="$router.push('/')">
        <span class="text-accent">TradeX</span>
      </h1>
      <button @click="toggleTheme" class="border px-4 py-2 rounded-full transition-all duration-300 text-sm"
        :class="theme === 'dark' ? 'border-gray-700 hover:bg-gray-200 hover:text-black' : 'border-gray-300 hover:bg-gray-900 hover:text-white'">
        {{ theme === 'dark' ? '☀️ Light' : '🌙 Dark' }}
      </button>
    </header>

    <main class="w-full max-w-7xl flex flex-col items-center relative z-10">
      <!-- Search Section -->
      <div class="w-full lg:w-2/3 mb-12 text-center">
        <h2 class="text-4xl font-bold mb-4">Find Your Next Investment</h2>
        <p class="text-gray-400 mb-6">Search for any Indian stock by name or ticker symbol.</p>
        <div class="relative">
          <input
            v-model="searchQuery"
            @input="handleSearch"
            type="text"
            placeholder="e.g., Reliance, INFY.NS, ^NSEI"
            class="w-full px-5 py-4 rounded-full shadow-lg border-2 focus:outline-none focus:ring-4 focus:ring-accent/50 transition-all duration-300 text-lg"
            :class="theme === 'dark' ? 'bg-[#161b22] border-gray-700' : 'bg-white border-gray-200'"
          />
          <ul
            v-if="suggestions.length > 0"
            class="absolute top-full mt-2 w-full text-left rounded-xl shadow-lg border overflow-hidden backdrop-blur-md z-50"
            :class="theme === 'dark' ? 'bg-[#161b22]/90 border-gray-700' : 'bg-white/90 border-gray-200'"
          >
            <li
              v-for="s in suggestions"
              :key="s.symbol"
              @click="selectStock(s.symbol)"
              class="px-5 py-3 cursor-pointer hover:bg-accent/80 hover:text-white transition-colors duration-200"
            >
              <span class="font-semibold">{{ s.name }}</span> — <span class="text-sm opacity-70">{{ s.symbol }}</span>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- Searched Stock Card (if any) -->
      <div v-if="searchedStock" class="w-full mb-12">
         <h2 class="text-3xl font-semibold mb-6">Search Result</h2>
         <div class="card-base-detailed group relative p-6">
            <canvas :id="'chart-search-' + searchedStock.symbol" class="absolute inset-0 w-full h-full opacity-20 chart-mask"></canvas>
            <div class="relative z-10 flex flex-col md:flex-row justify-between items-center gap-4">
              <div @click="$router.push(`/stock/${searchedStock.symbol}`)" class="flex-1 cursor-pointer text-center md:text-left">
                <h3 class="text-3xl font-bold">{{ searchedStock.name }}</h3>
                <p class="text-gray-400">{{ searchedStock.symbol }}</p>
              </div>

              <!-- "Add to Favorites" Button with Optimistic UI -->
              <button
                v-if="!isSearchedStockInFavorites"
                @click.stop="addFavorite(searchedStock)"
                class="bg-accent/80 text-white px-5 py-2 rounded-full font-semibold hover:bg-accent transition-colors duration-200 whitespace-nowrap"
              >
                ⭐ Add to Favorites
              </button>
               <div v-else class="text-accent font-semibold flex items-center gap-2">
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>
                 In Favorites
              </div>

              <div @click="$router.push(`/stock/${searchedStock.symbol}`)" class="flex-1 cursor-pointer text-center md:text-right">
                <p class="text-3xl font-semibold">₹{{ searchedStock.current.toFixed(2) }}</p>
                <p class="text-lg" :class="searchedStock.change >= 0 ? 'text-green-400' : 'text-red-400'">
                  {{ searchedStock.change >= 0 ? '+' : '' }}{{ searchedStock.change.toFixed(2) }}%
                </p>
              </div>
            </div>
         </div>
      </div>

      <!-- Favorites Section -->
      <div class="w-full">
        <h2 class="text-3xl font-semibold mb-6">Your Favorites</h2>
        <div v-if="loadingFavorites" class="text-center py-10 text-gray-400">Loading your favorites...</div>
        <div v-else-if="favorites.length === 0" class="card-base text-center py-16">
            <p class="text-2xl mb-2">Your watchlist is empty.</p>
            <p class="text-gray-400">Use the search bar above to find and add stocks to your list.</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          <div
            v-for="stock in favorites"
            :key="stock.symbol"
            class="card-base group relative overflow-hidden p-5 cursor-pointer flex flex-col justify-between h-48"
            @click="$router.push(`/stock/${stock.symbol}`)"
          >
            <canvas :id="'chart-' + stock.symbol" class="absolute left-0 bottom-0 w-full h-2/3 opacity-20 group-hover:opacity-30 transition-opacity duration-300 chart-mask"></canvas>
            
            <div class="relative z-10 flex justify-between items-start">
              <div>
                <h3 class="text-2xl font-bold">{{ stock.symbol }}</h3>
                <p class="text-sm text-gray-400 truncate w-40">{{ stock.name }}</p>
              </div>
              <button
                @click.stop="removeFavorite(stock.symbol)"
                class="text-sm opacity-50 hover:opacity-100 hover:text-red-400 transition-all duration-200"
              >
                ✕
              </button>
            </div>

            <div class="relative z-10 text-right">
              <p class="text-2xl font-semibold">₹{{ stock.current.toFixed(2) }}</p>
              <p class="font-medium" :class="stock.change >= 0 ? 'text-green-400' : 'text-red-400'">
                 {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from "vue";
import Chart from "chart.js/auto";
import axios from "axios";

// --- STATE ---
const theme = ref(localStorage.getItem("theme") || "dark");
const favorites = ref([]);
const searchQuery = ref("");
const suggestions = ref([]);
const searchedStock = ref(null);
const loadingFavorites = ref(true);
const userId = 1; 
let chartInstances = {};
let priceEventSource = null;

// --- COMPUTED PROPERTIES ---
const isSearchedStockInFavorites = computed(() => {
  if (!searchedStock.value) return false;
  return favorites.value.some(fav => fav.symbol === searchedStock.value.symbol);
});

// --- API & DATA (with Real-time Integration) ---
const fetchFavorites = async () => {
  loadingFavorites.value = true;
  try {
    const res = await axios.get(`http://127.0.0.1:5000/favorites/${userId}`);
    favorites.value = res.data;
  } catch (error) {
    console.error("Failed to fetch initial favorites:", error);
  } finally {
    loadingFavorites.value = false;
  }
};

const handleSearch = async () => {
  if (searchQuery.value.length < 2) {
    suggestions.value = [];
    return;
  }
  try {
    const res = await axios.get(`http://127.0.0.1:5000/search?query=${searchQuery.value}`);
    suggestions.value = res.data.symbols || [];
  } catch (error) {
    console.error("Search failed:", error);
  }
};

const selectStock = async (symbol) => {
  searchQuery.value = "";
  suggestions.value = [];
  try {
    // We get more complete data here, including a chart trend
    const res = await axios.get(`http://127.0.0.1:5000/stock_history/${symbol}`);
    // We rename the key for consistency with our chart function
    res.data.predictions = res.data.last_5_days_trend; 
    searchedStock.value = res.data;
  } catch (err) {
    console.error("Error fetching selected stock:", err);
  }
};

// --- Optimistic UI for Favorites ---
const addFavorite = (stockToAdd) => {
  favorites.value.push(stockToAdd);
  axios.post("http://127.0.0.1:5000/update_favorites", { user_id: userId, symbol: stockToAdd.symbol, action: "add" })
    .catch(err => {
      console.error("Failed to save favorite:", err);
      favorites.value = favorites.value.filter(s => s.symbol !== stockToAdd.symbol);
    });
};

const removeFavorite = (symbolToRemove) => {
  favorites.value = favorites.value.filter(s => s.symbol !== symbolToRemove);
  axios.post("http://127.0.0.1:5000/update_favorites", { user_id: userId, symbol: symbolToRemove, action: "remove" });
};

// --- Live Dashboard Stream ---
const startDashboardStream = () => {
  if (priceEventSource) priceEventSource.close();
  
  priceEventSource = new EventSource('http://127.0.0.1:5000/stream/all_prices');
  console.log("Dashboard stream connected.");

  priceEventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // Check if the update is for a stock in our favorites list
    const favToUpdate = favorites.value.find(s => s.symbol === data.symbol);
    if (favToUpdate) {
      favToUpdate.current = data.price;
      favToUpdate.change = data.change_pct; // Use direct pct change from producer
    }

    // Check if the update is for the currently searched stock
    if (searchedStock.value && searchedStock.value.symbol === data.symbol) {
      searchedStock.value.current = data.price;
       // We can also calculate a live change for the searched stock
      searchedStock.value.change = ((data.price - searchedStock.value.previousClose) / searchedStock.value.previousClose) * 100;
    }
  };

  priceEventSource.onerror = (err) => {
     console.error("Dashboard stream error:", err);
     priceEventSource.close();
  };
};

// --- CHARTING & THEME ---
const createOrUpdateChart = (stock) => {
  if (!stock || !stock.predictions) return;
  // Use a unique ID for the searched stock card chart
  const chartId = stock === searchedStock.value ? 'chart-search-' + stock.symbol : 'chart-' + stock.symbol;
  
  nextTick(() => {
    const ctx = document.getElementById(chartId);
    if (!ctx) return;
    if (chartInstances[chartId]) chartInstances[chartId].destroy();
    const isUp = stock.change >= 0;
    const color = isUp ? '#22c55e' : '#ef4444';
    chartInstances[chartId] = new Chart(ctx, { type: "line", data: { labels: Array.from({ length: stock.predictions.length }), datasets: [{ data: stock.predictions, borderColor: color, tension: 0.4, borderWidth: 3, pointRadius: 0 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false } } } });
  });
};

watch(favorites, (newFavorites) => { newFavorites.forEach(createOrUpdateChart); }, { deep: true });
watch(searchedStock, (newStock) => { if(newStock) createOrUpdateChart(newStock); });
const applyTheme = () => { document.documentElement.classList.toggle("dark", theme.value === "dark"); localStorage.setItem("theme", theme.value); };
const toggleTheme = () => { theme.value = theme.value === "dark" ? "light" : "dark"; };
watch(theme, applyTheme);

// --- LIFECYCLE HOOKS ---
onMounted(async () => {
  applyTheme();
  await fetchFavorites();
  startDashboardStream();
});

onUnmounted(() => {
  Object.values(chartInstances).forEach(chart => chart.destroy());
  if (priceEventSource) {
    priceEventSource.close();
    console.log("Dashboard stream closed.");
  }
});
</script>

<style scoped>
/* All styles from your final dashboard UI remain the same */
.text-accent { color: #00c896; }
.card-base, .card-base-detailed { @apply backdrop-blur-md border rounded-2xl shadow-lg transition-all duration-300; }
.dark .card-base, .dark .card-base-detailed { @apply bg-[#161b22]/70 border-gray-800; }
.light .card-base, .light .card-base-detailed { @apply bg-white/70 border-gray-200; }
.card-base:hover { @apply border-accent/80 -translate-y-1; }
.chart-mask { mask-image: linear-gradient(to top, rgba(0,0,0,1) 30%, rgba(0,0,0,0) 100%); -webkit-mask-image: linear-gradient(to top, rgba(0,0,0,1) 30%, rgba(0,0,0,0) 100%); }
.aurora-wrapper { @apply absolute top-0 left-0 w-full h-full -z-0 overflow-hidden; }
.aurora-blob-1, .aurora-blob-2 { @apply absolute rounded-full opacity-30 filter blur-3xl; }
.dark .aurora-blob-1 { @apply w-96 h-96 bg-accent -top-16 -left-16 animate-aurora-1; }
.dark .aurora-blob-2 { @apply w-72 h-72 bg-blue-500 -bottom-8 -right-8 animate-aurora-2; }
.light .aurora-blob-1 { @apply w-96 h-96 bg-teal-200 -top-16 -left-16 animate-aurora-1; }
.light .aurora-blob-2 { @apply w-72 h-72 bg-blue-200 -bottom-8 -right-8 animate-aurora-2; }
@keyframes aurora-1 { 0% { transform: translate(0, 0) rotate(0deg); } 50% { transform: translate(120px, 80px) rotate(180deg); } 100% { transform: translate(0, 0) rotate(360deg); } }
@keyframes aurora-2 { 0% { transform: translate(0, 0) rotate(0deg); } 50% { transform: translate(-100px, -60px) rotate(180deg); } 100% { transform: translate(0, 0) rotate(360deg); } }
.animate-aurora-1 { animation: aurora-1 25s ease-in-out infinite alternate; }
.animate-aurora-2 { animation: aurora-2 30s ease-in-out infinite alternate; }
</style>