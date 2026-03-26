<template>
  <AppLayout>
    <div class="p-6 sm:p-8 w-full">
      <div class="flex items-start justify-between gap-4 mb-8">
        <div>
          <h2 class="text-2xl font-bold text-ink-gray-9">Day {{ dayNum }}</h2>
          <p class="mt-1 text-base text-ink-gray-5">{{ dayInfo.desc }}</p>
        </div>
        <Button
          v-if="siteStore.hasSite"
          variant="solid"
          :loading="running"
          @click="runChecks"
        >
          {{ running ? "Checking..." : "Run Checks" }}
        </Button>
      </div>

      <div v-if="!siteStore.hasSite" class="mb-8">
        <Alert type="warning">
          No ERPNext site connected yet.
          <router-link to="/setup" class="underline font-medium ml-1">Set up your site first.</router-link>
        </Alert>
      </div>

      <Alert v-if="error" type="error" class="mb-8">
        <div>
          <p class="font-medium">{{ error }}</p>
          <router-link to="/setup" class="text-sm underline mt-1 inline-block">
            Go to Site Setup
          </router-link>
        </div>
      </Alert>

      <div v-if="results" class="space-y-6">
        <div class="p-5 rounded-lg border border-outline-gray-2 bg-surface-white">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <h3 class="text-lg font-semibold text-ink-gray-9">Results</h3>
              <Badge
                :theme="results.percentage === 100 ? 'green' : 'red'"
                size="md"
              >
                {{ results.percentage === 100 ? "Passed" : "Failed" }}
              </Badge>
            </div>
            <span class="text-xl font-bold" :class="scoreColor">
              {{ results.passed }}/{{ results.total }} ({{ results.percentage }}%)
            </span>
          </div>
          <Progress :value="results.percentage" size="md" />
        </div>

        <div class="space-y-3">
          <div
            v-for="section in sectionList"
            :key="section.name"
            class="rounded-lg border border-outline-gray-2 bg-surface-white overflow-hidden"
          >
            <button
              class="w-full flex items-center justify-between px-4 py-3 hover:bg-surface-gray-2 transition-colors"
              @click="toggleSection(section.name)"
            >
              <div class="flex items-center gap-2.5">
                <CheckCircle2
                  v-if="section.passed === section.total"
                  class="w-5 h-5 text-green-600"
                />
                <XCircle v-else class="w-5 h-5 text-red-600" />
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

            <div v-if="openSections[section.name]" class="border-t border-outline-gray-1">
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
                    :class="check.status === 'Fail' ? 'bg-red-50 dark:bg-red-900/10' : ''"
                    class="border-t border-outline-gray-1"
                  >
                    <td class="px-4 py-2.5 text-center">
                      <CheckCircle2 v-if="check.status === 'Pass'" class="w-4 h-4 text-green-600" />
                      <XCircle v-else class="w-4 h-4 text-red-600" />
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

      <div v-if="pastAttempts.length" class="mt-10">
        <h3 class="text-lg font-semibold text-ink-gray-9 mb-4">
          Past Attempts ({{ pastAttempts.length }})
        </h3>
        <div class="space-y-2">
          <div
            v-for="(attempt, idx) in pastAttempts"
            :key="attempt.name"
            class="rounded-lg border border-outline-gray-2 bg-surface-white overflow-hidden"
          >
            <button
              class="w-full flex items-center justify-between p-3 hover:bg-surface-gray-2 transition-colors"
              @click="toggleAttempt(attempt.name)"
            >
              <div class="flex items-center gap-3">
                <CheckCircle2
                  v-if="attempt.percentage === 100"
                  class="w-4 h-4 text-green-600"
                />
                <XCircle v-else class="w-4 h-4 text-red-600" />
                <span class="text-sm font-medium text-ink-gray-7">
                  #{{ pastAttempts.length - idx }}
                </span>
                <span class="text-sm text-ink-gray-9">
                  {{ attempt.passed_checks }}/{{ attempt.total_checks }}
                  ({{ attempt.percentage }}%)
                </span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-xs text-ink-gray-4">
                  {{ formatDate(attempt.checked_at) }}
                </span>
                <ChevronDown
                  class="w-3.5 h-3.5 text-ink-gray-4 transition-transform"
                  :class="{ 'rotate-180': openAttempts[attempt.name] }"
                />
              </div>
            </button>

            <div v-if="openAttempts[attempt.name]" class="border-t border-outline-gray-1">
              <div
                v-for="section in parsedSections(attempt)"
                :key="section.name"
                class="border-b border-outline-gray-1 last:border-b-0"
              >
                <div class="flex items-center justify-between px-4 py-2.5 bg-surface-gray-2 text-sm">
                  <div class="flex items-center gap-2">
                    <CheckCircle2
                      v-if="section.passed === section.total"
                      class="w-4 h-4 text-green-600"
                    />
                    <XCircle v-else class="w-4 h-4 text-red-600" />
                    <span class="font-medium text-ink-gray-7">{{ section.name }}</span>
                  </div>
                  <span class="text-ink-gray-5">{{ section.passed }}/{{ section.total }}</span>
                </div>
                <table class="w-full text-sm">
                  <tbody>
                    <tr
                      v-for="(check, cidx) in section.checks"
                      :key="cidx"
                      :class="check.status === 'Fail' ? 'bg-red-50 dark:bg-red-900/10' : ''"
                      class="border-t border-outline-gray-1"
                    >
                      <td class="px-4 py-2 w-6 text-center">
                        <CheckCircle2 v-if="check.status === 'Pass'" class="w-4 h-4 text-green-600" />
                        <XCircle v-else class="w-4 h-4 text-red-600" />
                      </td>
                      <td class="py-2 text-ink-gray-9">{{ check.check }}</td>
                      <td class="px-4 py-2 text-right text-ink-gray-5 text-xs">
                        <template v-if="check.status === 'Fail'">
                          Expected: {{ check.expected || "—" }} | Got: {{ check.actual || "—" }}
                        </template>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, reactive, watch } from "vue"
import { useRoute } from "vue-router"
import { createResource, call, Progress } from "frappe-ui"
import { CheckCircle2, XCircle, ChevronDown } from "lucide-vue-next"
import AppLayout from "@/components/AppLayout.vue"
import { useSiteStore } from "@/stores/site"

const route = useRoute()
const siteStore = useSiteStore()
const dayNum = computed(() => route.params.day)

const dayInfoMap = {
  1: { desc: "Master Data Setup — Company, Customers, Suppliers, Items, Warehouses, Users, Chart of Accounts" },
  2: { desc: "Sales & Purchase Module — Sales Order, Delivery Note, Payment, Purchase Order, Receipt, Stock Transfer" },
  3: { desc: "Basic Accounting & Manufacturing — Budget, Accounting Dimensions, Journal Entries, BOM" },
}

const dayInfo = computed(() => dayInfoMap[dayNum.value] || { desc: "" })

const myResults = createResource({
  url: "erpnext_assignment_portal.api.get_my_results",
  cache: "MyResults",
  auto: true,
})

const pastAttempts = computed(() => {
  if (!myResults.data) return []
  return myResults.data.filter((r) => r.day === `Day ${dayNum.value}`)
})

const running = ref(false)
const error = ref("")
const results = ref(null)
const openSections = reactive({})
const openAttempts = reactive({})

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

function toggleSection(name) {
  openSections[name] = !openSections[name]
}

function toggleAttempt(name) {
  openAttempts[name] = !openAttempts[name]
}

function parsedSections(result) {
  if (!result?.result_json) return []
  try {
    const data = JSON.parse(result.result_json)
    if (!data?.results) return []
    const map = {}
    const order = []
    for (const c of data.results) {
      if (!map[c.section]) {
        map[c.section] = { name: c.section, checks: [], passed: 0, total: 0 }
        order.push(c.section)
      }
      map[c.section].checks.push(c)
      map[c.section].total++
      if (c.status === "Pass") map[c.section].passed++
    }
    return order.map((s) => map[s])
  } catch {
    return []
  }
}

async function runChecks() {
  if (!siteStore.siteName) return
  running.value = true
  error.value = ""
  results.value = null

  try {
    const data = await call("erpnext_assignment_portal.api.run_check", {
      site_name: siteStore.siteName,
      day: `Day ${dayNum.value}`,
    })

    if (data.error) {
      error.value = data.error
      return
    }

    results.value = data
    myResults.reload()

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

function formatDate(dt) {
  if (!dt) return ""
  return new Date(dt).toLocaleString()
}
</script>
