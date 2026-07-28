<template>
  <div class="min-h-screen bg-gray-50 dark:bg-black text-black dark:text-white font-sans pb-12 transition-colors duration-200">
    <!-- Navbar -->
    <nav class="sticky top-0 z-50 bg-white dark:bg-black border-b border-gray-200 dark:border-[#1a1a1a] transition-colors duration-200">
      <div class="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-3">
            <span class="text-xl font-bold tracking-tight">TradeX</span>
            <span class="text-sm font-medium text-gray-500 dark:text-gray-400 px-2 py-1 bg-gray-100 dark:bg-[#1a1a1a] rounded-md">Paper Trading</span>
          </div>
          <div class="flex items-center space-x-6">
            <button @click="toggleTheme" class="text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors">
              <span v-if="theme === 'dark'">☀️</span>
              <span v-else>🌙</span>
            </button>
            <span class="text-sm text-gray-600 dark:text-gray-300" v-if="user">{{ user.email }}</span>
            <button @click="logout" class="text-sm font-semibold text-gray-900 dark:text-white hover:text-gray-600 dark:hover:text-gray-300 transition-colors">Sign out</button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Notification Center -->
    <NotificationCenter />

    <main class="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 mt-8 space-y-8">
      
      <!-- Hero / Search Section -->
      <section class="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-[#1a1a1a] rounded-2xl shadow-sm p-8 text-center flex flex-col items-center transition-colors duration-200">
        <p class="text-xs font-bold tracking-widest text-gray-500 dark:text-gray-400 uppercase mb-2">Live AI Stock Prediction</p>
        <h1 class="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl mb-2">Find your next investment</h1>
        <p class="text-gray-500 dark:text-gray-400 mb-8 max-w-2xl">Search thousands of stocks and get AI-powered insights to supercharge your paper trading portfolio.</p>
        
        <div class="relative w-full max-w-xl">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
              </svg>
            </div>
            <input 
              v-model="searchQuery" 
              @input="searchStocks"
              type="text" 
              placeholder="Search by symbol (e.g. AAPL, RELIANCE)..." 
              class="block w-full pl-11 pr-4 py-4 border border-gray-200 dark:border-[#1a1a1a] rounded-xl leading-5 bg-white dark:bg-[#1a1a1a] placeholder-gray-400 dark:text-white focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white focus:border-black dark:focus:border-white sm:text-sm transition-shadow shadow-sm"
            >
          </div>
          <ul v-if="suggestions.length > 0" class="absolute z-10 mt-2 w-full bg-white dark:bg-[#1a1a1a] shadow-lg max-h-60 rounded-xl border border-gray-100 dark:border-[#2a2a2a] overflow-auto text-left">
            <li v-for="sym in suggestions" :key="sym.symbol" class="cursor-pointer hover:bg-gray-50 dark:hover:bg-[#2a2a2a] flex items-center justify-between px-4 py-3 border-b border-gray-50 dark:border-[#2a2a2a] last:border-0 transition-colors" @click="openStock(sym.symbol); addWatchSymbol(sym.symbol)">
              <span class="font-bold text-gray-900 dark:text-white">{{ sym.symbol }}</span>
              <span class="text-sm text-gray-500 dark:text-gray-400">{{ sym.name || 'View Stock' }}</span>
            </li>
          </ul>
        </div>
      </section>

      <!-- Portfolio Metrics -->
      <section v-if="portfolio" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div class="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-[#1a1a1a] rounded-2xl p-6 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-200">
          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Virtual Cash</dt>
          <dd class="text-2xl font-bold text-gray-900 dark:text-white">{{ money(portfolio.balance_paise) }}</dd>
        </div>
        <div class="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-[#1a1a1a] rounded-2xl p-6 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-200">
          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Portfolio Equity</dt>
          <dd class="text-2xl font-bold text-gray-900 dark:text-white">{{ money(portfolio.equity_paise) }}</dd>
        </div>
        <div class="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-[#1a1a1a] rounded-2xl p-6 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-200">
          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Total P&L</dt>
          <dd class="text-2xl font-bold" :class="portfolio.total_pnl_paise >= 0 ? 'text-emerald-500 dark:text-emerald-400' : 'text-red-500 dark:text-red-400'">
            {{ signedMoney(portfolio.total_pnl_paise) }}
          </dd>
        </div>
        <div class="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-[#1a1a1a] rounded-2xl p-6 shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-200">
          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Win Rate</dt>
          <dd class="text-2xl font-bold text-gray-900 dark:text-white">
             {{ portfolio.win_rate ? portfolio.win_rate + '%' : '—' }}
          </dd>
        </div>
      </section>

      <!-- Main Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Left Column -->
        <div class="lg:col-span-1 space-y-8">
          <!-- Place Paper Order -->
          <div class="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-[#1a1a1a] rounded-2xl shadow-sm p-6 transition-colors duration-200">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Place Order</h2>
            <form @submit.prevent="placeOrder" class="space-y-4">
              <div class="relative">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Symbol</label>
                <input v-model="order.symbol" @input="searchOrderStocks" @blur="fetchOrderPreview(order.symbol)" type="text" placeholder="AAPL" class="w-full border border-gray-200 dark:border-[#1a1a1a] rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white bg-white dark:bg-[#1a1a1a] dark:text-white" required>
                <ul v-if="orderSuggestions.length > 0" class="absolute z-10 mt-1 w-full bg-white dark:bg-[#1a1a1a] shadow-lg max-h-48 rounded-xl border border-gray-100 dark:border-[#2a2a2a] overflow-auto text-left">
                  <li v-for="sym in orderSuggestions" :key="sym.symbol" class="cursor-pointer hover:bg-gray-50 dark:hover:bg-[#2a2a2a] flex items-center justify-between px-4 py-3 border-b border-gray-50 dark:border-[#2a2a2a] last:border-0 transition-colors" @click="order.symbol = sym.symbol; orderSuggestions = []; fetchOrderPreview(sym.symbol)">
                    <span class="font-bold text-gray-900 dark:text-white">{{ sym.symbol }}</span>
                    <span class="text-sm text-gray-500 dark:text-gray-400">{{ sym.name || 'Select' }}</span>
                  </li>
                </ul>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Side</label>
                  <select v-model="order.side" class="w-full border border-gray-200 dark:border-[#1a1a1a] rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white bg-white dark:bg-[#1a1a1a] dark:text-white">
                    <option value="BUY">Buy</option>
                    <option value="SELL">Sell</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Quantity</label>
                  <input v-model.number="order.quantity" type="number" min="1" class="w-full border border-gray-200 dark:border-[#1a1a1a] rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white bg-white dark:bg-[#1a1a1a] dark:text-white" required>
                </div>
              </div>
              
              <div v-if="orderPreviewPrice !== null && order.symbol" class="bg-gray-50 dark:bg-[#1a1a1a] p-4 rounded-xl border border-gray-200 dark:border-[#2a2a2a]">
                <div class="flex justify-between items-center mb-1">
                  <span class="text-sm text-gray-500 dark:text-gray-400">Current Price</span>
                  <span class="font-bold text-gray-900 dark:text-white">₹{{ orderPreviewPrice.toFixed(2) }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-500 dark:text-gray-400">Estimated Total</span>
                  <span class="font-bold text-emerald-600 dark:text-emerald-400">₹{{ (orderPreviewPrice * order.quantity).toFixed(2) }}</span>
                </div>
              </div>

              <div v-if="message" :class="messageType === 'error' ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-200 dark:border-red-900/50' : 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900/50'" class="p-3 rounded-lg text-sm font-medium border">
                {{ message }}
              </div>

              <button type="submit" class="w-full bg-black dark:bg-white text-white dark:text-black rounded-lg px-6 py-3 font-semibold hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors">
                Submit Order
              </button>
            </form>
          </div>

          <!-- Custom Alerts -->
          <div class="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-[#1a1a1a] rounded-2xl shadow-sm p-6 transition-colors duration-200">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Custom Alerts</h2>
            <form @submit.prevent="createAlert" class="space-y-4 mb-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Symbol</label>
                <input v-model="alert.symbol" type="text" placeholder="TSLA" class="w-full border border-gray-200 dark:border-[#1a1a1a] rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white bg-white dark:bg-[#1a1a1a] dark:text-white" required>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Condition</label>
                  <select v-model="alert.direction" class="w-full border border-gray-200 dark:border-[#1a1a1a] rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white bg-white dark:bg-[#1a1a1a] dark:text-white">
                    <option value="above">Above</option>
                    <option value="below">Below</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Price (₹)</label>
                  <input v-model.number="alert.threshold" type="number" class="w-full border border-gray-200 dark:border-[#1a1a1a] rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white bg-white dark:bg-[#1a1a1a] dark:text-white" required>
                </div>
              </div>
              <button type="submit" class="w-full bg-black dark:bg-white text-white dark:text-black rounded-lg px-6 py-3 font-semibold hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors">
                Create Alert
              </button>
            </form>
            
            <div class="space-y-3">
              <div v-for="a in alerts" :key="a.id" class="flex items-center justify-between p-3 border border-gray-100 dark:border-[#1a1a1a] rounded-lg hover:bg-gray-50 dark:hover:bg-[#1a1a1a] transition-colors">
                <div>
                  <div class="font-bold text-gray-900 dark:text-white">{{ a.symbol }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">{{ describeAlert(a) }}</div>
                </div>
                <button v-if="a.status === 'active'" @click="disableAlert(a.id)" class="text-xs font-semibold text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300">Disable</button>
              </div>
              <p v-if="alerts.length === 0" class="text-sm text-gray-500 dark:text-gray-400 italic text-center py-2">No active alerts.</p>
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="lg:col-span-2 space-y-8">
          
          <!-- Active Positions -->
          <div class="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-[#1a1a1a] rounded-2xl shadow-sm p-6 transition-colors duration-200">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-bold text-gray-900 dark:text-white">Active Positions</h2>
              <button @click="resetPortfolio" class="text-sm text-gray-500 dark:text-gray-400 hover:text-black dark:hover:text-white font-medium transition-colors">Reset Portfolio</button>
            </div>
            
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="border-b border-gray-100 dark:border-[#1a1a1a] text-sm text-gray-500 dark:text-gray-400">
                    <th class="pb-3 font-medium">Symbol</th>
                    <th class="pb-3 font-medium text-right">Shares</th>
                    <th class="pb-3 font-medium text-right">Avg Price</th>
                    <th class="pb-3 font-medium text-right">Current Price</th>
                    <th class="pb-3 font-medium text-right">P&L</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="pos in (portfolio?.positions || [])" :key="pos.symbol" class="border-b border-gray-50 dark:border-[#1a1a1a] last:border-0 hover:bg-gray-50 dark:hover:bg-[#1a1a1a] transition-colors group">
                    <td class="py-4">
                      <button @click="openStock(pos.symbol)" class="font-bold text-gray-900 dark:text-white hover:underline cursor-pointer">{{ pos.symbol }}</button>
                    </td>
                    <td class="py-4 text-right text-gray-900 dark:text-white">{{ pos.quantity }}</td>
                    <td class="py-4 text-right text-gray-600 dark:text-gray-300">{{ money(pos.average_cost_paise) }}</td>
                    <td class="py-4 text-right text-gray-600 dark:text-gray-300">{{ money(pos.last_price_paise) }}</td>
                    <td class="py-4 text-right font-medium" :class="pos.unrealized_pnl_paise >= 0 ? 'text-emerald-500 dark:text-emerald-400' : 'text-red-500 dark:text-red-400'">
                      {{ signedMoney(pos.unrealized_pnl_paise) }}
                    </td>
                  </tr>
                  <tr v-if="!(portfolio?.positions?.length)">
                    <td colspan="5" class="py-8 text-center text-gray-500 dark:text-gray-400 text-sm italic">No open positions. Start trading!</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- Watchlist -->
            <div class="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-[#1a1a1a] rounded-2xl shadow-sm p-6 transition-colors duration-200">
              <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Watchlist</h2>
              <form @submit.prevent="addWatch" class="flex gap-2 mb-4">
                <input v-model="watchSymbol" type="text" placeholder="Add symbol..." class="flex-1 border border-gray-200 dark:border-[#1a1a1a] bg-white dark:bg-[#1a1a1a] dark:text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white">
                <button type="submit" class="bg-black dark:bg-white text-white dark:text-black rounded-lg px-4 py-2 text-sm font-semibold hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors">Add</button>
              </form>
              <div class="space-y-2">
                <div v-for="w in watchlist" :key="w.symbol" class="flex items-center justify-between p-3 border border-gray-100 dark:border-[#1a1a1a] rounded-lg hover:bg-gray-50 dark:hover:bg-[#1a1a1a] transition-colors group">
                  <button @click="openStock(w.symbol)" class="font-bold text-gray-900 dark:text-white hover:underline">{{ w.symbol }}</button>
                  <button @click="removeWatch(w.symbol)" class="text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                  </button>
                </div>
                <p v-if="watchlist.length === 0" class="text-sm text-gray-500 dark:text-gray-400 italic text-center py-2">Watchlist is empty.</p>
              </div>
            </div>

            <!-- Recent Orders -->
            <div class="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-[#1a1a1a] rounded-2xl shadow-sm p-6 transition-colors duration-200">
              <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Recent Orders</h2>
              <div class="space-y-3">
                <div v-for="o in orders.slice(0, 5)" :key="o.id" class="flex items-center justify-between p-3 border border-gray-100 dark:border-[#1a1a1a] rounded-lg hover:bg-gray-50 dark:hover:bg-[#1a1a1a] transition-colors">
                  <div>
                    <div class="flex items-center space-x-2">
                      <span class="font-bold text-gray-900 dark:text-white">{{ o.symbol }}</span>
                      <span :class="o.side === 'BUY' ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-400' : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400'" class="px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wide">
                        {{ o.side }}
                      </span>
                    </div>
                    <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ o.quantity }} shs @ {{ money(o.price_paise) }}</div>
                  </div>
                  <div class="text-xs text-gray-400 dark:text-gray-500">{{ new Date(o.created_at).toLocaleDateString() }}</div>
                </div>
                <p v-if="orders.length === 0" class="text-sm text-gray-500 dark:text-gray-400 italic text-center py-2">No recent orders.</p>
              </div>
            </div>
          </div>
          
          <!-- Market News -->
          <div class="bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-[#1a1a1a] rounded-2xl shadow-sm p-6 transition-colors duration-200">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Market News</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <a v-for="(n, i) in globalNews" :key="i" :href="n.link" target="_blank" class="block p-4 border border-gray-100 dark:border-[#1a1a1a] rounded-xl hover:bg-gray-50 dark:hover:bg-[#1a1a1a] transition-colors group">
                <div class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 mb-1">{{ n.provider }} &middot; {{ new Date(n.pubDate).toLocaleDateString() }}</div>
                <h3 class="font-bold text-gray-900 dark:text-white mb-2 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">{{ n.title }}</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">{{ n.summary }}</p>
              </a>
            </div>
            <p v-if="globalNews.length === 0" class="text-sm text-gray-500 dark:text-gray-400 italic text-center py-2">No news available at the moment.</p>
          </div>

          
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import NotificationCenter from "./NotificationCenter.vue";
import { useTheme } from "../composables/useTheme.js";

const { theme, toggleTheme } = useTheme();

const router = useRouter(); const user = ref(); const portfolio = ref(); const orders = ref([]); const watchlist = ref([]); const alerts = ref([]); const globalNews = ref([]); const message = ref(""); const messageType = ref("success"); const searchQuery = ref(""); const suggestions = ref([]); const orderSuggestions = ref([]);
const order = reactive({ symbol: "", side: "BUY", quantity: 1 }); const alert = reactive({ symbol: "", kind: "price", direction: "below", threshold: "" }); const watchSymbol = ref("");
const orderPreviewPrice = ref(null); const previewingSymbol = ref("");
const money = (paise) => paise == null ? "—" : new Intl.NumberFormat("en-IN", { style:"currency", currency:"INR", maximumFractionDigits:2 }).format(paise / 100);
const signedMoney = (paise) => `${paise >= 0 ? '+' : '−'}${money(Math.abs(paise))}`; const profit = (paise) => paise == null ? "" : paise >= 0 ? "gain" : "loss";
const describeAlert = (item) => item.kind === "ai_movement" ? "AI forecast movement ≥ 1.5%" : `${item.direction === 'above' ? 'rises above' : 'drops below'} ${money(item.threshold_paise)} · ${item.status}`;
async function load() { const [me, p, o, w, a, n] = await Promise.all([api.get('/api/auth/me'), api.get('/api/portfolio'), api.get('/api/orders'), api.get('/api/watchlist'), api.get('/api/alerts'), api.get('/api/news').catch(() => ({data:[]}))]); user.value=me.data.user; portfolio.value=p.data; orders.value=o.data; watchlist.value=w.data; alerts.value=a.data; globalNews.value=n.data; }
async function placeOrder() { try { const { data } = await api.post('/api/orders', order); message.value=`${data.side} order filled at ${money(data.price_paise)}.`; messageType.value='success'; await load(); } catch (err) { message.value=err.response?.data?.error || 'Order failed.'; messageType.value='error'; } }
async function resetPortfolio() { if (!confirm('Archive this paper portfolio and start again with ₹10,00,000?')) return; await api.post('/api/portfolio/reset'); await load(); }
async function addWatchSymbol(symbol) { if (!symbol) return; await api.post('/api/watchlist', {symbol}); watchSymbol.value=''; suggestions.value=[]; await load(); }
async function addWatch() { await addWatchSymbol(watchSymbol.value); }
async function removeWatch(symbol) { await api.delete(`/api/watchlist/${symbol}`); await load(); }
async function searchStocks() { if (searchQuery.value.length < 2) { suggestions.value=[]; return; } try { suggestions.value=(await api.get('/search', {params:{query:searchQuery.value}})).data.symbols || []; } catch (_) { suggestions.value=[]; } }
async function searchOrderStocks() { if (order.symbol.length < 2) { orderSuggestions.value=[]; return; } try { orderSuggestions.value=(await api.get('/search', {params:{query:order.symbol}})).data.symbols || []; } catch (_) { orderSuggestions.value=[]; } }
async function fetchOrderPreview(sym) { if (!sym) { orderPreviewPrice.value = null; previewingSymbol.value = ""; return; } if (sym === previewingSymbol.value && orderPreviewPrice.value !== null) return; try { const { data } = await api.get(`/stock/${sym}`); orderPreviewPrice.value = data.current; previewingSymbol.value = sym; } catch (err) { try { const { data } = await api.get(`/stock_history/${sym}`); orderPreviewPrice.value = data.current; previewingSymbol.value = sym; } catch (e) { orderPreviewPrice.value = null; } } }
function openStock(symbol) { router.push(`/stock/${symbol}`); }
async function createAlert() { try { await api.post('/api/alerts', alert); alert.symbol=''; alert.threshold=''; await load(); } catch (err) { message.value=err.response?.data?.error || 'Alert could not be created.'; messageType.value='error'; } }
async function disableAlert(id) { await api.post(`/api/alerts/${id}/disable`); await load(); }
async function logout() { await api.post('/api/auth/logout'); router.replace('/'); }
onMounted(async () => { try { await load(); } catch (_) { router.replace('/login'); } });
</script>
