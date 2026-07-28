import { createRouter, createWebHistory } from "vue-router";

// Lazy-loaded components for better performance
const LandingPage = () => import("./components/LandingPage.vue");
const LoginPage = () => import("./components/LoginPage.vue");
const StockDashboard = () => import("./components/StockDashBoard.vue");
const StockDetail = () => import("./components/StockDetail.vue");

const routes = [
  {
    path: "/",
    name: "LandingPage",
    component: LandingPage,
  },
  {
    path: "/dashboard",
    name: "StockDashboard",
    component: StockDashboard,
  },
  {
    path: "/login",
    name: "Login",
    component: LoginPage,
  },
  {
    path: "/stock/:symbol",
    name: "StockDetail",
    component: StockDetail,
    props: true, // Enables symbol prop in component
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0, behavior: "smooth" };
  },
});

export default router;
