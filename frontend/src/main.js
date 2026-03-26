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

// Initialize theme from localStorage
const savedTheme = localStorage.getItem("ap_theme")
if (savedTheme) {
	document.documentElement.setAttribute("data-theme", savedTheme)
}

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

// Fetch a fresh CSRF token before mounting — the token in the HTML can
// become stale if the browser or CDN caches the page response.
fetch("/api/method/erpnext_assignment_portal.api.get_csrf_token", {
	method: "GET",
	headers: {
		Accept: "application/json",
		"X-Frappe-Site-Name": window.location.hostname,
	},
	credentials: "same-origin",
})
	.then((r) => r.json())
	.then((data) => {
		if (data.message) {
			window.csrf_token = data.message
		}
	})
	.catch(() => {})
	.finally(() => app.mount("#app"))
