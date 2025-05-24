<!-- src/components/Profile.vue -->
<template>
  <div class="container">
    <h1>Профиль пользователя</h1>
    <div v-if="userProfile">
      <p><strong>ID:</strong> {{ userProfile.id }}</p>
      <p><strong>Имя:</strong> {{ userProfile.first_name || 'Не указано' }}</p>
      <p><strong>Фамилия:</strong> {{ userProfile.last_name || 'Не указано' }}</p>
      <p><strong>Дата рождения:</strong> {{ userProfile.birth_date || 'Не указано' }}</p>
      <p><strong>Биография:</strong> {{ userProfile.bio || 'Не указано' }}</p>
      <p><strong>Страна:</strong> {{ userProfile.country || 'Не указано' }}</p>
      <p><strong>Город:</strong> {{ userProfile.city || 'Не указано' }}</p>
      <p><strong>Работа:</strong> {{ userProfile.job || 'Не указано' }}</p>
      <p><strong>Телефон:</strong> {{ userProfile.phone_number || 'Не указано' }}</p>
      <button class="btn btn-danger" @click="logoutUser ">Выйти</button> <!-- Кнопка выхода -->
    </div>
    <div v-else>
      <p>Загрузка профиля...</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ProfileComp',
  data() {
    return {
      userProfile: null,
    };
  },
  created() {
    this.fetchUserProfile();
  },
  methods: {
    fetchUserProfile() {
      const token = localStorage.getItem('token'); // Получаем токен из localStorage
      if (token) {
        axios.get('http://localhost:5000/api/v1/profiles/', {
          headers: {
            'Authorization': `Bearer ${token}`, // Добавляем токен в заголовок
            'accept': 'application/json',
          },
        })
        .then(response => {
          this.userProfile = response.data; // Сохраняем данные профиля
        })
        .catch(error => {
          console.error('Ошибка при получении профиля:', error);
        });
      } else {
        console.error('Токен не найден');
      }
    },
    logoutUser () {
      const token = localStorage.getItem('token'); // Получаем токен из localStorage
      if (token) {
        axios.post('http://localhost:5000/api/v1/auth/logout', {}, {
          headers: {
            'Authorization': `Bearer ${token}`, // Добавляем токен в заголовок
            'accept': 'application/json',
          },
        })
        .then(response => {
          console.log('Выход выполнен:', response.data);
          localStorage.removeItem('token'); // Удаляем токен из localStorage
          window.location.href = '/'; // Перенаправляем на главную страницу с полной перезагрузкой
        })
        .catch(error => {
          console.error('Ошибка при выходе:', error);
        });
      } else {
        console.error('Токен не найден');
      }
    },
  },
};
</script>

<style scoped>
.container {
  margin-top: 20px;
}
</style>