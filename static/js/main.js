(() => {
  const header = document.querySelector("#site-header");
  const menuToggle = document.querySelector(".menu-toggle");
  const navLinks = document.querySelector(".nav-links");

  const updateHeader = () => header?.classList.toggle("is-scrolled", window.scrollY > 8);
  updateHeader();
  window.addEventListener("scroll", updateHeader, { passive: true });

  menuToggle?.addEventListener("click", () => {
    const open = menuToggle.getAttribute("aria-expanded") !== "true";
    menuToggle.setAttribute("aria-expanded", String(open));
    menuToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    navLinks?.classList.toggle("is-open", open);
  });

  document.querySelectorAll(".password-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const input = button.parentElement.querySelector("input");
      if (!input) return;
      const showing = input.type === "password";
      input.type = showing ? "text" : "password";
      button.textContent = showing ? "Hide" : "Show";
      button.setAttribute("aria-label", showing ? "Hide password" : "Show password");
    });
  });

  document.querySelectorAll(".toast").forEach((toast) => {
    let timeout;
    const dismiss = () => {
      toast.classList.add("is-leaving");
      window.setTimeout(() => toast.remove(), 320);
    };
    toast.querySelector(".toast-close")?.addEventListener("click", dismiss);
    timeout = window.setTimeout(dismiss, 5200);
    toast.addEventListener("mouseenter", () => window.clearTimeout(timeout), { once: true });
  });

  const overlay = document.querySelector("#reminder-overlay");
  const reminderName = document.querySelector("#reminder-task-name");
  const reminderOpen = document.querySelector("#reminder-open");
  const reminderDismiss = document.querySelector("#reminder-dismiss");
  const reminderQueue = [];
  let reminderShowing = false;

  const closeReminder = () => {
    overlay?.classList.remove("is-open");
    overlay?.setAttribute("aria-hidden", "true");
    reminderShowing = false;
    window.setTimeout(showNextReminder, 260);
  };

  const showNextReminder = () => {
    if (reminderShowing || !reminderQueue.length || !overlay) return;
    const reminder = reminderQueue.shift();
    reminderShowing = true;
    reminderName.textContent = reminder.title;
    reminderOpen.href = reminder.url;
    overlay.classList.add("is-open");
    overlay.setAttribute("aria-hidden", "false");
    const taskCard = document.querySelector(`[data-task-id="${reminder.id}"]`);
    taskCard?.classList.add("reminder-highlight");
    if ("Notification" in window && Notification.permission === "granted") {
      const notification = new Notification("Taskora reminder", {
        body: `Your task “${reminder.title}” is scheduled for now.`,
        tag: `taskora-${reminder.id}`,
      });
      notification.onclick = () => {
        window.focus();
        window.location.href = reminder.url;
      };
    }
  };

  reminderDismiss?.addEventListener("click", closeReminder);
  overlay?.addEventListener("click", (event) => {
    if (event.target === overlay) closeReminder();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && reminderShowing) closeReminder();
  });

  const reminderData = document.querySelector("#reminder-data");
  if (reminderData) {
    let reminders = [];
    try {
      reminders = JSON.parse(reminderData.textContent);
    } catch {
      reminders = [];
    }
    const checkReminders = () => {
      const now = Date.now();
      reminders.forEach((reminder) => {
        const key = `taskora-reminder-${reminder.id}-${reminder.reminder}`;
        if (Date.parse(reminder.reminder) <= now && !localStorage.getItem(key)) {
          localStorage.setItem(key, "shown");
          reminderQueue.push(reminder);
        }
      });
      showNextReminder();
    };
    checkReminders();
    window.setInterval(checkReminders, 15000);
  }

  const enableNotifications = document.querySelector("#enable-notifications");
  enableNotifications?.addEventListener("click", async () => {
    if (!("Notification" in window)) {
      window.dispatchEvent(new CustomEvent("taskora:toast", { detail: "Browser notifications are not available here. Dashboard reminders will still appear." }));
      return;
    }
    const permission = await Notification.requestPermission();
    const text = permission === "granted"
      ? "Browser notifications are enabled. Keep the dashboard open for reminders."
      : "Browser notifications are disabled. You'll still receive reminders inside the dashboard.";
    window.dispatchEvent(new CustomEvent("taskora:toast", { detail: text }));
  });

  window.addEventListener("taskora:toast", (event) => {
    const stack = document.querySelector(".toast-stack");
    if (!stack) return;
    const toast = document.createElement("div");
    toast.className = "toast toast-info";
    const message = document.createElement("span");
    message.textContent = event.detail;
    const close = document.createElement("button");
    close.className = "toast-close";
    close.type = "button";
    close.setAttribute("aria-label", "Dismiss notification");
    close.textContent = "×";
    close.addEventListener("click", () => toast.remove());
    toast.append(message, close);
    stack.append(toast);
    window.setTimeout(() => toast.remove(), 5200);
  });

  if (matchMedia("(hover: hover) and (pointer: fine)").matches) {
    const dot = document.querySelector(".cursor-dot");
    const ring = document.querySelector(".cursor-ring");
    let pointerX = -100;
    let pointerY = -100;
    let ringX = pointerX;
    let ringY = pointerY;
    document.body.classList.add("custom-cursor");
    window.addEventListener("mousemove", (event) => {
      pointerX = event.clientX;
      pointerY = event.clientY;
      dot.style.left = `${pointerX}px`;
      dot.style.top = `${pointerY}px`;
      dot.classList.add("is-visible");
      ring.classList.add("is-visible");
    }, { passive: true });
    const followPointer = () => {
      ringX += (pointerX - ringX) * 0.19;
      ringY += (pointerY - ringY) * 0.19;
      ring.style.left = `${ringX}px`;
      ring.style.top = `${ringY}px`;
      requestAnimationFrame(followPointer);
    };
    requestAnimationFrame(followPointer);
    document.addEventListener("mouseover", (event) => {
      if (event.target.closest("a, button, input, textarea, select, .task-card")) ring.classList.add("is-hovering");
    });
    document.addEventListener("mouseout", (event) => {
      if (event.target.closest("a, button, input, textarea, select, .task-card")) ring.classList.remove("is-hovering");
    });
    document.addEventListener("mouseleave", () => {
      dot.classList.remove("is-visible");
      ring.classList.remove("is-visible");
    });
    document.addEventListener("mouseenter", () => {
      dot.classList.add("is-visible");
      ring.classList.add("is-visible");
    });
  }
})();
