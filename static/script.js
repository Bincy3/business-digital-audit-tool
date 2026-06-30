document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const submitButton = document.querySelector(".audit-submit");

  if (!form || !submitButton) {
    return;
  }

  form.addEventListener("submit", () => {
    const label = submitButton.querySelector(".button-label");
    const loading = submitButton.querySelector(".button-loading");

    submitButton.disabled = true;
    if (label && loading) {
      label.classList.add("d-none");
      loading.classList.remove("d-none");
    }
  });
});
