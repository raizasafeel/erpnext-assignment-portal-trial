import { createRouter, createWebHistory } from "vue-router"
import { usersStore } from "@/stores/user"
import { sessionStore } from "@/stores/session"

const routes = [
	{
		path: "/",
		name: "Dashboard",
		component: () => import("@/pages/Dashboard.vue"),
		meta: { studentOnly: true },
	},
	{
		path: "/setup",
		name: "Setup",
		component: () => import("@/pages/Setup.vue"),
		meta: { studentOnly: true },
	},
	{
		path: "/day/:day",
		name: "DayCheck",
		component: () => import("@/pages/DayCheck.vue"),
		meta: { studentOnly: true },
	},
	{
		path: "/dashboard",
		name: "StaffDashboard",
		component: () => import("@/pages/StaffDashboard.vue"),
		meta: { staffOnly: true },
	},
	{
		path: "/students/:student",
		name: "StudentDetail",
		component: () => import("@/pages/StudentDetail.vue"),
		meta: { staffOnly: true },
	},
]

const router = createRouter({
	history: createWebHistory("/assignment-portal"),
	routes,
})

router.beforeEach(async (to, _from, next) => {
	const users = usersStore()
	const session = sessionStore()

	try {
		await users.userResource.promise
	} catch {
		// ignore — auth check is cookie-based below
	}

	if (!session.isLoggedIn) {
		window.location.href = `/login?redirect-to=/assignment-portal${to.fullPath}`
		return
	}

	if (to.meta.staffOnly && !users.isAdmin) {
		return next("/")
	}
	if (to.meta.studentOnly && users.isAdmin) {
		return next("/dashboard")
	}

	next()
})

export default router
