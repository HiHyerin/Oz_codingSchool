const uiMappers = {
    genderToApi(value) {
        if (value === 'male') return 'M';
        if (value === 'female') return 'F';
        return value;
    },
    genderToTemplate(value) {
        if (value === 'M') return 'male';
        if (value === 'F') return 'female';
        return value;
    },
    genderToLabel(value) {
        if (value === 'M' || value === 'male') return 'Male';
        if (value === 'F' || value === 'female') return 'Female';
        return value || '-';
    },
    departmentToApi(value) {
        return {
            'developer': 'DEV',
            'medical team': 'MEDICAL',
            'researcher': 'RESEARCH',
        }[value] || value;
    },
    departmentToTemplate(value) {
        return {
            DEV: 'developer',
            MEDICAL: 'medical team',
            RESEARCH: 'researcher',
        }[value] || value;
    },
    roleToLabel(value) {
        return {
            PENDING: 'Pending',
            STAFF: 'Staff',
            ADMIN: 'Admin',
        }[value] || value || '-';
    },
};

const pages = {
    async renderHome() {
        const html = await utils.loadTemplate('home');
        if (state.currentPage !== '/' && state.currentPage !== '/home') return;
        document.getElementById('app').innerHTML = html;

        const actions = document.getElementById('home-actions');
        if (!state.user) {
            actions.innerHTML = '<button onclick="navigate(\'/login\')">Login to start</button>';
        } else if (state.user.role === 'PENDING') {
            actions.innerHTML = '<p>Waiting for admin approval.</p>';
        } else {
            actions.innerHTML = '<button onclick="navigate(\'/patients\')">Open patients</button>';
        }
    },

    async renderLogin() {
        document.getElementById('app').innerHTML = await utils.loadTemplate('login');
    },

    async renderSignup() {
        document.getElementById('app').innerHTML = await utils.loadTemplate('signup');
        const phoneInput = document.getElementById('signup-phone');
        if (phoneInput) phoneInput.addEventListener('input', (event) => utils.handlePhoneInput(event));
    },

    async renderPatients(params = {}) {
        const patients = await apis.getPatients(params);
        const html = await utils.loadTemplate('patients');
        if (state.currentPage !== '/patients') return;
        document.getElementById('app').innerHTML = html;

        const nameInput = document.getElementById('search-name');
        const genderSelect = document.getElementById('filter-gender');
        const minAgeInput = document.getElementById('filter-min-age');
        const maxAgeInput = document.getElementById('filter-max-age');

        if (nameInput && params.search) nameInput.value = params.search;
        if (genderSelect && params.gender) genderSelect.value = uiMappers.genderToTemplate(params.gender);
        if (minAgeInput && params.min_age) minAgeInput.value = params.min_age;
        if (maxAgeInput && params.max_age) maxAgeInput.value = params.max_age;

        const listBody = document.getElementById('patients-list');
        if (!patients.length) {
            listBody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:2rem;">No patients found.</td></tr>';
            return;
        }

        listBody.innerHTML = patients.map((patient) => `
            <tr>
                <td>${patient.id}</td>
                <td>${patient.name}</td>
                <td>${patient.age}</td>
                <td>${uiMappers.genderToLabel(patient.gender)}</td>
                <td>${utils.formatPhoneNumber(patient.phone)}</td>
                <td><button onclick="navigate('/patients/${patient.id}')">Detail</button></td>
            </tr>
        `).join('');
    },

    async renderPatientCreate() {
        document.getElementById('app').innerHTML = await utils.loadTemplate('patient-create');
        const phoneInput = document.getElementById('phone_number');
        if (phoneInput) phoneInput.addEventListener('input', (event) => utils.handlePhoneInput(event));
    },

    async renderPatientDetail(patientId) {
        const patient = await apis.getPatient(patientId);
        const records = await apis.getPatientMedicalRecords(patientId);
        const html = await utils.loadTemplate('patient-detail');
        if (!state.currentPage.startsWith('/patients/')) return;
        document.getElementById('app').innerHTML = html;

        document.getElementById('patient-name').innerText = `${patient.name} (${uiMappers.genderToLabel(patient.gender)})`;
        document.getElementById('patient-info').innerText = `Age: ${patient.age} | Phone: ${utils.formatPhoneNumber(patient.phone)}`;
        document.getElementById('update-name').value = patient.name;
        document.getElementById('update-phone').value = utils.formatPhoneNumber(patient.phone);

        const updatePhoneInput = document.getElementById('update-phone');
        if (updatePhoneInput) updatePhoneInput.addEventListener('input', (event) => utils.handlePhoneInput(event));

        document.getElementById('add-record-btn').onclick = () => navigate(`/patients/${patientId}/medical-records/create`);
        state.currentPatientId = patientId;

        const listBody = document.getElementById('records-list');
        if (!records.length) {
            listBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:2rem;">No medical records.</td></tr>';
            return;
        }

        listBody.innerHTML = records.map((record) => `
            <tr>
                <td>${record.id}</td>
                <td>${record.chart_number}</td>
                <td>${record.symptoms}</td>
                <td>${new Date(record.created_at).toLocaleString()}</td>
                <td><button onclick="navigate('/patients/${patientId}/medical-records/${record.id}')">Detail</button></td>
            </tr>
        `).join('');
    },

    async renderRecordCreate(patientId) {
        document.getElementById('app').innerHTML = await utils.loadTemplate('record-create');
        const imageInput = document.getElementById('xray_image');
        const previewContainer = document.getElementById('image-preview-container');

        imageInput.onchange = (event) => {
            const file = event.target.files[0];
            if (!file) {
                previewContainer.innerHTML = '<p>Image preview appears here.</p>';
                return;
            }

            const reader = new FileReader();
            reader.onload = (readerEvent) => {
                previewContainer.innerHTML = `<img src="${readerEvent.target.result}" style="max-width:100%; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1);">`;
            };
            reader.readAsDataURL(file);
        };

        document.getElementById('record-create-form').onsubmit = (event) => this.handleRecordCreate(event, patientId);
        document.getElementById('cancel-btn').onclick = () => navigate(`/patients/${patientId}`);
    },

    async renderRecordDetail(patientId, recordId) {
        const record = await apis.getMedicalRecord(patientId, recordId);
        const analyses = await apis.getMedicalRecordAnalyses(patientId, recordId);
        document.getElementById('app').innerHTML = await utils.loadTemplate('record-detail');

        document.getElementById('record-id').innerText = record.id;
        document.getElementById('chart-number').innerText = record.chart_number;
        document.getElementById('symptoms-text').innerText = record.symptoms;
        document.getElementById('created-at').innerText = new Date(record.created_at).toLocaleString();

        const xrayImage = record.xray_images?.[0];
        const imageElement = document.getElementById('xray-img');
        imageElement.src = xrayImage?.image_url || '';
        imageElement.alt = xrayImage ? 'X-ray image' : 'No X-ray image';

        document.getElementById('predict-btn').onclick = () => this.handlePredict(patientId, recordId);
        document.getElementById('back-to-patient-btn').onclick = () => navigate(`/patients/${record.patient_id}`);

        const analysisList = document.getElementById('analysis-list');
        if (!analyses.length) {
            analysisList.innerHTML = '<p>No AI analysis results.</p>';
            return;
        }

        analysisList.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Created At</th>
                        <th>Pneumonia</th>
                        <th>Confidence</th>
                        <th>AI Model</th>
                    </tr>
                </thead>
                <tbody>
                    ${analyses.map((analysis) => `
                        <tr class="${analysis.is_pneumonia ? 'result-positive' : 'result-negative'}">
                            <td>${new Date(analysis.created_at).toLocaleString()}</td>
                            <td><strong>${analysis.is_pneumonia ? 'Positive' : 'Negative'}</strong></td>
                            <td>${Math.round(Number(analysis.confidence) * 100)}%</td>
                            <td>${analysis.ai_model}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    },

    async renderMyPage() {
        document.getElementById('app').innerHTML = await utils.loadTemplate('my-page');

        document.getElementById('me-email').innerText = state.user.email;
        document.getElementById('me-name-display').innerText = state.user.name;
        document.getElementById('me-department-display').innerText = state.user.department;
        document.getElementById('me-gender-display').innerText = uiMappers.genderToLabel(state.user.gender);
        document.getElementById('me-phone-display').innerText = utils.formatPhoneNumber(state.user.phone_number);
        document.getElementById('me-role-display').innerText = uiMappers.roleToLabel(state.user.role);
        document.getElementById('update-me-department').value = uiMappers.departmentToTemplate(state.user.department);
        document.getElementById('update-me-phone').value = utils.formatPhoneNumber(state.user.phone_number);

        const mePhoneInput = document.getElementById('update-me-phone');
        if (mePhoneInput) mePhoneInput.addEventListener('input', (event) => utils.handlePhoneInput(event));

        document.getElementById('update-me-form').onsubmit = (event) => this.handleUpdateMe(event);
        document.getElementById('update-password-form').onsubmit = (event) => this.handleUpdatePassword(event);
        document.getElementById('delete-me-btn').onclick = () => this.handleDeleteMe();
    },

    async renderAdminUsers(params = {}) {
        const users = await apis.adminGetUsers(params);
        document.getElementById('app').innerHTML = await utils.loadTemplate('admin-users');

        const queryInput = document.getElementById('admin-search-query');
        const deptSelect = document.getElementById('admin-filter-dept');
        if (queryInput && params.search) queryInput.value = params.search;
        if (deptSelect && params.department) deptSelect.value = uiMappers.departmentToTemplate(params.department);

        const listBody = document.getElementById('admin-users-list');
        if (!users.length) {
            listBody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:2rem;">No users found.</td></tr>';
            return;
        }

        listBody.innerHTML = users.map((user) => `
            <tr>
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>${user.department}</td>
                <td>${utils.formatPhoneNumber(user.phone_number)}</td>
                <td>
                    <select onchange="pages.handleRoleUpdate(${user.id}, this.value)" ${user.id === state.user.id ? 'disabled' : ''}>
                        <option value="PENDING" ${user.role === 'PENDING' ? 'selected' : ''}>Pending</option>
                        <option value="STAFF" ${user.role === 'STAFF' ? 'selected' : ''}>Staff</option>
                        <option value="ADMIN" ${user.role === 'ADMIN' ? 'selected' : ''}>Admin</option>
                    </select>
                </td>
                <td>${user.is_active ? '<span class="status-badge success">Active</span>' : '<span class="status-badge error">Inactive</span>'}</td>
            </tr>
        `).join('');
    },

    handleAdminSearch() {
        const search = document.getElementById('admin-search-query').value;
        const department = uiMappers.departmentToApi(document.getElementById('admin-filter-dept').value);
        const params = new URLSearchParams();
        if (search) params.set('search', search);
        if (department) params.set('department', department);
        navigate('/admin/users' + (params.toString() ? `?${params.toString()}` : ''));
    },

    resetAdminSearch() {
        navigate('/admin/users');
    },

    async handleRoleUpdate(userId, newRole) {
        await apis.adminUpdateUserRole({ user_id: userId, new_role: newRole });
        utils.showAlert('Role updated.', 'success');
        this.handleAdminSearch();
    },

    async handleUpdateMe(event) {
        event.preventDefault();
        const data = {
            department: uiMappers.departmentToApi(document.getElementById('update-me-department').value),
            phone_number: document.getElementById('update-me-phone').value.replace(/[^\d]/g, ''),
        };

        await apis.updateMe(data);
        utils.showAlert('Profile updated.', 'success');
        await checkAuth();
        this.renderMyPage();
    },

    async handleUpdatePassword(event) {
        event.preventDefault();
        const data = {
            current_password: document.getElementById('old-password').value,
            new_password: document.getElementById('new-password').value,
        };

        await apis.updatePassword(data);
        utils.showAlert('Password updated.', 'success');
        event.target.reset();
    },

    async handleDeleteMe() {
        if (!confirm('Delete your account?')) return;
        await apis.deleteMe();
        utils.showAlert('Account deleted.', 'success');
        logout();
    },

    async handleLogin(event) {
        event.preventDefault();
        await login(
            document.getElementById('email').value,
            document.getElementById('password').value,
        );
    },

    async handleSignup(event) {
        event.preventDefault();
        const userData = {
            email: document.getElementById('signup-email').value,
            name: document.getElementById('signup-name').value,
            department: uiMappers.departmentToApi(document.getElementById('signup-department').value),
            gender: uiMappers.genderToApi(document.getElementById('signup-gender').value),
            phone_number: document.getElementById('signup-phone').value.replace(/[^\d]/g, ''),
            password: document.getElementById('signup-password').value,
        };

        await apis.signup(userData);
        utils.showAlert('Signup completed. Please login.', 'success');
        navigate('/login');
    },

    async handlePatientCreate(event) {
        event.preventDefault();
        const patientData = {
            name: document.getElementById('name').value,
            age: parseInt(document.getElementById('age').value, 10),
            gender: uiMappers.genderToApi(document.getElementById('gender').value),
            phone: document.getElementById('phone_number').value.replace(/[^\d]/g, ''),
        };

        await apis.createPatient(patientData);
        utils.showAlert('Patient created.', 'success');
        navigate('/patients');
    },

    handleSearch() {
        const search = document.getElementById('search-name').value;
        const gender = uiMappers.genderToApi(document.getElementById('filter-gender').value);
        const minAge = document.getElementById('filter-min-age').value;
        const maxAge = document.getElementById('filter-max-age').value;
        const params = new URLSearchParams();
        if (search) params.set('search', search);
        if (gender) params.set('gender', gender);
        if (minAge) params.set('min_age', minAge);
        if (maxAge) params.set('max_age', maxAge);
        navigate('/patients' + (params.toString() ? `?${params.toString()}` : ''));
    },

    resetSearch() {
        navigate('/patients');
    },

    async handleRecordCreate(event, patientId) {
        event.preventDefault();
        const imageFile = document.getElementById('xray_image').files[0];
        if (!imageFile) {
            utils.showAlert('Please select an X-ray image.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('chart_number', document.getElementById('chart_number').value);
        formData.append('symptoms', document.getElementById('symptoms').value);
        formData.append('shooting_datetime', new Date().toISOString());
        formData.append('xray_image', imageFile);

        await apis.createMedicalRecord(patientId, formData);
        utils.showAlert('Medical record created.', 'success');
        navigate(`/patients/${patientId}`);
    },

    openUpdateModal() {
        document.getElementById('update-modal').classList.add('show');
    },

    closeUpdateModal() {
        document.getElementById('update-modal').classList.remove('show');
    },

    async handlePatientUpdate(event) {
        event.preventDefault();
        const patientId = state.currentPatientId;
        const updateData = {
            name: document.getElementById('update-name').value,
            phone: document.getElementById('update-phone').value.replace(/[^\d]/g, ''),
        };

        await apis.updatePatient(patientId, updateData);
        utils.showAlert('Patient updated.', 'success');
        this.closeUpdateModal();
        this.renderPatientDetail(patientId);
    },

    confirmDeletePatient() {
        document.getElementById('delete-modal').classList.add('show');
    },

    closeDeleteModal() {
        document.getElementById('delete-modal').classList.remove('show');
    },

    async handlePatientDelete() {
        const patientId = state.currentPatientId;
        await apis.deletePatient(patientId);
        utils.showAlert('Patient deleted.', 'success');
        this.closeDeleteModal();
        navigate('/patients');
    },

    async handlePredict(patientId, recordId) {
        await apis.predictPneumonia(patientId, recordId);
        utils.showAlert('AI prediction completed.', 'success');
        navigate(`/patients/${patientId}/medical-records/${recordId}`, false);
    },
};
