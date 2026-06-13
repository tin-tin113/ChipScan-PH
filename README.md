# ChipScan PH 📱💾

**ChipScan PH** is a premium, mobile-responsive smartphone storage chip grading and valuation application designed for repair shop technicians and administrators.

It leverages a robust Django backend, SQLite database, and custom OpenCV + **PaddleOCR** image processing pipeline to extract chip codes, grade modules, and calculate buying rates in real-time.

---

## 🚀 Key Features

*   **Cyberpunk Glassmorphic UI**: Beautiful custom CSS templates with light/dark theme controllers and responsive viewports (430px wide max) simulating a modern smartphone.
*   **Camera Viewfinder with Fallbacks**: Uses browser webcams (`MediaDevices.getUserMedia`) with a server-side MJPEG video stream simulator if a physical camera is unavailable.
*   **Advanced Image Pre-processing**: Uses OpenCV to automatically convert images to grayscale, scale to 1600px, deskew orientation, and filter screen moire grid noise, CLAHE contrast adjustments, median blur, and unsharp sharpening.
*   **Dual Matching Pipeline**:
    *   *Perceptual Visual Matcher*: Combines `dHash` and `aHash` to generate a 32-character hex hash, bypassing OCR if Hamming distance $\le 10$.
    *   *OCR Heuristic Matcher*: Normalizes extracted PaddleOCR texts and matches them against chip codes, aliases, or alternate codes using SequenceMatcher similarity and manufacturer prefixes.
*   **Role-Based Price Matrix**: Adjustable grades (A1 to A5) and size-based (16GB to 1TB) pricing configurations for administrators and technicians.
*   **Technician Approval Queue**: Technicians can submit photo requests for unrecognized chip markings; administrators can review, reject, or approve and seed them into the catalog.

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+ (Python 3.13 verified)
- SQLite3

### 1. Installation
Install all required package dependencies:
```bash
pip install django djangorestframework opencv-python pillow pillow-heif paddlepaddle paddleocr
```

### 2. Database Migrations
Create and apply SQLite schema migrations:
```bash
python manage.py makemigrations scanner
python manage.py migrate
```

### 3. Launch Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```
Open your browser and navigate to **[http://localhost:8000](http://localhost:8000)**.

---

## 🔑 Pre-Seeded Default Users

When the application loads, it lazily seeds the database with the following default credentials:

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Adjust prices, approve requests, add manual chips, read stats |
| **Technician** | `tech1` | `tech123` | Capture scan photos, request catalog approvals, view history |

*Note: You can also use **Login with Google** on the login view which runs an age-gated mock verification and logs you in as `google_user` (Technician).*

---

## 🧪 Running Automated Tests

A comprehensive unit test suite is included to verify database pre-seeding, MD5/Plaintext password check fallbacks, OCR heuristic scoring, and visual Hamming distance calculations:

```bash
python manage.py test scanner
```

---

## 📁 System Architecture
Refer to the [system_overview.md](file:///c:/Users/Administrator/Desktop/ChipScan_PH/system_overview.md) file for extensive layout structures, database schemas, and OCR/Hashing workflow pipelines.
