import { useState } from "react";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Sparkles,
  Cpu, Zap, Shield, Users, Globe, Database,
  ChevronRight, Save, RotateCcw, Plus, Trash2,
  Edit3, CheckCircle, AlertTriangle, Eye, EyeOff, Key, LayoutDashboard
} from "lucide-react";

const NAV = [
  { icon: LayoutDashboard, label: "Dashboard", sub: "Tổng quan", id: "dashboard" },
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa", badge: 3 },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail" },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen" },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings", active: true },
];

const SETTINGS_TABS = [
  { id: "model", label: "AI & Embedding", icon: Cpu },
  { id: "gen", label: "Sinh biến thể", icon: Zap },
  { id: "qa", label: "QA & Kiểm định", icon: Shield },
  { id: "users", label: "Người dùng", icon: Users },
  { id: "system", label: "Hệ thống", icon: Globe },
];

const USERS = [
  { name: "Nguyễn V. An", email: "an.nguyen@bk.edu.vn", role: "Admin", avatar: "NA", color: "#185FA5", lastActive: "Hôm nay" },
  { name: "Trần M. Đức", email: "duc.tran@bk.edu.vn", role: "Editor", avatar: "TD", color: "#534AB7", lastActive: "Hôm nay" },
  { name: "Lê T. Hương", email: "huong.le@neu.edu.vn", role: "Viewer", avatar: "LH", color: "#993556", lastActive: "Hôm qua" },
  { name: "Phạm Q. Minh", email: "minh.pham@vnu.edu.vn", role: "Editor", avatar: "PM", color: "#0f766e", lastActive: "3 ngày trước" },
];

const roleColor = {
  Admin: "text-blue-700 bg-blue-50 border-blue-200",
  Editor: "text-emerald-700 bg-emerald-50 border-emerald-200",
  Viewer: "text-slate-600 bg-slate-50 border-slate-200",
};

function Toggle({ on, onToggle }) {
  return (
    <button onClick={onToggle}
      className={`w-9 h-5 rounded-full relative transition-all flex-shrink-0 ${on ? "bg-blue-600" : "bg-slate-200"}`}>
      <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all ${on ? "right-0.5" : "left-0.5"}`} />
    </button>
  );
}

function Row({ label, sub, children }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-slate-50 last:border-0">
      <div>
        <p className="text-[12px] font-medium text-slate-700">{label}</p>
        {sub && <p className="text-[10px] text-slate-400 mt-0.5">{sub}</p>}
      </div>
      <div className="flex-shrink-0 ml-4">{children}</div>
    </div>
  );
}

export default function SettingsPage({ activePage = "settings", onNavigate = () => {} }) {
  const [activeTab, setActiveTab] = useState("model");
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);

  // Toggle states
  const [reranker, setReranker] = useState(true);
  const [cacheEmbed, setCacheEmbed] = useState(true);
  const [autoQA, setAutoQA] = useState(true);
  const [latexVal, setLatexVal] = useState(true);
  const [deduplication, setDeduplication] = useState(true);
  const [emailReport, setEmailReport] = useState(false);
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [devMode, setDevMode] = useState(false);
  const [saveHistory, setSaveHistory] = useState(true);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

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
            <div key={item.id} onClick={() => onNavigate(item.id)} className={`flex items-center gap-2.5 px-2.5 py-2 rounded-lg cursor-pointer transition-all ${isActive ? "bg-blue-50 ring-1 ring-blue-100" : "hover:bg-slate-50"}`}>
              <item.icon size={15} className={isActive ? "text-blue-600" : "text-slate-400"} strokeWidth={isActive ? 2.5 : 1.8} />
              <div className="flex-1 min-w-0">
                <p className={`text-[11px] font-semibold truncate ${isActive ? "text-blue-700" : "text-slate-500"}`}>{item.label}</p>
                <p className="text-[10px] text-slate-400 truncate">{item.sub}</p>
              </div>
              {item.badge && <span className="text-[10px] font-bold text-white bg-red-500 px-1.5 py-0.5 rounded-full">{item.badge}</span>}
            </div>
            );
          })}
        </nav>
        <div className="px-2 pb-3 border-t border-slate-100 pt-2">
          <div className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-50 cursor-pointer">
            <div className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-white text-[10px] font-bold">N</div>
            <div><p className="text-[11px] font-semibold text-slate-700">Nguyễn V. An</p><p className="text-[10px] text-slate-400">Administrator</p></div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="bg-white border-b border-slate-100 px-5 py-3 flex items-center justify-between flex-shrink-0">
          <div>
            <h1 className="text-sm font-bold text-slate-800">Cài đặt hệ thống</h1>
            <p className="text-[11px] text-slate-400">Cấu hình mô hình AI, QA, phân quyền và các tuỳ chọn hệ thống</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handleSave}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-semibold rounded-lg transition-all ${saved ? "bg-emerald-600 text-white" : "bg-blue-600 text-white hover:bg-blue-700"}`}>
              {saved ? <CheckCircle size={12} /> : <Save size={12} />}
              {saved ? "Đã lưu!" : "Lưu thay đổi"}
            </button>
            <button className="flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-semibold text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50">
              <RotateCcw size={12} /> Khôi phục mặc định
            </button>
            <button className="relative p-2 rounded-lg hover:bg-slate-50 text-slate-400">
              <Bell size={14} />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
            </button>
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-[11px] font-bold">N</div>
          </div>
        </header>

        <div className="flex-1 overflow-hidden flex">
          {/* Tabs sidebar */}
          <div className="w-44 flex-shrink-0 border-r border-slate-100 bg-white p-3 space-y-0.5">
            {SETTINGS_TABS.map((tab) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-all ${activeTab === tab.id ? "bg-blue-50 text-blue-700" : "text-slate-500 hover:bg-slate-50"}`}>
                <tab.icon size={13} className={activeTab === tab.id ? "text-blue-600" : "text-slate-400"} />
                <span className="text-[11px] font-semibold">{tab.label}</span>
                {activeTab === tab.id && <ChevronRight size={10} className="ml-auto text-blue-400" />}
              </button>
            ))}
          </div>

          {/* Settings content */}
          <div className="flex-1 overflow-y-auto p-5">
            {/* Model tab */}
            {activeTab === "model" && (
              <div className="max-w-2xl space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-2 h-2 rounded-full bg-emerald-500" />
                    <span className="text-[12px] font-bold text-blue-800">BGE-M3 — Đang hoạt động</span>
                  </div>
                  <p className="text-[11px] text-blue-600">Embedding model 1024-dim · Hỗ trợ đa ngôn ngữ · Tốc độ: ~85ms/query</p>
                </div>

                <div className="bg-white border border-slate-100 rounded-xl p-4">
                  <p className="text-[12px] font-bold text-slate-700 mb-3">Cấu hình Embedding</p>
                  <Row label="Mô hình embedding" sub="Ảnh hưởng đến chất lượng tìm kiếm ngữ nghĩa">
                    <select className="text-[11px] px-2.5 py-1.5 border border-slate-200 rounded-lg bg-slate-50 text-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-400">
                      <option>BGE-M3 (1024-dim) ✓</option>
                      <option>text-embedding-3-large</option>
                      <option>E5-large-v2</option>
                    </select>
                  </Row>
                  <Row label="Ngưỡng cosine similarity" sub="Dưới ngưỡng này sẽ bị loại khỏi kết quả">
                    <div className="flex items-center gap-2">
                      <input type="range" min="0.5" max="0.99" step="0.01" defaultValue="0.75" className="w-24 accent-blue-600" />
                      <span className="text-[12px] font-bold text-slate-700 w-8">0.75</span>
                    </div>
                  </Row>
                  <Row label="Số kết quả tối đa" sub="Top-K kết quả trả về mỗi truy vấn">
                    <select className="text-[11px] px-2.5 py-1.5 border border-slate-200 rounded-lg bg-slate-50 text-slate-700 focus:outline-none">
                      <option>10</option><option selected>20</option><option>50</option>
                    </select>
                  </Row>
                  <Row label="Reranker" sub="Cross-encoder rerank sau bước retrieval">
                    <Toggle on={reranker} onToggle={() => setReranker((s) => !s)} />
                  </Row>
                  <Row label="Cache embedding" sub="Lưu vector vào cache để tăng tốc">
                    <Toggle on={cacheEmbed} onToggle={() => setCacheEmbed((s) => !s)} />
                  </Row>
                </div>

                <div className="bg-white border border-slate-100 rounded-xl p-4">
                  <p className="text-[12px] font-bold text-slate-700 mb-3">API Keys</p>
                  <Row label="Anthropic API Key" sub="Dùng cho tính năng sinh biến thể và giải thích AI">
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5">
                        <Key size={11} className="text-slate-400" />
                        <code className="text-[11px] font-mono text-slate-600">
                          {showKey ? "sk-ant-api03-xxxxx-xxxxxxxxxxxxx" : "sk-ant-api03-••••••••••••••••••"}
                        </code>
                        <button onClick={() => setShowKey((s) => !s)} className="ml-1 text-slate-400 hover:text-slate-600">
                          {showKey ? <EyeOff size={11} /> : <Eye size={11} />}
                        </button>
                      </div>
                    </div>
                  </Row>
                </div>
              </div>
            )}

            {/* Gen tab */}
            {activeTab === "gen" && (
              <div className="max-w-2xl space-y-4">
                <div className="bg-white border border-slate-100 rounded-xl p-4">
                  <p className="text-[12px] font-bold text-slate-700 mb-3">Cấu hình sinh biến thể</p>
                  <Row label="Mô hình sinh" sub="LLM được dùng để tạo biến thể bài tập">
                    <select className="text-[11px] px-2.5 py-1.5 border border-slate-200 rounded-lg bg-slate-50 text-slate-700 focus:outline-none">
                      <option>claude-sonnet-4-5 ✓</option>
                      <option>claude-opus-4-5</option>
                      <option>gpt-4o</option>
                    </select>
                  </Row>
                  <Row label="Temperature" sub="Độ sáng tạo khi sinh — cao hơn = đa dạng hơn">
                    <div className="flex items-center gap-2">
                      <input type="range" min="0" max="1" step="0.1" defaultValue="0.8" className="w-24 accent-blue-600" />
                      <span className="text-[12px] font-bold text-slate-700 w-6">0.8</span>
                    </div>
                  </Row>
                  <Row label="Số biến thể tối đa / lần" sub="Giới hạn số biến thể mỗi lần gọi API">
                    <select className="text-[11px] px-2.5 py-1.5 border border-slate-200 rounded-lg bg-slate-50 text-slate-700 focus:outline-none">
                      <option>5</option><option selected>10</option><option>20</option>
                    </select>
                  </Row>
                  <Row label="Tự động QA sau khi sinh" sub="Chạy kiểm định LaTeX và metadata tự động">
                    <Toggle on={autoQA} onToggle={() => setAutoQA((s) => !s)} />
                  </Row>
                  <Row label="Lưu lịch sử sinh" sub="Ghi lại tất cả biến thể vào log hệ thống">
                    <Toggle on={saveHistory} onToggle={() => setSaveHistory((s) => !s)} />
                  </Row>
                </div>
              </div>
            )}

            {/* QA tab */}
            {activeTab === "qa" && (
              <div className="max-w-2xl space-y-4">
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 flex items-start gap-2">
                  <AlertTriangle size={13} className="text-amber-600 mt-0.5 flex-shrink-0" />
                  <p className="text-[11px] text-amber-700">Thay đổi cấu hình QA sẽ ảnh hưởng đến tất cả lần quét tiếp theo. Các kết quả quét hiện tại không bị ảnh hưởng.</p>
                </div>
                <div className="bg-white border border-slate-100 rounded-xl p-4">
                  <p className="text-[12px] font-bold text-slate-700 mb-3">Cấu hình QA Rules</p>
                  <Row label="Tự động quét khi upload" sub="Chạy QA ngay sau khi file được ingested">
                    <Toggle on={latexVal} onToggle={() => setLatexVal((s) => !s)} />
                  </Row>
                  <Row label="Kiểm tra cú pháp LaTeX" sub="Validate LaTeX parser với KaTeX engine">
                    <Toggle on={deduplication} onToggle={() => setDeduplication((s) => !s)} />
                  </Row>
                  <Row label="Ngưỡng phát hiện trùng lặp" sub="Cosine similarity ngưỡng để coi là trùng">
                    <div className="flex items-center gap-2">
                      <input type="range" min="0.85" max="0.99" step="0.01" defaultValue="0.97" className="w-24 accent-blue-600" />
                      <span className="text-[12px] font-bold text-slate-700 w-8">0.97</span>
                    </div>
                  </Row>
                  <Row label="Gửi báo cáo qua email" sub="Nhận email tóm tắt kết quả QA hàng ngày">
                    <Toggle on={emailReport} onToggle={() => setEmailReport((s) => !s)} />
                  </Row>
                </div>
              </div>
            )}

            {/* Users tab */}
            {activeTab === "users" && (
              <div className="max-w-2xl space-y-4">
                <div className="flex items-center justify-between">
                  <p className="text-[12px] font-bold text-slate-700">{USERS.length} người dùng</p>
                  <button className="flex items-center gap-1.5 text-[11px] font-semibold text-blue-600 bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-lg hover:bg-blue-100 transition-all">
                    <Plus size={12} /> Thêm người dùng
                  </button>
                </div>
                <div className="space-y-2">
                  {USERS.map((u) => (
                    <div key={u.name} className="bg-white border border-slate-100 rounded-xl p-4 flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full flex items-center justify-center text-white text-[12px] font-bold flex-shrink-0"
                        style={{ background: u.color }}>
                        {u.avatar}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-[12px] font-semibold text-slate-700">{u.name}</p>
                        <p className="text-[10px] text-slate-400">{u.email}</p>
                      </div>
                      <span className="text-[10px] text-slate-400 mr-2">Hoạt động: {u.lastActive}</span>
                      <div className="flex items-center gap-2">
                        <select className={`text-[11px] font-semibold px-2.5 py-1.5 border rounded-lg focus:outline-none ${roleColor[u.role]}`}>
                          <option>Admin</option>
                          <option selected={u.role === "Editor"}>Editor</option>
                          <option selected={u.role === "Viewer"}>Viewer</option>
                        </select>
                        <button className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all">
                          <Edit3 size={12} />
                        </button>
                        <button className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all">
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* System tab */}
            {activeTab === "system" && (
              <div className="max-w-2xl space-y-4">
                <div className="bg-white border border-slate-100 rounded-xl p-4">
                  <p className="text-[12px] font-bold text-slate-700 mb-3">Thông tin hệ thống</p>
                  {[
                    ["Phiên bản", "v2.1.0"],
                    ["Vector database", "Qdrant 1.9.2"],
                    ["Backend", "FastAPI 0.111"],
                    ["Python runtime", "3.11.9"],
                    ["Dung lượng index", "2.4 GB / 50 GB"],
                    ["Cập nhật lần cuối", "07/05/2026"],
                  ].map(([k, v]) => (
                    <Row key={k} label={k}>
                      <code className="text-[11px] font-mono font-semibold text-slate-700 bg-slate-50 px-2 py-0.5 rounded">{v}</code>
                    </Row>
                  ))}
                </div>
                <div className="bg-white border border-slate-100 rounded-xl p-4">
                  <p className="text-[12px] font-bold text-slate-700 mb-3">Chế độ hệ thống</p>
                  <Row label="Maintenance Mode" sub="Tắt tất cả truy vấn từ người dùng thông thường">
                    <Toggle on={maintenanceMode} onToggle={() => setMaintenanceMode((s) => !s)} />
                  </Row>
                  <Row label="Developer Mode" sub="Bật log chi tiết và debug endpoints">
                    <Toggle on={devMode} onToggle={() => setDevMode((s) => !s)} />
                  </Row>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                  <p className="text-[12px] font-bold text-red-700 mb-1">Vùng nguy hiểm</p>
                  <p className="text-[11px] text-red-600 mb-3">Các thao tác này không thể hoàn tác. Hãy chắc chắn trước khi thực hiện.</p>
                  <div className="flex gap-2">
                    <button className="flex items-center gap-1.5 px-3 py-2 text-[11px] font-semibold text-red-700 border border-red-300 rounded-lg hover:bg-red-100 transition-all">
                      <RotateCcw size={12} /> Xóa toàn bộ cache
                    </button>
                    <button className="flex items-center gap-1.5 px-3 py-2 text-[11px] font-semibold text-white bg-red-600 rounded-lg hover:bg-red-700 transition-all">
                      <Trash2 size={12} /> Xóa toàn bộ corpus
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
