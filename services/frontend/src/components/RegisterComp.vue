<!-- src/components/Register.vue -->
<template>
  <div class="container">
    <h1>Регистрация</h1>
    <form @submit.prevent="registerUser">
      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div class="mb-3">
        <label for="username" class="form-label">Имя пользователя</label>
        <input
          type="text"
          class="form-control"
          id="username"
          v-model="username"
          required
          :disabled="loading"
        >
      </div>

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
        <small class="form-text text-muted">Минимум 8 символов</small>
      </div>

      <div class="mb-3">
        <label for="userRole" class="form-label">Роль</label>
        <select
          class="form-select"
          id="userRole"
          v-model="userRole"
          required
          :disabled="loading"
        >
          <option value="CREATOR">Создатель хакатона</option>
          <option value="PARTICIPANT">Участник</option>
        </select>
      </div>

      <button
        type="submit"
        class="btn btn-primary"
        :disabled="loading"
      >
        <span v-if="loading">Регистрация...</span>
        <span v-else>Зарегистрироваться</span>
      </button>

      <div class="mt-3 text-center">
        <router-link to="/login">Уже есть аккаунт? Войти</router-link>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'RegisterComp',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      userRole: 'CREATOR',
      error: null,
      loading: false
    };
  },
  methods: {
    async registerUser() {
      this.error = null;

      if (!this.validateForm()) return;

      this.loading = true;

      try {
        const userData = {
          username: this.username,
          email: this.email,
          password: this.password,
          user_role: this.userRole
        };

        const response = await axios.post(
          'http://localhost:5000/api/v1/auth/register',
          userData
        );

        if (response.status === 201) {
          this.$router.push({
            path: '/login',
            query: { registered: 'success' }
          });
        }
      } catch (error) {
        this.handleError(error);
      } finally {
        this.loading = false;
      }
    },

    validateForm() {
      if (this.password.length < 8) {
        this.error = 'Пароль должен содержать минимум 8 символов';
        return false;
      }

      if (!this.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
        this.error = 'Введите корректный email';
        return false;
      }

      return true;
    },

    handleError(error) {
      if (error.response) {
        switch (error.response.status) {
          case 400:
            this.error = this.parseValidationErrors(error.response.data);
            break;
          case 409:
            this.error = 'Пользователь с таким email уже существует';
            break;
          default:
            this.error = 'Ошибка регистрации. Попробуйте позже';
        }
      } else {
        this.error = 'Сервер недоступен. Проверьте соединение';
      }
      console.error('Ошибка регистрации:', error);
    },

    parseValidationErrors(data) {
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          return data.detail.map(e => e.msg).join(', ');
        }
        return data.detail;
      }
      return 'Неверные данные для регистрации';
    }
  }
};
</script>

<style scoped>
.container {
  max-width: 500px;
  margin: 2rem auto;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-radius: 8px;
}

.form-text {
  font-size: 0.875em;
}

.btn-primary {
  width: 100%;
  padding: 10px;
}

.alert {
  margin-bottom: 1.5rem;
}
</style>