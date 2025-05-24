import { createRouter, createWebHistory } from 'vue-router';
import HackathonList from '../components/HackathonList.vue';
import RegisterComp from '../components/RegisterComp.vue';
import LoginComp from '../components/LoginComp.vue';
import ProfileComp from '../components/ProfileComp.vue';
import HackathonDetail from '../components/HackathonDetail.vue';
import CreateHackathon from '../components/CreateHackathon.vue';

// Определяем маршруты
const routes = [
  {
    path: '/',
    name: 'HackathonList',
    component: HackathonList,
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterComp,
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginComp,
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileComp,
    meta: { requiresAuth: true }, // Защита маршрута
  },
  {
    path: '/hackathons',
    name: 'Hackathons',
    component: HackathonList, // Добавляем маршрут для хакатонов
  },
  {
    path: '/hackathons/:id',
    name: 'HackathonDetail',
    component: HackathonDetail,
    meta: { requiresAuth: true }, // Защита маршрута
  },
  {
    path: '/hackathons/create',
    name: 'CreateHackathon',
    component: CreateHackathon,
    meta: { requiresAuth: true }, // Защита маршрута
  }
];

// Создаем экземпляр маршрутизатора
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Глобальный навигационный гард для проверки аутентификации
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token'); // Проверяем наличие токена
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    next({ name: 'Login' }); // Перенаправляем на страницу входа
  } else {
    next(); // Продолжаем навигацию
  }
});

export default router;