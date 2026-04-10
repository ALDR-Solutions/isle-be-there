import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { pinia } from './pinia'
import { registerUnauthorizedHandler } from './services/api'
import { useAuthStore } from './stores/auth'
import './style.css'
import VueTelInput from 'vue-tel-input';
import 'vue-tel-input/vue-tel-input.css';

const app = createApp(App)
const authStore = useAuthStore(pinia)

registerUnauthorizedHandler(async () => {
  const currentRoute = router.currentRoute.value

  authStore.logout()

  if (currentRoute.meta?.requiresAuth || currentRoute.meta?.role) {
    await router.push({
      name: 'Login',
      query: { redirect: currentRoute.fullPath },
    })
  }
})

app.use(pinia)
app.use(router)
app.use(VueTelInput)

app.mount('#app')
