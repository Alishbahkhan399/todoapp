(() => {
  const backendUrl = __BACKEND_URL__;
  const accountLinks = document.querySelectorAll("[data-backend-path]");
  const backendNotice = document.querySelector("#backend-required");

  if (!backendUrl) {
    accountLinks.forEach((link) => {
      link.setAttribute("aria-disabled", "true");
      link.addEventListener("click", () => {
        if (backendNotice) backendNotice.hidden = false;
      });
    });
    return;
  }

  accountLinks.forEach((link) => {
    link.href = new URL(link.dataset.backendPath, `${backendUrl}/`).href;
    link.removeAttribute("aria-disabled");
  });
})();