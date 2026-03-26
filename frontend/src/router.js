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
	{
		path: "/unauthorized",
		name: "Unauthorized",
		component: () => import("@/pages/Unauthorized.vue"),
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

	try {
		await users.portalStatus.promise
	} catch {
		// ignore
	}

	if (!session.isLoggedIn) {
		window.location.href = `/login?redirect-to=/assignment-portal${to.fullPath}`
		return
	}

	if (to.name === "Unauthorized") {
		return next()
	}

	if (!users.isAdmin && !users.isStudent) {
		return next("/unauthorized")
	}

	if (to.meta.staffOnly && !users.isAdmin) {
		return next("/")
	}
	if (to.meta.studentOnly && !users.isStudent) {
		return next("/dashboard")
	}

	next()
})

export default router
