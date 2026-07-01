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

  document.querySelectorAll("[data-copy-message]").forEach((button) => {
    button.addEventListener("click", async () => {
      const message = button.getAttribute("data-copy-message") || "";
      const originalHtml = button.innerHTML;
      try {
        if (navigator.clipboard && message) {
          await navigator.clipboard.writeText(message);
        }
        button.innerHTML = '<i class="fa-solid fa-check me-2"></i>Copied';
        setTimeout(() => {
          button.innerHTML = originalHtml;
        }, 1800);
      } catch (error) {
        button.innerHTML = '<i class="fa-solid fa-triangle-exclamation me-2"></i>Copy failed';
        setTimeout(() => {
          button.innerHTML = originalHtml;
        }, 1800);
      }
    });
  });
});
