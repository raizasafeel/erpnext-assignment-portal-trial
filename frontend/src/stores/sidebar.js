import { defineStore } from "pinia"
import { ref } from "vue"

export const useSidebar = defineStore("assignment-portal-sidebar", () => {
	const isSidebarCollapsed = ref(false)

	if (localStorage.getItem("ap_sidebar_collapsed")) {
		isSidebarCollapsed.value = JSON.parse(
			localStorage.getItem("ap_sidebar_collapsed"),
		)
	}

	return { isSidebarCollapsed }
})
