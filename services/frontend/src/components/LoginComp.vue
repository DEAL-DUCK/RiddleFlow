<!-- src/components/LoginComp.vue -->
<template>
  <div class="container">
    <h1>Вход</h1>
    <form @submit.prevent="loginUser ">
      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input
          type="email"
          class="form-control"
          id="email"
          v-model="email"
          required
          :disabled="loading"
        >
      </div>

      <div class="mb-3">
        <label for="password" class="form-label">Пароль</label>
        <input
          type="password"
          class="form-control"
          id="password"
          v-model="password"
          required
          :disabled="loading"
        >
      </div>

      <button
        type="submit"
        class="btn btn-primary"
        :disabled="loading"
      >
        <span v-if="loading">Вход...</span>
        <span v-else>Войти</span>
      </button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LoginComp',
  data() {
    return {
      email: '',
      password: '',
      error: null,
      loading: false
    };
  },
  methods: {
    async loginUser () {
      this.error = null;
      this.loading = true;

      try {
        const formData = new URLSearchParams();
        formData.append('username', this.email);
        formData.append('password', this.password);
        formData.append('grant_type', 'password');

        const response = await axios.post(
          'http://localhost:5000/api/v1/auth/login',
          formData,
          {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            }
          }
        );

        if (!response.data.access_token) {
          throw new Error('Ошибка аутентификации');
        }

        localStorage.setItem('token', response.data.access_token);
        window.location.reload(); // Перезагружаем страницу

      } catch (error) {
        this.handleError(error);
      } finally {
        this.loading = false;
      }
    },

    handleError(error) {
      if (error.response) {
        switch (error.response.status) {
          case 401:
            this.error = 'Неверный email или пароль';
            break;
          case 500:
            this.error = 'Ошибка сервера. Попробуйте позже';
            break;
          default:
            this.error = 'Произошла ошибка. Попробуйте снова';
        }
      } else {
        this.error = 'Нет соединения с сервером';
      }
      console.error('Ошибка входа:', error);
    }
  },
  mounted() {
    // Проверяем наличие токена после перезагрузки страницы
    if (localStorage.getItem('token')) {
      // Если токен существует, перенаправляем на главную страницу через 1 секунду
      setTimeout(() => {
        window.location.href = '/'; // Перенаправляем на главную страницу
      }, 1000);
    }
  }
};
</script>

<style scoped>
.container {
  max-width: 400px;
  margin: 2rem auto;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-radius: 8px;
}

.alert {
  margin-bottom: 1.5rem;
}

.btn-primary {
  width: 100%;
  padding: 10px;
}
</style>