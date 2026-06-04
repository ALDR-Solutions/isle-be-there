import { computed, ref } from "vue";

import { uploadsAPI } from "../services/api";

export function useImageManager({
  form,
  imageField = "image_urls",
  folder = "misc",
} = {}) {
  const fileInputRef = ref(null);
  const isDragging = ref(false);
  const uploadingCount = ref(0);
  const pendingImages = ref([]);
  const imagePendingRemoval = ref(null);
  const originalImageUrls = ref([]);
  const originalPayload = ref(null);
  const showImagePreviewModal = ref(false);
  const previewImageIndex = ref(0);
  let pendingImageId = 0;

  const displayImages = computed(() => [
    ...getCurrentImageUrls().map((url, index) => ({
      key: `existing-${index}-${url}`,
      url,
      index,
      isPending: false,
    })),
    ...pendingImages.value.map((image) => ({
      key: `pending-${image.id}`,
      url: image.previewUrl,
      id: image.id,
      isPending: true,
    })),
  ]);

  const activePreviewImage = computed(
    () => displayImages.value[previewImageIndex.value] ?? null,
  );

  function ensureImageArray() {
    if (!form.value) return [];
    if (!Array.isArray(form.value[imageField])) {
      form.value[imageField] = [];
    }
    return form.value[imageField];
  }

  function getCurrentImageUrls() {
    return ensureImageArray().filter(Boolean);
  }

  function clearPendingImages() {
    for (const image of pendingImages.value) {
      URL.revokeObjectURL(image.previewUrl);
    }
    pendingImages.value = [];
  }

  function clearOriginalState() {
    originalImageUrls.value = [];
    originalPayload.value = null;
  }

  function resetImageUi() {
    clearPendingImages();
    closeImagePreview();
    cancelRemoveImage();
  }

  function setOriginalState({ imageUrls = [], payload = null } = {}) {
    originalImageUrls.value = Array.isArray(imageUrls) ? [...imageUrls] : [];
    originalPayload.value = payload;
  }

  function openFilePicker() {
    fileInputRef.value?.click();
  }

  function stageFiles(files) {
    for (const file of files) {
      if (!file?.type?.startsWith("image/")) continue;
      pendingImageId += 1;
      pendingImages.value.push({
        id: pendingImageId,
        file,
        previewUrl: URL.createObjectURL(file),
      });
    }
  }

  function onFileChange(event) {
    stageFiles(Array.from(event.target?.files ?? []));
    if (event.target) {
      event.target.value = "";
    }
  }

  function onDrop(event) {
    isDragging.value = false;
    stageFiles(Array.from(event.dataTransfer?.files ?? []));
  }

  async function uploadPendingImages() {
    const uploadedUrls = [];

    try {
      for (const image of pendingImages.value) {
        uploadingCount.value += 1;
        try {
          const formData = new FormData();
          formData.append("file", image.file);
          const response = await uploadsAPI.uploadImage(formData, { folder });
          uploadedUrls.push(response.data.url);
        } finally {
          uploadingCount.value -= 1;
        }
      }
    } catch (error) {
      error.uploadedUrls = uploadedUrls;
      throw error;
    }

    return uploadedUrls;
  }

  async function cleanupUploadedImages(urls) {
    if (!urls.length) return;

    try {
      await uploadsAPI.deleteImages(urls);
    } catch (error) {
      console.error("Failed to clean up uploaded images", error);
    }
  }

  async function deleteImagesOrThrow(urls) {
    if (!urls.length) return;
    await uploadsAPI.deleteImages(urls);
  }

  function getMergedImageUrls(uploadedUrls = []) {
    return [...getCurrentImageUrls(), ...uploadedUrls];
  }

  function getRemovedOriginalUrls(nextUrls) {
    return originalImageUrls.value.filter((url) => !nextUrls.includes(url));
  }

  function openImagePreview(imageKey) {
    const nextIndex = displayImages.value.findIndex(
      (image) => image.key === imageKey,
    );
    if (nextIndex === -1) return;
    previewImageIndex.value = nextIndex;
    showImagePreviewModal.value = true;
  }

  function closeImagePreview() {
    showImagePreviewModal.value = false;
    previewImageIndex.value = 0;
  }

  function showPreviousImage() {
    if (!displayImages.value.length) return;
    previewImageIndex.value =
      (previewImageIndex.value - 1 + displayImages.value.length) %
      displayImages.value.length;
  }

  function showNextImage() {
    if (!displayImages.value.length) return;
    previewImageIndex.value =
      (previewImageIndex.value + 1) % displayImages.value.length;
  }

  function showRemoveConfirmation(image) {
    if (image.isPending) {
      removeImage(image);
    } else {
      imagePendingRemoval.value = image;
    }
  }

  function cancelRemoveImage() {
    imagePendingRemoval.value = null;
  }

  function confirmRemoveImage() {
    if (!imagePendingRemoval.value) return;
    removeImage(imagePendingRemoval.value);
    cancelRemoveImage();
  }

  function removeImage(image) {
    if (image.isPending) {
      const index = pendingImages.value.findIndex((item) => item.id === image.id);
      if (index === -1) return;
      const [removed] = pendingImages.value.splice(index, 1);
      URL.revokeObjectURL(removed.previewUrl);
      if (!displayImages.value.length) closeImagePreview();
      return;
    }

    const urls = ensureImageArray();
    urls.splice(image.index, 1);
    if (!displayImages.value.length) {
      closeImagePreview();
    } else if (previewImageIndex.value >= displayImages.value.length) {
      previewImageIndex.value = displayImages.value.length - 1;
    }
  }

  const showRemoveImageConfirmation = computed(
    () => imagePendingRemoval.value !== null,
  );

  return {
    fileInputRef,
    isDragging,
    uploadingCount,
    pendingImages,
    imagePendingRemoval,
    originalImageUrls,
    originalPayload,
    showImagePreviewModal,
    showRemoveImageConfirmation,
    previewImageIndex,
    displayImages,
    activePreviewImage,
    clearPendingImages,
    clearOriginalState,
    resetImageUi,
    setOriginalState,
    getCurrentImageUrls,
    openFilePicker,
    stageFiles,
    onFileChange,
    onDrop,
    uploadPendingImages,
    cleanupUploadedImages,
    deleteImagesOrThrow,
    getMergedImageUrls,
    getRemovedOriginalUrls,
    openImagePreview,
    closeImagePreview,
    showPreviousImage,
    showNextImage,
    showRemoveConfirmation,
    cancelRemoveImage,
    confirmRemoveImage,
    removeImage,
  };
}
