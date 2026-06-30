import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  BarChart2,
  Bell,
  BookOpen,
  Box,
  CheckCircle,
  CheckSquare,
  ChevronRight,
  Cpu,
  Database,
  FileText,
  Hash,
  KeyRound,
  LayoutDashboard,
  RefreshCcw,
  Search,
  Server,
  Settings,
  Shield,
  Sparkles,
  Upload,
  Users,
  XCircle,
} from "lucide-react";

import { filterNavigationItems } from "../auth/navigation";
import UserMenu from "../components/UserMenu";
import { getHealth, getReadiness } from "../services/healthApi";

const NAV = [
  { icon: LayoutDashboard, label: "Dashboard", sub: "Tổng quan", id: "dashboard" },
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa" },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail" },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen" },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

const SETTINGS_TABS = [
  { id: "overview", label: "Tổng quan", icon: Activity },
  { id: "model", label: "AI & Embedding", icon: Cpu },
  { id: "qa_generation", label: "QA & Generation", icon: Shield },
  { id: "permissions", label: "Phân quyền", icon: Users },
];

const AI_CONFIG = [
  ["Mô hình AI chính", "gemini-2.5-flash"],
  ["Mô hình embedding", "gemini-embedding-2"],
  ["Số chiều embedding", "768"],
  ["Vector database", "Qdrant"],
  ["Question collection", "question_embeddings"],
  ["Formula collection", "formula_embeddings"],
  ["Max upload size", "40 MB"],
];

const GENERATION_PIPELINE = [
  "Sinh biến thể câu hỏi từ câu hỏi gốc",
  "Chuyển câu tự luận sang câu hỏi trắc nghiệm",
  "Sinh phương án nhiễu cho câu hỏi MCQ",
  "Lưu câu hỏi generated vào ngân hàng câu hỏi",
];

const QA_PIPELINE = [
  "Kiểm tra cấu trúc câu hỏi trắc nghiệm",
  "Kiểm tra đáp án đúng và lựa chọn hợp lệ",
  "Kiểm tra phương án nhiễu và trùng lặp nội dung",
  "Kiểm tra symbolic solver nếu có solver phù hợp",
  "Đánh dấu câu hỏi cần review nếu phát hiện cảnh báo",
];

const ADMIN_PERMISSIONS = [
  "Dashboard",
  "Upload Document",
  "Semantic Search",
  "Calculus Taxonomy",
  "QA Rules",
  "Sinh biến thể",
  "Analytics",
  "Settings",
];

const USER_PERMISSIONS = [
  "Dashboard",
  "Semantic Search",
  "Calculus Taxonomy",
  "Xem chi tiết bài tập",
  "Xem lời giải và đáp án",
];

const DEMO_USERS = [
  ["admin", "Quản trị viên"],
  ["user1", "Người dùng"],
  ["user2", "Người dùng"],
  ["user3", "Người dùng"],
];

function Row({ label, sub, children }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-slate-50 last:border-0">
      <div className="min-w-0">
        <p className="text-[12px] font-medium text-slate-700">{label}</p>
        {sub && <p className="text-[10px] text-slate-400 mt-0.5">{sub}</p>}
      </div>
      <div className="flex-shrink-0 ml-4">{children}</div>
    </div>
  );
}

function StatusPill({ ok, label }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold ${
        ok
          ? "border-emerald-200 bg-emerald-50 text-emerald-700"
          : "border-red-200 bg-red-50 text-red-700"
      }`}
    >
      {ok ? <CheckCircle size={12} /> : <XCircle size={12} />}
      {label}
    </span>
  );
}

function InfoTile({ icon: Icon, label, value, ok }) {
  return (
    <div className="bg-white border border-slate-100 rounded-xl px-4 py-3">
      <div className="flex items-center gap-2 mb-2">
        <Icon size={14} className="text-slate-400" />
        <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">
          {label}
        </p>
      </div>
      <div className="flex items-center justify-between gap-3">
        <p className="text-[12px] font-bold text-slate-700 break-all">{value}</p>
        {typeof ok === "boolean" && (
          <span
            className={`h-2.5 w-2.5 rounded-full flex-shrink-0 ${
              ok ? "bg-emerald-500" : "bg-red-500"
            }`}
          />
        )}
      </div>
    </div>
  );
}

function SectionCard({ title, children }) {
  return (
    <section className="bg-white border border-slate-100 rounded-xl p-4">
      <p className="text-[12px] font-bold text-slate-700 mb-3">{title}</p>
      {children}
    </section>
  );
}

function Checklist({ items }) {
  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div key={item} className="flex items-start gap-2">
          <CheckCircle size={13} className="mt-0.5 flex-shrink-0 text-emerald-600" />
          <p className="text-[12px] text-slate-600">{item}</p>
        </div>
      ))}
    </div>
  );
}

export default function SystemSettings({
  activePage = "settings",
  onNavigate = () => {},
  currentUser = null,
  onLogout = () => {},
}) {
  const [activeTab, setActiveTab] = useState("overview");
  const [health, setHealth] = useState(null);
  const [readiness, setReadiness] = useState(null);
  const [systemLoading, setSystemLoading] = useState(true);
  const [systemError, setSystemError] = useState(null);

  const loadSystemStatus = useCallback(async () => {
    setSystemLoading(true);
    setSystemError(null);

    try {
      const [healthData, readinessData] = await Promise.all([
        getHealth(),
        getReadiness(),
      ]);

      setHealth(healthData);
      setReadiness(readinessData);
    } catch (requestError) {
      setSystemError(requestError.message);
    } finally {
      setSystemLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadInitialStatus() {
      setSystemLoading(true);
      setSystemError(null);

      try {
        const [healthData, readinessData] = await Promise.all([
          getHealth(),
          getReadiness(),
        ]);

        if (!cancelled) {
          setHealth(healthData);
          setReadiness(readinessData);
        }
      } catch (requestError) {
        if (!cancelled) {
          setSystemError(requestError.message);
        }
      } finally {
        if (!cancelled) {
          setSystemLoading(false);
        }
      }
    }

    loadInitialStatus();

    return () => {
      cancelled = true;
    };
  }, []);

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
  const apiOnline = health?.status === "ok";
  const databaseOnline = readiness?.checks?.database === true;
  const qdrantOnline = readiness?.checks?.qdrant === true;
  const systemReady = readiness?.status === "ready";
  const userInitial = currentUser?.username?.charAt(0)?.toUpperCase() ?? "A";

  return (
    <div className="flex h-screen bg-slate-50 font-sans overflow-hidden">
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
          <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest px-2 mb-1.5">
            Chức năng
          </p>
          {filterNavigationItems(NAV, currentUser?.role).map((item) => {
            const isActive = activePage === item.id;

            return (
              <div
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`flex items-center gap-2.5 px-2.5 py-2 rounded-lg cursor-pointer transition-all ${
                  isActive ? "bg-blue-50 ring-1 ring-blue-100" : "hover:bg-slate-50"
                }`}
              >
                <item.icon
                  size={15}
                  className={isActive ? "text-blue-600" : "text-slate-400"}
                  strokeWidth={isActive ? 2.5 : 1.8}
                />
                <div className="flex-1 min-w-0">
                  <p className={`text-[11px] font-semibold truncate ${isActive ? "text-blue-700" : "text-slate-500"}`}>
                    {item.label}
                  </p>
                  <p className="text-[10px] text-slate-400 truncate">{item.sub}</p>
                </div>
              </div>
            );
          })}
        </nav>

        <div className="px-2 pb-3 border-t border-slate-100 pt-2">
          <UserMenu currentUser={currentUser} onLogout={onLogout} />
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="bg-white border-b border-slate-100 px-5 py-3 flex items-center justify-between flex-shrink-0">
          <div>
            <h1 className="text-sm font-bold text-slate-800">Cài đặt hệ thống</h1>
            <p className="text-[11px] text-slate-400">
              Xem trạng thái hệ thống, cấu hình AI và phân quyền demo
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={loadSystemStatus}
              disabled={systemLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-semibold rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70 transition-all"
            >
              <RefreshCcw size={12} className={systemLoading ? "animate-spin" : ""} />
              Làm mới trạng thái
            </button>
            <button className="relative p-2 rounded-lg hover:bg-slate-50 text-slate-400">
              <Bell size={14} />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
            </button>
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-[11px] font-bold">
              {userInitial}
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-hidden flex">
          <div className="w-44 flex-shrink-0 border-r border-slate-100 bg-white p-3 space-y-0.5">
            {SETTINGS_TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-all ${
                  activeTab === tab.id
                    ? "bg-blue-50 text-blue-700"
                    : "text-slate-500 hover:bg-slate-50"
                }`}
              >
                <tab.icon size={13} className={activeTab === tab.id ? "text-blue-600" : "text-slate-400"} />
                <span className="text-[11px] font-semibold">{tab.label}</span>
                {activeTab === tab.id && <ChevronRight size={10} className="ml-auto text-blue-400" />}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-5">
            {activeTab === "overview" && (
              <div className="max-w-3xl space-y-4">
                <div
                  className={`border rounded-xl p-4 ${
                    systemLoading
                      ? "bg-blue-50 border-blue-200"
                      : systemReady
                        ? "bg-emerald-50 border-emerald-200"
                        : "bg-red-50 border-red-200"
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-[12px] font-bold text-slate-800 mb-1">
                        Trạng thái kết nối backend
                      </p>
                      <p className="text-[11px] text-slate-600">
                        {systemLoading
                          ? "Đang kiểm tra /health và /ready..."
                          : systemError
                            ? systemError
                            : systemReady
                              ? "Backend, database và vector DB đang sẵn sàng."
                              : "Một hoặc nhiều thành phần hệ thống chưa sẵn sàng."}
                      </p>
                    </div>
                    <StatusPill
                      ok={!systemLoading && systemReady}
                      label={systemReady ? "Ready" : "Not ready"}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <InfoTile icon={Server} label="API Base URL" value={apiBaseUrl} />
                  <InfoTile icon={Activity} label="Backend API" value={apiOnline ? "Online" : "Offline"} ok={apiOnline} />
                  <InfoTile icon={Database} label="Database" value={databaseOnline ? "Ready" : "Not ready"} ok={databaseOnline} />
                  <InfoTile icon={Box} label="Qdrant" value={qdrantOnline ? "Ready" : "Not ready"} ok={qdrantOnline} />
                </div>

                <SectionCard title="Thông tin vận hành">
                  <Row label="Môi trường cấu hình" sub="Frontend đọc API base URL từ VITE_API_BASE_URL">
                    <code className="text-[11px] font-mono font-semibold text-slate-700 bg-slate-50 px-2 py-0.5 rounded">
                      local/demo
                    </code>
                  </Row>
                  <Row label="JWT access token" sub="Thời gian hết hạn theo cấu hình backend">
                    <code className="text-[11px] font-mono font-semibold text-slate-700 bg-slate-50 px-2 py-0.5 rounded">
                      480 phút
                    </code>
                  </Row>
                  <Row label="Upload tối đa" sub="Giới hạn file ingestion trong backend">
                    <code className="text-[11px] font-mono font-semibold text-slate-700 bg-slate-50 px-2 py-0.5 rounded">
                      40 MB
                    </code>
                  </Row>
                </SectionCard>
              </div>
            )}

            {activeTab === "model" && (
              <div className="max-w-3xl space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-2 h-2 rounded-full bg-emerald-500" />
                    <span className="text-[12px] font-bold text-blue-800">
                      Gemini + Qdrant đang là cấu hình chính của hệ thống
                    </span>
                  </div>
                  <p className="text-[11px] text-blue-600">
                    Trang này chỉ hiển thị cấu hình đang dùng; việc thay đổi model/API key thực hiện qua backend environment.
                  </p>
                </div>

                <SectionCard title="Cấu hình AI & Embedding">
                  {AI_CONFIG.map(([label, value]) => (
                    <Row key={label} label={label}>
                      <code className="text-[11px] font-mono font-semibold text-slate-700 bg-slate-50 px-2 py-0.5 rounded">
                        {value}
                      </code>
                    </Row>
                  ))}
                </SectionCard>

                <SectionCard title="Ghi chú cấu hình">
                  <div className="space-y-2">
                    <p className="text-[12px] text-slate-600">
                      Hệ thống sử dụng Gemini cho các tác vụ sinh, phân tích và phân loại nội dung toán học.
                    </p>
                    <p className="text-[12px] text-slate-600">
                      Vector câu hỏi và công thức được lưu trong Qdrant để phục vụ semantic search và formula search.
                    </p>
                    <p className="text-[12px] text-slate-600">
                      API key không hiển thị trên frontend để tránh lộ thông tin nhạy cảm khi demo.
                    </p>
                  </div>
                </SectionCard>
              </div>
            )}

            {activeTab === "qa_generation" && (
              <div className="max-w-3xl space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <SectionCard title="Pipeline sinh câu hỏi">
                    <Checklist items={GENERATION_PIPELINE} />
                  </SectionCard>

                  <SectionCard title="Pipeline kiểm định">
                    <Checklist items={QA_PIPELINE} />
                  </SectionCard>
                </div>

                <SectionCard title="Phạm vi truy cập">
                  <Row label="Generation" sub="Sinh biến thể, convert MCQ và lưu câu hỏi generated">
                    <StatusPill ok label="Admin" />
                  </Row>
                  <Row label="QA Rules" sub="Kiểm định chất lượng và rà soát câu hỏi">
                    <StatusPill ok label="Admin" />
                  </Row>
                  <Row label="Question Detail / Search" sub="Khai thác ngân hàng câu hỏi dùng chung">
                    <span className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-700">
                      Admin & User
                    </span>
                  </Row>
                </SectionCard>
              </div>
            )}

            {activeTab === "permissions" && (
              <div className="max-w-3xl space-y-4">
                <div className="bg-white border border-slate-100 rounded-xl p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0">
                      <KeyRound size={16} className="text-blue-600" />
                    </div>
                    <div>
                      <p className="text-[12px] font-bold text-slate-700 mb-1">
                        Mô hình phân quyền RBAC
                      </p>
                      <p className="text-[12px] text-slate-600">
                        Hệ thống dùng hai vai trò chính là <strong>admin</strong> và <strong>user</strong>. Dữ liệu câu hỏi,
                        tài liệu, taxonomy và embedding dùng chung; quyền thao tác được kiểm soát theo vai trò.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <SectionCard title="Admin">
                    <Checklist items={ADMIN_PERMISSIONS} />
                  </SectionCard>

                  <SectionCard title="User">
                    <Checklist items={USER_PERMISSIONS} />
                  </SectionCard>
                </div>

                <SectionCard title="Tài khoản demo">
                  {DEMO_USERS.map(([username, role]) => (
                    <Row key={username} label={username} sub={role}>
                      <span
                        className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-semibold ${
                          username === "admin"
                            ? "border-blue-200 bg-blue-50 text-blue-700"
                            : "border-slate-200 bg-slate-50 text-slate-600"
                        }`}
                      >
                        {username === "admin" ? "admin" : "user"}
                      </span>
                    </Row>
                  ))}
                  <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2">
                    <p className="text-[11px] text-amber-700">
                      Tài khoản demo được tạo bằng seed script. Trong phạm vi đồ án,
                      hệ thống không triển khai quản lý tài khoản trực tiếp trên frontend.
                    </p>
                  </div>
                </SectionCard>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
