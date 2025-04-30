<!-- src/components/CreateHackathon.vue -->
<template>
  <div class="container">
    <h1 class="mb-4">Создать новый хакатон</h1>

    <div v-if="error" class="alert alert-danger mb-4">
      {{ error }}
    </div>

    <form @submit.prevent="submitForm">
      <!-- Название -->
      <div class="mb-3">
        <label for="title" class="form-label">Название*</label>
        <input
          type="text"
          class="form-control"
          id="title"
          v-model="form.title"
          required
        >
      </div>

      <!-- Описание -->
      <div class="mb-3">
        <label for="description" class="form-label">Описание*</label>
        <textarea
          class="form-control"
          id="description"
          v-model="form.description"
          rows="4"
          required
        ></textarea>
      </div>

      <!-- Даты проведения -->
      <div class="row g-3 mb-4">
        <div class="col-md-6">
          <label for="start_time" class="form-label">Дата начала*</label>
          <input
            type="datetime-local"
            class="form-control"
            id="start_time"
            v-model="form.start_time"
            required
          >
        </div>

        <div class="col-md-6">
          <label for="end_time" class="form-label">Дата окончания*</label>
          <input
            type="datetime-local"
            class="form-control"
            id="end_time"
            v-model="form.end_time"
            required
          >
        </div>
      </div>

      <!-- Участники и команды -->
      <div class="row g-3 mb-4">
        <div class="col-md-6">
          <label for="max_participants" class="form-label">Макс. участников*</label>
          <input
            type="number"
            class="form-control"
            id="max_participants"
            v-model.number="form.max_participants"
            min="1"
            required
          >
        </div>

        <div class="col-md-6">
          <div class="form-check mt-4 pt-2">
            <input
              type="checkbox"
              class="form-check-input"
              id="allow_teams"
              v-model="form.allow_teams"
            >
            <label class="form-check-label" for="allow_teams">Разрешить команды</label>
          </div>
        </div>
      </div>

      <!-- Кнопка отправки -->
      <button
        type="submit"
        class="btn btn-primary w-100 py-2"
        :disabled="loading"
      >
        <template v-if="loading">
          <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
          Создание...
        </template>
        <template v-else>Создать хакатон</template>
      </button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CreateHackathon',
  data() {
    return {
      form: {
        title: '',
        description: '',
        allow_teams: false,
        max_participants: 1,
        start_time: '',
        end_time: ''
      },
      loading: false,
      error: null
    };
  },
  methods: {
    async submitForm() {
      this.error = null;
      this.loading = true;

      try {
        const token = localStorage.getItem('token');
        const response = await axios.post(
          'http://localhost:5000/api/v1/hackathons/',
          {
            ...this.form,
            start_time: new Date(this.form.start_time).toISOString(),
            end_time: new Date(this.form.end_time).toISOString()
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );

        if (response.data?.id) {
          this.$router.push({
            name: 'HackathonDetail',
            params: { id: response.data.id },
            query: { newlyCreated: 'true' }
          });
        }
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
            this.$router.push('/login');
            break;
          case 403:
            this.error = 'Доступ запрещен. Только организаторы могут создавать хакатоны';
            break;
          case 400:
            this.error = this.parseBackendError(error.response.data);
            break;
          default:
            this.error = 'Ошибка сервера. Пожалуйста, попробуйте позже';
        }
      } else {
        this.error = 'Не удалось подключиться к серверу. Проверьте интернет-соединение';
      }
    },

    parseBackendError(data) {
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          return data.detail.map(e =>
            `${e.loc?.join('.') ? e.loc.join('.') + ': ' : ''}${e.msg}`
          ).join(', ');
        }
        return data.detail;
      }
      return 'Неверные данные в форме';
    }
  }
};
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.alert {
  border-radius: 8px;
  padding: 1rem;
}

.form-control {
  border-radius: 8px;
  padding: 0.75rem 1rem;
}

.form-check-input {
  margin-top: 0.35em;
}

.btn-primary {
  font-weight: 600;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.btn-primary:disabled {
  opacity: 0.8;
}
</style>