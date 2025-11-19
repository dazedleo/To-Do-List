const API_BASE = 'http://localhost:8000/'; // Change base URL as per your backend

const app = document.getElementById('app');

let accessToken = localStorage.getItem('access_token') || null;

// Render signup page
function renderSignup() {
  app.innerHTML = `
    <h1>Sign Up</h1>
    <form id="signupForm">
      <input type="text" name="username" placeholder="Username" required />
      <input type="email" name="email" placeholder="Email" required />
      <input type="password" name="password" placeholder="Password" required />
      <button type="submit">Sign Up</button>
    </form>
    <nav>Already have an account? <a href="#" id="toLogin">Login</a></nav>
  `;

  document.getElementById('toLogin').addEventListener('click', e => {
    e.preventDefault();
    renderLogin();
  });

  document.getElementById('signupForm').addEventListener('submit', async e => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
      username: formData.get('username'),
      email: formData.get('email'),
      password: formData.get('password')
    };
    try {
      const res = await fetch(`${API_BASE}/api/accounts/signup/`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
      });
      const json = await res.json();
      if (res.ok) {
        alert('Signup successful! Please login.');
        renderLogin();
      } else {
        alert('Error: ' + JSON.stringify(json.message));
      }
    } catch (err) {
      alert('Network error: ' + err.message);
    }
  });
}

// Render login page
function renderLogin() {
  app.innerHTML = `
    <h1>Login</h1>
    <form id="loginForm">
      <input type="email" name="email" placeholder="Email" required />
      <input type="password" name="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
    <nav>Don't have an account? <a href="#" id="toSignup">Sign Up</a></nav>
  `;

  document.getElementById('toSignup').addEventListener('click', e => {
    e.preventDefault();
    renderSignup();
  });

  document.getElementById('loginForm').addEventListener('submit', async e => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
      email: formData.get('email'),
      password: formData.get('password')
    };
    try {
      const res = await fetch(`${API_BASE}/api/accounts/login/`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
      });
      const json = await res.json();
      if (res.ok) {
        accessToken = json.result.access_token;
        localStorage.setItem('access_token', accessToken);
        renderTaskList();
      } else {
        alert('Error: ' + JSON.stringify(json.message));
      }
    } catch (err) {
      alert('Network error: ' + err.message);
    }
  });
}

// Utility for authorized fetches
async function authFetch(url, options = {}) {
  options.headers = options.headers || {};
  options.headers['Authorization'] = 'Bearer ' + accessToken;
  return fetch(url, options);
}

// Render main task list UI
function renderTaskList() {
  app.innerHTML = `
    <h1>Task List</h1>
    <div>
      <button id="createTaskBtn" style="background:#28a745;">Create Task</button>
      <button id="allTasksBtn">All Tasks</button>
      <button id="notStartedTasksBtn">Not Started</button>
      <button id="inProgressTasksBtn">In Progress</button>
      <button id="completedTasksBtn">Completed</button>
      <button id="canceledTasksBtn">Canceled</button>
      <button id="logoutBtn" style="float:right; background: #dc3545;">Logout</button>
    </div>
    <ul id="taskList" style="list-style:none; padding-left: 0;"></ul>
    <div id="taskDetails"></div>
  `;

  document.getElementById('logoutBtn').addEventListener('click', () => {
    accessToken = null;
    localStorage.removeItem('access_token');
    renderLogin();
  });

  document.getElementById('createTaskBtn').addEventListener('click', () => renderCreateTask());
  document.getElementById('allTasksBtn').addEventListener('click', () => loadTasks('all'));
  document.getElementById('notStartedTasksBtn').addEventListener('click', () => loadTasks('not_started'));
  document.getElementById('inProgressTasksBtn').addEventListener('click', () => loadTasks('in_progress'));
  document.getElementById('completedTasksBtn').addEventListener('click', () => loadTasks('completed'));
  document.getElementById('canceledTasksBtn').addEventListener('click', () => loadTasks('canceled'));

  loadTasks('all');
}

// Load tasks from API by status filter
async function loadTasks(status = 'all') {
  const taskListEl = document.getElementById('taskList');
  taskListEl.innerHTML = 'Loading tasks...';

  try {
    const url =
      status === 'all'
        ? `${API_BASE}/api/tasks/list-of-task/?status=${status}`
        : `${API_BASE}/api/tasks/list-of-task/?status=${status}`;

    const res = await authFetch(url);
    const json = await res.json();

    if (res.ok) {
      taskListEl.innerHTML = '';

      if (!json.result.length) {
        taskListEl.innerHTML = `<li>No tasks found.</li>`;
        return;
      }

      json.result.forEach(task => {
        const li = document.createElement('li');

        // Pretty label conversion
        const statusLabels = {
          not_started: "Not Started",
          in_progress: "In Progress",
          completed: "Completed",
          canceled: "Canceled",
        };

        li.textContent = `[${statusLabels[task.status]}] ${task.title}`;
        li.className = 'task-item';
        li.addEventListener('click', () => renderTaskDetails(task.id));

        taskListEl.appendChild(li);
      });
    } else {
      taskListEl.innerHTML = `Error: ${JSON.stringify(json.message)}`;
    }
  } catch (err) {
    taskListEl.innerHTML = `Network error: ${err.message}`;
  }

  document.getElementById('taskDetails').innerHTML = '';
}


// Render task details with edit and delete
async function renderTaskDetails(taskId) {
  try {
    const res = await authFetch(`${API_BASE}/api/tasks/retrieve-task/?task_id=${taskId}`);
    const json = await res.json();

    if (!res.ok) {
      app.innerHTML = `Error loading task: ${JSON.stringify(json.message)}`;
      return;
    }

    const task = json.result;

    app.innerHTML = `
      <h1>Edit Task</h1>

      <form id="editTaskForm">
        
        <label>Title:<br />
          <input type="text" name="title" required value="${task.title}" />
        </label><br/>

        <label>Description:<br />
          <textarea name="description" rows="4">${task.description || ''}</textarea>
        </label><br/>

        <label>Due Date:<br />
          <input type="date" name="due_date" value="${task.due_date || ''}" />
        </label><br/>

        <label>Status:<br />
          <select name="status" required>
            <option value="not_started" ${task.status === 'not_started' ? 'selected' : ''}>Not Started</option>
            <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
            <option value="completed" ${task.status === 'completed' ? 'selected' : ''}>Completed</option>
            <option value="canceled" ${task.status === 'canceled' ? 'selected' : ''}>Canceled</option>
          </select>
        </label><br/><br/>

        <button type="submit">Update Task</button>
        <button type="button" id="deleteTaskBtn" style="background:#dc3545; margin-left:10px;">Delete Task</button>
        <button type="button" id="backBtn" style="margin-left:10px;">Back</button>
      </form>
    `;

    // Handle Update
    document.getElementById("editTaskForm").addEventListener("submit", async e => {
      e.preventDefault();
      const formData = new FormData(e.target);

      const data = {
        title: formData.get('title'),
        description: formData.get('description'),
        due_date: formData.get('due_date'),
        status: formData.get('status')
      };

      try {
        const updateRes = await authFetch(`${API_BASE}/api/tasks/update-task/?task_id=${taskId}`, {
          method: "PUT",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(data)
        });

        const updateJson = await updateRes.json();

        if (updateRes.ok) {
          alert("Task updated successfully!");
          renderTaskList();
        } else {
          alert("Error: " + JSON.stringify(updateJson.message));
        }
      } catch (err) {
        alert("Network error: " + err.message);
      }
    });

    // Handle Delete
    document.getElementById("deleteTaskBtn").addEventListener("click", async () => {
      if (!confirm("Are you sure you want to delete this task?")) return;

      try {
        const deleteRes = await authFetch(`${API_BASE}/api/tasks/destroy-task/?task_id=${taskId}`, {
          method: "DELETE"
        });
        let deleteJson = {};
        try {
          deleteJson = await deleteRes.json();   // Try to parse JSON
        } catch (e) {
          deleteJson = {}; // Avoid crash if response is empty
        }
        // const deleteJson = await deleteRes.json();

        if (deleteRes.ok) {
          alert("Task deleted successfully!");
          renderTaskList();
        } else {
          alert("Error: " + JSON.stringify(deleteJson.message));
        }
      } catch (err) {
        alert("Network error: " + err.message);
      }
    });

    // Back button
    document.getElementById("backBtn").addEventListener("click", () => {
      renderTaskList();
    });

  } catch (err) {
    app.innerHTML = `Network error: ${err.message}`;
  }
}

function renderCreateTask() {
  app.innerHTML = `
    <h1>Create New Task</h1>
    <form id="createTaskForm">
      <label>Title:<br />
        <input type="text" name="title" required />
      </label><br/>

      <label>Description:<br />
        <textarea name="description" rows="4" placeholder="Enter task description..."></textarea>
      </label><br/>

      <label>Due Date:<br />
        <input type="date" name="due_date" />
      </label><br/>

      <label>Status:<br />
        <select name="status" required>
          <option value="not_started">Not Started</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="canceled">Canceled</option>
        </select>
      </label><br/><br/>

      <button type="submit">Create Task</button>
      <button type="button" id="cancelCreateBtn" style="margin-left:10px;">Cancel</button>
    </form>
  `;

  // Handle submit
  document.getElementById('createTaskForm').addEventListener('submit', async e => {
    e.preventDefault();
    const formData = new FormData(e.target);

    const data = {
      title: formData.get('title'),
      description: formData.get('description'),
      due_date: formData.get('due_date'),
      status: formData.get('status')
    };

    try {
      const res = await authFetch(`${API_BASE}/api/tasks/create-task/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const json = await res.json();

      if (res.ok) {
        alert('Task created successfully');
        renderTaskList();
      } else {
        alert('Error: ' + JSON.stringify(json.message));
      }
    } catch (err) {
      alert('Network error: ' + err.message);
    }
  });

  document.getElementById('cancelCreateBtn').addEventListener('click', () => renderTaskList());
}



// Initialize
if (accessToken) {
  renderTaskList();
} else {
  renderLogin();
}
