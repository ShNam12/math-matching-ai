# Huong Dan Buoc 4.12: Ket Noi Frontend Upload Voi Backend API

## 1. Muc tieu

Buoc 4.12 thay UI mock trong trang upload bang du lieu that tu backend.

Luong sau khi hoan thanh:

```text
Mo trang Upload Document
 -> GET /documents
 -> Hien thi danh sach document tu PostgreSQL

Chon hoac keo tha file
 -> POST /documents/upload
 -> Backend tao document status uploaded
 -> Backend background ingestion xu ly R2 / Gemini / Markdown
 -> Frontend polling GET /documents
 -> UI cap nhat uploaded / processing / completed / failed
```

Backend hien da co du endpoint:

```text
POST /documents/upload
GET  /documents
GET  /documents/{document_id}
GET  /documents/{document_id}/status
GET  /documents/{document_id}/markdown
```

## 2. Trang thai hien tai

File frontend chinh:

```text
apps/frontend/src/pages/UploadDocument.jsx
```

Hien tai trang nay van la UI mock:

```text
- DOCS la mang hard-code.
- Nut "Chon file" chua mo input file.
- Drop zone chua upload file.
- Nut "Lam moi" chua goi backend.
- Danh sach khong doc PostgreSQL.
- Status UI dang dung done / processing / error.
```

Trong khi backend tra status:

```text
uploaded
processing
completed
failed
```

Vi vay frontend phai dung truc tiep status cua backend, khong tiep tuc dung `done` va `error`.

## 3. Cac file can them va sua

Them hai file:

```text
apps/frontend/src/services/apiClient.js
apps/frontend/src/services/ingestionApi.js
```

Sua:

```text
apps/frontend/src/pages/UploadDocument.jsx
```

Chua sua:

```text
apps/api/main.py
```

Ly do: CORS cho browser la buoc 4.13. Sau khi hoan thanh code frontend, browser co the bao loi CORS cho den khi lam tiep buoc 4.13.

## 4. Tao API client dung chung

Tao file:

```text
apps/frontend/src/services/apiClient.js
```

Them toan bo noi dung:

```js
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const contentType = response.headers.get("content-type") ?? "";

  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      typeof data === "object" && data?.detail
        ? data.detail
        : "Request failed";

    throw new Error(message);
  }

  return data;
}
```

Muc dich:

```text
- Khong viet lai fetch o tung component.
- Dung VITE_API_BASE_URL neu sau nay cau hinh backend URL bang bien moi truong.
- Mac dinh goi backend local tai http://localhost:8000.
- Doc loi JSON cua FastAPI, vi du {"detail": "..."}.
- Nem Error de component hien thong bao cho nguoi dung.
```

Khong dat header `Content-Type` mac dinh trong file nay.

Ly do:

```text
Upload file dung FormData.
Browser phai tu tao Content-Type multipart/form-data kem boundary.
Neu gan Content-Type thu cong, backend co the khong doc duoc file.
```

## 5. Tao ingestion API

Tao file:

```text
apps/frontend/src/services/ingestionApi.js
```

Them toan bo noi dung:

```js
import { apiRequest } from "./apiClient";

export function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export function listDocuments() {
  return apiRequest("/documents");
}

export function getDocument(documentId) {
  return apiRequest(`/documents/${documentId}`);
}

export function getDocumentStatus(documentId) {
  return apiRequest(`/documents/${documentId}/status`);
}

export function getDocumentMarkdown(documentId) {
  return apiRequest(`/documents/${documentId}/markdown`);
}
```

Muc dich:

```text
- Gom cac endpoint ingestion vao mot file.
- Component React chi goi ham co ten ro rang.
- De tai su dung getDocumentMarkdown o buoc hien thi Markdown sau nay.
```

## 6. Sua imports trong `UploadDocument.jsx`

Mo file:

```text
apps/frontend/src/pages/UploadDocument.jsx
```

Tai dong 1, thay:

```js
import { useState } from "react";
```

bang:

```js
import { useCallback, useEffect, useRef, useState } from "react";
```

Sau block import icon tu `lucide-react`, them:

```js
import {
  listDocuments,
  uploadDocument,
} from "../services/ingestionApi";
```

Muc dich:

```text
useState       Luu documents, uploading, error va filter.
useEffect      Load danh sach va polling.
useCallback    Giu tham chieu on dinh cho ham loadDocuments.
useRef         Mo input file an khi nhan nut Chon file.
```

Ghi chu:

```text
Frontend hien co mot so icon import nhung khong dung.
Co the xoa icon thua khi chay npm run lint.
Viec xoa icon khong anh huong logic upload.
```

## 7. Xoa du lieu mock `DOCS`

Trong:

```text
apps/frontend/src/pages/UploadDocument.jsx
```

Xoa toan bo block:

```js
const DOCS = [
  ...
];
```

Block nay hien nam khoang dong 21-88.

Ly do:

```text
- Danh sach phai den tu GET /documents.
- Mock dang co DOCX va TEX trong khi backend khong ho tro.
- Mock dung field name, size, date khac contract backend.
```

## 8. Them helper format du lieu API

Tai vi tri vua xoa `DOCS`, them:

```js
function formatFileSize(sizeBytes) {
  if (sizeBytes < 1024) return `${sizeBytes} B`;
  if (sizeBytes < 1024 * 1024) return `${(sizeBytes / 1024).toFixed(1)} KB`;
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value) {
  return new Date(value).toLocaleString("vi-VN");
}

function getFileTypeStyle(sourceType) {
  if (sourceType === "pdf") {
    return { label: "PDF", color: "#A32D2D", bg: "#FCEBEB" };
  }

  return { label: "MD", color: "#185FA5", bg: "#E6F1FB" };
}
```

Muc dich:

```text
- Backend tra size_bytes la so byte, frontend format thanh B / KB / MB.
- Backend tra timestamp ISO, frontend hien theo locale vi-VN.
- Backend chi ho tro source_type pdf va markdown.
```

## 9. Sua `FileTypeIcon`

Tim ham hien tai:

```js
function FileTypeIcon({ type, color, bg }) {
  const labels = { pdf: "PDF", docx: "DOC", tex: "TEX", txt: "TXT" };
  ...
}
```

Thay toan bo ham bang:

```js
function FileTypeIcon({ sourceType }) {
  const { label, color, bg } = getFileTypeStyle(sourceType);

  return (
    <div
      style={{ background: bg, border: `1px solid ${color}30` }}
      className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
    >
      <span style={{ color, fontSize: 9, fontWeight: 700, letterSpacing: 0.5 }}>
        {label}
      </span>
    </div>
  );
}
```

Ly do:

```text
Khong con DOCX, TEX hoac TXT.
Icon chi dua vao source_type backend tra ve.
```

## 10. Sua `StatusBadge`

Tim ham:

```js
function StatusBadge({ status, progress, errorMsg }) {
```

Thay toan bo ham bang:

```js
function StatusBadge({ status }) {
  if (status === "completed") {
    return (
      <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
        <CheckCircle size={10} /> Hoan thanh
      </span>
    );
  }

  if (status === "uploaded" || status === "processing") {
    return (
      <span className="flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded-full">
        <Loader size={10} className="animate-spin" />
        {status === "uploaded" ? "Dang cho xu ly" : "Dang xu ly"}
      </span>
    );
  }

  return (
    <span className="flex items-center gap-1 text-[11px] font-semibold text-red-700 bg-red-50 border border-red-200 px-2.5 py-0.5 rounded-full">
      <AlertCircle size={10} /> Loi
    </span>
  );
}
```

Ly do:

```text
- Backend khong tra progress phan tram.
- `uploaded` va `processing` deu can hien trang thai dang cho.
- `completed` thay cho mock `done`.
- `failed` roi vao badge Loi.
```

Khong tu tao phan tram gia neu backend chua co du lieu progress.

## 11. Them state va ham goi API trong component

Tim dau component:

```js
export default function UploadDocument({ activePage = "upload", onNavigate = () => {} }) {
  const [dragging, setDragging] = useState(false);
  const [filterStatus, setFilterStatus] = useState("all");
```

Them ngay sau `filterStatus`:

```js
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const loadDocuments = useCallback(async () => {
    try {
      const data = await listDocuments();
      setDocuments(data);
      setError(null);
    } catch (requestError) {
      setError(requestError.message);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  useEffect(() => {
    const hasPendingDocument = documents.some(
      (document) =>
        document.status === "uploaded" || document.status === "processing",
    );

    if (!hasPendingDocument) return undefined;

    const intervalId = window.setInterval(loadDocuments, 2500);
    return () => window.clearInterval(intervalId);
  }, [documents, loadDocuments]);

  async function handleUpload(file) {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      await uploadDocument(file);
      await loadDocuments();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragging(false);
    handleUpload(event.dataTransfer.files[0]);
  }
```

Muc dich:

```text
documents       Danh sach document that tu PostgreSQL.
uploading       Khoa nut upload khi request dang chay.
error           Hien loi backend hoac loi network.
fileInputRef    Mo va reset input file an.
loadDocuments   Goi GET /documents.
useEffect 1     Load danh sach khi mo trang.
useEffect 2     Poll moi 2.5 giay neu co document dang xu ly.
handleUpload    Goi POST /documents/upload va refresh danh sach.
handleDrop      Lay file dau tien khi nguoi dung keo tha.
```

## 12. Thay cac bien tinh toan tu `DOCS`

Tim:

```js
const filtered = DOCS.filter((d) =>
  filterStatus === "all" ? true : d.status === filterStatus
);
const totalProblems = DOCS.filter((d) => d.status === "done").reduce((a, b) => a + (b.problems || 0), 0);
```

Thay bang:

```js
  const filtered = documents.filter((document) =>
    filterStatus === "all" ? true : document.status === filterStatus,
  );

  const totalSizeBytes = documents.reduce(
    (total, document) => total + document.size_bytes,
    0,
  );

  const processingCount = documents.filter(
    (document) =>
      document.status === "uploaded" || document.status === "processing",
  ).length;

  const failedCount = documents.filter(
    (document) => document.status === "failed",
  ).length;
```

Ly do:

```text
Backend buoc 4 chua co so luong bai tap.
Khong dung mock totalProblems nua.
Summary chi hien thong tin backend dang co that.
```

## 13. Noi input file va drop zone

Tim drop zone:

```js
<div
  onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
  onDragLeave={() => setDragging(false)}
  onDrop={() => setDragging(false)}
```

Thay `onDrop` bang:

```js
  onDrop={handleDrop}
```

Ngay ben trong drop zone, truoc icon upload, them input an:

```jsx
<input
  ref={fileInputRef}
  type="file"
  accept=".pdf,.md,.markdown"
  className="hidden"
  onChange={(event) => handleUpload(event.target.files[0])}
/>
```

Tim nut:

```jsx
<button className="flex items-center gap-2 mx-auto px-5 py-2.5 bg-blue-600 text-white text-[12px] font-semibold rounded-lg hover:bg-blue-700 transition-colors">
  <FolderOpen size={14} /> Chon file
</button>
```

Them props:

```jsx
type="button"
disabled={uploading}
onClick={() => fileInputRef.current?.click()}
```

Ket qua:

```jsx
<button
  type="button"
  disabled={uploading}
  onClick={() => fileInputRef.current?.click()}
  className="flex items-center gap-2 mx-auto px-5 py-2.5 bg-blue-600 text-white text-[12px] font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60"
>
  <FolderOpen size={14} />
  {uploading ? "Dang upload..." : "Chon file"}
</button>
```

## 14. Sua text dinh dang duoc ho tro

Tim:

```jsx
{["PDF", "DOCX", "TEX", "TXT", "EPUB"].map((f) => (
```

Thay bang:

```jsx
{["PDF", "Markdown"].map((fileType) => (
```

Trong hai dong ben duoi, doi `f` thanh `fileType`.

Ly do:

```text
Backend chi chap nhan:
.pdf
.md
.markdown
```

Neu UI van hien DOCX, TEX, TXT va EPUB thi nguoi dung se thay thong tin sai.

## 15. Hien loi upload hoac network

Ngay sau ket thuc drop zone, them:

```jsx
{error && (
  <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-[12px] text-red-700">
    {error}
  </div>
)}
```

Muc dich:

```text
- Hien loi file khong duoc ho tro.
- Hien loi file rong hoac qua 40 MB.
- Hien loi network.
- Hien loi CORS trong giai doan chua lam buoc 4.13.
```

## 16. Sua header danh sach va nut lam moi

Tim:

```jsx
{DOCS.length} files
```

Thay bang:

```jsx
{documents.length} files
```

Tim nut `Lam moi`:

```jsx
<button className="flex items-center gap-1.5 text-[11px] text-slate-500 border border-slate-200 px-2.5 py-1.5 rounded-lg hover:bg-slate-50">
```

Them:

```jsx
type="button"
onClick={loadDocuments}
```

Muc dich:

```text
Nut Lam moi goi lai GET /documents.
```

## 17. Sua bo loc status

Tim mang filter:

```js
[["all", "Tat ca"], ["done", "Hoan thanh"], ["processing", "Dang xu ly"], ["error", "Loi"]]
```

Thay bang:

```js
[
  ["all", "Tat ca"],
  ["completed", "Hoan thanh"],
  ["processing", "Dang xu ly"],
  ["failed", "Loi"],
]
```

Ghi chu:

```text
Document status uploaded van hien trong Tat ca.
UI badge se hien "Dang cho xu ly".
Khong can them tab rieng cho uploaded trong MVP.
```

## 18. Sua tung row document

Tim block:

```jsx
{filtered.map((doc, i) => (
  <div key={i} ...
```

Thay:

```jsx
key={i}
```

bang:

```jsx
key={doc.id}
```

Thay:

```jsx
<FileTypeIcon type={doc.type} color={doc.color} bg={doc.bg} />
```

bang:

```jsx
<FileTypeIcon sourceType={doc.source_type} />
```

Thay:

```jsx
{doc.name}
```

bang:

```jsx
{doc.filename}
```

Thay:

```jsx
{doc.size}
```

bang:

```jsx
{formatFileSize(doc.size_bytes)}
```

Xoa block hien pages:

```jsx
{doc.pages && <><span ...>{doc.pages} trang</span></>}
```

Ly do:

```text
Backend chua tra page count.
```

Thay:

```jsx
{doc.date}
```

bang:

```jsx
{formatDate(doc.created_at)}
```

Thay dieu kien hien loi:

```jsx
{doc.status === "error" && (
```

bang:

```jsx
{doc.status === "failed" && doc.error_message && (
```

Thay:

```jsx
{doc.errorMsg}
```

bang:

```jsx
{doc.error_message}
```

Xoa block:

```jsx
{doc.problems && (
  ...
)}
```

Ly do:

```text
Backend buoc 4 chua tra problems.
```

Thay:

```jsx
<StatusBadge status={doc.status} progress={doc.progress} errorMsg={doc.errorMsg} />
```

bang:

```jsx
<StatusBadge status={doc.status} />
```

## 19. Sua summary bar

Summary mock hien tai dang dung gia tri hard-code va `totalProblems`.

Tim block mang trong summary:

```js
[
  { label: "Tong dung luong", value: "87.7 MB", icon: Database },
  { label: "Bai tap da index", value: totalProblems.toLocaleString(), icon: FileText },
  { label: "Dang xu ly", value: "2 files", icon: Loader },
  { label: "Loi can xu ly", value: "1 file", icon: AlertCircle },
]
```

Thay bang:

```js
[
  { label: "Tong dung luong", value: formatFileSize(totalSizeBytes), icon: Database },
  { label: "Tai lieu da upload", value: `${documents.length} files`, icon: FileText },
  { label: "Dang xu ly", value: `${processingCount} files`, icon: Loader },
  { label: "Loi can xu ly", value: `${failedCount} files`, icon: AlertCircle },
]
```

Ly do:

```text
Tat ca gia tri summary phai den tu backend.
Khong hien so bai tap khi chua co module segmentation.
```

Tai header phia tren, neu van con `totalProblems`, thay phan gia tri bang:

```jsx
{documents.length.toLocaleString()}
```

Va doi label thanh:

```text
Tong tai lieu da ingested
```

## 20. Polling va gioi han cua BackgroundTasks

Frontend polling khi co:

```text
uploaded
processing
```

Moi:

```text
2500 ms
```

Se goi lai:

```text
GET /documents
```

Khi tat ca document da:

```text
completed
failed
```

polling tu dung.

Luu y:

```text
FastAPI BackgroundTasks phu hop MVP.
Neu restart server khi dang xu ly, job co the mat.
Worker queue rieng se lam sau, khong them Celery/RQ trong buoc 4.12.
```

## 21. Chay frontend build

Tai thu muc frontend:

```powershell
cd apps/frontend
npm run build
```

Muc dich:

```text
Kiem tra import sai.
Kiem tra JSX sai cu phap.
Kiem tra file services moi duoc resolve.
```

Neu muon chay lint:

```powershell
npm run lint
```

Neu lint bao icon import nhung khong su dung, xoa icon do khoi block import `lucide-react`.

## 22. Chay thu frontend va backend

Terminal 1, tai thu muc goc:

```powershell
uvicorn apps.api.main:app --reload
```

Terminal 2:

```powershell
cd apps/frontend
npm run dev
```

Mo:

```text
http://localhost:5173
```

Chuyen sang trang:

```text
Upload Document
```

Ket qua code frontend mong doi:

```text
- Trang goi GET http://localhost:8000/documents.
- Nut Chon file mo file picker.
- Chi cho chon PDF va Markdown.
- Drop file goi upload.
- Danh sach hien document tu backend.
- Nut Lam moi goi lai API.
- Document dang xu ly duoc polling.
```

## 23. Loi CORS la buoc tiep theo

Khi chay browser, co kha nang thay loi dang:

```text
Access to fetch at 'http://localhost:8000/documents'
from origin 'http://localhost:5173'
has been blocked by CORS policy
```

Day la ket qua du kien neu backend chua cau hinh CORS.

Khong sua workaround trong component.

Chuyen sang buoc 4.13 de them:

```text
CORSMiddleware
allow_origins=["http://localhost:5173"]
```

vao:

```text
apps/api/main.py
```

## 24. Tieu chi hoan thanh

Buoc 4.12 hoan thanh khi:

```text
1. Co apps/frontend/src/services/apiClient.js.
2. Co apps/frontend/src/services/ingestionApi.js.
3. UploadDocument.jsx khong con DOCS mock.
4. Trang load danh sach bang GET /documents.
5. Nut Chon file mo input accept .pdf,.md,.markdown.
6. Drop zone upload file dau tien duoc tha vao.
7. Upload dung FormData va khong gan Content-Type thu cong.
8. Status UI dung uploaded / processing / completed / failed.
9. Frontend polling khi tai lieu dang uploaded hoac processing.
10. Nut Lam moi goi lai listDocuments.
11. Summary khong con gia tri mock.
12. UI chi ghi ho tro PDF va Markdown.
13. npm run build thanh cong.
```

Sau buoc 4.12, chuyen sang buoc 4.13 de cau hinh CORS cho Vite dev server.
