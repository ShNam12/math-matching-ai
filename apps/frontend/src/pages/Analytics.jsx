import { useState } from "react";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Sparkles,
  TrendingUp, TrendingDown, Database, Activity,
  FileText as FT, Zap, Users, Clock, Download,
  ArrowUpRight, ArrowDownRight, Minus, RefreshCw
} from "lucide-react";

const NAV = [
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy" },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa", badge: 3 },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail" },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen" },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics", active: true },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

const STATS = [
  { label: "Tổng bài tập", val: "12,847", delta: "+234", trend: "up", sub: "tuần này", icon: FT, color: "text-blue-600", bg: "bg-blue-50" },
  { label: "Tài liệu đã index", val: "1,203", delta: "+12", trend: "up", sub: "tháng này", icon: Database, color: "text-indigo-600", bg: "bg-indigo-50" },
  { label: "Truy vấn / ngày", val: "3,891", delta: "+18%", trend: "up", sub: "so hôm qua", icon: Activity, color: "text-teal-600", bg: "bg-teal-50" },
  { label: "Biến thể đã sinh", val: "4,210", delta: "-3%", trend: "down", sub: "tuần này", icon: Zap, color: "text-purple-600", bg: "bg-purple-50" },
  { label: "Người dùng", val: "8", delta: "0", trend: "flat", sub: "không thay đổi", icon: Users, color: "text-slate-600", bg: "bg-slate-50" },
  { label: "Uptime hệ thống", val: "99.97%", delta: "", trend: "up", sub: "30 ngày qua", icon: Clock, color: "text-emerald-600", bg: "bg-emerald-50" },
];

// Bar chart data — truy vấn 7 ngày
const QUERY_TREND = [
  { day: "01/05", val: 2840 },
  { day: "02/05", val: 3120 },
  { day: "03/05", val: 2980 },
  { day: "04/05", val: 3450 },
  { day: "05/05", val: 3200 },
  { day: "06/05", val: 3670 },
  { day: "07/05", val: 3891 },
];
const MAX_QUERY = Math.max(...QUERY_TREND.map((d) => d.val));

// Horizontal bars — topic breakdown
const TOPIC_DATA = [
  { label: "Tích phân", val: 4891, color: "bg-blue-500", pct: 38 },
  { label: "Đạo hàm", val: 3456, color: "bg-indigo-500", pct: 27 },
  { label: "Chuỗi số", val: 3260, color: "bg-purple-500", pct: 25 },
  { label: "Giới hạn", val: 1240, color: "bg-teal-500", pct: 10 },
];

// Difficulty donut data
const DIFF_DATA = [
  { label: "Dễ", pct: 50, color: "#22c55e", light: "bg-emerald-500" },
  { label: "Vừa", pct: 34, color: "#f59e0b", light: "bg-amber-500" },
  { label: "Khó", pct: 16, color: "#ef4444", light: "bg-red-500" },
];

const LOGS = [
  { time: "07/05 14:32", action: "Upload", user: "Nguyễn V.An", detail: "Calculus_VNU.tex — 312 trang", status: "processing" },
  { time: "07/05 13:17", action: "Sinh biến thể", user: "Trần M.Đức", detail: "∫x²eˣdx → 3 biến thể mới", status: "done" },
  { time: "07/05 11:45", action: "QA Scan", user: "System", detail: "Quét toàn corpus — 36 vấn đề phát hiện", status: "done" },
  { time: "07/05 09:22", action: "Search", user: "Lê T.Hương", detail: "\"chuỗi hội tụ tiêu chuẩn\" — 18 kết quả", status: "done" },
  { time: "06/05 16:10", action: "Upload", user: "Nguyễn V.An", detail: "HUST_Giai_tich_2_2023.pdf — 521 trang", status: "done" },
  { time: "06/05 14:05", action: "Export", user: "Trần M.Đức", detail: "Export 45 bài tích phân từng phần → LaTeX", status: "done" },
];

// Simple Donut SVG
function Donut({ data }) {
  let offset = 0;
  const r = 34;
  const circ = 2 * Math.PI * r;
  return (
    <svg viewBox="0 0 80 80" className="w-20 h-20">
      {data.map((d, i) => {
        const dash = (d.pct / 100) * circ;
        const gap = circ - dash;
        const el = (
          <circle key={i} cx="40" cy="40" r={r}
            fill="none" stroke={d.color} strokeWidth="12"
            strokeDasharray={`${dash} ${gap}`}
            strokeDashoffset={-offset}
            transform="rotate(-90 40 40)" />
        );
        offset += dash;
        return el;
      })}
      <text x="40" y="37" textAnchor="middle" fontSize="9" fill="#1e293b" fontWeight="700">12,847</text>
      <text x="40" y="47" textAnchor="middle" fontSize="6.5" fill="#94a3b8">bài tập</text>
    </svg>
  );
}

export default function Analytics({ activePage = "analytics", onNavigate = () => {} }) {
  const [period, setPeriod] = useState("7d");

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
            <h1 className="text-sm font-bold text-slate-800">Analytics</h1>
            <p className="text-[11px] text-slate-400">Thống kê & hoạt động hệ thống · Cập nhật 07/05/2026 15:00</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex rounded-lg overflow-hidden border border-slate-200">
              {[["7d","7 ngày"],["30d","30 ngày"],["all","Tất cả"]].map(([v,l])=>(
                <button key={v} onClick={()=>setPeriod(v)}
                  className={`text-[11px] px-2.5 py-1.5 transition-all ${period===v?"bg-blue-600 text-white font-semibold":"bg-white text-slate-500 hover:bg-slate-50"}`}>{l}</button>
              ))}
            </div>
            <button className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-600 border border-slate-200 px-2.5 py-1.5 rounded-lg hover:bg-slate-50">
              <Download size={12} /> Xuất báo cáo
            </button>
            <button className="p-2 text-slate-400 hover:bg-slate-50 rounded-lg relative">
              <Bell size={14} />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
            </button>
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-[11px] font-bold">N</div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Stats grid */}
          <div className="grid grid-cols-6 gap-3">
            {STATS.map((s, i) => (
              <div key={i} className="bg-white border border-slate-100 rounded-xl p-3">
                <div className={`w-7 h-7 rounded-lg ${s.bg} flex items-center justify-center mb-2`}>
                  <s.icon size={14} className={s.color} />
                </div>
                <p className="text-[10px] text-slate-400 leading-tight mb-0.5">{s.label}</p>
                <p className="text-[16px] font-bold text-slate-800 leading-none">{s.val}</p>
                {s.delta && (
                  <div className="flex items-center gap-0.5 mt-1">
                    {s.trend === "up" && <ArrowUpRight size={10} className="text-emerald-500" />}
                    {s.trend === "down" && <ArrowDownRight size={10} className="text-red-500" />}
                    {s.trend === "flat" && <Minus size={10} className="text-slate-400" />}
                    <span className={`text-[10px] font-semibold ${s.trend==="up"?"text-emerald-600":s.trend==="down"?"text-red-600":"text-slate-400"}`}>{s.delta}</span>
                    <span className="text-[10px] text-slate-400 ml-0.5">{s.sub}</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Charts row */}
          <div className="grid grid-cols-3 gap-3">
            {/* Query trend */}
            <div className="col-span-2 bg-white border border-slate-100 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <p className="text-[12px] font-bold text-slate-700">Truy vấn theo ngày</p>
                <span className="text-[10px] text-slate-400">7 ngày gần nhất</span>
              </div>
              <div className="flex items-end gap-2 h-28">
                {QUERY_TREND.map((d, i) => {
                  const h = Math.round((d.val / MAX_QUERY) * 100);
                  const isToday = i === QUERY_TREND.length - 1;
                  return (
                    <div key={i} className="flex-1 flex flex-col items-center gap-1.5">
                      <span className="text-[9px] text-slate-400 font-semibold">{d.val.toLocaleString()}</span>
                      <div className="w-full rounded-t-md transition-all"
                        style={{ height: `${h}%`, background: isToday ? "#2563eb" : "#bfdbfe" }} />
                      <span className="text-[9px] text-slate-400">{d.day}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Donut */}
            <div className="bg-white border border-slate-100 rounded-xl p-4">
              <p className="text-[12px] font-bold text-slate-700 mb-3">Phân bố độ khó</p>
              <div className="flex items-center gap-3">
                <Donut data={DIFF_DATA} />
                <div className="space-y-2 flex-1">
                  {DIFF_DATA.map((d) => (
                    <div key={d.label}>
                      <div className="flex justify-between mb-0.5">
                        <span className="text-[11px] text-slate-500">{d.label}</span>
                        <span className="text-[11px] font-bold text-slate-700">{d.pct}%</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-slate-100 overflow-hidden">
                        <div className={`h-full rounded-full ${d.light}`} style={{ width: `${d.pct}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Topic breakdown + Activity log */}
          <div className="grid grid-cols-2 gap-3">
            {/* Topic */}
            <div className="bg-white border border-slate-100 rounded-xl p-4">
              <p className="text-[12px] font-bold text-slate-700 mb-3">Bài tập theo chủ đề</p>
              <div className="space-y-3">
                {TOPIC_DATA.map((t) => (
                  <div key={t.label}>
                    <div className="flex justify-between mb-1">
                      <span className="text-[11px] text-slate-600 font-medium">{t.label}</span>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[11px] font-bold text-slate-700">{t.val.toLocaleString()}</span>
                        <span className="text-[10px] text-slate-400">({t.pct}%)</span>
                      </div>
                    </div>
                    <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                      <div className={`h-full rounded-full ${t.color} transition-all`} style={{ width: `${t.pct}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Activity log */}
            <div className="bg-white border border-slate-100 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <p className="text-[12px] font-bold text-slate-700">Hoạt động gần đây</p>
                <button className="text-[10px] text-blue-500 hover:text-blue-700 font-medium">Xem tất cả →</button>
              </div>
              <div className="space-y-0">
                {LOGS.map((log, i) => (
                  <div key={i} className="flex items-start gap-2.5 py-2 border-b border-slate-50 last:border-0">
                    <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${log.status === "done" ? "bg-emerald-500" : "bg-amber-400"}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-[11px] font-semibold text-slate-700">{log.action}</span>
                        <span className="text-[10px] text-slate-400">— {log.user}</span>
                      </div>
                      <p className="text-[10px] text-slate-500 truncate">{log.detail}</p>
                    </div>
                    <span className="text-[10px] text-slate-400 flex-shrink-0">{log.time.split(" ")[1]}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
