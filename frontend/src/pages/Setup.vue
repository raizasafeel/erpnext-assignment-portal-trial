<template>
  <AppLayout>
    <div class="p-8 max-w-2xl">
      <h2 class="text-2xl font-bold text-gray-900 mb-1">Site Setup</h2>
      <p class="text-gray-500 mb-8">Connect your ERPNext demo site so we can check your assignments.</p>

      <!-- Existing sites -->
      <div v-if="sites.data?.length" class="mb-8 space-y-3">
        <div
          v-for="site in sites.data"
          :key="site.name"
          class="flex items-center justify-between p-4 bg-white rounded-lg border"
        >
          <div class="flex items-center gap-3">
            <div
              class="w-2.5 h-2.5 rounded-full"
              :class="site.connection_status === 'Connected' ? 'bg-green-500' : site.connection_status === 'Failed' ? 'bg-red-500' : 'bg-gray-300'"
            />
            <div>
              <div class="font-medium text-gray-900">{{ site.site_url }}</div>
              <div class="text-sm text-gray-500">{{ site.site_username }}</div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Button
              size="sm"
              :loading="testingConnection === site.name"
              @click="testConnection(site.name)"
            >
              Test
            </Button>
            <Button
              size="sm"
              variant="ghost"
              theme="red"
              @click="deleteSite(site.name)"
            >
              Remove
            </Button>
          </div>
        </div>
      </div>

      <!-- Add new site form -->
      <div class="p-6 bg-white rounded-lg border">
        <h3 class="font-semibold text-gray-900 mb-4">Add ERPNext Site</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Site URL <span class="text-red-500">*</span>
            </label>
            <input
              type="text"
              v-model="form.site_url"
              placeholder="https://your-site.erpnext.com"
              class="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              :class="fieldErrors.site_url ? 'border-red-500 bg-red-50' : 'border-gray-300'"
            />
            <p v-if="fieldErrors.site_url" class="text-xs text-red-600 mt-1">{{ fieldErrors.site_url }}</p>
            <p v-else class="text-xs text-gray-400 mt-1">Enter the full URL of your ERPNext demo site</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Username <span class="text-red-500">*</span>
            </label>
            <input
              type="text"
              v-model="form.site_username"
              placeholder="admin@example.com"
              class="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              :class="fieldErrors.site_username ? 'border-red-500 bg-red-50' : 'border-gray-300'"
            />
            <p v-if="fieldErrors.site_username" class="text-xs text-red-600 mt-1">{{ fieldErrors.site_username }}</p>
            <p v-else class="text-xs text-gray-400 mt-1">Enter the email address you use to log in to your ERPNext site</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Password <span class="text-red-500">*</span>
            </label>
            <input
              type="password"
              v-model="form.site_password"
              placeholder="Your site password"
              class="w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              :class="fieldErrors.site_password ? 'border-red-500 bg-red-50' : 'border-gray-300'"
            />
            <p v-if="fieldErrors.site_password" class="text-xs text-red-600 mt-1">{{ fieldErrors.site_password }}</p>
            <p v-else class="text-xs text-gray-400 mt-1">Enter your ERPNext site password</p>
          </div>

          <!-- Consent checkbox -->
          <div class="flex items-start gap-2 pt-2">
            <input
              id="consent"
              type="checkbox"
              v-model="consentGiven"
              class="mt-0.5 h-4 w-4 rounded text-gray-900 focus:ring-gray-900"
              :class="fieldErrors.consent ? 'border-red-500 ring-2 ring-red-500' : 'border-gray-300'"
            />
            <label for="consent" class="text-sm leading-tight" :class="fieldErrors.consent ? 'text-red-600' : 'text-gray-600'">
              By providing these credentials, I consent to the Assignment Portal
              accessing my site in read-only mode to verify my assignment completion.
              No data will be modified on my site.
              <span class="text-red-500">*</span>
            </label>
          </div>

          <ErrorMessage v-if="createError" :message="createError" />

          <div class="flex gap-2">
            <Button variant="solid" :loading="creating" @click="addSite">
              Save & Test Connection
            </Button>
          </div>
        </div>
      </div>

      <!-- Test result -->
      <div v-if="testResult" class="mt-4 p-4 rounded-lg border" :class="testResult.status === 'Connected' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'">
        <div class="flex items-center gap-2">
          <CheckCircle2 v-if="testResult.status === 'Connected'" class="w-5 h-5 text-green-600" />
          <XCircle v-else class="w-5 h-5 text-red-600" />
          <span :class="testResult.status === 'Connected' ? 'text-green-800' : 'text-red-800'" class="font-medium">
            {{ testResult.status === "Connected" ? `Connected as ${testResult.user}` : `Failed: ${testResult.error}` }}
          </span>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive } from "vue"
import { useRouter } from "vue-router"
import { createListResource, call, toast } from "frappe-ui"
import { CheckCircle2, XCircle } from "lucide-vue-next"
import AppLayout from "@/components/AppLayout.vue"

const router = useRouter()

const sites = createListResource({
  doctype: "ERPNext Site",
  fields: ["name", "site_url", "site_username", "connection_status"],
  auto: true,
})

const form = reactive({
  site_url: "",
  site_username: "",
  site_password: "",
})

const fieldErrors = reactive({
  site_url: "",
  site_username: "",
  site_password: "",
  consent: false,
})

const creating = ref(false)
const createError = ref("")
const testingConnection = ref(null)
const testResult = ref(null)
const consentGiven = ref(false)

function clearFieldErrors() {
  fieldErrors.site_url = ""
  fieldErrors.site_username = ""
  fieldErrors.site_password = ""
  fieldErrors.consent = false
}

function validateForm() {
  clearFieldErrors()
  let valid = true
  const missing = []

  if (!form.site_url.trim()) {
    fieldErrors.site_url = "Site URL is mandatory"
    missing.push("Site URL")
    valid = false
  }
  if (!form.site_username.trim()) {
    fieldErrors.site_username = "Username is mandatory"
    missing.push("Username")
    valid = false
  }
  if (!form.site_password) {
    fieldErrors.site_password = "Password is mandatory"
    missing.push("Password")
    valid = false
  }
  if (!consentGiven.value) {
    fieldErrors.consent = true
    missing.push("Consent")
    valid = false
  }

  if (!valid) {
    toast.error(`Please fill mandatory fields: ${missing.join(", ")}`)
  }

  return valid
}

async function addSite() {
  if (!validateForm()) return

  creating.value = true
  createError.value = ""
  testResult.value = null

  try {
    const doc = await call("frappe.client.insert", {
      doc: {
        doctype: "ERPNext Site",
        site_url: form.site_url.trim(),
        site_username: form.site_username.trim(),
        site_password: form.site_password,
      },
    })

    // Test connection
    const result = await call("erpnext_assignment_portal.api.test_connection", {
      site_name: doc.name,
    })
    testResult.value = result

    // Reset form
    form.site_url = ""
    form.site_username = ""
    form.site_password = ""
    consentGiven.value = false
    clearFieldErrors()

    sites.reload()

    if (result.status === "Connected") {
      toast.success("Site connected! Redirecting to Day 1 assignment...")
      setTimeout(() => router.push("/day/1"), 1500)
    }
  } catch (err) {
    console.error("addSite error:", err)
    createError.value =
      err?.messages?.[0] ||
      err?.exc_type ||
      err?.message ||
      "Failed to save site. Please try again."
    toast.error(createError.value)
  } finally {
    creating.value = false
  }
}

async function testConnection(siteName) {
  testingConnection.value = siteName
  testResult.value = null
  try {
    const result = await call("erpnext_assignment_portal.api.test_connection", {
      site_name: siteName,
    })
    testResult.value = result
    sites.reload()
    if (result.status === "Connected") {
      toast.success(`Connected successfully as ${result.user}`)
    } else {
      toast.error(`Connection failed: ${result.error}`)
    }
  } catch (err) {
    testResult.value = { status: "Failed", error: err.message }
    toast.error(`Connection failed: ${err.message}`)
  } finally {
    testingConnection.value = null
  }
}

async function deleteSite(siteName) {
  try {
    await call("erpnext_assignment_portal.api.delete_site", {
      site_name: siteName,
    })
    sites.reload()
    testResult.value = null
    toast.success("Site removed successfully")
  } catch (err) {
    toast.error(err?.messages?.[0] || err?.message || "Failed to remove site")
  }
}
</script>
