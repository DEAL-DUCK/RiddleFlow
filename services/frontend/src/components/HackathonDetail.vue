<!-- src/components/HackathonDetail.vue -->
<template>
  <div class="container">
    <h1>{{ hackathon.title }}</h1>
    <img v-if="hackathon.logo_url" :src="hackathon.logo_url" alt="Логотип хакатона" class="img-fluid mb-3">

    <div class="hackathon-info">
      <p><strong>Описание:</strong> {{ hackathon.description }}</p>
      <p><strong>Дата начала:</strong> {{ formatDate(hackathon.start_time) }}</p>
      <p><strong>Дата окончания:</strong> {{ formatDate(hackathon.end_time) }}</p>
      <p><strong>Статус:</strong> {{ statusLabel }}</p>
      <p><strong>Участники:</strong> {{ hackathon.current_participants }} / {{ hackathon.max_participants }}</p>
      <p><strong>Команды:</strong> {{ hackathon.allow_teams ? 'Разрешены' : 'Запрещены' }}</p>
      <p><strong>Создан:</strong> {{ formatDate(hackathon.created_at) }}</p>
    </div>

    <!-- Блок участия -->
    <div class="participation-section">
      <button
        class="btn btn-primary"
        @click="handleParticipation"
        :disabled="participationLoading"
      >
        <span v-if="participationLoading">
          <span class="spinner-border spinner-border-sm"></span>
          Обработка...
        </span>
        <span v-else>Участвовать</span>
      </button>

      <div v-if="participationMessage" class="alert mt-3" :class="{
        'alert-success': participationSuccess,
        'alert-danger': !participationSuccess
      }">
        {{ participationMessage }}
      </div>
    </div>

    <button @click="goBack" class="btn btn-outline-secondary mt-4">
      Назад к списку
    </button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'HackathonDetail',
  data() {
    return {
      hackathon: {},
      userProfile: null,
      participationLoading: false,
      participationMessage: '',
      participationSuccess: false
    };
  },
  computed: {
    statusLabel() {
      const statuses = {
        'UPCOMING': 'Предстоящий',
        'ACTIVE': 'Активный',
        'FINISHED': 'Завершен'
      };
      return statuses[this.hackathon.status] || this.hackathon.status;
    },
  },
  async created() {
    await this.fetchUserProfile();
    await this.fetchHackathonDetail();
  },
  methods: {
    formatDate(dateString) {
      return new Date(dateString).toLocaleString();
    },

    async fetchHackathonDetail() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/api/v1/hackathons/${this.$route.params.id}`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        this.hackathon = response.data;
      } catch (error) {
        console.error('Ошибка загрузки хакатона:', error);
      }
    },

    async fetchUserProfile() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          'http://localhost:5000/api/v1/profiles/',
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        this.userProfile = response.data;
      } catch (error) {
        console.error('Ошибка загрузки профиля:', error);
      }
    },

    async handleParticipation() {
      this.participationLoading = true;
      this.participationMessage = '';
      this.participationSuccess = false;

      try {
        const token = localStorage.getItem('token');
        await axios.post(
          `http://localhost:5000/api/v1/hackathons/${this.hackathon.id}/users`,
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        this.participationSuccess = true;
        this.participationMessage = 'Вы успешно зарегистрированы на хакатон!';
        await this.fetchHackathonDetail();
      } catch (error) {
        this.handleParticipationError(error);
      } finally {
        this.participationLoading = false;
      }
    },

    handleParticipationError(error) {
      if (error.response) {
        switch (error.response.status) {
          case 401:
            this.participationMessage = 'Требуется авторизация';
            this.$router.push('/login');
            break;
          case 403:
            this.participationMessage = 'Только участники могут регистрироваться';
            break;
          case 409:
            this.participationMessage = 'Вы уже участвуете в этом хакатоне';
            break;
          case 400:
            this.participationMessage = 'Невозможно зарегистрироваться. Проверьте условия хакатона';
            break;
          default:
            this.participationMessage = 'Ошибка сервера. Попробуйте позже';
        }
      } else {
        this.participationMessage = 'Ошибка соединения с сервером';
      }
    },

    goBack() {
      this.$router.push({ name: 'HackathonList' });
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

.hackathon-info p {
  margin-bottom: 0.8rem;
  font-size: 1.1rem;
}

.img-fluid {
  max-height: 300px;
  object-fit: cover;
  border-radius: 8px;
}

.participation-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.btn-primary {
  padding: 0.75rem 2rem;
  font-weight: 600;
}

.alert {
  border-radius: 8px;
  padding: 1rem;
}
</style>