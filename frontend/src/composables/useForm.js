import { computed, ref } from 'vue'

function cloneValue(value) {
  return JSON.parse(JSON.stringify(value))
}

export function useForm(initialValues) {
  const values = ref(cloneValue(initialValues))
  const initialSnapshot = ref(cloneValue(initialValues))
  const errors = ref({})
  const submitError = ref('')
  const isSubmitting = ref(false)

  const isDirty = computed(() => JSON.stringify(values.value) !== JSON.stringify(initialSnapshot.value))

  function reset(nextValues = initialSnapshot.value) {
    values.value = cloneValue(nextValues)
    initialSnapshot.value = cloneValue(nextValues)
    errors.value = {}
    submitError.value = ''
    isSubmitting.value = false
  }

  function setErrors(nextErrors = {}) {
    errors.value = { ...nextErrors }
  }

  function setFieldError(field, message) {
    errors.value = {
      ...errors.value,
      [field]: message,
    }
  }

  function clearErrors() {
    errors.value = {}
    submitError.value = ''
  }

  return {
    values,
    errors,
    submitError,
    isDirty,
    isSubmitting,
    reset,
    setErrors,
    setFieldError,
    clearErrors,
  }
}
