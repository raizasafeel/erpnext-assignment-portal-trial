import { defineStore } from "pinia"
import { createResource } from "frappe-ui"
import { computed } from "vue"

export const usersStore = defineStore("assignment-portal-users", () => {
	let userResource = createResource({
		url: "lms.lms.api.get_user_info",
		cache: "CheckerUser",
		auto: true,
		onError(error) {
			if (error && error.exc_type === "AuthenticationError") {
				window.location.href = "/login"
			}
		},
	})

	const isAdmin = computed(() => {
		const d = userResource.data
		return d?.is_moderator || d?.is_instructor || d?.is_evaluator || false
	})

	const isStudent = computed(() => {
		return userResource.data?.is_student || false
	})

	return {
		userResource,
		isAdmin,
		isStudent,
	}
})
