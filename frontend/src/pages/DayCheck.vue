<template>
  <AppLayout>
    <div class="p-8 max-w-4xl">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-2xl font-bold text-ink-gray-9">Day {{ dayNum }}</h2>
          <p class="text-ink-gray-5">{{ dayInfo.desc }}</p>
        </div>
        <Button
          variant="solid"
          :loading="running"
          :disabled="!selectedSite"
          @click="runChecks"
        >
          {{ running ? "Checking..." : "Run Checks" }}
        </Button>
      </div>

      <div v-if="sites.data?.length" class="mb-6">
        <label class="block text-sm font-medium text-ink-gray-7 mb-1">Select your ERPNext site</label>
        <select
          v-model="selectedSite"
          class="w-full max-w-md border border-outline-gray-2 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
        >
          <option value="">Choose a site...</option>
          <option v-for="site in sites.data" :key="site.name" :value="site.name">
            {{ site.site_url }} ({{ site.site_username }})
          </option>
        </select>
      </div>
      <div v-else class="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p class="text-yellow-800 text-sm">
          No ERPNext site connected yet.
          <router-link to="/setup" class="underline font-medium">Set up your site first.</router-link>
        </p>
      </div>

      <div v-if="error" class="mb-6 p-5 bg-red-50 border border-red-200 rounded-lg">
        <div class="flex items-start gap-3">
          <XCircle class="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <div>
            <p class="text-red-800 font-medium">{{ error }}</p>
            <router-link to="/setup" class="text-sm text-red-600 underline hover:text-red-800 mt-2 inline-block">
              Go to Site Setup
            </router-link>
          </div>
        </div>
      </div>

      <div v-if="results" class="mb-6">
        <div class="p-5 bg-surface-white rounded-lg border">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-3">
              <h3 class="text-lg font-semibold text-ink-gray-9">Results</h3>
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-semibold"
                :class="results.percentage === 100 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
              >
                {{ results.percentage === 100 ? "Passed" : "Failed" }}
              </span>
            </div>
            <span
              class="text-xl font-bold"
              :class="scoreColor"
            >
              {{ results.passed }}/{{ results.total }} ({{ results.percentage }}%)
            </span>
          </div>
          <div class="w-full bg-gray-100 rounded-full h-2.5">
            <div
              class="h-2.5 rounded-full transition-all duration-500"
              :class="barColor"
              :style="{ width: `${results.percentage}%` }"
            />
          </div>
        </div>
      </div>

      <div v-if="results" class="space-y-3">
        <div
          v-for="section in sectionList"
          :key="section.name"
          class="bg-surface-white rounded-lg border overflow-hidden"
        >
          <button
            class="w-full flex items-center justify-between px-4 py-3 hover:bg-surface-gray-2 transition-colors"
            @click="toggleSection(section.name)"
          >
            <div class="flex items-center gap-2.5">
              <CheckCircle2
                v-if="section.passed === section.total"
                class="w-5 h-5 text-green-500"
              />
              <XCircle v-else class="w-5 h-5 text-red-500" />
              <span class="font-medium text-ink-gray-9">{{ section.name }}</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-sm text-ink-gray-5">{{ section.passed }}/{{ section.total }}</span>
              <ChevronDown
                class="w-4 h-4 text-ink-gray-4 transition-transform"
                :class="{ 'rotate-180': openSections[section.name] }"
              />
            </div>
          </button>

          <div v-if="openSections[section.name]" class="border-t">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-surface-gray-2 text-ink-gray-5">
                  <th class="px-4 py-2 text-left w-8"></th>
                  <th class="px-4 py-2 text-left">Check</th>
                  <th class="px-4 py-2 text-left w-36">Expected</th>
                  <th class="px-4 py-2 text-left w-36">Actual</th>
                  <th class="px-4 py-2 text-left w-48">Details</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(check, idx) in section.checks"
                  :key="idx"
                  :class="check.status === 'Fail' ? 'bg-red-50' : ''"
                  class="border-t"
                >
                  <td class="px-4 py-2.5 text-center">
                    <CheckCircle2
                      v-if="check.status === 'Pass'"
                      class="w-4 h-4 text-green-500"
                    />
                    <XCircle v-else class="w-4 h-4 text-red-500" />
                  </td>
                  <td class="px-4 py-2.5 text-ink-gray-9">{{ check.check }}</td>
                  <td class="px-4 py-2.5 text-ink-gray-5">{{ check.expected || "—" }}</td>
                  <td class="px-4 py-2.5" :class="check.status === 'Fail' ? 'text-red-700 font-medium' : 'text-ink-gray-5'">
                    {{ check.actual || "—" }}
                  </td>
                  <td class="px-4 py-2.5 text-ink-gray-4">{{ check.message || "" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, reactive, watch } from "vue"
import { useRoute } from "vue-router"
import { createListResource, call } from "frappe-ui"
import { CheckCircle2, XCircle, ChevronDown } from "lucide-vue-next"
import AppLayout from "@/components/AppLayout.vue"

const route = useRoute()
const dayNum = computed(() => route.params.day)

const dayInfoMap = {
  1: { desc: "Master Data Setup — Company, Customers, Suppliers, Items, Warehouses, Users, Chart of Accounts" },
  2: { desc: "Sales & Purchase Module — Sales Order, Delivery Note, Payment, Purchase Order, Receipt, Stock Transfer" },
  3: { desc: "Basic Accounting & Manufacturing — Budget, Accounting Dimensions, Journal Entries, BOM" },
}

const dayInfo = computed(() => dayInfoMap[dayNum.value] || { desc: "" })

const sites = createListResource({
  doctype: "ERPNext Site",
  fields: ["name", "site_url", "site_username"],
  auto: true,
})

const selectedSite = ref("")
const running = ref(false)
const error = ref("")
const results = ref(null)
const openSections = reactive({})

// Auto-select first site
watch(
  () => sites.data,
  (data) => {
    if (data?.length && !selectedSite.value) {
      selectedSite.value = data[0].name
    }
  },
  { immediate: true }
)

// Clear results when switching days
watch(dayNum, () => {
  results.value = null
  error.value = ""
})

const sectionList = computed(() => {
  if (!results.value) return []
  const map = {}
  const order = []
  for (const r of results.value.results) {
    if (!map[r.section]) {
      map[r.section] = { name: r.section, checks: [], passed: 0, total: 0 }
      order.push(r.section)
    }
    map[r.section].checks.push(r)
    map[r.section].total++
    if (r.status === "Pass") map[r.section].passed++
  }
  return order.map((s) => map[s])
})

const scoreColor = computed(() => {
  if (!results.value) return ""
  const p = results.value.percentage
  if (p >= 80) return "text-green-600"
  if (p >= 50) return "text-yellow-600"
  return "text-red-600"
})

const barColor = computed(() => {
  if (!results.value) return "bg-gray-300"
  const p = results.value.percentage
  if (p >= 80) return "bg-green-500"
  if (p >= 50) return "bg-yellow-500"
  return "bg-red-500"
})

function toggleSection(name) {
  openSections[name] = !openSections[name]
}

async function runChecks() {
  if (!selectedSite.value) return
  running.value = true
  error.value = ""
  results.value = null

  try {
    const data = await call("erpnext_assignment_portal.api.run_check", {
      site_name: selectedSite.value,
      day: `Day ${dayNum.value}`,
    })

    if (data.error) {
      error.value = data.error
      return
    }

    results.value = data

    // Auto-expand failed sections
    for (const section of sectionList.value) {
      if (section.passed < section.total) {
        openSections[section.name] = true
      }
    }
  } catch (err) {
    error.value = err.messages?.[0] || err.message || "Failed to run checks. Is your site connected?"
  } finally {
    running.value = false
  }
}
</script>
