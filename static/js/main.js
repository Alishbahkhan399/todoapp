document.addEventListener('DOMContentLoaded', () => {
    initCustomCursor();
    initPasswordToggles();
    initMobileNavigation();
    initDeleteModal();
    initTaskReminderSystem();
    initToasts();
    handleNotificationPrompt();
});

function initCustomCursor() {
    if (window.matchMedia('(pointer: coarse)').matches) {
        document.body.classList.remove('cursor-enabled');
        return;
    }

    const dot = document.querySelector('.cursor-dot');
    const ring = document.querySelector('.cursor-ring');
    if (!dot || !ring) return;

    document.body.classList.add('cursor-enabled');

    let mouseX = 0;
    let mouseY = 0;
    let ringX = 0;
    let ringY = 0;

    document.addEventListener('pointermove', (event) => {
        mouseX = event.clientX;
        mouseY = event.clientY;
        dot.style.left = `${mouseX}px`;
        dot.style.top = `${mouseY}px`;
    });

    const animateCursor = () => {
        ringX += (mouseX - ringX) * 0.14;
        ringY += (mouseY - ringY) * 0.14;
        ring.style.left = `${ringX}px`;
        ring.style.top = `${ringY}px`;
        requestAnimationFrame(animateCursor);
    };

    requestAnimationFrame(animateCursor);

    const interactiveSelector = 'a, button, input, textarea, select, .task-card, .nav-link';
    document.querySelectorAll(interactiveSelector).forEach((element) => {
        element.addEventListener('mouseenter', () => {
            ring.style.transform = 'translate(-50%, -50%) scale(1.45)';
        });

        element.addEventListener('mouseleave', () => {
            ring.style.transform = 'translate(-50%, -50%) scale(1)';
        });
    });
}

function initPasswordToggles() {
    document.querySelectorAll('.toggle-password').forEach((button) => {
        button.addEventListener('click', () => {
            const input = button.parentElement.querySelector('input');
            if (!input) return;

            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            button.textContent = isPassword ? 'Hide' : 'Show';
        });
    });
}

function initMobileNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if (!navToggle || !navMenu) return;

    navToggle.addEventListener('click', () => {
        const isOpen = navMenu.classList.toggle('open');
        navToggle.setAttribute('aria-expanded', String(isOpen));
    });

    document.querySelectorAll('.nav-link').forEach((link) => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('open');
            navToggle.setAttribute('aria-expanded', 'false');
        });
    });
}

function initDeleteModal() {
    const modal = document.getElementById('delete-modal');
    const deleteForm = document.getElementById('delete-form');
    const deleteTaskName = document.getElementById('delete-task-name');
    const cancelButton = document.getElementById('cancel-delete');

    if (!modal || !deleteForm || !deleteTaskName || !cancelButton) return;

    document.querySelectorAll('.open-delete').forEach((button) => {
        button.addEventListener('click', () => {
            const taskTitle = button.dataset.title || 'this task';
            const taskUrl = button.dataset.url;
            deleteTaskName.textContent = `Delete "${taskTitle}"?`;
            deleteForm.setAttribute('action', taskUrl || '#');
            modal.classList.remove('hidden');
        });
    });

    cancelButton.addEventListener('click', () => modal.classList.add('hidden'));
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.classList.add('hidden');
        }
    });
}

function initToasts() {
    const container = document.getElementById('toast-container') || createToastContainer();

    if (window.taskoraMessages && window.taskoraMessages.length) {
        window.taskoraMessages.forEach((message) => {
            showToast(message.text, message.tags || 'success');
        });
    }
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.setAttribute('role', 'status');
    toast.innerHTML = `
        <button type="button" class="toast-close" aria-label="Close notification">×</button>
        <span>${message}</span>
    `;

    toast.querySelector('.toast-close').addEventListener('click', () => toast.remove());
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4300);
}

function handleNotificationPrompt() {
    const shouldRequest = sessionStorage.getItem('taskora_request_permission') === 'true';
    if (shouldRequest) {
        sessionStorage.removeItem('taskora_request_permission');
        requestBrowserPermission();
    }

    const notificationStatus = document.getElementById('notification-status');
    if (!notificationStatus) return;

    if ('Notification' in window && Notification.permission === 'denied') {
        notificationStatus.textContent = "Browser notifications are disabled. You'll still receive reminders inside the dashboard.";
        notificationStatus.classList.remove('hidden');
    } else if ('Notification' in window && Notification.permission === 'granted') {
        notificationStatus.textContent = 'Browser notifications are enabled for your reminders.';
        notificationStatus.classList.remove('hidden');
    }
}

function requestBrowserPermission() {
    if (!('Notification' in window)) return false;

    if (Notification.permission === 'granted') {
        return true;
    }

    Notification.requestPermission().then((permission) => {
        const notificationStatus = document.getElementById('notification-status');
        if (permission === 'granted') {
            if (notificationStatus) {
                notificationStatus.textContent = 'Browser notifications are enabled for your reminders.';
                notificationStatus.classList.remove('hidden');
            }
            return true;
        }

        if (notificationStatus) {
            notificationStatus.textContent = "Browser notifications are disabled. You'll still receive reminders inside the dashboard.";
            notificationStatus.classList.remove('hidden');
        }
        return false;
    });

    return false;
}

function initTaskReminderSystem() {
    const tasks = window.taskoraDashboardTasks || [];
    if (!Array.isArray(tasks) || tasks.length === 0) return;

    const storageKey = 'taskora-reminded';
    const reminded = new Set(JSON.parse(localStorage.getItem(storageKey) || '[]'));

    const checkReminders = () => {
        const now = new Date();

        tasks.forEach((task) => {
            if (!task || task.completed) return;
            const reminderTime = new Date(task.reminder_datetime);
            const key = `${task.id}:${task.reminder_datetime}`;

            if (!isNaN(reminderTime.getTime()) && reminderTime <= now && !reminded.has(key)) {
                reminded.add(key);
                localStorage.setItem(storageKey, JSON.stringify([...reminded]));
                triggerTaskReminder(task);
            }
        });
    };

    checkReminders();
    setInterval(checkReminders, 30000);

    const form = document.querySelector('.task-form');
    if (form) {
        form.addEventListener('submit', () => {
            sessionStorage.setItem('taskora_request_permission', 'true');
        });
    }
}

function triggerTaskReminder(task) {
    const card = document.querySelector(`.task-card[data-id="${task.id}"]`);
    if (card) {
        card.classList.add('is-reminded');
        setTimeout(() => card.classList.remove('is-reminded'), 2200);
    }

    const modal = document.getElementById('reminder-modal');
    const taskName = document.getElementById('reminder-task-name');
    const reminderText = document.getElementById('reminder-text');
    const viewLink = document.getElementById('view-reminder-task');
    const dismissButton = document.getElementById('dismiss-reminder');

    if (modal && taskName && reminderText && viewLink && dismissButton) {
        taskName.textContent = task.title;
        reminderText.textContent = `Your scheduled task is due now.`;
        viewLink.href = task.url;
        modal.classList.remove('hidden');
    }

    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Task Reminder', {
            body: `Your task '${task.title}' is scheduled for now.`,
            tag: `task-${task.id}`
        });
    }

    showToast(`Reminder: ${task.title} is due now.`, 'info');
}

const reminderDismiss = document.getElementById('dismiss-reminder');
if (reminderDismiss) {
    reminderDismiss.addEventListener('click', () => {
        const modal = document.getElementById('reminder-modal');
        if (modal) modal.classList.add('hidden');
    });
}

window.addEventListener('scroll', () => {
    const header = document.querySelector('.site-header');
    if (!header) return;
    header.classList.toggle('scrolled', window.scrollY > 8);
});
