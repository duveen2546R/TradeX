import { ref, watch, onMounted } from "vue";

const theme = ref(localStorage.getItem("theme") || "light");

function applyTheme() {
  const root = document.documentElement;
  if (theme.value === "dark") {
    root.classList.add("dark");
  } else {
    root.classList.remove("dark");
  }
  localStorage.setItem("theme", theme.value);
}

export function useTheme() {
  onMounted(applyTheme);
  watch(theme, applyTheme);

  function toggleTheme() {
    theme.value = theme.value === "dark" ? "light" : "dark";
  }

  return { theme, toggleTheme };
}
