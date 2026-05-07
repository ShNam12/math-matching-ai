import { useState } from "react";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Sparkles, ChevronDown,
  ChevronRight, Plus, Edit3, Trash2, MoreHorizontal,
  TrendingUp, ArrowRight, Info, Tag, Database
} from "lucide-react";

const NAV = [
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy", active: true },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa", badge: 3 },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail" },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen" },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

const CHAPTERS = [
  {
    id: 1,
    title: "Chương 1: Giới hạn & Liên tục",
    total: 1240,
    topics: [
      { name: "Giới hạn dãy số", easy: 124, med: 86, hard: 42, skills: ["Tính toán", "Chứng minh"] },
      { name: "Giới hạn hàm số", easy: 98, med: 112, hard: 57, skills: ["Tính toán"] },
      { name: "Vô cùng lớn, vô cùng bé", easy: 76, med: 54, hard: 23, skills: ["Tính toán", "Chứng minh"] },
      { name: "Tính liên tục & điểm gián đoạn", easy: 63, med: 89, hard: 44, skills: ["Chứng minh"] },
      { name: "Định lý về hàm liên tục", easy: 45, med: 67, hard: 61, skills: ["Chứng minh", "Ứng dụng"] },
    ],
  },
  {
    id: 2,
    title: "Chương 2: Đạo hàm & Vi phân",
    total: 3456,
    topics: [
      { name: "Đạo hàm cơ bản", easy: 312, med: 198, hard: 67, skills: ["Tính toán"] },
      { name: "Đạo hàm hàm hợp (Chain rule)", easy: 156, med: 243, hard: 89, skills: ["Tính toán"] },
      { name: "Đạo hàm hàm ẩn", easy: 87, med: 134, hard: 98, skills: ["Tính toán", "Chứng minh"] },
      { name: "Đạo hàm cấp cao", easy: 67, med: 89, hard: 45, skills: ["Tính toán"] },
      { name: "Cực trị & khảo sát hàm số", easy: 87, med: 178, hard: 134, skills: ["Tính toán", "Ứng dụng"] },
      { name: "Quy tắc L'Hôpital", easy: 112, med: 145, hard: 78, skills: ["Tính toán"] },
      { name: "Vi phân & xấp xỉ tuyến tính", easy: 89, med: 112, hard: 34, skills: ["Tính toán", "Ứng dụng"] },
    ],
  },
  {
    id: 3,
    title: "Chương 3: Tích phân",
    total: 4891,
    topics: [
      { name: "Tích phân bất định cơ bản", easy: 445, med: 312, hard: 187, skills: ["Tính toán"] },
      { name: "Tích phân từng phần", easy: 178, med: 289, hard: 245, skills: ["Tính toán"] },
      { name: "Tích phân lượng giác", easy: 134, med: 167, hard: 98, skills: ["Tính toán"] },
      { name: "Tích phân xác định & Newton-Leibniz", easy: 289, med: 367, hard: 213, skills: ["Tính toán", "Chứng minh"] },
      { name: "Tích phân suy rộng", easy: 89, med: 134, hard: 167, skills: ["Tính toán", "Chứng minh"] },
      { name: "Tích phân bội đôi", easy: 76, med: 134, hard: 189, skills: ["Tính toán"] },
      { name: "Ứng dụng tích phân (diện tích, thể tích)", easy: 234, med: 178, hard: 67, skills: ["Ứng dụng"] },
    ],
  },
  {
    id: 4,
    title: "Chương 4: Chuỗi số & Chuỗi hàm",
    total: 3260,
    topics: [
      { name: "Chuỗi số cơ bản & tiêu chuẩn hội tụ", easy: 178, med: 234, hard: 145, skills: ["Tính toán", "Chứng minh"] },
      { name: "Chuỗi số Leibniz & hội tụ tuyệt đối", easy: 89, med: 134, hard: 167, skills: ["Chứng minh"] },
      { name: "Chuỗi lũy thừa & miền hội tụ", easy: 134, med: 178, hard: 145, skills: ["Tính toán"] },
      { name: "Chuỗi Taylor & Maclaurin", easy: 112, med: 167, hard: 134, skills: ["Tính toán", "Ứng dụng"] },
      { name: "Chuỗi Fourier", easy: 56, med: 112, hard: 189, skills: ["Tính toán", "Chứng minh"] },
    ],
  },
];

const skillColor = {
  "Tính toán": "bg-blue-50 text-blue-700 border-blue-200",
  "Chứng minh": "bg-purple-50 text-purple-700 border-purple-200",
  "Ứng dụng": "bg-teal-50 text-teal-700 border-teal-200",
};

export default function CalculusTaxonomy() {
  const [openChapters, setOpenChapters] = useState([1, 3]);
  const [selectedTopic, setSelectedTopic] = useState({ chapterId: 3, topicIdx: 1 });

  const toggleChapter = (id) =>
    setOpenChapters((prev) => prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]);

  const selTopic =
    selectedTopic &&
    CHAPTERS.find((c) => c.id === selectedTopic.chapterId)?.topics[selectedTopic.topicIdx];

  const totalAll = CHAPTERS.reduce((a, b) => a + b.total, 0);

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
          {NAV.map((item) => (
            <div key={item.id} className={`flex items-center gap-2.5 px-2.5 py-2 rounded-lg cursor-pointer transition-all ${item.active ? "bg-blue-50 ring-1 ring-blue-100" : "hover:bg-slate-50"}`}>
              <item.icon size={15} className={item.active ? "text-blue-600" : "text-slate-400"} strokeWidth={item.active ? 2.5 : 1.8} />
              <div className="flex-1 min-w-0">
                <p className={`text-[11px] font-semibold truncate ${item.active ? "text-blue-700" : "text-slate-500"}`}>{item.label}</p>
                <p className="text-[10px] text-slate-400 truncate">{item.sub}</p>
              </div>
              {item.badge && <span className="text-[10px] font-bold text-white bg-red-500 px-1.5 py-0.5 rounded-full">{item.badge}</span>}
            </div>
          ))}
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
        <header className="bg-white border-b border-slate-100 px-5 py-3 flex items-center justify-between flex-shrink-0">
          <div>
            <h1 className="text-sm font-bold text-slate-800">Calculus Taxonomy</h1>
            <p className="text-[11px] text-slate-400">Cây phân loại chủ đề Giải tích · {totalAll.toLocaleString()} bài tập</p>
          </div>
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-1.5 text-[11px] font-semibold text-blue-600 bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-lg hover:bg-blue-100 transition-all">
              <Plus size={12} /> Thêm chủ đề
            </button>
            <button className="relative p-2 rounded-lg hover:bg-slate-50 text-slate-400">
              <Bell size={14} />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
            </button>
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-[11px] font-bold">N</div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 flex gap-4">
          {/* Tree */}
          <div className="flex-1 min-w-0 space-y-2">
            {CHAPTERS.map((chapter) => {
              const isOpen = openChapters.includes(chapter.id);
              const chTotal = chapter.topics.reduce((a, t) => a + t.easy + t.med + t.hard, 0);
              return (
                <div key={chapter.id} className="bg-white border border-slate-100 rounded-xl overflow-hidden">
                  <div
                    onClick={() => toggleChapter(chapter.id)}
                    className="flex items-center gap-2.5 px-4 py-3 bg-slate-50 cursor-pointer hover:bg-slate-100 transition-all border-b border-slate-100">
                    {isOpen ? <ChevronDown size={14} className="text-slate-400" /> : <ChevronRight size={14} className="text-slate-400" />}
                    <BookOpen size={14} className="text-blue-600" />
                    <span className="text-[12px] font-bold text-slate-700 flex-1">{chapter.title}</span>
                    <span className="text-[10px] text-slate-500 bg-white border border-slate-200 px-2 py-0.5 rounded-full font-semibold">
                      {chTotal.toLocaleString()} bài
                    </span>
                    <div className="w-24 h-1.5 rounded-full bg-slate-200 overflow-hidden ml-2">
                      <div className="h-full rounded-full bg-blue-500" style={{ width: `${(chTotal / totalAll) * 100}%` }} />
                    </div>
                    <span className="text-[10px] text-slate-400 w-8 text-right">{Math.round((chTotal / totalAll) * 100)}%</span>
                  </div>
                  {isOpen && (
                    <div className="divide-y divide-slate-50">
                      {chapter.topics.map((topic, ti) => {
                        const isSelected = selectedTopic?.chapterId === chapter.id && selectedTopic?.topicIdx === ti;
                        const topTotal = topic.easy + topic.med + topic.hard;
                        return (
                          <div key={ti}
                            onClick={() => setSelectedTopic({ chapterId: chapter.id, topicIdx: ti })}
                            className={`flex items-center gap-3 px-4 py-2.5 cursor-pointer transition-all ${isSelected ? "bg-blue-50" : "hover:bg-slate-50"}`}>
                            <div className="w-1.5 h-1.5 rounded-full bg-slate-300 ml-4 flex-shrink-0" />
                            <span className={`text-[11px] font-medium flex-1 ${isSelected ? "text-blue-700" : "text-slate-600"}`}>{topic.name}</span>
                            <div className="flex items-center gap-1.5">
                              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">D {topic.easy}</span>
                              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">V {topic.med}</span>
                              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-red-50 text-red-700 border border-red-200">K {topic.hard}</span>
                              <span className="text-[10px] text-slate-400 ml-1 w-10 text-right">{topTotal}</span>
                            </div>
                            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100">
                              <button className="p-1 text-slate-400 hover:text-blue-600 rounded transition-all">
                                <Edit3 size={11} />
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Detail panel */}
          <div className="w-64 flex-shrink-0 space-y-3">
            {selTopic && (
              <>
                <div className="bg-blue-600 rounded-xl p-4 text-white">
                  <div className="flex items-center gap-1.5 mb-1">
                    <Info size={12} className="opacity-70" />
                    <span className="text-[10px] opacity-70 uppercase tracking-wider font-semibold">Chủ đề đang chọn</span>
                  </div>
                  <p className="text-[13px] font-bold leading-snug">{selTopic.name}</p>
                  <div className="mt-3 flex items-center gap-1">
                    <span className="text-[11px] opacity-70">Chương</span>
                    <ArrowRight size={10} className="opacity-50" />
                    <span className="text-[11px]">{CHAPTERS.find(c => c.id === selectedTopic.chapterId)?.title.split(":")[0]}</span>
                  </div>
                </div>

                {/* Stats */}
                <div className="bg-white border border-slate-100 rounded-xl p-4">
                  <p className="text-[11px] font-bold text-slate-700 mb-3">Phân bố độ khó</p>
                  {[
                    { label: "Dễ", val: selTopic.easy, color: "bg-emerald-500", total: selTopic.easy + selTopic.med + selTopic.hard },
                    { label: "Vừa", val: selTopic.med, color: "bg-amber-500", total: selTopic.easy + selTopic.med + selTopic.hard },
                    { label: "Khó", val: selTopic.hard, color: "bg-red-500", total: selTopic.easy + selTopic.med + selTopic.hard },
                  ].map((d) => (
                    <div key={d.label} className="mb-2">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[11px] text-slate-500">{d.label}</span>
                        <span className="text-[11px] font-bold text-slate-700">{d.val} <span className="text-slate-400 font-normal">({Math.round((d.val / d.total) * 100)}%)</span></span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
                        <div className={`h-full rounded-full ${d.color} transition-all`} style={{ width: `${(d.val / d.total) * 100}%` }} />
                      </div>
                    </div>
                  ))}
                  <div className="pt-2 border-t border-slate-100 mt-2">
                    <div className="flex justify-between">
                      <span className="text-[11px] text-slate-500">Tổng cộng</span>
                      <span className="text-[13px] font-bold text-blue-700">{selTopic.easy + selTopic.med + selTopic.hard}</span>
                    </div>
                  </div>
                </div>

                {/* Skills */}
                <div className="bg-white border border-slate-100 rounded-xl p-4">
                  <p className="text-[11px] font-bold text-slate-700 mb-2">Kỹ năng yêu cầu</p>
                  <div className="flex flex-wrap gap-1.5">
                    {selTopic.skills.map((s) => (
                      <span key={s} className={`text-[11px] font-semibold px-2.5 py-1 rounded-lg border ${skillColor[s]}`}>{s}</span>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="bg-white border border-slate-100 rounded-xl p-4 space-y-2">
                  <p className="text-[11px] font-bold text-slate-700 mb-2">Thao tác</p>
                  <button className="w-full flex items-center gap-2 px-3 py-2 text-[11px] font-semibold text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-all">
                    <Search size={12} /> Xem bài tập trong chủ đề
                  </button>
                  <button className="w-full flex items-center gap-2 px-3 py-2 text-[11px] font-semibold text-slate-600 bg-slate-50 border border-slate-200 rounded-lg hover:bg-slate-100 transition-all">
                    <Edit3 size={12} /> Chỉnh sửa thông tin
                  </button>
                  <button className="w-full flex items-center gap-2 px-3 py-2 text-[11px] font-semibold text-red-600 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-all">
                    <Trash2 size={12} /> Xoá chủ đề
                  </button>
                </div>
              </>
            )}

            {/* Global stats */}
            <div className="bg-white border border-slate-100 rounded-xl p-4">
              <p className="text-[11px] font-bold text-slate-700 mb-3">Tổng quan corpus</p>
              {[
                { label: "Tổng bài tập", val: totalAll.toLocaleString(), icon: Database },
                { label: "Số chủ đề", val: CHAPTERS.reduce((a, c) => a + c.topics.length, 0), icon: Tag },
                { label: "Cập nhật", val: "07/05/2026", icon: TrendingUp },
              ].map((s) => (
                <div key={s.label} className="flex items-center gap-2 py-1.5 border-b border-slate-50 last:border-0">
                  <s.icon size={12} className="text-slate-400" />
                  <span className="text-[11px] text-slate-500 flex-1">{s.label}</span>
                  <span className="text-[11px] font-bold text-slate-700">{s.val}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
