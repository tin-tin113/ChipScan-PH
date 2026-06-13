// State Management
let currentUser = null;
let activeTab = 'panel-scan';
let cameraStream = null;
let useLiveCamera = false;
let cropperInstance = null;
let hasHardwareZoom = false;

// DOM Selectors
const DOM = {
    loginView: document.getElementById('login-view'),
    appView: document.getElementById('app-view'),
    credentialsForm: document.getElementById('credentials-login-form'),
    googleLoginBtn: document.getElementById('google-login-trigger'),
    loginError: document.getElementById('login-error-msg'),
    
    displayUsername: document.getElementById('display-username'),
    displayRoleBadge: document.getElementById('display-role-badge'),
    themeToggle: document.getElementById('theme-toggle'),
    logoutBtn: document.getElementById('logout-btn'),
    
    // Notifications
    bellBtn: document.getElementById('notification-bell'),
    notifBadge: document.getElementById('notif-badge'),
    notifDropdown: document.getElementById('notifications-dropdown'),
    notifList: document.getElementById('notifications-list'),
    notifClear: document.getElementById('notif-clear'),
    
    // Nav Tabs
    navTabs: document.querySelectorAll('.nav-tab'),
    viewPanels: document.querySelectorAll('.view-panel'),
    navTabApprovals: document.getElementById('nav-tab-approvals'),
    navBadgeApprovals: document.getElementById('nav-badge-approvals'),
    
    // Scanner
    cameraVideo: document.getElementById('camera-video'),
    cameraCanvas: document.getElementById('camera-canvas'),
    btnCapture: document.getElementById('btn-capture'),
    btnGallery: document.getElementById('btn-gallery'),
    galleryInput: document.getElementById('gallery-input'),
    scannerLoader: document.getElementById('scanner-loader'),
    scanResultCard: document.getElementById('scan-result-card'),
    cameraZoomSlider: document.getElementById('camera-zoom-slider'),
    zoomValueLabel: document.getElementById('zoom-value-label'),
    zoomControlContainer: document.getElementById('zoom-control-container'),
    bgaGuideSelect: document.getElementById('bga-guide-select'),
    viewfinderReticle: document.getElementById('viewfinder-reticle'),
    manualChipSearch: document.getElementById('manual-chip-search'),
    btnClearSearch: document.getElementById('btn-clear-search'),
    searchSuggestionsBox: document.getElementById('search-suggestions-box'),
    
    // Scan Details
    resultMakerCode: document.getElementById('result-maker-code'),
    resultStatusBadge: document.getElementById('result-status-badge'),
    valMaker: document.getElementById('val-maker'),
    valCode: document.getElementById('val-code'),
    valSize: document.getElementById('val-size'),
    valType: document.getElementById('val-type'),
    valGrade: document.getElementById('val-grade'),
    valScore: document.getElementById('val-score'),
    valPriceCoded: document.getElementById('val-price-coded'),
    valPriceNoncode: document.getElementById('val-price-noncode'),
    valNotes: document.getElementById('val-notes'),
    scanPreviewImg: document.getElementById('scan-preview-img'),
    requestApprovalSection: document.getElementById('request-approval-section'),
    btnRequestApproval: document.getElementById('btn-request-approval'),
    nearlyMatchedBox: document.getElementById('nearly-matched-box'),
    suggestedCode: document.getElementById('suggested-code'),
    suggestedMeta: document.getElementById('suggested-meta'),
    btnAcceptSuggestion: document.getElementById('btn-accept-suggestion'),
    
    // History
    historyContainer: document.getElementById('history-items-container'),
    
    // Approvals
    approvalsContainer: document.getElementById('approvals-items-container'),
    
    // Admin Stats
    statTotalScans: document.getElementById('stat-total-scans'),
    statAccuracy: document.getElementById('stat-accuracy'),
    statPendingApprovals: document.getElementById('stat-pending-approvals'),
    statTotalChips: document.getElementById('stat-total-chips'),
    
    // Admin Pricing Form
    pricingForm: document.getElementById('pricing-matrix-form'),
    matrixGradesBody: document.getElementById('matrix-grades-body'),
    matrixSizesBody: document.getElementById('matrix-sizes-body'),
    pricingSuccess: document.getElementById('pricing-success-banner'),
    
    // Admin Chip Catalog
    catalogSearch: document.getElementById('chip-catalog-search'),
    catalogBody: document.getElementById('catalog-chips-body'),
    btnOpenCreateChip: document.getElementById('btn-open-create-chip'),
    
    // Modals
    confirmModal: document.getElementById('confirm-modal'),
    confirmTitle: document.getElementById('confirm-title'),
    confirmMessage: document.getElementById('confirm-message'),
    btnConfirmCancel: document.getElementById('btn-confirm-cancel'),
    btnConfirmOk: document.getElementById('btn-confirm-ok'),
    
    googleAgeGateModal: document.getElementById('google-age-gate-modal'),
    googleBirthYearInput: document.getElementById('google-birth-year'),
    googleAgeGateSubmit: document.getElementById('btn-google-auth-submit'),
    googleAgeGateError: document.getElementById('age-gate-error'),
    btnCloseAgeGate: document.getElementById('btn-close-age-gate'),
    
    submitUnknownModal: document.getElementById('submit-unknown-modal'),
    unknownCodeInput: document.getElementById('unknown-code'),
    unknownMakerInput: document.getElementById('unknown-maker'),
    unknownSizeInput: document.getElementById('unknown-size'),
    unknownTypeInput: document.getElementById('unknown-type'),
    unknownClassificationInput: document.getElementById('unknown-classification'),
    unknownImageUrlHidden: document.getElementById('unknown-image-url'),
    unknownChipForm: document.getElementById('unknown-chip-form'),
    btnCloseUnknown: document.getElementById('btn-close-unknown-modal'),
    
    adminResolveModal: document.getElementById('admin-resolve-modal'),
    adminReqId: document.getElementById('admin-req-id'),
    adminReqCode: document.getElementById('admin-req-code'),
    adminReqTech: document.getElementById('admin-req-tech'),
    adminReqDetails: document.getElementById('admin-req-details'),
    adminReqImage: document.getElementById('admin-req-image'),
    resolveGradeInput: document.getElementById('resolve-grade'),
    resolveMakerInput: document.getElementById('resolve-maker'),
    btnResolveReject: document.getElementById('btn-resolve-reject'),
    adminResolveForm: document.getElementById('admin-resolve-form'),
    btnCloseResolve: document.getElementById('btn-close-resolve-modal'),
    
    adminCreateChipModal: document.getElementById('admin-create-chip-modal'),
    adminCreateChipForm: document.getElementById('admin-create-chip-form'),
    createCodeInput: document.getElementById('create-code'),
    createMakerInput: document.getElementById('create-maker'),
    createGradeInput: document.getElementById('create-grade'),
    createSizeInput: document.getElementById('create-size'),
    createTypeInput: document.getElementById('create-type'),
    createAliasInput: document.getElementById('create-alias'),
    createAlternateInput: document.getElementById('create-alternate'),
    createNoteInput: document.getElementById('create-note'),
    createImageInput: document.getElementById('create-image'),
    createChipError: document.getElementById('create-chip-error'),
    btnCloseCreateChipModal: document.getElementById('btn-close-create-chip-modal'),
    
    // Cropper Selectors
    imageCropModal: document.getElementById('image-crop-modal'),
    cropperTargetImage: document.getElementById('cropper-target-image'),
    btnCropRotateLeft: document.getElementById('btn-crop-rotate-left'),
    btnCropRotateRight: document.getElementById('btn-crop-rotate-right'),
    btnCropReset: document.getElementById('btn-crop-reset'),
    btnCropCancel: document.getElementById('btn-crop-cancel'),
    btnCropSubmit: document.getElementById('btn-crop-submit'),
    btnCloseCropModal: document.getElementById('btn-close-crop-modal')
};

// ==================== CUSTOM CONFIRMATION DIALOG ====================
function showCustomConfirm(title, message) {
    return new Promise((resolve) => {
        DOM.confirmTitle.innerText = title;
        DOM.confirmMessage.innerText = message;
        DOM.confirmModal.classList.remove('hidden');
        
        const cleanup = (value) => {
            DOM.confirmModal.classList.add('hidden');
            DOM.btnConfirmCancel.removeEventListener('click', handleCancel);
            DOM.btnConfirmOk.removeEventListener('click', handleOk);
            resolve(value);
        };
        
        const handleCancel = () => cleanup(false);
        const handleOk = () => cleanup(true);
        
        DOM.btnConfirmCancel.addEventListener('click', handleCancel);
        DOM.btnConfirmOk.addEventListener('click', handleOk);
    });
}

// ==================== AUTHENTICATION ====================

// Set CSRF token helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Check session on load
window.addEventListener('DOMContentLoaded', () => {
    // If browser supports theme, restore it
    const storedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', storedTheme);
});

DOM.credentialsForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ username, password })
        });
        const result = await response.json();
        
        if (response.ok && result.success) {
            handleLoginSuccess(result.user);
        } else {
            DOM.loginError.classList.remove('hidden');
            DOM.loginError.querySelector('span').innerText = result.error || 'Authentication failed';
        }
    } catch (err) {
        DOM.loginError.classList.remove('hidden');
        DOM.loginError.querySelector('span').innerText = 'Network error occurred';
    }
});

// Google Mock Auth age gate flow
DOM.googleLoginBtn.addEventListener('click', () => {
    DOM.googleAgeGateModal.classList.remove('hidden');
    DOM.googleBirthYearInput.value = '';
    DOM.googleAgeGateError.classList.add('hidden');
});

DOM.btnCloseAgeGate.addEventListener('click', () => {
    DOM.googleAgeGateModal.classList.add('hidden');
});

DOM.googleAgeGateSubmit.addEventListener('click', async () => {
    const birthYear = parseInt(DOM.googleBirthYearInput.value);
    if (!birthYear) {
        DOM.googleAgeGateError.classList.remove('hidden');
        DOM.googleAgeGateError.querySelector('span').innerText = 'Please enter a valid birth year';
        return;
    }
    
    const currentYear = new Date().getFullYear();
    const age = currentYear - birthYear;
    
    if (age < 18) {
        DOM.googleAgeGateError.classList.remove('hidden');
        DOM.googleAgeGateError.querySelector('span').innerText = 'Age restriction: you must be 18+ to log in.';
        return;
    }
    
    // Proceed to mock authenticate
    try {
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ provider: 'google', birth_year: birthYear })
        });
        const result = await response.json();
        
        if (response.ok && result.success) {
            DOM.googleAgeGateModal.classList.add('hidden');
            handleLoginSuccess(result.user);
        } else {
            DOM.googleAgeGateError.classList.remove('hidden');
            DOM.googleAgeGateError.querySelector('span').innerText = result.error || 'Google Login failed';
        }
    } catch (err) {
        DOM.googleAgeGateError.classList.remove('hidden');
        DOM.googleAgeGateError.querySelector('span').innerText = 'Network connection failed';
    }
});

function handleLoginSuccess(user) {
    currentUser = user;
    DOM.loginView.classList.add('hidden');
    DOM.appView.classList.remove('hidden');
    
    DOM.displayUsername.innerText = user.username;

    if (user.role === 'admin') {
        DOM.displayRoleBadge.innerText = 'ADMINISTRATOR';
        DOM.displayRoleBadge.className = 'role-badge badge-admin';
        document.querySelectorAll('.admin-only').forEach(el => el.classList.remove('hidden'));
        // Admin-specific approvals panel labels
        const approvalsTitle = document.querySelector('#panel-approvals .view-title-bar h2');
        const approvalsSubtitle = document.getElementById('approvals-subtitle');
        if (approvalsTitle) approvalsTitle.innerText = 'Approvals Queue';
        if (approvalsSubtitle) approvalsSubtitle.innerText = 'Pending chip code registrations from technicians';
    } else {
        DOM.displayRoleBadge.innerText = 'TECHNICIAN';
        DOM.displayRoleBadge.className = 'role-badge badge-tech';
        document.querySelectorAll('.admin-only').forEach(el => el.classList.add('hidden'));
        // Tech-specific approvals panel labels
        const approvalsTitle = document.querySelector('#panel-approvals .view-title-bar h2');
        const approvalsSubtitle = document.getElementById('approvals-subtitle');
        if (approvalsTitle) approvalsTitle.innerText = 'My Requests';
        if (approvalsSubtitle) approvalsSubtitle.innerText = 'Track your submitted chip code requests';

        // ── SECURITY: Remove the admin panel from the DOM entirely for non-admin users.
        const adminPanel = document.getElementById('panel-admin');
        if (adminPanel) adminPanel.remove();
    }
    
    // Start Camera & Load Initial Data
    initCamera();
    loadDashboardData();
    refreshChipsCache();
    
    // Set up polling for approvals and notifications
    startPolling();
}

async function refreshChipsCache() {
    try {
        const response = await fetch('/api/chips/');
        const data = await response.json();
        if (data.chips) {
            catalogChips = data.chips;
        }
    } catch (err) {
        console.error("Failed to refresh chip cache: ", err);
    }
}

DOM.logoutBtn.addEventListener('click', async () => {
    if (await showCustomConfirm("Logout", "Are you sure you want to log out of ChipScan PH?")) {
        stopCamera();
        await fetch('/api/logout/', { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } });
        currentUser = null;
        window.location.reload();
    }
});

// ==================== THEME TOGGLER ====================
DOM.themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

// ==================== NAVIGATION TABS ====================
DOM.navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const target = tab.getAttribute('data-target');

        // ── SECURITY: Hard-block non-admin users from activating the admin panel
        // even if the nav button somehow became visible or was clicked programmatically.
        if (target === 'panel-admin' && (!currentUser || currentUser.role !== 'admin')) {
            return;
        }

        // ── SAFETY: If the target panel was removed from the DOM (tech user), abort.
        if (!document.getElementById(target)) {
            return;
        }

        DOM.navTabs.forEach(t => t.classList.remove('active'));
        DOM.viewPanels.forEach(p => p.classList.remove('active'));
        
        tab.classList.add('active');
        document.getElementById(target).classList.add('active');
        activeTab = target;
        
        // Handle Tab Specific Events
        if (target === 'panel-scan') {
            initCamera();
        } else {
            stopCamera();
        }
        
        if (target === 'panel-history') {
            loadScanHistory();
        } else if (target === 'panel-approvals') {
            loadApprovalsQueue();
        } else if (target === 'panel-admin') {
            loadAdminPanel();
        }
    });
});

// ==================== WEBCAM VIEW FINDER ====================
async function initCamera() {
    if (cameraStream) return;
    
    try {
        const constraints = {
            video: {
                facingMode: 'environment', // Use back camera if mobile
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        };
        cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
        DOM.cameraVideo.srcObject = cameraStream;
        DOM.cameraVideo.classList.remove('hidden');
        
        let mockImg = document.getElementById('camera-mock-img');
        if (mockImg) {
            mockImg.classList.add('hidden');
        }
        
        useLiveCamera = true;

        // Initialize with default digital zoom values first
        DOM.zoomControlContainer.style.display = 'flex';
        DOM.cameraZoomSlider.min = 1;
        DOM.cameraZoomSlider.max = 4;
        DOM.cameraZoomSlider.step = 0.1;
        DOM.cameraZoomSlider.value = 1.0;
        DOM.zoomValueLabel.innerText = '1.0x';
        hasHardwareZoom = false;

        // Check zoom capabilities on the track for hardware-based zoom
        const track = cameraStream.getVideoTracks()[0];
        if (track) {
            try {
                // Wait briefly for capabilities to populate
                setTimeout(() => {
                    if (!cameraStream) return;
                    const capabilities = track.getCapabilities();
                    if (capabilities.zoom) {
                        hasHardwareZoom = true;
                        DOM.cameraZoomSlider.min = capabilities.zoom.min || 1;
                        DOM.cameraZoomSlider.max = capabilities.zoom.max || 5;
                        DOM.cameraZoomSlider.step = capabilities.zoom.step || 0.1;
                        DOM.cameraZoomSlider.value = track.getSettings().zoom || 1;
                        DOM.zoomValueLabel.innerText = `${parseFloat(DOM.cameraZoomSlider.value).toFixed(1)}x`;
                    }
                }, 400);
            } catch (e) {
                console.log("Hardware zoom check failed, falling back to digital zoom:", e);
            }
        }
    } catch (err) {
        // Fallback: If webcam fails or is rejected, stream from mock web cam stream route
        console.warn("Camera init failed, falling back to mock stream endpoint: ", err);
        DOM.cameraVideo.classList.add('hidden');
        
        // Show zoom slider for simulated digital scale zoom in mock camera mode
        DOM.zoomControlContainer.style.display = 'flex';
        DOM.cameraZoomSlider.min = 1;
        DOM.cameraZoomSlider.max = 4;
        DOM.cameraZoomSlider.step = 0.1;
        DOM.cameraZoomSlider.value = 1.0;
        DOM.zoomValueLabel.innerText = '1.0x';
        hasHardwareZoom = false;
        
        // Create an image element to load stream instead
        let mockImg = document.getElementById('camera-mock-img');
        if (!mockImg) {
            mockImg = document.createElement('img');
            mockImg.id = 'camera-mock-img';
            mockImg.className = 'camera-feed';
            DOM.cameraVideo.parentNode.insertBefore(mockImg, DOM.cameraVideo);
        }
        mockImg.src = '/camera/stream/';
        mockImg.classList.remove('hidden');
        useLiveCamera = false;
    }
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    DOM.cameraVideo.srcObject = null;
    DOM.zoomControlContainer.style.display = 'none';
    
    // Reset any digital scale transformations
    DOM.cameraVideo.style.transform = 'none';
    const mockImg = document.getElementById('camera-mock-img');
    if (mockImg) {
        mockImg.style.transform = 'none';
    }
}

// CAPTURE FRAME ACTION
DOM.btnCapture.addEventListener('click', async () => {
    let imageBlob = null;
    
    if (useLiveCamera) {
        // Draw frame from live video tag onto hidden canvas
        const video = DOM.cameraVideo;
        const canvas = DOM.cameraCanvas;
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        
        const ctx = canvas.getContext('2d');
        const zoomVal = parseFloat(DOM.cameraZoomSlider.value) || 1.0;
        
        if (zoomVal > 1.0 && !hasHardwareZoom) {
            // Apply digital zoom by cropping a sub-rectangle centered in the source video
            const sw = canvas.width / zoomVal;
            const sh = canvas.height / zoomVal;
            const sx = (canvas.width - sw) / 2;
            const sy = (canvas.height - sh) / 2;
            ctx.drawImage(video, sx, sy, sw, sh, 0, 0, canvas.width, canvas.height);
        } else {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        }
        
        // Convert to blob
        await new Promise((resolve) => {
            canvas.toBlob((blob) => {
                imageBlob = blob;
                resolve();
            }, 'image/jpeg', 0.95);
        });
    } else {
        // Mock capture mode: Since we are using simulated stream, we request a sample frame
        // We will generate a mock image with text and send it to trigger OCR pipeline
        const canvas = DOM.cameraCanvas;
        canvas.width = 800;
        canvas.height = 600;
        const ctx = canvas.getContext('2d');
        const zoomVal = parseFloat(DOM.cameraZoomSlider.value) || 1.0;
        
        // Dark gray package background
        ctx.fillStyle = '#22252a';
        ctx.fillRect(0, 0, 800, 600);
        
        ctx.save();
        if (zoomVal > 1.0) {
            // Translate to center, scale, translate back to draw centered digital zoom
            ctx.translate(400, 300);
            ctx.scale(zoomVal, zoomVal);
            ctx.translate(-400, -300);
        }
        
        // Draw chip outlines
        ctx.strokeStyle = '#3e4249';
        ctx.lineWidth = 4;
        ctx.strokeRect(100, 100, 600, 400);
        
        // Draw pins
        ctx.fillStyle = '#cfd3db';
        for (let x = 120; x < 680; x += 30) {
            ctx.fillRect(x, 85, 12, 15);
            ctx.fillRect(x, 500, 12, 15);
        }
        
        // Laser markings text (SAMSUNG KLUEG8UHDB-C2D1)
        ctx.fillStyle = '#d8dbdf';
        ctx.font = 'bold 36px monospace';
        ctx.textAlign = 'center';
        
        // Generate random seeded mock chip index for varied capture tests
        const mockChips = [
            { text1: 'SAMSUNG', text2: 'KLUEG8UHDB', text3: 'C2D1' },
            { text1: 'SK hynix', text2: 'H9HQ15AECM', text3: 'BDAR-KEM' },
            { text1: 'TOSHIBA', text2: 'THGAF8T0T4', text3: '3BAIR' },
            { text1: 'MICRON', text2: 'MTFC128GAJ', text3: 'AECE-5M' },
            { text1: 'UNBRANDED', text2: 'MODEL-XYZ999', text3: '2026' }
        ];
        const choice = mockChips[Math.floor(Math.random() * mockChips.length)];
        
        ctx.fillText(choice.text1, 400, 240);
        ctx.fillText(choice.text2, 400, 310);
        ctx.fillText(choice.text3, 400, 380);
        
        ctx.restore();
        
        await new Promise((resolve) => {
            canvas.toBlob((blob) => {
                imageBlob = blob;
                resolve();
            }, 'image/jpeg');
        });
    }
    
    if (imageBlob) {
        const url = URL.createObjectURL(imageBlob);
        initCropperFlow(url);
    } else {
        alert("Failed to capture image frame.");
    }
});

// GALLERY UPLOAD ACTION
DOM.btnGallery.addEventListener('click', () => {
    DOM.galleryInput.click();
});

DOM.galleryInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const url = URL.createObjectURL(file);
        initCropperFlow(url);
    }
});

// Cropper Flow implementation
function initCropperFlow(imageSrc) {
    DOM.cropperTargetImage.src = imageSrc;
    DOM.imageCropModal.classList.remove('hidden');
    
    if (cropperInstance) {
        cropperInstance.destroy();
    }
    
    // Initialize Cropper
    cropperInstance = new Cropper(DOM.cropperTargetImage, {
        viewMode: 1,
        dragMode: 'move',
        autoCropArea: 0.8,
        restore: false,
        guides: true,
        center: true,
        highlight: false,
        cropBoxMovable: true,
        cropBoxResizable: true,
        toggleDragModeOnDblclick: false
    });
}

// Bind Crop Actions once when script loads
DOM.btnCropRotateLeft.addEventListener('click', () => {
    if (cropperInstance) cropperInstance.rotate(-90);
});
DOM.btnCropRotateRight.addEventListener('click', () => {
    if (cropperInstance) cropperInstance.rotate(90);
});
DOM.btnCropReset.addEventListener('click', () => {
    if (cropperInstance) cropperInstance.reset();
});

const closeCropFlow = () => {
    DOM.imageCropModal.classList.add('hidden');
    if (cropperInstance) {
        cropperInstance.destroy();
        cropperInstance = null;
    }
};

DOM.btnCropCancel.addEventListener('click', closeCropFlow);
DOM.btnCloseCropModal.addEventListener('click', closeCropFlow);

DOM.btnCropSubmit.addEventListener('click', () => {
    if (cropperInstance) {
        const canvas = cropperInstance.getCroppedCanvas({
            maxWidth: 1600,
            maxHeight: 1600,
            imageSmoothingQuality: 'high'
        });
        canvas.toBlob((blob) => {
            closeCropFlow();
            DOM.scanResultCard.classList.add('hidden');
            DOM.scannerLoader.classList.remove('hidden');
            setScannerBusyState(true);
            uploadScanImage(blob);
        }, 'image/jpeg', 0.95);
    }
});

function setScannerBusyState(isBusy) {
    if (isBusy) {
        DOM.btnCapture.disabled = true;
        DOM.btnGallery.disabled = true;
        DOM.galleryInput.disabled = true;
        DOM.btnCapture.style.opacity = '0.5';
        DOM.btnGallery.style.opacity = '0.5';
        DOM.btnCapture.style.pointerEvents = 'none';
        DOM.btnGallery.style.pointerEvents = 'none';
    } else {
        DOM.btnCapture.disabled = false;
        DOM.btnGallery.disabled = false;
        DOM.galleryInput.disabled = false;
        DOM.btnCapture.style.opacity = '1';
        DOM.btnGallery.style.opacity = '1';
        DOM.btnCapture.style.pointerEvents = 'auto';
        DOM.btnGallery.style.pointerEvents = 'auto';
    }
}

async function uploadScanImage(imageFileOrBlob) {
    const formData = new FormData();
    formData.append('image', imageFileOrBlob, 'scan_capture.jpg');
    
    try {
        const response = await fetch('/api/scan/image/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });
        const result = await response.json();
        DOM.scannerLoader.classList.add('hidden');
        setScannerBusyState(false);
        
        if (response.ok && result.success) {
            displayScanResult(result.scan);
        } else {
            alert(result.error || "Scan request failed.");
        }
    } catch (err) {
        DOM.scannerLoader.classList.add('hidden');
        setScannerBusyState(false);
        alert("Network error: failed to submit scan image.");
    }
    DOM.galleryInput.value = '';
}

function displayScanResult(scan) {
    DOM.scanResultCard.classList.remove('hidden');
    
    DOM.resultMakerCode.innerText = `${scan.maker.toUpperCase()} ${scan.code}`;
    if (scan.image_url) {
        DOM.scanPreviewImg.src = scan.image_url;
        DOM.scanPreviewImg.parentNode.classList.remove('hidden');
    } else {
        DOM.scanPreviewImg.parentNode.classList.add('hidden');
    }
    
    DOM.valMaker.innerText = scan.maker;
    DOM.valCode.innerText = scan.code;
    DOM.valSize.innerText = scan.size;
    DOM.valType.innerText = scan.type;
    DOM.valGrade.innerText = scan.grade;
    DOM.valScore.innerText = scan.match_score;
    DOM.valPriceCoded.innerText = `₱${scan.price_coded.toLocaleString()}`;
    DOM.valPriceNoncode.innerText = `₱${scan.price_noncode.toLocaleString()}`;
    
    if (scan.scan_status === 'MATCHED') {
        DOM.resultStatusBadge.innerText = 'MATCHED';
        DOM.resultStatusBadge.className = 'match-badge badge-matched';
        DOM.requestApprovalSection.classList.add('hidden');
        DOM.valGrade.innerText = scan.grade;
    } else {
        DOM.resultStatusBadge.innerText = 'UNRECOGNIZED CHIP';
        DOM.resultStatusBadge.className = 'match-badge badge-unknown';
        DOM.valGrade.innerText = 'N/A';
        
        // Show submission form options
        DOM.requestApprovalSection.classList.remove('hidden');
        DOM.unknownImageUrlHidden.value = scan.image_url;

        // Handle text detection label
        if (!scan.ocr_text || scan.ocr_text.trim() === '') {
            DOM.requestApprovalSection.querySelector('p').innerHTML = `<i class="fa-solid fa-circle-question"></i> No text markings detected. Scanner could not recognize this chip code.`;
            DOM.unknownCodeInput.value = 'UNRECOGNIZED';
        } else {
            DOM.requestApprovalSection.querySelector('p').innerHTML = `<i class="fa-solid fa-circle-question"></i> Scanner could not recognize this chip code.`;
            DOM.unknownCodeInput.value = scan.ocr_text;
        }

        // Toggle action button description dynamically based on role
        if (currentUser.role === 'admin') {
            DOM.btnRequestApproval.innerHTML = `<i class="fa-solid fa-plus"></i> Add Directly to Catalog`;
        } else {
            DOM.btnRequestApproval.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Submit to Admin for Approval`;
        }

        // Suggested match handling
        if (scan.nearly_matched) {
            DOM.suggestedCode.innerText = scan.nearly_matched.code;
            DOM.suggestedMeta.innerText = `${scan.nearly_matched.maker} | ${scan.nearly_matched.size} | ${scan.nearly_matched.type} | Grade ${scan.nearly_matched.grade} (${Math.round(scan.nearly_matched.score * 100)}% Match)`;
            DOM.nearlyMatchedBox.classList.remove('hidden');
            DOM.btnAcceptSuggestion.onclick = () => {
                if (currentUser.role === 'admin') {
                    DOM.adminCreateChipModal.classList.remove('hidden');
                    DOM.adminCreateChipForm.reset();
                    DOM.createChipError.classList.add('hidden');
                    DOM.createCodeInput.value = scan.nearly_matched.code;
                    DOM.createMakerInput.value = scan.nearly_matched.maker;
                    DOM.createSizeInput.value = scan.nearly_matched.size;
                    DOM.createTypeInput.value = scan.nearly_matched.type;
                    DOM.createNoteInput.value = scan.nearly_matched.note || '';
                } else {
                    DOM.unknownMakerInput.value = scan.nearly_matched.maker;
                    DOM.unknownSizeInput.value = scan.nearly_matched.size;
                    DOM.unknownTypeInput.value = scan.nearly_matched.type;
                    DOM.unknownCodeInput.value = scan.nearly_matched.code;
                    DOM.submitUnknownModal.classList.remove('hidden');
                }
            };
        } else {
            DOM.nearlyMatchedBox.classList.add('hidden');
            DOM.btnAcceptSuggestion.onclick = null;
        }
    }
    
    // Auto scroll result into view
    DOM.scanResultCard.scrollIntoView({ behavior: 'smooth' });
}

// Technician submit or admin add unknown chip
DOM.btnRequestApproval.addEventListener('click', () => {
    if (currentUser.role === 'admin') {
        DOM.adminCreateChipModal.classList.remove('hidden');
        DOM.adminCreateChipForm.reset();
        DOM.createChipError.classList.add('hidden');
        
        const codeVal = DOM.unknownCodeInput.value !== 'UNRECOGNIZED' ? DOM.unknownCodeInput.value : '';
        DOM.createCodeInput.value = codeVal;
        
        DOM.createMakerInput.value = DOM.unknownMakerInput.value || '';
        DOM.createSizeInput.value = DOM.unknownSizeInput.value || '128GB';
        DOM.createTypeInput.value = DOM.unknownTypeInput.value || 'UFS 2.1';
    } else {
        DOM.submitUnknownModal.classList.remove('hidden');
    }
});

DOM.btnCloseUnknown.addEventListener('click', () => {
    DOM.submitUnknownModal.classList.add('hidden');
});

DOM.unknownChipForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (await showCustomConfirm("Submit Request", "Are you sure you want to submit this chip code for administrator approval?")) {
        const formData = new FormData();
        formData.append('code', DOM.unknownCodeInput.value);
        formData.append('maker', DOM.unknownMakerInput.value || 'Unknown');
        formData.append('size', DOM.unknownSizeInput.value);
        formData.append('type', DOM.unknownTypeInput.value);
        formData.append('classification', DOM.unknownClassificationInput.value);
        formData.append('image_url', DOM.unknownImageUrlHidden.value);
        
        try {
            const response = await fetch('/api/approvals/submit/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });
            const result = await response.json();
            
            if (response.ok && result.success) {
                DOM.submitUnknownModal.classList.add('hidden');
                DOM.requestApprovalSection.classList.add('hidden');
                alert("Approval request submitted to administrators.");
                loadApprovalsQueue();
            } else {
                alert(result.error || "Submission failed.");
            }
        } catch (err) {
            alert("Network error: failed to submit request.");
        }
    }
});

// ==================== SCAN HISTORY ====================
async function loadScanHistory() {
    try {
        const response = await fetch('/api/scan/history/');
        const result = await response.json();
        
        if (response.ok && result.scans) {
            renderScanHistory(result.scans);
        }
    } catch (err) {
        console.error("Failed to load scan history: ", err);
    }
}

function renderScanHistory(scans) {
    if (scans.length === 0) {
        DOM.historyContainer.innerHTML = `
            <div class="empty-state">
                <i class="fa-regular fa-folder-open"></i>
                <p>No scans performed yet.</p>
            </div>`;
        return;
    }
    
    DOM.historyContainer.innerHTML = scans.map(s => {
        const isMatched = s.scan_status === 'MATCHED';
        const iconClass = isMatched ? 'icon-matched' : 'icon-unknown';
        const displayCode = isMatched ? s.code : 'UNRECOGNIZED CHIP';
        const details = isMatched ? `${s.maker} | ${s.size} | ${s.type}` : `OCR: "${s.code.substring(0,20)}"`;
        const tagText = isMatched ? `Grade ${s.grade}` : 'Non-Code';
        
        return `
            <div class="list-item-card glass">
                <div class="item-icon ${iconClass}">
                    <i class="fa-solid fa-microchip"></i>
                </div>
                <div class="item-info">
                    <h4>${displayCode}</h4>
                    <p class="item-meta">${details}</p>
                    <span class="status-badge ${isMatched ? 'status-approved' : 'status-pending'} mt-1 inline-block">${tagText}</span>
                </div>
                <div class="item-action-price">
                    <span class="item-price">₱${s.price_coded.toLocaleString()}</span>
                    <span class="item-time">${s.timestamp}</span>
                </div>
            </div>`;
    }).join('');
}

// ==================== APPROVALS QUEUE ====================
async function loadApprovalsQueue() {
    try {
        const response = await fetch('/api/approvals/');
        const result = await response.json();
        
        if (response.ok && result.approvals) {
            renderApprovalsQueue(result.approvals);
        }
    } catch (err) {
        console.error("Failed to load approvals queue: ", err);
    }
}

function renderApprovalsQueue(reqs) {
    const pendingCount = reqs.filter(r => r.status === 'pending').length;
    if (pendingCount > 0) {
        DOM.navBadgeApprovals.innerText = pendingCount;
        DOM.navBadgeApprovals.classList.remove('hidden');
    } else {
        DOM.navBadgeApprovals.classList.add('hidden');
    }

    const isAdmin = currentUser.role === 'admin';

    if (reqs.length === 0) {
        DOM.approvalsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-clipboard-check"></i>
                <p>${isAdmin ? 'No pending approval requests.' : 'You have not submitted any requests yet.'}</p>
            </div>`;
        return;
    }

    DOM.approvalsContainer.innerHTML = reqs.map(r => {
        const statusClass = `status-${r.status}`;
        const canResolve = isAdmin && r.status === 'pending';

        // Build status outcome line — meaningful for both roles
        let outcomeHtml = '';
        if (r.status === 'approved') {
            outcomeHtml = `<p class="req-outcome outcome-approved"><i class="fa-solid fa-circle-check"></i> Approved — added to catalog</p>`;
        } else if (r.status === 'rejected') {
            outcomeHtml = `<p class="req-outcome outcome-rejected"><i class="fa-solid fa-circle-xmark"></i> Rejected by administrator</p>`;
        } else {
            outcomeHtml = `<p class="req-outcome outcome-pending"><i class="fa-solid fa-hourglass-half"></i> Awaiting admin review</p>`;
        }

        // Admin sees who submitted; tech sees their own chip details prominently
        const bodyLine2 = isAdmin
            ? `<p class="item-meta">Submitted by: <strong>${r.technician}</strong> &nbsp;|&nbsp; Est: ${r.size} ${r.type}</p>`
            : `<p class="item-meta">Est: ${r.size} ${r.type} &nbsp;&bull;&nbsp; ${r.classification === 'noncode' ? 'Non-Code' : 'Coded'}</p>`;

        return `
            <div class="approval-req-card glass">
                <div class="req-header">
                    <span class="status-badge ${statusClass}">${r.status.toUpperCase()}</span>
                    <span class="item-time">${r.created_at}</span>
                </div>
                <div class="req-body">
                    <p><strong>Code:</strong> <span class="font-mono text-cyan">${r.code}</span></p>
                    ${bodyLine2}
                    ${outcomeHtml}
                </div>
                <div class="req-footer">
                    ${r.image_path ? `<a href="${r.image_path}" target="_blank" class="btn-text"><i class="fa-regular fa-image"></i> View Photo</a>` : '<span class="text-muted" style="font-size:0.75rem">No image</span>'}
                    ${canResolve ? `<button class="btn btn-primary btn-xs" onclick="openResolveModal(${r.id}, '${r.code}', '${r.technician}', '${r.size} ${r.type}', '${r.image_path}')"><i class="fa-solid fa-gavel"></i> Review</button>` : ''}
                </div>
            </div>`;
    }).join('');
}

// Global hook for resolve action button
window.openResolveModal = (id, code, tech, details, img) => {
    DOM.adminResolveModal.classList.remove('hidden');
    DOM.adminReqId.value = id;
    DOM.adminReqCode.innerText = code;
    DOM.adminReqTech.innerText = tech;
    DOM.adminReqDetails.innerText = details;
    DOM.adminReqImage.src = img || '';
    DOM.resolveMakerInput.value = '';
};

DOM.btnCloseResolve.addEventListener('click', () => {
    DOM.adminResolveModal.classList.add('hidden');
});

// Admin approves request
DOM.adminResolveForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = DOM.adminReqId.value;
    const grade = DOM.resolveGradeInput.value;
    const maker = DOM.resolveMakerInput.value;
    
    if (await showCustomConfirm("Approve & Seed", `Are you sure you want to approve this request and seed it into the catalog as Grade ${grade}?`)) {
        await submitResolveAction(id, 'approved', grade, maker);
    }
});

// Admin rejects request
DOM.btnResolveReject.addEventListener('click', async () => {
    const id = DOM.adminReqId.value;
    if (await showCustomConfirm("Reject Request", "Are you sure you want to reject this request?")) {
        await submitResolveAction(id, 'rejected');
    }
});

async function submitResolveAction(id, action, grade = 'A1', maker = 'Unknown') {
    try {
        const response = await fetch('/api/approvals/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ id, action, grade, maker })
        });
        
        if (response.ok) {
            DOM.adminResolveModal.classList.add('hidden');
            loadApprovalsQueue();
            loadDashboardData();
        } else {
            const err = await response.json();
            alert(err.error || "Failed to resolve request.");
        }
    } catch (err) {
        alert("Network error: failed to submit resolve decision.");
    }
}

// ==================== ADMIN CONFIGS ====================
function loadAdminPanel() {
    // ── SECURITY: Double-check role server-side before rendering any admin config.
    if (!currentUser || currentUser.role !== 'admin') {
        console.warn('[ChipScan] Unauthorized attempt to access admin panel blocked.');
        return;
    }
    loadPricingConfigurations();
    loadChipCatalog();
}

async function loadPricingConfigurations() {
    try {
        const response = await fetch('/api/prices/');
        const result = await response.json();
        
        if (response.ok && result.prices) {
            renderPricingMatrices(result.prices, result.size_prices);
        }
    } catch (err) {
        console.error("Failed to load prices: ", err);
    }
}

function renderPricingMatrices(prices, sizePrices) {
    // Organize by grades
    const grades = ['A1', 'A2', 'A3', 'A4', 'A5'];
    let gradesHTML = '';
    
    grades.forEach(g => {
        const adminPrice = prices.find(p => p.grade === g && p.role === 'admin') || { price_coded: 0, price_noncode: 0 };
        const techPrice = prices.find(p => p.grade === g && p.role === 'tech') || { price_coded: 0, price_noncode: 0 };
        
        gradesHTML += `
            <tr>
                <td class="font-mono"><strong>${g}</strong></td>
                <td><input type="number" name="grade_${g}_admin_coded" value="${adminPrice.price_coded}"></td>
                <td><input type="number" name="grade_${g}_admin_noncode" value="${adminPrice.price_noncode}"></td>
                <td><input type="number" name="grade_${g}_tech_coded" value="${techPrice.price_coded}"></td>
                <td><input type="number" name="grade_${g}_tech_noncode" value="${techPrice.price_noncode}"></td>
            </tr>`;
    });
    DOM.matrixGradesBody.innerHTML = gradesHTML;
    
    // Organize by sizes
    const sizes = ['16GB', '32GB', '64GB', '128GB', '256GB', '512GB', '1TB'];
    let sizesHTML = '';
    
    sizes.forEach(s => {
        const adminSize = sizePrices.find(sp => sp.size === s && sp.role === 'admin') || { price: 0 };
        const techSize = sizePrices.find(sp => sp.size === s && sp.role === 'tech') || { price: 0 };
        
        sizesHTML += `
            <tr>
                <td class="font-mono">${s}</td>
                <td><input type="number" name="size_${s}_admin_price" value="${adminSize.price}"></td>
                <td><input type="number" name="size_${s}_tech_price" value="${techSize.price}"></td>
            </tr>`;
    });
    DOM.matrixSizesBody.innerHTML = sizesHTML;
}

// Pricing Save Form
DOM.pricingForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (await showCustomConfirm("Save Buying Rates", "Are you sure you want to save the updated buying rates?")) {
        const grades = ['A1', 'A2', 'A3', 'A4', 'A5'];
        const prices = [];
        
        grades.forEach(g => {
            prices.push({
                grade: g,
                role: 'admin',
                price_coded: parseInt(DOM.pricingForm[`grade_${g}_admin_coded`].value) || 0,
                price_noncode: parseInt(DOM.pricingForm[`grade_${g}_admin_noncode`].value) || 0
            });
            prices.push({
                grade: g,
                role: 'tech',
                price_coded: parseInt(DOM.pricingForm[`grade_${g}_tech_coded`].value) || 0,
                price_noncode: parseInt(DOM.pricingForm[`grade_${g}_tech_noncode`].value) || 0
            });
        });
        
        const sizes = ['16GB', '32GB', '64GB', '128GB', '256GB', '512GB', '1TB'];
        const sizePrices = [];
        
        sizes.forEach(s => {
            sizePrices.push({
                size: s,
                role: 'admin',
                price: parseInt(DOM.pricingForm[`size_${s}_admin_price`].value) || 0
            });
            sizePrices.push({
                size: s,
                role: 'tech',
                price: parseInt(DOM.pricingForm[`size_${s}_tech_price`].value) || 0
            });
        });
        
        try {
            const response = await fetch('/api/prices/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ prices, size_prices: sizePrices })
            });
            
            if (response.ok) {
                DOM.pricingSuccess.classList.remove('hidden');
                setTimeout(() => { DOM.pricingSuccess.classList.add('hidden'); }, 4000);
            } else {
                alert("Failed to save price changes.");
            }
        } catch (err) {
            alert("Network error: failed to submit price changes.");
        }
    }
});

// Catalog List & Search
let catalogChips = [];

async function loadChipCatalog() {
    try {
        const response = await fetch('/api/chips/');
        const result = await response.json();
        
        if (response.ok && result.chips) {
            catalogChips = result.chips;
            renderChipCatalog(catalogChips);
        }
    } catch (err) {
        console.error("Failed to load catalog: ", err);
    }
}

function renderChipCatalog(chips) {
    if (chips.length === 0) {
        DOM.catalogBody.innerHTML = `<tr><td colspan="6" class="text-center">No chips in catalog</td></tr>`;
        return;
    }
    
    DOM.catalogBody.innerHTML = chips.map(c => `
        <tr>
            <td class="font-mono"><strong>${c.code}</strong></td>
            <td>${c.maker}</td>
            <td class="text-cyan font-mono">${c.grade}</td>
            <td>${c.size}</td>
            <td>${c.type}</td>
            <td>
                ${c.is_manual ? `<button class="btn btn-danger btn-xs" onclick="deleteCatalogChip('${c.code}')"><i class="fa-solid fa-trash-can"></i></button>` : '<span class="text-muted">System</span>'}
            </td>
        </tr>`).join('');
}

DOM.catalogSearch.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase();
    const filtered = catalogChips.filter(c => 
        c.code.toLowerCase().includes(q) || 
        c.maker.toLowerCase().includes(q) || 
        c.grade.toLowerCase().includes(q) ||
        c.size.toLowerCase().includes(q) ||
        c.type.toLowerCase().includes(q)
    );
    renderChipCatalog(filtered);
});

window.deleteCatalogChip = async (code) => {
    if (await showCustomConfirm("Delete Chip Definition", `Are you sure you want to delete chip "${code}" from the catalog?`)) {
        try {
            const response = await fetch(`/api/chips/${code}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            if (response.ok) {
                loadChipCatalog();
                loadDashboardData();
            } else {
                alert("Failed to delete custom chip definition.");
            }
        } catch (err) {
            alert("Network connection error.");
        }
    }
};

// Create manual chip catalog modal
DOM.btnOpenCreateChip.addEventListener('click', () => {
    DOM.adminCreateChipModal.classList.remove('hidden');
    DOM.adminCreateChipForm.reset();
    DOM.createChipError.classList.add('hidden');
});

DOM.btnCloseCreateChipModal.addEventListener('click', () => {
    DOM.adminCreateChipModal.classList.add('hidden');
});

DOM.adminCreateChipForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const code = DOM.createCodeInput.value;
    if (await showCustomConfirm("Add Chip to Catalog", `Are you sure you want to add the new chip "${code}" to the catalog?`)) {
        const formData = new FormData();
        formData.append('code', DOM.createCodeInput.value);
        formData.append('maker', DOM.createMakerInput.value);
        formData.append('grade', DOM.createGradeInput.value);
        formData.append('size', DOM.createSizeInput.value);
        formData.append('type', DOM.createTypeInput.value);
        formData.append('alias', DOM.createAliasInput.value);
        formData.append('alternate_codes', DOM.createAlternateInput.value);
        formData.append('note', DOM.createNoteInput.value);
        
        const imgFile = DOM.createImageInput.files[0];
        if (imgFile) {
            formData.append('reference_image', imgFile);
        }
        
        try {
            const response = await fetch('/api/chips/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });
            const result = await response.json();
            
            if (response.ok && result.success) {
                DOM.adminCreateChipModal.classList.add('hidden');
                loadChipCatalog();
                loadDashboardData();
            } else {
                DOM.createChipError.classList.remove('hidden');
                DOM.createChipError.querySelector('span').innerText = result.error || 'Failed to add chip.';
            }
        } catch (err) {
            DOM.createChipError.classList.remove('hidden');
            DOM.createChipError.querySelector('span').innerText = 'Network request error.';
        }
    }
});

// ==================== STATS & NOTIFICATIONS ====================
async function loadDashboardData() {
    if (!currentUser) return;
    
    // Load Stats (Admin only)
    if (currentUser.role === 'admin') {
        try {
            const response = await fetch('/api/stats/');
            const result = await response.json();
            if (response.ok && result.success) {
                DOM.statTotalScans.innerText = result.stats.total_scans;
                DOM.statAccuracy.innerText = `${result.stats.accuracy}%`;
                DOM.statPendingApprovals.innerText = result.stats.pending_approvals;
                DOM.statTotalChips.innerText = result.stats.total_inventory;
                
                // Set approvals indicator badge if pending approvals exist
                const pa = result.stats.pending_approvals;
                if (pa > 0) {
                    DOM.navBadgeApprovals.innerText = pa;
                    DOM.navBadgeApprovals.classList.remove('hidden');
                } else {
                    DOM.navBadgeApprovals.classList.add('hidden');
                }
            }
        } catch (err) {
            console.error("Error loading dashboard statistics: ", err);
        }
    }
    
    // Load Notifications
    loadNotificationsList();
}

async function loadNotificationsList() {
    try {
        const response = await fetch('/api/notifications/');
        const result = await response.json();
        
        if (response.ok && result.notifications) {
            renderNotifications(result.notifications);
        }
    } catch (err) {
        console.error("Failed to load notifications: ", err);
    }
}

function renderNotifications(notifs) {
    const unread = notifs.filter(n => !n.is_read).length;
    if (unread > 0) {
        DOM.notifBadge.classList.remove('hidden');
    } else {
        DOM.notifBadge.classList.add('hidden');
    }
    
    if (notifs.length === 0) {
        DOM.notifList.innerHTML = `<div class="notif-empty">No notifications</div>`;
        return;
    }
    
    DOM.notifList.innerHTML = notifs.map(n => `
        <div class="notif-item ${n.is_read ? 'read' : 'unread'}">
            <p>${n.message}</p>
            <span class="notif-time"><i class="fa-regular fa-clock"></i> ${n.created_at}</span>
        </div>`).join('');
}

// Notifications toggle drop down
DOM.bellBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    DOM.notifDropdown.classList.toggle('hidden');
    if (!DOM.notifDropdown.classList.contains('hidden')) {
        // Read notifications clears the red badge
        DOM.notifBadge.classList.add('hidden');
    }
});

// Clear dropdown when clicking elsewhere
document.addEventListener('click', () => {
    DOM.notifDropdown.classList.add('hidden');
});
DOM.notifDropdown.addEventListener('click', (e) => {
    e.stopPropagation();
});

DOM.notifClear.addEventListener('click', () => {
    DOM.notifList.innerHTML = `<div class="notif-empty">No notifications</div>`;
    DOM.notifBadge.classList.add('hidden');
});

// Polling intervals
let pollingTimer = null;

function startPolling() {
    stopPolling();
    // Poll notifications and statistics every 10 seconds
    pollingTimer = setInterval(() => {
        loadDashboardData();
        // If approvals tab is visible, refresh it
        if (activeTab === 'panel-approvals') {
            loadApprovalsQueue();
        }
    }, 10000);
}

function stopPolling() {
    if (pollingTimer) {
        clearInterval(pollingTimer);
        pollingTimer = null;
    }
}

// ==================== CALIBRATION CONTROLS (ZOOM & SHAPE OVERLAY) ====================
function applyZoom(zoomVal) {
    if (!cameraStream) return;
    const track = cameraStream.getVideoTracks()[0];
    if (track) {
        try {
            const capabilities = track.getCapabilities();
            if (capabilities.zoom) {
                const min = capabilities.zoom.min || 1;
                const max = capabilities.zoom.max || 5;
                const clamped = Math.max(min, Math.min(max, zoomVal));
                track.applyConstraints({
                    advanced: [{ zoom: clamped }]
                });
            }
        } catch (e) {
            console.warn("Failed to apply camera zoom: ", e);
        }
    }
}

// Bind listeners for zoom slider and shape guide select dropdown
if (DOM.cameraZoomSlider) {
    DOM.cameraZoomSlider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        DOM.zoomValueLabel.innerText = `${val.toFixed(1)}x`;
        applyZoom(val);
    });
}

if (DOM.bgaGuideSelect) {
    DOM.bgaGuideSelect.addEventListener('change', (e) => {
        const shape = e.target.value;
        if (DOM.viewfinderReticle) {
            // Remove previous guide classes
            DOM.viewfinderReticle.className = 'scanner-reticle';
            if (shape !== 'none') {
                DOM.viewfinderReticle.classList.add(`reticle-${shape}`);
            } else {
                DOM.viewfinderReticle.classList.add('reticle-none');
            }
        }
    });
}

// ==================== MANUAL CHIP SEARCH AUTOCOMPLETE ====================
if (DOM.manualChipSearch) {
    DOM.manualChipSearch.addEventListener('focus', async () => {
        if (!catalogChips || catalogChips.length === 0) {
            console.log("[Autocomplete] Input focused, cache empty. Refreshing...");
            await refreshChipsCache();
            console.log(`[Autocomplete] Cache loaded: ${catalogChips.length} chips.`);
        }
    });

    DOM.manualChipSearch.addEventListener('input', async (e) => {
        const q = e.target.value.trim().toLowerCase();
        if (!q) {
            DOM.searchSuggestionsBox.classList.add('hidden');
            DOM.btnClearSearch.classList.add('hidden');
            return;
        }
        
        DOM.btnClearSearch.classList.remove('hidden');
        
        if (!catalogChips || catalogChips.length === 0) {
            console.log("[Autocomplete] Typing, cache empty. Refreshing...");
            await refreshChipsCache();
            console.log(`[Autocomplete] Cache loaded: ${catalogChips.length} chips.`);
        }
        
        // Filter catalogChips safely
        const filtered = (catalogChips || []).filter(c => {
            const code = (c.code || '').toLowerCase();
            const maker = (c.maker || '').toLowerCase();
            const alias = (c.alias || '').toLowerCase();
            const alt = (c.alternate_codes || '').toLowerCase();
            return code.includes(q) || maker.includes(q) || alias.includes(q) || alt.includes(q);
        }).slice(0, 8); // limit to 8 suggestions
        
        console.log(`[Autocomplete] Query "${q}" matched ${filtered.length} chips out of ${catalogChips.length}`);
        
        if (filtered.length === 0) {
            DOM.searchSuggestionsBox.innerHTML = `<div style="padding: 10px 14px; font-size: 0.8rem; color: var(--text-muted); text-align: center;">No matches found</div>`;
        } else {
            DOM.searchSuggestionsBox.innerHTML = filtered.map(c => `
                <div class="suggestion-item" data-code="${c.code}">
                    <span class="suggestion-code">${c.code}</span>
                    <span class="suggestion-meta">${c.maker} | ${c.size} | ${c.type}</span>
                </div>
            `).join('');
            
            // Attach click listeners to suggestion items
            DOM.searchSuggestionsBox.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', () => {
                    const code = item.getAttribute('data-code');
                    DOM.manualChipSearch.value = code;
                    DOM.searchSuggestionsBox.classList.add('hidden');
                    submitManualLookup(code);
                });
            });
        }
        DOM.searchSuggestionsBox.classList.remove('hidden');
    });
}

if (DOM.btnClearSearch) {
    DOM.btnClearSearch.addEventListener('click', () => {
        DOM.manualChipSearch.value = '';
        DOM.searchSuggestionsBox.classList.add('hidden');
        DOM.btnClearSearch.classList.add('hidden');
    });
}

// Close suggestions dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (DOM.searchSuggestionsBox && !DOM.manualChipSearch.contains(e.target) && !DOM.searchSuggestionsBox.contains(e.target)) {
        DOM.searchSuggestionsBox.classList.add('hidden');
    }
});

async function submitManualLookup(code) {
    DOM.scanResultCard.classList.add('hidden');
    DOM.scannerLoader.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/scan/manual/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ code })
        });
        const result = await response.json();
        DOM.scannerLoader.classList.add('hidden');
        
        if (response.ok && result.success) {
            displayScanResult(result.scan);
        } else {
            alert(result.error || "Manual lookup failed.");
        }
    } catch (err) {
        DOM.scannerLoader.classList.add('hidden');
        alert("Network error: failed to submit manual lookup.");
    }
}
