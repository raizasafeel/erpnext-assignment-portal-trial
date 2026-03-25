<template>
	<div
		class="flex h-full flex-col justify-between transition-all duration-300 ease-in-out border-r bg-surface-menu-bar"
		:class="sidebarStore.isSidebarCollapsed ? 'w-14' : 'w-56'"
	>
		<div
			class="flex flex-col overflow-y-auto"
			:class="sidebarStore.isSidebarCollapsed ? 'items-center' : ''"
		>
			<UserDropdown :isCollapsed="sidebarStore.isSidebarCollapsed" />
			<div class="flex flex-col overflow-y-auto">
				<div
					v-for="section in sidebarLinks"
					:key="section.label"
					class="mx-2 my-2.5"
				>
					<div
						v-if="
							section.label &&
							!sidebarStore.isSidebarCollapsed
						"
						class="mb-2 mt-3 flex cursor-pointer gap-1.5 px-1 text-base font-medium text-ink-gray-5 transition-all duration-300 ease-in-out"
					>
						<span>{{ section.label }}</span>
					</div>
					<nav class="space-y-1">
						<SidebarLink
							v-for="item in section.items"
							:key="item.to"
							:link="item"
							:isCollapsed="sidebarStore.isSidebarCollapsed"
						/>
					</nav>
				</div>
			</div>
		</div>
		<div
			class="m-2 flex items-center"
			:class="
				sidebarStore.isSidebarCollapsed
					? 'justify-center'
					: 'justify-end'
			"
		>
			<Tooltip
				:text="
					sidebarStore.isSidebarCollapsed ? 'Expand' : 'Collapse'
				"
			>
				<ChevronsLeft
					class="size-4 text-ink-gray-7 duration-300 stroke-1.5 ease-in-out cursor-pointer"
					:class="{
						'[transform:rotateY(180deg)]':
							sidebarStore.isSidebarCollapsed,
					}"
					@click="toggleSidebar"
				/>
			</Tooltip>
		</div>
	</div>
</template>

<script setup>
import { computed } from "vue"
import { Tooltip } from "frappe-ui"
import { ChevronsLeft } from "lucide-vue-next"
import { storeToRefs } from "pinia"
import { usersStore } from "@/stores/user"
import { useSidebar } from "@/stores/sidebar"
import UserDropdown from "@/components/Sidebar/UserDropdown.vue"
import SidebarLink from "@/components/Sidebar/SidebarLink.vue"

const sidebarStore = useSidebar()
const { isAdmin } = storeToRefs(usersStore())

const toggleSidebar = () => {
	sidebarStore.isSidebarCollapsed = !sidebarStore.isSidebarCollapsed
	localStorage.setItem(
		"ap_sidebar_collapsed",
		JSON.stringify(sidebarStore.isSidebarCollapsed),
	)
}

const sidebarLinks = computed(() => {
	if (isAdmin.value) {
		return [
			{
				label: "",
				items: [
					{
						to: "/dashboard",
						label: "Dashboard",
						icon: "LayoutDashboard",
					},
				],
			},
		]
	}
	return [
		{
			label: "",
			items: [
				{
					to: "/",
					label: "Dashboard",
					icon: "LayoutDashboard",
				},
				{
					to: "/setup",
					label: "Site Setup",
					icon: "Settings",
				},
			],
		},
		{
			label: "Assignments",
			items: [
				{
					to: "/day/1",
					label: "Day 1 — Master Data",
					icon: "ClipboardList",
				},
				{
					to: "/day/2",
					label: "Day 2 — Sales & Purchase",
					icon: "ShoppingCart",
				},
				{
					to: "/day/3",
					label: "Day 3 — Accounting",
					icon: "Calculator",
				},
			],
		},
	]
})
</script>
