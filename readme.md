# Florisys Backend API

This is the backend API for **Florisys**, providing endpoints for:

- Managing **plots**
- Managing **beds** within plots
- Managing **spatial maps** for beds
- (Future) AI applications such as plant health analysis

The backend is built in **Python** (FastAPI) and uses **MongoDB** for storage.
It is designed to work with the **Florisys Next.js frontend**.

---

## 📋 API Overview

### 1️⃣ Plot Endpoints

| Method | Endpoint         | Description |
|--------|------------------|-------------|
| `POST` | `/upload`        | Upload a `.tif` orthomosaic file for a new plot. Stores empty JSON metadata in DB. |
| `GET`  | `/view`          | List all plots with basic info. |
| `GET`  | `/view_plot`     | Get a specific plot's `.tif` file and associated JSON metadata. |

---

### 2️⃣ Bed Endpoints

| Method | Endpoint   | Description |
|--------|-----------|-------------|
| `POST` | `/add`    | Add a new bed to a plot. Requires name, 4 coordinates, count, average volume, and grade. |
| `PUT`  | `/edit`   | Edit an existing bed's details or coordinates. |
| `DELETE` | `/delete` | Remove a bed from a plot. |
| `GET`  | `/view`   | View details of a specific bed, including all spatial maps linked to it. |

---

### 3️⃣ Spatial Map Endpoints

| Method | Endpoint   | Description |
|--------|-----------|-------------|
| `POST` | `/add`    | Add a spatial map (PLY file) to a bed. Includes upload date and plant count. |
| `GET`  | `/view`   | View spatial map file and metadata for a specific bed. |

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/florisys-backend.git
cd florisys-backend

### 2. Create & activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=florisys
UPLOAD_DIR=./uploads
```

### 5. Run the backend

```bash
uvicorn app.main:app --reload
```

By default, the server runs at **`http://localhost:8000`**.

---

## 🐳 Run with Docker

```bash
docker build -t florisys-backend .
docker run -d -p 8000:8000 --env-file .env florisys-backend
```

---

## 📦 Example API Usage

### Upload a Plot

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@map.tif" \
  -F "name=North Field"
```

### Add a Bed

```bash
curl -X POST "http://localhost:8000/add" \
  -H "Content-Type: application/json" \
  -d '{
    "plot_id": "64e2a9d9f1e45b2b8c1f4f29",
    "name": "A15",
    "coordinates": [
      [-87.753085, 30.642042],
      [-87.753068, 30.642043],
      [-87.753069, 30.642060],
      [-87.753086, 30.642059]
    ],
    "count": 120,
    "average_volume": 3.5,
    "grade": "A"
  }'
```

### Add a Spatial Map to a Bed

```bash
curl -X POST "http://localhost:8000/add" \
  -F "bed_id=64e2abf3f1e45b2b8c1f4f2a" \
  -F "file=@scan.ply" \
  -F "count=150"
```

---

## 📊 Data Model

**Plot**

```json
{
  "_id": "ObjectId",
  "name": "North Field",
  "tif_file": "uploads/north_field.tif",
  "beds": []
}
```

**Bed**

```json
{
  "id": "UUID",
  "name": "A15",
  "coordinates": [[lon, lat], ...],
  "count": 120,
  "average_volume": 3.5,
  "grade": "A",
  "spatial_maps": []
}
```

**Spatial Map**

```json
{
  "file": "uploads/bed_A15_map1.ply",
  "upload_date": "2025-08-13T15:00:00Z",
  "count": 150
}
```

---

## 🚀 Future Plans

* AI-powered plant health classification
* Automatic bed detection from orthomosaic
* Real-time rover integration

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

```

---

If you want, I can also **add example request/response JSON for each endpoint** so that the frontend team has clear payload structures to follow. That would make this README serve as a full API spec.
```
