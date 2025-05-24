<!-- src/components/Navbar.vue -->
<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <router-link to="/" class="navbar-brand">RiddleFlow</router-link>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <!-- Ссылка на главную страницу -->
          <li class="nav-item">
            <router-link to="/" class="nav-link">
              <i class="bi bi-house me-1"></i>Главная
            </router-link>
          </li>

          <!-- Ссылка на хакатоны -->
          <li class="nav-item">
            <router-link to="/hackathons" class="nav-link">
              <i class="bi bi-trophy me-1"></i>Хакатоны
            </router-link>
          </li>

          <!-- Ссылка на профиль для всех пользователей -->
          <li class="nav-item">
            <router-link to="/profile" class="nav-link">
              <i class="bi bi-person-circle me-1"></i>Профиль
            </router-link>
          </li>

          <!-- Ссылка на вход для неавторизованных пользователей -->
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link to="/login" class="nav-link">
              <i class="bi bi-box-arrow-in-right me-1"></i>Вход
            </router-link>
          </li>

          <!-- Кнопка выхода для авторизованных пользователей -->
          <li class="nav-item" v-if="isAuthenticated">
            <a href="#" class="nav-link" @click.prevent="logout">
              <i class="bi bi-box-arrow-right me-1"></i>Выход
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'AppNavbar',
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem('token'); // Проверяем наличие токена
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token'); // Удаляем токен
      window.location.href = '/'; // Перенаправляем на главную страницу
    }
  }
};
</script>

<style scoped>
.navbar {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.nav-link {
  transition: all 0.2s ease;
}

.nav-link:hover {
  opacity: 0.8;
}

.bi {
  font-size: 1.1em;
}
</style>