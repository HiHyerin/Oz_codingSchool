const state = {
    user: null,
    token: localStorage.getItem('token'),
    currentPage: '/',
};

async function login(email, password) {
    const errorEl = document.getElementById('login-error');
    if (errorEl) errorEl.style.display = 'none';

    try {
        const data = await apis.login(email, password);

        if (data && data.status === 401) {
            if (errorEl) errorEl.style.display = 'block';
            return;
        }

        if (!data) return;

        state.token = data.access_token;
        localStorage.setItem('token', state.token);
        localStorage.setItem('isLoggedIn', 'true');
        await checkAuth();

        if (state.user && state.user.role === 'PENDING') {
            navigate('/');
        } else {
            navigate('/patients');
        }
    } catch (err) {
        if (errorEl) {
            errorEl.innerText = err.message || 'Login failed.';
            errorEl.style.display = 'block';
        }
    }
}

async function logout(event) {
    if (event) event.preventDefault();

    try {
        if (typeof apis !== 'undefined' && apis.logout) {
            await apis.logout();
        }
    } catch (err) {
        console.error('Logout failed:', err);
    } finally {
        state.token = null;
        state.user = null;
        localStorage.removeItem('token');
        localStorage.removeItem('isLoggedIn');
        updateNav();
        await navigate('/login');
    }
}

async function checkAuth() {
    if (!state.token && localStorage.getItem('isLoggedIn') === 'true') {
        try {
            const refreshResponse = await apis.refresh();
            if (refreshResponse.ok) {
                const data = await refreshResponse.json();
                state.token = data.access_token;
                localStorage.setItem('token', state.token);
            } else {
                localStorage.removeItem('isLoggedIn');
                return;
            }
        } catch (err) {
            return;
        }
    }

    if (!state.token) {
        updateNav();
        return;
    }

    try {
        state.user = await apis.getMe();
        updateNav();
    } catch (err) {
        if (state.token) logout();
    }
}

function updateNav() {
    const authLink = document.getElementById('auth-link');
    const adminLinkContainer = document.getElementById('admin-link-container');

    if (state.user) {
        document.body.classList.add('logged-in');

        if (state.user.role === 'ADMIN') {
            adminLinkContainer.innerHTML = `<li><a href="/admin/users" onclick="route(event)" class="nav-btn">User Admin</a></li>`;
        } else {
            adminLinkContainer.innerHTML = '';
        }

        authLink.innerHTML = `
            <span class="user-info" onclick="navigate('/my-page')" style="cursor:pointer;">${state.user.name}(${state.user.department})</span>
            <a href="#" onclick="logout(event)" class="nav-btn logout-btn">Logout</a>
        `;
    } else {
        document.body.classList.remove('logged-in');
        adminLinkContainer.innerHTML = '';
        authLink.innerHTML = `<a href="/login" onclick="route(event)" class="nav-btn login-btn">Login</a>`;
    }
}

function route(event) {
    event.preventDefault();
    const path = event.target.getAttribute('href') || event.currentTarget.getAttribute('href');
    navigate(path);
}

async function navigate(path, pushState = true) {
    if (pushState) {
        window.history.pushState({}, '', path);
    }

    const url = new URL(window.location.origin + path);
    const pathname = url.pathname;
    const searchParams = Object.fromEntries(url.searchParams);

    state.currentPage = pathname;
    const app = document.getElementById('app');
    app.innerHTML = '<div class="card">Loading...</div>';

    try {
        const publicPaths = ['/', '/home', '/login', '/signup'];
        if (!state.user && !publicPaths.includes(pathname)) {
            await navigate('/login');
            return;
        }

        if (state.user && state.user.role === 'PENDING' && !publicPaths.includes(pathname)) {
            utils.showAlert('Your account is waiting for admin approval.', 'error', 'Access denied');
            await navigate('/');
            return;
        }

        if (pathname === '/admin/users' && state.user?.role !== 'ADMIN') {
            utils.showAlert('Admin permission is required.', 'error', 'Access denied');
            await navigate('/');
            return;
        }

        if (pathname === '/' || pathname === '/home') {
            await pages.renderHome();
        } else if (pathname === '/login') {
            await pages.renderLogin();
        } else if (pathname === '/signup') {
            await pages.renderSignup();
        } else if (pathname === '/patients') {
            await pages.renderPatients(searchParams);
        } else if (pathname === '/patients/create') {
            await pages.renderPatientCreate();
        } else if (pathname.startsWith('/patients/') && pathname.endsWith('/medical-records/create')) {
            const patientId = pathname.split('/')[2];
            await pages.renderRecordCreate(patientId);
        } else if (pathname.startsWith('/patients/') && pathname.includes('/medical-records/')) {
            const parts = pathname.split('/');
            await pages.renderRecordDetail(parts[2], parts[4]);
        } else if (pathname === '/my-page') {
            await pages.renderMyPage();
        } else if (pathname === '/admin/users') {
            await pages.renderAdminUsers(searchParams);
        } else if (pathname.startsWith('/patients/')) {
            const patientId = pathname.split('/')[2];
            await pages.renderPatientDetail(patientId);
        } else {
            app.innerHTML = '<div class="card"><h2>404</h2><p>Page not found.</p></div>';
        }
    } catch (err) {
        app.innerHTML = `<div class="card"><h2>Error</h2><p>${err.message}</p><button onclick="navigate('/')">Home</button></div>`;
    }
}

window.onpopstate = () => {
    navigate(window.location.pathname + window.location.search, false);
};

document.addEventListener('DOMContentLoaded', () => {
    checkAuth().then(() => {
        navigate(window.location.pathname + window.location.search, false);
    });
});
