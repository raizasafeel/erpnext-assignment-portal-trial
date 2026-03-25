<template>
	<router-link
		v-if="link"
		:to="link.to"
		class="flex w-full h-7 cursor-pointer items-center rounded text-ink-gray-8 duration-300 ease-in-out focus:outline-none focus-visible:rounded focus-visible:ring-2 focus-visible:ring-outline-gray-3"
		:class="
			isActive
				? 'bg-surface-selected shadow-sm'
				: 'hover:bg-surface-gray-2'
		"
	>
		<div
			class="flex items-center w-full duration-300 ease-in-out"
			:class="isCollapsed ? 'p-1 justify-center' : 'px-2 py-1'"
		>
			<Tooltip
				:text="link.label"
				placement="right"
				:disabled="!isCollapsed"
			>
				<span class="grid h-5 w-6 flex-shrink-0 place-items-center">
					<component
						:is="icons[link.icon]"
						class="h-4 w-4 stroke-1.5 text-ink-gray-8"
					/>
				</span>
			</Tooltip>
			<span
				class="flex-shrink-0 text-sm duration-300 ease-in-out"
				:class="
					isCollapsed
						? 'ml-0 w-0 overflow-hidden opacity-0'
						: 'ml-2 w-auto opacity-100'
				"
			>
				{{ link.label }}
			</span>
		</div>
	</router-link>
</template>

<script setup>
import { Tooltip } from "frappe-ui"
import { computed } from "vue"
import { useRoute } from "vue-router"
import * as icons from "lucide-vue-next"

const route = useRoute()

const props = defineProps({
	link: {
		type: Object,
		required: true,
	},
	isCollapsed: {
		type: Boolean,
		default: false,
	},
})

const isActive = computed(() => {
	if (props.link.to === "/") return route.path === "/"
	return route.path.startsWith(props.link.to)
})
</script>
