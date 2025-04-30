<!-- src/components/HackathonList.vue -->
<template>
  <div class="container">
    <h1>Список хакатонов</h1>
    <router-link to="/hackathons/create" class="btn btn-success mb-3">Создать Хакатон</router-link>
    <ul class="list-group">
      <li class="list-group-item" v-for="hackathon in hackathons" :key="hackathon.id">
        <router-link :to="{ name: 'HackathonDetail', params: { id: hackathon.id } }" class="text-decoration-none text-dark">
          <h5>{{ hackathon.title }}</h5>
          <p>{{ hackathon.description }}</p>
          <p>Максимальное количество участников: {{ hackathon.max_participants }}</p>
          <p>Дата начала: {{ formatDate(hackathon.start_time) }}</p>
          <p>Дата окончания: {{ formatDate(hackathon.end_time) }}</p>
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'HackathonList',
  data() {
    return {
      hackathons: [],
    };
  },
  created() {
    this.fetchHackathons();
  },
  methods: {
    async fetchHackathons() {
      try {
        const response = await axios.get('http://localhost:5000/api/v1/hackathons/');
        this.hackathons = response.data; // Предполагается, что данные приходят в формате массива
      } catch (error) {
        console.error('Ошибка при получении хакатонов:', error);
      }
    },
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
      return new Date(dateString).toLocaleString('ru-RU', options); // Форматируем дату для отображения
    },
  },
};
</script>

<style scoped>
.container {
  margin-top: 20px;
}
.list-group-item {
  margin-bottom: 10px;
  border: 1px solid #ccc; /* Добавляем границу для элементов списка */
  border-radius: 5px; /* Закругляем углы */
  padding: 15px; /* Добавляем отступы */
  transition: background-color 0.3s; /* Плавный переход для фона */
}
.list-group-item:hover {
  background-color: #f8f9fa; /* Изменяем фон при наведении */
}
.text-decoration-none {
  text-decoration: none; /* Убираем подчеркивание у ссылки */
}
.text-dark {
  color: #000; /* Устанавливаем цвет текста */
}
.btn-success {
  margin-bottom: 20px; /* Отступ снизу для кнопки */
}
</style>