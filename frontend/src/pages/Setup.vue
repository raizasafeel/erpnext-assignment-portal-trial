<template>
  <AppLayout>
    <div class="p-6 sm:p-8 w-full">
      <h2 class="text-2xl font-bold text-ink-gray-9">Site Setup</h2>
      <p class="mt-1 text-base text-ink-gray-5 mb-8">Connect your ERPNext demo site so we can check your assignments.</p>

      <div v-if="siteStore.hasSite" class="mb-8">
        <div class="flex items-center justify-between p-4 rounded-lg border border-outline-gray-2 bg-surface-white">
          <div class="flex items-center gap-3">
            <div
              class="w-2.5 h-2.5 rounded-full"
              :class="siteStore.site.connection_status === 'Connected' ? 'bg-green-500' : siteStore.site.connection_status === 'Failed' ? 'bg-red-500' : 'bg-gray-300'"
            />
            <div>
              <div class="font-medium text-ink-gray-9">{{ siteStore.site.site_url }}</div>
              <div class="text-sm text-ink-gray-5 mt-0.5">{{ siteStore.site.site_username }}</div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Button
              size="sm"
              :loading="testingConnection"
              @click="testConnection(siteStore.siteName)"
            >
              Test
            </Button>
            <Button
              size="sm"
              variant="ghost"
              theme="red"
              @click="deleteSite(siteStore.siteName)"
            >
              Remove
            </Button>
          </div>
        </div>
      </div>

      <div class="p-6 rounded-lg border border-outline-gray-2 bg-surface-white">
        <h3 class="font-semibold text-ink-gray-9 mb-6">Add ERPNext Site</h3>
        <div class="space-y-5">
          <FormControl
            v-model="form.site_url"
            type="text"
            label="Site URL"
            placeholder="https://your-site.erpnext.com"
            :description="fieldErrors.site_url || 'Enter the full URL of your ERPNext demo site'"
            required
          />
          <FormControl
            v-model="form.site_username"
            type="text"
            label="Username"
            placeholder="admin@example.com"
            :description="fieldErrors.site_username || 'Enter the email address you use to log in to your ERPNext site'"
            required
          />
          <FormControl
            v-model="form.site_password"
            type="password"
            label="Password"
            placeholder="Your site password"
            :description="fieldErrors.site_password || 'Enter your ERPNext site password'"
            required
          />

          <Checkbox
            v-model="consentGiven"
            label="By providing these credentials, I consent to the Assignment Portal accessing my site in read-only mode to verify my assignment completion. No data will be modified on my site."
          />

          <ErrorMessage v-if="createError" :message="createError" />

          <Button variant="solid" :loading="creating" @click="addSite">
            Save & Test Connection
          </Button>
        </div>
      </div>

      <div v-if="testResult" class="mt-6">
        <Alert :type="testResult.status === 'Connected' ? 'success' : 'error'">
          {{ testResult.status === "Connected" ? `Connected as ${testResult.user}` : `Failed: ${testResult.error}` }}
        </Alert>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive } from "vue"
import { useRouter } from "vue-router"
import { call, toast, Checkbox } from "frappe-ui"
import AppLayout from "@/components/AppLayout.vue"
import { useSiteStore } from "@/stores/site"

const router = useRouter()
const siteStore = useSiteStore()

const form = reactive({
  site_url: "",
  site_username: "",
  site_password: "",
})

const fieldErrors = reactive({
  site_url: "",
  site_username: "",
  site_password: "",
})

const creating = ref(false)
const createError = ref("")
const testingConnection = ref(false)
const testResult = ref(null)
const consentGiven = ref(false)

function clearFieldErrors() {
  fieldErrors.site_url = ""
  fieldErrors.site_username = ""
  fieldErrors.site_password = ""
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
    const doc = await call("erpnext_assignment_portal.api.create_site", {
      site_url: form.site_url,
      site_username: form.site_username,
      site_password: form.site_password,
    })

    const result = await call("erpnext_assignment_portal.api.test_connection", {
      site_name: doc.name,
    })
    testResult.value = result

    form.site_url = ""
    form.site_username = ""
    form.site_password = ""
    consentGiven.value = false
    clearFieldErrors()

    siteStore.reload()

    if (result.status === "Connected") {
      toast.success("Site connected! Redirecting to Day 1 assignment...")
      setTimeout(() => router.push("/day/1"), 1500)
    }
  } catch (err) {
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
  testingConnection.value = true
  testResult.value = null
  try {
    const result = await call("erpnext_assignment_portal.api.test_connection", {
      site_name: siteName,
    })
    testResult.value = result
    siteStore.reload()
    if (result.status === "Connected") {
      toast.success(`Connected successfully as ${result.user}`)
    } else {
      toast.error(result.error)
    }
  } catch (err) {
    testResult.value = { status: "Failed", error: err.message }
    toast.error(`Connection failed: ${err.message}`)
  } finally {
    testingConnection.value = false
  }
}

async function deleteSite(siteName) {
  try {
    await call("erpnext_assignment_portal.api.delete_site", {
      site_name: siteName,
    })
    siteStore.reload()
    testResult.value = null
    toast.success("Site removed successfully")
  } catch (err) {
    toast.error(err?.messages?.[0] || err?.message || "Failed to remove site")
  }
}
</script>
