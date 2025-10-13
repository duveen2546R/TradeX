<template>
  <div class="p-8 bg-darkBg text-gray-200 min-h-screen">
    <h2 class="text-3xl font-bold text-accent mb-6">Live Stock Predictions</h2>

    <div class="bg-darkCard p-6 rounded-2xl shadow-lg border border-gray-800">
      <div v-if="loading" class="text-gray-400">Loading predictions...</div>

      <div v-else>
        <table class="w-full text-left">
          <thead>
            <tr class="text-accent border-b border-gray-700">
              <th class="py-2">Stock</th>
              <th class="py-2">Current Price</th>
              <th class="py-2">Predicted Price</th>
              <th class="py-2">Change</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="s in stocks"
              :key="s.symbol"
              class="border-b border-gray-800 hover:bg-gray-900 transition"
            >
              <td>{{ s.symbol }}</td>
              <td>{{ s.current }}</td>
              <td>{{ s.predicted }}</td>
              <td :class="s.predicted - s.current > 0 ? 'text-green-400' : 'text-red-400'">
                {{ ((s.predicted - s.current) / s.current * 100).toFixed(2) }}%
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const stocks = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const res = await axios.get("http://localhost:5000/api/stocks");
    stocks.value = res.data;
  } catch (e) {
    console.error("Error fetching stocks:", e);
  } finally {
    loading.value = false;
  }
});
</script>