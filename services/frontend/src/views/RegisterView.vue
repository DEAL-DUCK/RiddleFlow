<template>
  <div class="register-form">
    <h2>Регистрация</h2>

    <form @submit.prevent="handleSubmit">
      <!-- Поле email -->
      <div class="form-group">
        <label for="email">Email:</label>
        <input
          type="email"
          id="email"
          v-model="form.email"
          required
          placeholder="Введите ваш email"
        />
      </div>

      <!-- Поле пароля -->
      <div class="form-group">
        <label for="password">Пароль:</label>
        <input
          type="password"
          id="password"
          v-model="form.password"
          required
          placeholder="Введите пароль (минимум 3 символа)"
          minlength="3"
        />
      </div>

      <!-- Поле имени -->
      <div class="form-group">
        <label for="username">Имя пользователя:</label>
        <input
          type="text"
          id="username"
          v-model="form.username"
          required
          placeholder="Введите имя пользователя"
          minlength="8"
        />
        <div v-if="usernameError" class="error-message">
          {{ usernameError }}
        </div>
      </div>

      <!-- Поле выбора роли -->
      <div class="form-group">
        <label for="user_role">Роль пользователя:</label>
        <select
          id="user_role"
          v-model="form.user_role"
          required
        >
          <option
            v-for="role in roleOptions"
            :value="role"
            :key="role"
          >{{ role }}</option>
        </select>
      </div>




      <!-- Кнопка отправки -->
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Регистрируем...' : 'Зарегистрироваться' }}
      </button>

      <!-- Сообщения об ошибках -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <!-- Сообщение об успехе -->
      <div v-if="isSuccess" class="success-message">
        Регистрация прошла успешно! Теперь вы можете войти.
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      form: {
        email: '',
        password: '',
        username: '',
        user_role: 'PARTICIPANT',
      },
      isLoading: false,
      error: null,
      usernameError: null,
      emailError: null,    
      isSuccess: false,
      roleOptions: ['PARTICIPANT', 'CREATOR']
    };
  },
  methods: {
    async handleSubmit() {
      this.error = null;
      this.usernameError = null;
      this.emailError = null;

      if (this.form.username.length < 8) {
        this.usernameError = 'Имя должно быть не менее 8 символов';
        return;
      }

      if (!this.isValidEmail(this.form.email)) {
        this.emailError = 'Введите корректный email';
        return;
      }

      this.isLoading = true;

      try {
        // Отправка данных на сервер
        await axios.post('http://localhost:5000/api/v1/auth/register', {
          email: this.form.email,
          password: this.form.password,
          username: this.form.username,
          user_role: this.form.user_role,
          is_active: true,
          is_superuser: false,
          is_verified: false
        });

        // Успешная регистрация
        this.isSuccess = true;
        this.form = {
          email: '',
          password: '',
          username: '',
          user_role: 'PARTICIPANT'
        };

        // Перенаправление на страницу входа через 2 секунды
        setTimeout(() => {
          this.$router.push('/login');
        }, 2000);

      } catch (error) {
          if (error.response) {
          const errorData = error.response.data;

          if (error.response.status === 409) {
            if (errorData.detail === 'REGISTER_USER_ALREADY_EXISTS') {
              this.emailError = 'Этот email может быть уже зарегистрирован';
            } else {
              this.usernameError = 'Это имя пользователя может быть уже занято';
            }
          }
          else if (error.response.status === 422) {
            if (errorData.detail && Array.isArray(errorData.detail)) {
              errorData.detail.forEach(err => {
                if (err.loc?.includes('username')) {
                  this.usernameError = err.msg;
                }
                if (err.loc?.includes('email')) {
                  this.emailError = err.msg;
                }
                if (err.loc?.includes('password')) {
                  this.error = `Ошибка пароля: ${err.msg}`;
                }
              });
            }
          }
          else {
            this.error = errorData.detail || 'Произошла ошибка при регистрации';
          }
        } else {
          this.error = 'Не удалось подключиться к серверу';
        }
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.register-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  background-color: #42b983;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: red;
  margin-top: 10px;
}

.success-message {
  color: green;
  margin-top: 10px;
}

select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
}

</style>