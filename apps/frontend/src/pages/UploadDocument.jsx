import { useCallback, useEffect, useRef, useState } from "react";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Database,
  CloudUpload, CheckCircle, Loader, AlertCircle,
  Eye, Trash2, RefreshCw, FolderOpen, Sparkles, LayoutDashboard,
} from "lucide-react";

import {
  getDocument,
  getDocumentMarkdown,
  getDocumentStatus,
  listDocuments,
  uploadDocument,
} from "../services/ingestionApi";
  
const NAV = [
  { icon: LayoutDashboard, label: "Dashboard", sub: "Tổng quan", id: "dashboard" },
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload", active: true },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa", badge: 3 },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail" },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen" },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

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

function StatusBadge({ status }) {
  if (status === "completed") {
    return (
      <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
        <CheckCircle size={10} /> Hoàn thành
      </span>
    );
  }

  if (status === "uploaded" || status === "processing") {
    return (
      <span className="flex items-center gap-1 text-[11px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded-full">
        <Loader size={10} className="animate-spin" />
        {status === "uploaded" ? "Đang chờ xử lý" : "Đang xử lý"}
      </span>
    );
  }

  return (
    <span className="flex items-center gap-1 text-[11px] font-semibold text-red-700 bg-red-50 border border-red-200 px-2.5 py-0.5 rounded-full">
      <AlertCircle size={10} /> Lỗi
    </span>
  );
}

export default function UploadDocument({ activePage = "upload", onNavigate = () => {} }) {
  const [dragging, setDragging] = useState(false);
  const [filterStatus, setFilterStatus] = useState("all");

  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [refreshingDocumentId, setRefreshingDocumentId] = useState(null);
  const [markdownViewer, setMarkdownViewer] = useState({
    open: false,
    loading: false,
    document: null,
    content: "",
    checksum: null,
    error: null,
  });

  const [documentDetailViewer, setDocumentDetailViewer] = useState({
    open: false,
    loading: false,
    document: null,
    error: null,
  });

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
      const timeoutId = window.setTimeout(loadDocuments, 0);
      return () => window.clearTimeout(timeoutId);
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
    if (!file || uploading) return;

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

  async function handleViewMarkdown(document) {
    if (!document.markdown_available) return;

    setMarkdownViewer({
      open: true,
      loading: true,
      document,
      content: "",
      checksum: null,
      error: null,
    });

    try {
      const data = await getDocumentMarkdown(document.id);

      setMarkdownViewer({
        open: true,
        loading: false,
        document,
        content: data.markdown_content,
        checksum: data.markdown_checksum,
        error: null,
      });
    } catch (requestError) {
      setMarkdownViewer({
        open: true,
        loading: false,
        document,
        content: "",
        checksum: null,
        error: requestError.message,
      });
    }
  }

  function closeMarkdownViewer() {
    setMarkdownViewer({
      open: false,
      loading: false,
      document: null,
      content: "",
      checksum: null,
      error: null,
    });
  }

  async function handleRefreshDocumentStatus(documentId) {
    if (refreshingDocumentId) return;

    setRefreshingDocumentId(documentId);
    setError(null);

    try {
      const statusData = await getDocumentStatus(documentId);

      setDocuments((currentDocuments) =>
        currentDocuments.map((document) =>
          document.id === documentId
            ? {
                ...document,
                status: statusData.status,
                message: statusData.message,
                markdown_available: statusData.markdown_available,
                error_message: statusData.error_message,
                updated_at: statusData.updated_at,
              }
            : document,
        ),
      );
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setRefreshingDocumentId(null);
    }
  }

  async function handleViewDocumentDetail(documentId) {
    setDocumentDetailViewer({
      open: true,
      loading: true,
      document: null,
      error: null,
    });

    try {
      const data = await getDocument(documentId);

      setDocumentDetailViewer({
        open: true,
        loading: false,
        document: data,
        error: null,
      });
    } catch (requestError) {
      setDocumentDetailViewer({
        open: true,
        loading: false,
        document: null,
        error: requestError.message,
      });
    }
  }

  function closeDocumentDetailViewer() {
    setDocumentDetailViewer({
      open: false,
      loading: false,
      document: null,
      error: null,
    });
  }

    const filtered = documents.filter((document) => {
    if (filterStatus === "all") return true;

    if (filterStatus === "processing") {
      return (
        document.status === "uploaded" ||
        document.status === "processing"
      );
    }

    return document.status === filterStatus;
  });

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

  return (
    <div className="flex h-screen bg-slate-50 font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 flex-shrink-0 bg-white border-r border-slate-100 flex flex-col">
        <div className="px-4 py-4 border-b border-slate-100 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <Hash size={15} className="text-white" strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-[13px] font-bold text-slate-800 leading-none">Calculus AI</p>
            <p className="text-[10px] text-slate-400 mt-0.5 tracking-widest uppercase">System v2.1</p>
          </div>
        </div>

        <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
          <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest px-2 mb-1.5">Chức năng</p>
          {NAV.map((item) => {
            const isActive = activePage === item.id;
            return (
            <div key={item.id} onClick={() => onNavigate(item.id)}
              className={`flex items-center gap-2.5 px-2.5 py-2 rounded-lg cursor-pointer transition-all ${
                isActive ? "bg-blue-50 ring-1 ring-blue-100" : "hover:bg-slate-50"
              }`}>
              <item.icon size={15}
                className={isActive ? "text-blue-600" : "text-slate-400"}
                strokeWidth={isActive ? 2.5 : 1.8} />
              <div className="flex-1 min-w-0">
                <p className={`text-[11px] font-semibold truncate ${isActive ? "text-blue-700" : "text-slate-500"}`}>
                  {item.label}
                </p>
                <p className="text-[10px] text-slate-400 truncate">{item.sub}</p>
              </div>
              {item.badge && (
                <span className="text-[10px] font-bold text-white bg-red-500 px-1.5 py-0.5 rounded-full">{item.badge}</span>
              )}
            </div>
            );
          })}
        </nav>

        <div className="px-2 pb-3 border-t border-slate-100 pt-2">
          <div className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-50 cursor-pointer">
            <div className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-white text-[10px] font-bold">N</div>
            <div>
              <p className="text-[11px] font-semibold text-slate-700">Nguyễn V. An</p>
              <p className="text-[10px] text-slate-400">Administrator</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-white border-b border-slate-100 px-6 py-3 flex items-center justify-between flex-shrink-0">
          <div>
            <h1 className="text-sm font-bold text-slate-800">Upload Document</h1>
            <p className="text-[11px] text-slate-400">Ingestion — bóc tách &amp; xử lý tài liệu toán học</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="text-right mr-2">
              <p className="text-[10px] text-slate-400">Tổng tài liệu đã upload</p>
              <p className="text-sm font-bold text-blue-700">
                {documents.length.toLocaleString()}
              </p>
            </div>
            <button className="relative p-2 rounded-lg hover:bg-slate-50 text-slate-400">
              <Bell size={15} />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
            </button>
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-[11px] font-bold">N</div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-5">
          {/* Upload zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-8 text-center mb-5 cursor-pointer transition-all ${
              dragging
                ? "border-blue-400 bg-blue-50"
                : "border-slate-200 hover:border-blue-300 hover:bg-slate-50"
            }`}>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.md,.markdown"
              className="hidden"
              onChange={(event) => handleUpload(event.target.files[0])}
            />
            <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center mx-auto mb-3">
              <CloudUpload size={28} className="text-blue-500" strokeWidth={1.5} />
            </div>
            <p className="text-sm font-semibold text-slate-700 mb-1">Kéo &amp; thả tài liệu vào đây</p>
            <p className="text-[12px] text-slate-400 mb-3">hoặc nhấn để chọn file từ máy tính của bạn</p>
            <div className="flex items-center justify-center gap-2 mb-4">
              {["PDF", "Markdown"].map((fileType) => (
                <span
                  key={fileType}
                  className="text-[10px] font-semibold px-2.5 py-1 rounded-md bg-white border border-slate-200 text-slate-500"
                >
                  {fileType}
                </span>
              ))}
            </div>
            <button
              type="button"
              disabled={uploading}
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center gap-2 mx-auto px-5 py-2.5 bg-blue-600 text-white text-[12px] font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60"
            >
              <FolderOpen size={14} />
              {uploading ? "Đang upload..." : "Chọn file"}
            </button>
            <p className="text-[10px] text-slate-400 mt-2.5">Giới hạn 40 MB/file · Hỗ trợ LaTeX, Unicode, MathML</p>
          </div>

          {error && (
            <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-[12px] text-red-700">
              {error}
            </div>
          )}

          {/* File list header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <span className="text-[12px] font-bold text-slate-700">Tài liệu đã upload</span>
              <span className="text-[10px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">{documents.length} files</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex rounded-lg overflow-hidden border border-slate-200">
                {[
                  ["all", "Tất cả"],
                  ["completed", "Hoàn thành"],
                  ["processing", "Đang xử lý"],
                  ["failed", "Lỗi"],
                ].map(([value, label]) => (
                  <button 
                    key={value}
                    onClick={() => setFilterStatus(value)}
                    className={`text-[11px] px-2.5 py-1.5 transition-all ${
                      filterStatus === value ? "bg-blue-600 text-white font-semibold" : "bg-white text-slate-500 hover:bg-slate-50"
                    }`}>
                    {label}
                  </button>
                ))}
              </div>
              <button
                type="button"
                onClick={loadDocuments}
                className="flex items-center gap-1.5 text-[11px] text-slate-500 border border-slate-200 px-2.5 py-1.5 rounded-lg hover:bg-slate-50"
              >
                <RefreshCw size={11} /> Làm mới
              </button>
            </div>
          </div>

          {/* File rows */}
          <div className="space-y-2">
            {filtered.map((doc) => (
              <div
                key={doc.id}
                className="bg-white border border-slate-100 rounded-xl p-3.5 flex items-center gap-3 hover:border-blue-100 hover:shadow-sm transition-all"
              >
                <FileTypeIcon sourceType={doc.source_type} />

                <div className="flex-1 min-w-0">
                  <p className="text-[12px] font-semibold text-slate-700 truncate">
                    {doc.filename}
                  </p>

                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[10px] text-slate-400">
                      {formatFileSize(doc.size_bytes)}
                    </span>

                    <span className="text-slate-200">·</span>

                    <span className="text-[10px] text-slate-400">
                      {formatDate(doc.created_at)}
                    </span>

                    {doc.r2_original_url && (
                      <>
                        <span className="text-slate-200">·</span>
                        <a
                          href={doc.r2_original_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[10px] font-semibold text-blue-600 hover:text-blue-700 hover:underline"
                          onClick={(event) => event.stopPropagation()}
                        >
                          Mở file gốc
                        </a>
                      </>
                    )}

                    {doc.status === "failed" && doc.error_message && (
                      <>
                        <span className="text-slate-200">·</span>
                        <span className="text-[10px] text-red-500">
                          {doc.error_message}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                <StatusBadge status={doc.status} />

                <div className="flex items-center gap-1 ml-1">
                  
                  <button
                    type="button"
                    disabled={refreshingDocumentId === doc.id}
                    title="Làm mới trạng thái"
                    onClick={() => handleRefreshDocumentStatus(doc.id)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-all disabled:opacity-40"
                  >
                    <RefreshCw
                      size={13}
                      className={refreshingDocumentId === doc.id ? "animate-spin" : ""}
                    />
                  </button>

                  <button
                    type="button"
                    title="Xem chi tiết document"
                    onClick={() => handleViewDocumentDetail(doc.id)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-all"
                  >
                    <FileText size={13} />
                  </button>

                  <button
                    type="button"
                    disabled={!doc.markdown_available}
                    title={doc.markdown_available ? "Xem markdown" : "Chưa có markdown"}
                    onClick={() => handleViewMarkdown(doc)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-all disabled:opacity-40 disabled:hover:bg-transparent disabled:hover:text-slate-400"
                  >
                    <Eye size={13} />
                  </button>
                  <button className="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-all">
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Summary bar */}
          <div className="mt-4 bg-white border border-slate-100 rounded-xl p-3.5 flex items-center gap-6">
            {[
              { label: "Tổng dung lượng", value: formatFileSize(totalSizeBytes), icon: Database },
              { label: "Tài liệu đã upload", value: `${documents.length} files`, icon: FileText },
              { label: "Đang xử lý", value: `${processingCount} files`, icon: Loader },
              { label: "Lỗi cần xử lý", value: `${failedCount} files`, icon: AlertCircle },
            ].map((s, i) => (
              <div key={i} className="flex items-center gap-2">
                <s.icon size={14} className="text-slate-400" />
                <div>
                  <p className="text-[10px] text-slate-400">{s.label}</p>
                  <p className="text-[12px] font-bold text-slate-700">{s.value}</p>
                </div>
                {i < 3 && <div className="w-px h-6 bg-slate-100 ml-4" />}
              </div>
            ))}
          </div>
        </div>
      </div>
      {markdownViewer.open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
          <div className="w-full max-w-4xl max-h-[85vh] bg-white rounded-xl border border-slate-200 shadow-xl flex flex-col overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="text-[13px] font-bold text-slate-800 truncate">
                  {markdownViewer.document?.filename}
                </p>
                <p className="text-[10px] text-slate-400">
                  Markdown đã xử lý
                  {markdownViewer.checksum ? ` · ${markdownViewer.checksum}` : ""}
                </p>
              </div>

              <button
                type="button"
                onClick={closeMarkdownViewer}
                className="px-3 py-1.5 rounded-lg text-[11px] font-semibold text-slate-500 border border-slate-200 hover:bg-slate-50"
              >
                Đóng
              </button>
            </div>

            <div className="flex-1 overflow-auto p-4 bg-slate-50">
              {markdownViewer.loading && (
                <div className="flex items-center gap-2 text-[12px] text-slate-500">
                  <Loader size={14} className="animate-spin" />
                  Đang tải markdown...
                </div>
              )}

              {!markdownViewer.loading && markdownViewer.error && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-[12px] text-red-700">
                  {markdownViewer.error}
                </div>
              )}

              {!markdownViewer.loading && !markdownViewer.error && (
                <pre className="whitespace-pre-wrap break-words text-[12px] leading-6 text-slate-700 font-mono">
                  {markdownViewer.content || "Tài liệu chưa có nội dung markdown."}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}

      {documentDetailViewer.open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
          <div className="w-full max-w-3xl max-h-[85vh] bg-white rounded-xl border border-slate-200 shadow-xl flex flex-col overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="text-[13px] font-bold text-slate-800 truncate">
                  Chi tiết document
                </p>
                <p className="text-[10px] text-slate-400 truncate">
                  {documentDetailViewer.document?.filename || "Đang tải dữ liệu"}
                </p>
              </div>

              <button
                type="button"
                onClick={closeDocumentDetailViewer}
                className="px-3 py-1.5 rounded-lg text-[11px] font-semibold text-slate-500 border border-slate-200 hover:bg-slate-50"
              >
                Đóng
              </button>
            </div>

            <div className="flex-1 overflow-auto p-4 bg-slate-50">
              {documentDetailViewer.loading && (
                <div className="flex items-center gap-2 text-[12px] text-slate-500">
                  <Loader size={14} className="animate-spin" />
                  Đang tải chi tiết document...
                </div>
              )}

              {!documentDetailViewer.loading && documentDetailViewer.error && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-[12px] text-red-700">
                  {documentDetailViewer.error}
                </div>
              )}

              {!documentDetailViewer.loading && documentDetailViewer.document && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-[12px]">
                  {[
                    ["ID", documentDetailViewer.document.id],
                    ["Tên file", documentDetailViewer.document.filename],
                    ["Loại nguồn", documentDetailViewer.document.source_type],
                    ["Content type", documentDetailViewer.document.content_type || "Không có"],
                    ["Kích thước", formatFileSize(documentDetailViewer.document.size_bytes)],
                    ["Trạng thái", documentDetailViewer.document.status],
                    ["Message", documentDetailViewer.document.message || "Không có"],
                    ["Có markdown", documentDetailViewer.document.markdown_available ? "Có" : "Không"],
                    ["R2 key", documentDetailViewer.document.r2_original_key || "Không có"],
                    ["R2 URL", documentDetailViewer.document.r2_original_url || "Không có"],
                    ["Lỗi", documentDetailViewer.document.error_message || "Không có"],
                    ["Ngày tạo", formatDate(documentDetailViewer.document.created_at)],
                    ["Cập nhật", formatDate(documentDetailViewer.document.updated_at)],
                    [
                      "Xử lý xong",
                      documentDetailViewer.document.processed_at
                        ? formatDate(documentDetailViewer.document.processed_at)
                        : "Chưa có",
                    ],
                  ].map(([label, value]) => (
                    <div
                      key={label}
                      className="rounded-lg border border-slate-200 bg-white px-3 py-2 min-w-0"
                    >
                      <p className="text-[10px] font-semibold uppercase text-slate-400">
                        {label}
                      </p>
                      <p className="mt-1 break-words text-slate-700">
                        {value}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
