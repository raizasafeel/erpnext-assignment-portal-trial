import { createApp } from "vue"
import { createPinia } from "pinia"

import App from "./App.vue"
import router from "./router"
import { initSocket } from "./socket"

import {
	Alert,
	Badge,
	Button,
	Dialog,
	ErrorMessage,
	FormControl,
	Input,
	TextInput,
	frappeRequest,
	pageMetaPlugin,
	resourcesPlugin,
	setConfig,
} from "frappe-ui"

import "./index.css"

const globalComponents = {
	Button,
	TextInput,
	Input,
	FormControl,
	ErrorMessage,
	Dialog,
	Alert,
	Badge,
}

const app = createApp(App)
const pinia = createPinia()

setConfig("resourceFetcher", frappeRequest)

app.use(pinia)
app.use(router)
app.use(resourcesPlugin)
app.use(pageMetaPlugin)

const socket = initSocket()
app.config.globalProperties.$socket = socket

for (const key in globalComponents) {
	app.component(key, globalComponents[key])
}

// CSRF Bandaid
async function initCsrfToken() {
	try {
		const res = await fetch("/api/method/frappe.auth.get_csrf_token", {
			credentials: "include",
		})
		const data = await res.json()
		if (data.message) {
			window.csrf_token = data.message
		}
	} catch {
		// Fall back to the token from the HTML template
	}
}

initCsrfToken().then(() => app.mount("#app"))
