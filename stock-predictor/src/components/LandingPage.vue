<template>
  <div class="min-h-screen bg-white dark:bg-black text-black dark:text-white font-sans overflow-x-hidden selection:bg-emerald-100 selection:text-emerald-900 dark:selection:bg-emerald-900 dark:selection:text-emerald-100 transition-colors duration-300">
    

    <!-- Navbar -->
    <header class="sticky top-0 z-50 bg-white/80 dark:bg-black/80 backdrop-blur-md border-b border-gray-100 dark:border-[#1a1a1a] px-6 py-4 flex items-center justify-between transition-all">
      <div class="flex items-center">
        <router-link to="/" class="text-2xl font-black tracking-tight text-black dark:text-white flex items-center gap-2 hover:opacity-80 transition-opacity">
          TradeX
        </router-link>
      </div>

      <nav class="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600 dark:text-gray-400">
        <router-link to="/dashboard" class="hover:text-black dark:hover:text-white transition-colors">Dashboard</router-link>
      </nav>

      <div class="flex items-center gap-4">
        <button class="text-gray-500 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-[#1a1a1a]">
          <font-awesome-icon :icon="['fas', 'search']" />
        </button>
        <router-link to="/login" class="hidden sm:block text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors">
          Sign In
        </router-link>
        <button @click="toggleTheme" class="theme-toggle text-gray-500 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-[#1a1a1a]" :title="theme === 'dark' ? 'Switch to light' : 'Switch to dark'">
          <font-awesome-icon v-if="theme === 'dark'" :icon="['fas', 'sun']" />
          <font-awesome-icon v-else :icon="['fas', 'moon']" />
        </button>
        <router-link to="/login" class="bg-black dark:bg-white text-white dark:text-black text-sm font-medium px-5 py-2.5 rounded-full hover:bg-gray-800 dark:hover:bg-gray-200 transition-all shadow-sm hover:shadow-md">
          Get Started
        </router-link>
      </div>
    </header>

    <!-- Hero Section -->
    <main class="relative max-w-7xl mx-auto px-6 pt-20 pb-32 md:pt-32 md:pb-40 grid md:grid-cols-2 gap-16 items-center">
      
      <!-- Left: Text content -->
      <div>
        <Motion :initial="{ opacity: 0, y: 20 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: 0.6 }">
          <span class="inline-block py-1 px-3 rounded-full bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold tracking-wider mb-6 border border-emerald-100 dark:border-emerald-800/50">
            AI-POWERED TRADING PLATFORM
          </span>
          <h1 class="text-5xl md:text-7xl font-extrabold tracking-tight text-black dark:text-white leading-[1.1] mb-6">
            Predict.<br/>Invest.<br/><span class="text-emerald-500">Grow.</span>
          </h1>
          <p class="text-lg md:text-xl text-gray-500 dark:text-gray-400 mb-10 max-w-lg leading-relaxed">
            Experience the future of investing with TradeX. Leverage real-time market data and state-of-the-art AI predictions to trade smarter.
          </p>
          <div class="flex flex-col sm:flex-row gap-4">
            <router-link to="/dashboard" class="bg-black dark:bg-white text-white dark:text-black text-center font-semibold px-8 py-4 rounded-full hover:bg-gray-800 dark:hover:bg-gray-200 hover:-translate-y-0.5 transition-all duration-300 shadow-lg hover:shadow-xl flex items-center justify-center gap-2">
              Launch Dashboard <font-awesome-icon :icon="['fas', 'arrow-right']" class="text-sm" />
            </router-link>
            <a href="#learn-more" class="bg-white dark:bg-black text-black dark:text-white border border-gray-200 dark:border-[#1a1a1a] text-center font-semibold px-8 py-4 rounded-full hover:bg-gray-50 dark:hover:bg-[#0a0a0a] transition-all duration-300 flex items-center justify-center">
              Learn More
            </a>
          </div>
        </Motion>
      </div>

      <!-- Right: Visual -->
      <div class="relative w-full flex justify-center md:justify-end perspective-1000">
        <Motion :initial="{ opacity: 0, scale: 0.95, rotateY: 5 }" :animate="{ opacity: 1, scale: 1, rotateY: 0 }" :transition="{ duration: 0.8, delay: 0.2 }" class="w-full max-w-md">
          <div class="bg-white dark:bg-[#0a0a0a] rounded-3xl p-8 shadow-[0_20px_50px_-12px_rgba(0,0,0,0.1)] dark:shadow-[0_20px_50px_-12px_rgba(0,0,0,0.5)] border border-gray-100 dark:border-[#1a1a1a] relative z-10 hover:shadow-[0_30px_60px_-15px_rgba(0,0,0,0.15)] dark:hover:shadow-[0_30px_60px_-15px_rgba(0,0,0,0.7)] hover:-translate-y-1 transition-all duration-500">
            <div class="flex justify-between items-start mb-8">
              <div>
                <div class="text-sm font-bold text-gray-400 dark:text-gray-500 mb-1">RELIANCE.NS</div>
                <div class="text-4xl font-black tracking-tight text-black dark:text-white">₹2,847.50</div>
              </div>
              <div class="bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 px-3 py-1.5 rounded-full text-sm font-bold flex items-center gap-1">
                <font-awesome-icon :icon="['fas', 'arrow-up']" class="text-xs" /> 1.24%
              </div>
            </div>
            
            <!-- SVG Line Chart -->
            <div class="h-32 w-full mt-4">
              <svg viewBox="0 0 400 120" class="w-full h-full overflow-visible">
                <defs>
                  <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stop-color="#10b981" stop-opacity="0.2" />
                    <stop offset="100%" stop-color="#10b981" stop-opacity="1" />
                  </linearGradient>
                  <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#10b981" stop-opacity="0.2" />
                    <stop offset="100%" stop-color="#10b981" stop-opacity="0" />
                  </linearGradient>
                </defs>
                <path 
                  d="M0,100 C40,90 80,110 120,80 C160,50 200,60 240,40 C280,20 320,50 360,20 L400,0" 
                  fill="none" 
                  stroke="url(#lineGradient)" 
                  stroke-width="4" 
                  stroke-linecap="round"
                  class="chart-line-anim"
                />
                <path 
                  d="M0,100 C40,90 80,110 120,80 C160,50 200,60 240,40 C280,20 320,50 360,20 L400,0 L400,120 L0,120 Z" 
                  fill="url(#areaGradient)" 
                  class="chart-area-anim"
                />
                <!-- Current point dot -->
                <circle cx="400" cy="0" r="6" fill="#10b981" class="chart-dot-anim" />
                <circle cx="400" cy="0" r="14" fill="#10b981" opacity="0.2" class="chart-pulse-anim" />
              </svg>
            </div>
          </div>
          
          <!-- Decorative element behind card -->
          <div class="absolute -inset-4 bg-gradient-to-tr from-gray-100 to-gray-50 dark:from-[#171717] dark:to-[#0a0a0a] rounded-[2.5rem] -z-10 transform rotate-3 scale-105 transition-colors duration-500"></div>
        </Motion>
      </div>
    </main>

    <!-- Live Markets & News Section -->
    <section class="max-w-7xl mx-auto px-6 pb-24">
      <div class="grid lg:grid-cols-3 gap-12">
        
        <!-- Live Market Ticker / Cards -->
        <div class="lg:col-span-2">
          <div class="flex items-center justify-between mb-8">
            <h2 class="text-2xl md:text-3xl font-extrabold text-black dark:text-white tracking-tight">Top Movers</h2>
            <router-link to="/dashboard" class="text-sm font-semibold text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-1">
              View All <font-awesome-icon :icon="['fas', 'arrow-right']" class="text-xs" />
            </router-link>
          </div>
          <div v-if="loadingStocks" class="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div v-for="i in 6" :key="i" class="h-28 bg-gray-100 dark:bg-[#1a1a1a] rounded-2xl animate-pulse"></div>
          </div>
          <div v-else class="grid grid-cols-2 md:grid-cols-3 gap-4">
            <router-link v-for="stock in topStocks" :key="stock.symbol" :to="`/stock/${stock.symbol}`" class="bg-white dark:bg-[#121212] border border-gray-100 dark:border-[#1a1a1a] p-5 rounded-2xl shadow-sm hover:shadow-xl dark:shadow-none dark:hover:bg-[#171717] transition-all flex flex-col justify-between group cursor-pointer">
              <div class="font-bold text-gray-600 dark:text-gray-400 mb-4 tracking-wide text-sm">{{ stock.name }}</div>
              <div class="flex flex-col gap-1">
                <div class="text-2xl font-black text-black dark:text-white">₹{{ stock.price.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</div>
                <div :class="stock.change_percent >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'" class="text-sm font-bold flex items-center gap-1">
                  <font-awesome-icon :icon="['fas', stock.change_percent >= 0 ? 'caret-up' : 'caret-down']" />
                  {{ Math.abs(stock.change_percent).toFixed(2) }}%
                </div>
              </div>
            </router-link>
          </div>
        </div>

        <!-- Latest News -->
        <div>
          <div class="flex items-center justify-between mb-8">
            <h2 class="text-2xl md:text-3xl font-extrabold text-black dark:text-white tracking-tight">Market News</h2>
          </div>
          <div v-if="loadingNews" class="space-y-4">
            <div v-for="i in 3" :key="i" class="h-24 bg-gray-100 dark:bg-[#1a1a1a] rounded-2xl animate-pulse"></div>
          </div>
          <div v-else class="space-y-4">
            <a v-for="news in marketNews.slice(0, 3)" :key="news.link" :href="news.link" target="_blank" class="block bg-white dark:bg-[#121212] border border-gray-100 dark:border-[#1a1a1a] p-5 rounded-2xl shadow-sm hover:shadow-lg dark:shadow-none dark:hover:bg-[#171717] transition-all group">
              <h3 class="font-bold text-base mb-2 leading-snug line-clamp-2 text-black dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">{{ news.title }}</h3>
              <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 flex items-center justify-between">
                <span>{{ news.provider }}</span>
                <span>{{ new Date(news.pubDate).toLocaleDateString(undefined, {month: 'short', day: 'numeric'}) }}</span>
              </p>
            </a>
          </div>
        </div>

      </div>
    </section>

    <!-- Categories Section -->
    <section id="learn-more" class="bg-gray-50 dark:bg-[#0a0a0a] py-24 border-y border-gray-100 dark:border-[#1a1a1a] transition-colors">
      <div class="max-w-7xl mx-auto px-6">
        <Motion :initial="{ opacity: 0, y: 20 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: 0.6 }">
          <div class="text-center mb-16">
            <h2 class="text-3xl md:text-4xl font-extrabold tracking-tight mb-4 text-black dark:text-white">Everything you need to trade smarter</h2>
            <p class="text-gray-500 dark:text-gray-400 text-lg max-w-2xl mx-auto">Powerful tools built for modern investors, seamlessly combining live data and intelligent forecasts.</p>
          </div>
        </Motion>

        <!-- 2 Large Cards -->
        <div class="grid md:grid-cols-2 gap-8 mb-8">
          <Motion :initial="{ opacity: 0, y: 20 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: 0.6, delay: 0.1 }">
            <div class="group bg-white dark:bg-[#121212] rounded-3xl p-10 h-full border border-gray-100 dark:border-[#1a1a1a] shadow-sm hover:shadow-xl dark:hover:shadow-2xl dark:shadow-none transition-all duration-500 hover:-translate-y-1 relative overflow-hidden cursor-pointer">
              <div class="absolute top-0 right-0 w-64 h-64 bg-emerald-50 dark:bg-emerald-900/10 rounded-full blur-3xl -mr-20 -mt-20 transition-transform group-hover:scale-150 duration-700"></div>
              <div class="relative z-10">
                <div class="w-14 h-14 bg-black dark:bg-white text-white dark:text-black rounded-2xl flex items-center justify-center mb-8 shadow-md">
                  <font-awesome-icon :icon="['fas', 'bolt']" class="text-2xl text-emerald-400 dark:text-emerald-500" />
                </div>
                <h3 class="text-2xl font-bold mb-3 text-black dark:text-white">Real-Time Market Data</h3>
                <p class="text-gray-500 dark:text-gray-400 leading-relaxed text-lg">Stream live prices instantly via Kafka. Analyze trends with precision candlestick charts and advanced technical indicators.</p>
              </div>
            </div>
          </Motion>

          <Motion :initial="{ opacity: 0, y: 20 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: 0.6, delay: 0.2 }">
            <div class="group bg-white dark:bg-[#121212] rounded-3xl p-10 h-full border border-gray-100 dark:border-[#1a1a1a] shadow-sm hover:shadow-xl dark:hover:shadow-2xl dark:shadow-none transition-all duration-500 hover:-translate-y-1 relative overflow-hidden cursor-pointer">
              <div class="absolute top-0 right-0 w-64 h-64 bg-blue-50 dark:bg-blue-900/10 rounded-full blur-3xl -mr-20 -mt-20 transition-transform group-hover:scale-150 duration-700"></div>
              <div class="relative z-10">
                <div class="w-14 h-14 bg-black dark:bg-white text-white dark:text-black rounded-2xl flex items-center justify-center mb-8 shadow-md">
                  <font-awesome-icon :icon="['fas', 'brain']" class="text-2xl text-emerald-400 dark:text-emerald-500" />
                </div>
                <h3 class="text-2xl font-bold mb-3 text-black dark:text-white">AI Predictions</h3>
                <p class="text-gray-500 dark:text-gray-400 leading-relaxed text-lg">Utilize cutting-edge machine learning models that forecast stock movements to give you a strategic trading advantage.</p>
              </div>
            </div>
          </Motion>
        </div>

        <!-- 3 Small Cards -->
        <div class="grid md:grid-cols-3 gap-8">
          <Motion :initial="{ opacity: 0, y: 20 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: 0.6, delay: 0.3 }">
            <div class="bg-white dark:bg-[#121212] rounded-3xl p-8 border border-gray-100 dark:border-[#1a1a1a] shadow-sm hover:shadow-lg dark:shadow-none dark:hover:bg-[#171717] transition-all duration-300 hover:-translate-y-1">
              <div class="w-10 h-10 bg-gray-100 dark:bg-[#1a1a1a] text-black dark:text-white rounded-xl flex items-center justify-center mb-6">
                <font-awesome-icon :icon="['fas', 'wallet']" class="text-lg" />
              </div>
              <h4 class="text-xl font-bold mb-2 text-black dark:text-white">Paper Trading</h4>
              <p class="text-gray-500 dark:text-gray-400">Practice your strategies risk-free with ₹10,00,000 virtual cash on sign up.</p>
            </div>
          </Motion>

          <Motion :initial="{ opacity: 0, y: 20 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: 0.6, delay: 0.4 }">
            <div class="bg-white dark:bg-[#121212] rounded-3xl p-8 border border-gray-100 dark:border-[#1a1a1a] shadow-sm hover:shadow-lg dark:shadow-none dark:hover:bg-[#171717] transition-all duration-300 hover:-translate-y-1">
              <div class="w-10 h-10 bg-gray-100 dark:bg-[#1a1a1a] text-black dark:text-white rounded-xl flex items-center justify-center mb-6">
                <font-awesome-icon :icon="['fas', 'bell']" class="text-lg" />
              </div>
              <h4 class="text-xl font-bold mb-2 text-black dark:text-white">Smart Alerts</h4>
              <p class="text-gray-500 dark:text-gray-400">Get instant notifications for price crossings and critical AI movement shifts.</p>
            </div>
          </Motion>

          <Motion :initial="{ opacity: 0, y: 20 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: 0.6, delay: 0.5 }">
            <div class="bg-white dark:bg-[#121212] rounded-3xl p-8 border border-gray-100 dark:border-[#1a1a1a] shadow-sm hover:shadow-lg dark:shadow-none dark:hover:bg-[#171717] transition-all duration-300 hover:-translate-y-1">
              <div class="w-10 h-10 bg-gray-100 dark:bg-[#1a1a1a] text-black dark:text-white rounded-xl flex items-center justify-center mb-6">
                <font-awesome-icon :icon="['fas', 'chart-pie']" class="text-lg" />
              </div>
              <h4 class="text-xl font-bold mb-2 text-black dark:text-white">Portfolio Analytics</h4>
              <p class="text-gray-500 dark:text-gray-400">Track all your open positions, overall P&L, and strategy win rates over time.</p>
            </div>
          </Motion>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="py-32 px-6">
      <div class="max-w-7xl mx-auto text-center">
        <Motion :initial="{ opacity: 0, y: 20 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: 0.6 }">
          <h2 class="text-3xl md:text-4xl font-extrabold tracking-tight mb-16 text-black dark:text-white">How it works</h2>
        </Motion>

        <div class="grid md:grid-cols-3 gap-12 relative">
          <!-- Connector line -->
          <div class="hidden md:block absolute top-12 left-[15%] right-[15%] h-0.5 bg-gray-100 dark:bg-[#1a1a1a] -z-10"></div>
          
          <Motion :initial="{ opacity: 0, scale: 0.9 }" :animate="{ opacity: 1, scale: 1 }" :transition="{ duration: 0.5, delay: 0.1 }">
            <div class="flex flex-col items-center">
              <div class="w-24 h-24 bg-white dark:bg-[#0a0a0a] border-4 border-gray-50 dark:border-[#1a1a1a] rounded-full flex items-center justify-center text-3xl font-black shadow-sm mb-6 relative z-10 text-emerald-500">
                1
              </div>
              <h3 class="text-xl font-bold mb-3 text-black dark:text-white">Search</h3>
              <p class="text-gray-500 dark:text-gray-400 max-w-xs mx-auto">Find thousands of Indian stocks instantly using our powerful real-time search engine.</p>
            </div>
          </Motion>

          <Motion :initial="{ opacity: 0, scale: 0.9 }" :animate="{ opacity: 1, scale: 1 }" :transition="{ duration: 0.5, delay: 0.3 }">
            <div class="flex flex-col items-center">
              <div class="w-24 h-24 bg-white dark:bg-[#0a0a0a] border-4 border-gray-50 dark:border-[#1a1a1a] rounded-full flex items-center justify-center text-3xl font-black shadow-sm mb-6 relative z-10 text-emerald-500">
                2
              </div>
              <h3 class="text-xl font-bold mb-3 text-black dark:text-white">Analyze</h3>
              <p class="text-gray-500 dark:text-gray-400 max-w-xs mx-auto">View AI confidence scores, technical indicators, and historical trends in one clean view.</p>
            </div>
          </Motion>

          <Motion :initial="{ opacity: 0, scale: 0.9 }" :animate="{ opacity: 1, scale: 1 }" :transition="{ duration: 0.5, delay: 0.5 }">
            <div class="flex flex-col items-center">
              <div class="w-24 h-24 bg-black dark:bg-white border-4 border-gray-50 dark:border-[#1a1a1a] rounded-full flex items-center justify-center text-3xl font-black shadow-xl shadow-black/10 dark:shadow-white/10 mb-6 relative z-10 text-white dark:text-black">
                3
              </div>
              <h3 class="text-xl font-bold mb-3 text-black dark:text-white">Trade</h3>
              <p class="text-gray-500 dark:text-gray-400 max-w-xs mx-auto">Execute paper trades instantly and track your portfolio's performance securely.</p>
            </div>
          </Motion>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-white dark:bg-black border-t border-gray-100 dark:border-[#1a1a1a] py-12 px-6 transition-colors">
      <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
        <div class="flex items-center gap-2">
          <span class="text-xl font-black tracking-tight text-black dark:text-white">TradeX</span>
        </div>
        
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400 flex gap-6">
          <router-link to="/dashboard" class="hover:text-black dark:hover:text-white transition-colors">Dashboard</router-link>
        </div>
        
        <div class="text-sm text-gray-400 dark:text-gray-600">
          © {{ new Date().getFullYear() }} TradeX Platform. All rights reserved.
        </div>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api.js";
import { Motion } from "@motionone/vue";
import { library } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { fas } from "@fortawesome/free-solid-svg-icons";
import { useTheme } from "../composables/useTheme.js";

library.add(fas);

const { theme, toggleTheme } = useTheme();

const topStocks = ref([]);
const marketNews = ref([]);
const loadingStocks = ref(true);
const loadingNews = ref(true);

onMounted(async () => {
  try {
    const [stocksRes, newsRes] = await Promise.all([
      api.get("/api/top_stocks").catch(() => ({ data: [] })),
      api.get("/api/news").catch(() => ({ data: [] }))
    ]);
    topStocks.value = stocksRes.data;
    loadingStocks.value = false;
    marketNews.value = newsRes.data;
    loadingNews.value = false;
  } catch (error) {
    console.error("Error fetching landing page data", error);
    loadingStocks.value = false;
    loadingNews.value = false;
  }
});
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap");

.font-sans {
  font-family: "Inter", sans-serif;
}

/* Chart Animations */
.chart-line-anim {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: drawLine 2s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  animation-delay: 0.5s;
}

.chart-area-anim {
  opacity: 0;
  animation: fadeIn 1s ease-out forwards;
  animation-delay: 2s;
}

.chart-dot-anim {
  opacity: 0;
  animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
  animation-delay: 2.5s;
}

.chart-pulse-anim {
  opacity: 0;
  transform-origin: center;
  animation: pulse 2s infinite cubic-bezier(0.4, 0, 0.6, 1);
  animation-delay: 2.5s;
}

@keyframes drawLine {
  to {
    stroke-dashoffset: 0;
  }
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

@keyframes popIn {
  from {
    opacity: 0;
    transform: scale(0);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  70% {
    transform: scale(2);
    opacity: 0;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

/* Custom Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #d1d5db;
}

/* Dark mode scrollbar */
:global(.dark) ::-webkit-scrollbar-thumb {
  background: #333;
}
:global(.dark) ::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>