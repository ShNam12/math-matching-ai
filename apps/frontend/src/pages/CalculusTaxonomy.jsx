import { useEffect, useMemo, useRef, useState } from "react";
import { getTaxonomy, getTaxonomyStats } from "../services/taxonomyApi";
import { filterNavigationItems } from "../auth/navigation";
import UserMenu from "../components/UserMenu";
import {
  Hash, Upload, Search, BookOpen, CheckSquare, Bell,
  Settings, BarChart2, FileText, Sparkles, ChevronDown,
  ChevronRight, Plus, Edit3,
  TrendingUp, ArrowRight, Info, Tag, Database, LayoutDashboard
} from "lucide-react";

const NAV = [
  { icon: LayoutDashboard, label: "Dashboard", sub: "Tổng quan", id: "dashboard" },
  { icon: Upload, label: "Upload Document", sub: "Ingestion", id: "upload" },
  { icon: Search, label: "Semantic Search", sub: "Tìm kiếm", id: "search" },
  { icon: BookOpen, label: "Calculus Taxonomy", sub: "Phân loại", id: "taxonomy", active: true },
  { icon: CheckSquare, label: "QA Rules", sub: "Kiểm định", id: "qa" },
  { icon: FileText, label: "Chi tiết bài tập", sub: "Xem & Giải", id: "detail" },
  { icon: Sparkles, label: "Sinh biến thể", sub: "Gen AI", id: "gen" },
  { icon: BarChart2, label: "Analytics", sub: "Thống kê", id: "analytics" },
  { icon: Settings, label: "Cài đặt", sub: "System", id: "settings" },
];

const FALLBACK_CHAPTERS = [
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

// const skillColor = {
//   "Tính toán": "bg-blue-50 text-blue-700 border-blue-200",
//   "Chứng minh": "bg-purple-50 text-purple-700 border-purple-200",
//   "Ứng dụng": "bg-teal-50 text-teal-700 border-teal-200",
// };

export default function CalculusTaxonomy({
  activePage = "taxonomy",
  onNavigate = () => {},
  currentUser = null,
  onLogout = () => {},
  onOpenSearchWithFilters = () => {},
}) {
  const [openChapters, setOpenChapters] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [taxonomy, setTaxonomy] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedProblemType, setSelectedProblemType] = useState(null);
  const [taxonomyStats, setTaxonomyStats] = useState([]);
  const initializedTaxonomyView = useRef(false);

  useEffect(() => {
    let cancelled = false;

    async function loadTaxonomyData() {
      setLoading(true);
      setError(null);

      try {
        const [taxonomyData, statsData] = await Promise.all([
          getTaxonomy(),
          getTaxonomyStats(),
        ]);

        if (!cancelled) {
          setTaxonomy(taxonomyData);
          setTaxonomyStats(Array.isArray(statsData) ? statsData : []);
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(requestError.message || "Không tải được cây tri thức.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadTaxonomyData();

    return () => {
      cancelled = true;
    };
  }, []);

  const statsByProblemType = useMemo(() => {
    const map = new Map();

    taxonomyStats.forEach((item) => {
      if (item.problem_type_code) {
        map.set(item.problem_type_code, item.question_count || 0);
      }
    });

    return map;
  }, [taxonomyStats]);

  const chapters = (() => {
    if (!taxonomy?.chapters) {
      return FALLBACK_CHAPTERS;
    }

    return taxonomy.chapters.map((chapter) => {
      const topics = chapter.topics.map((topic) => {
        const problemTypes = topic.problem_types.map((problemType) => {
          const questionCount = statsByProblemType.get(problemType.code) || 0;

          return {
            code: problemType.code,
            name: problemType.display_name,
            description: problemType.description,
            aliases: problemType.aliases || [],
            skills: problemType.skills || [],
            defaultDifficulty: problemType.default_difficulty,
            positiveSignals: problemType.positive_signals || [],
            negativeSignals: problemType.negative_signals || [],
            examples: problemType.examples || [],
            questionCount,
          };
        });

        const total = problemTypes.reduce(
          (sum, problemType) => sum + problemType.questionCount,
          0,
        );

        return {
          code: topic.code,
          name: topic.display_name,
          description: topic.description,
          aliases: topic.aliases || [],
          skills: topic.skills || [],
          positiveSignals: topic.positive_signals || [],
          negativeSignals: topic.negative_signals || [],
          problemTypes,
          total,
        };
      });

      const total = topics.reduce((sum, topic) => sum + topic.total, 0);

      return {
        id: chapter.code,
        code: chapter.code,
        title: chapter.display_name,
        description: chapter.description,
        aliases: chapter.aliases || [],
        skills: chapter.skills || [],
        topics,
        total,
      };
    });
  })();

  useEffect(() => {
    if (
      !taxonomy?.chapters ||
      chapters.length === 0 ||
      initializedTaxonomyView.current
    ) {
      return;
    }

    initializedTaxonomyView.current = true;

    const firstChapter = chapters[0];
    const firstTopic = firstChapter.topics?.[0];

    setOpenChapters((current) =>
      current.length === 0 ? [firstChapter.code] : current
    );

    setSelectedTopic((current) => {
      if (!current && firstTopic) {
        return {
          chapterCode: firstChapter.code,
          topicCode: firstTopic.code,
        };
      }

      return current;
    });
  }, [taxonomy, chapters]);

  const toggleChapter = (id) =>
    setOpenChapters((prev) => prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]);

  const selectedChapter = selectedTopic
    ? chapters.find((chapter) => chapter.code === selectedTopic.chapterCode)
    : null;

  const selTopic = selectedChapter
    ? selectedChapter.topics.find((topic) => topic.code === selectedTopic.topicCode)
    : null;

  const totalAll = chapters.reduce((sum, chapter) => sum + chapter.total, 0);

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
          {filterNavigationItems(NAV, currentUser?.role).map((item) => {
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
          <UserMenu currentUser={currentUser} onLogout={onLogout} />
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
            {loading && (
              <div className="rounded-xl border border-blue-100 bg-blue-50 px-4 py-3 text-[12px] font-semibold text-blue-700">
                Đang tải cây tri thức Giải tích 1...
              </div>
            )}

            {error && (
              <div className="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-[12px] font-semibold text-red-700">
                {error}
              </div>
            )}

            {chapters.map((chapter) => {
              const isOpen = openChapters.includes(chapter.id);
              const chTotal = chapter.total;
              const chapterPercent = totalAll > 0 ? Math.round((chTotal / totalAll) * 100) : 0;
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
                      <div className="h-full rounded-full bg-blue-500" style={{ width: `${chapterPercent}%` }} />
                    </div>
                    <span className="text-[10px] text-slate-400 w-8 text-right">
                      {chapterPercent}%
                    </span>
                  </div>
                  {isOpen && (
                    <div className="divide-y divide-slate-50">
                      {chapter.topics.map((topic) => {
                        const isSelected =
                          selectedTopic?.chapterCode === chapter.code &&
                          selectedTopic?.topicCode === topic.code;

                        const topTotal = topic.total;
                        return (
                          <div
                            key={topic.code}
                            onClick={() => {
                              setSelectedTopic({
                                chapterCode: chapter.code,
                                topicCode: topic.code,
                              });
                              setSelectedProblemType(null);
                            }}
                            className={`cursor-pointer transition-all ${
                              isSelected ? "bg-blue-50" : "hover:bg-slate-50"
                            }`}
                          >
                            <div className="flex items-center gap-3 px-4 py-2.5">
                              <div className="w-1.5 h-1.5 rounded-full bg-slate-300 ml-4 flex-shrink-0" />

                              <div className="flex-1 min-w-0">
                                <p
                                  className={`text-[11px] font-medium truncate ${
                                    isSelected ? "text-blue-700" : "text-slate-600"
                                  }`}
                                >
                                  {topic.name}
                                </p>

                                {topic.code && (
                                  <p className="mt-0.5 text-[9px] font-mono text-slate-400 truncate">
                                    {topic.code}
                                  </p>
                                )}
                              </div>

                              <div className="flex items-center gap-1.5">
                                <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                                  {topic.problemTypes?.length || 0} dạng
                                </span>

                                <span className="text-[10px] text-slate-400 ml-1 w-10 text-right">
                                  {topTotal}
                                </span>
                              </div>

                              <button className="p-1 text-slate-400 hover:text-blue-600 rounded transition-all">
                                <Edit3 size={11} />
                              </button>
                            </div>

                            {isSelected && topic.problemTypes?.length > 0 && (
                              <div className="ml-8 mr-3 mb-2 space-y-1">
                                {topic.problemTypes.map((problemType) => (
                                  <button
                                    key={problemType.code}
                                    type="button"
                                    onClick={(event) => {
                                      event.stopPropagation();
                                      setSelectedTopic({
                                        chapterCode: chapter.code,
                                        topicCode: topic.code,
                                      });
                                      setSelectedProblemType(problemType);
                                    }}
                                    className={`w-full text-left rounded-lg px-2.5 py-1.5 text-[10px] transition-all ${
                                      selectedProblemType?.code === problemType.code
                                        ? "bg-blue-100 text-blue-700 font-semibold"
                                        : "text-slate-500 hover:bg-slate-100"
                                    }`}
                                  >
                                    <span>{problemType.name}</span>
                                    <span className="ml-2 text-slate-400">
                                      {problemType.questionCount} bài
                                    </span>
                                  </button>
                                ))}
                              </div>
                            )}
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
                    <span className="text-[10px] opacity-70 uppercase tracking-wider font-semibold">
                      {selectedProblemType ? "Dạng bài đang chọn" : "Chủ đề đang chọn"}
                    </span>
                  </div>

                  <p className="text-[13px] font-bold leading-snug">
                    {selectedProblemType?.name || selTopic.name}
                  </p>

                  <p className="mt-2 text-[10px] font-mono text-white/70 break-all">
                    {selectedProblemType?.code || selTopic.code}
                  </p>

                  <div className="mt-3 flex items-center gap-1">
                    <span className="text-[11px] opacity-70">Chương</span>
                    <ArrowRight size={10} className="opacity-50" />
                    <span className="text-[11px]">
                      {selectedChapter?.title?.split(":")[0] || "Chưa xác định"}
                    </span>
                  </div>
                </div>

                <div className="bg-white border border-slate-100 rounded-xl p-4">
                  <p className="text-[11px] font-bold text-slate-700 mb-2">Mô tả</p>
                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    {selectedProblemType?.description || selTopic.description || "Chưa có mô tả."}
                  </p>
                </div>

                <div className="bg-white border border-slate-100 rounded-xl p-4">
                  <p className="text-[11px] font-bold text-slate-700 mb-2">
                    Kỹ năng yêu cầu
                  </p>

                  <div className="flex flex-wrap gap-1.5">
                    {(selectedProblemType?.skills || selTopic.skills || []).length > 0 ? (
                      (selectedProblemType?.skills || selTopic.skills || []).map((skill) => (
                        <span
                          key={skill}
                          className="text-[11px] font-semibold px-2.5 py-1 rounded-lg border bg-blue-50 text-blue-700 border-blue-200"
                        >
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span className="text-[11px] text-slate-400">
                        Chưa khai báo kỹ năng.
                      </span>
                    )}
                  </div>
                </div>

                <div className="bg-white border border-slate-100 rounded-xl p-4">
                  <p className="text-[11px] font-bold text-slate-700 mb-2">
                    Dấu hiệu nhận diện
                  </p>

                  <div className="space-y-1">
                    {(selectedProblemType?.positiveSignals || selTopic.positiveSignals || []).length > 0 ? (
                      (selectedProblemType?.positiveSignals || selTopic.positiveSignals || [])
                        .slice(0, 5)
                        .map((signal) => (
                          <p key={signal} className="text-[10px] text-slate-500 leading-relaxed">
                            • {signal}
                          </p>
                        ))
                    ) : (
                      <p className="text-[10px] text-slate-400">
                        Chưa có dấu hiệu nhận diện.
                      </p>
                    )}
                  </div>
                </div>

                {selectedProblemType && (
                  <div className="bg-white border border-slate-100 rounded-xl p-4">
                    <p className="text-[11px] font-bold text-slate-700 mb-2">
                      Thông tin dạng bài
                    </p>

                    <div className="space-y-1.5">
                      <div className="flex justify-between gap-3">
                        <span className="text-[11px] text-slate-500">Độ khó mặc định</span>
                        <span className="text-[11px] font-bold text-slate-700">
                          {selectedProblemType.defaultDifficulty || "Chưa có"}
                        </span>
                      </div>

                      <div className="flex justify-between gap-3">
                        <span className="text-[11px] text-slate-500">Số câu đã match</span>
                        <span className="text-[11px] font-bold text-blue-700">
                          {selectedProblemType.questionCount || 0}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                <div className="bg-white border border-slate-100 rounded-xl p-4 space-y-2">
                  <p className="text-[11px] font-bold text-slate-700 mb-2">Thao tác</p>

                  <button
                    type="button"
                    onClick={() => {
                      onOpenSearchWithFilters({
                        chapter_code: selectedTopic?.chapterCode || null,
                        topic_code: selectedTopic?.topicCode || null,
                        problem_type_code: selectedProblemType?.code || null,
                        label: selectedProblemType?.name || selTopic?.name || "Bộ lọc taxonomy",
                      });
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-[11px] font-semibold text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-all"
                  >
                    <Search size={12} /> Xem bài tập trong mục này
                  </button>

                  <button className="w-full flex items-center gap-2 px-3 py-2 text-[11px] font-semibold text-slate-600 bg-slate-50 border border-slate-200 rounded-lg hover:bg-slate-100 transition-all">
                    <Edit3 size={12} /> Chỉnh sửa thông tin
                  </button>
                </div>
              </>
            )}

            {/* Global stats */}
            <div className="bg-white border border-slate-100 rounded-xl p-4">
              <p className="text-[11px] font-bold text-slate-700 mb-3">Tổng quan corpus</p>
                {[
                  {
                    label: "Tổng bài tập",
                    val: totalAll.toLocaleString(),
                    icon: Database,
                  },
                  {
                    label: "Số chủ đề",
                    val: chapters.reduce(
                      (sum, chapter) => sum + chapter.topics.length,
                      0,
                    ),
                    icon: Tag,
                  },
                  {
                    label: "Số dạng bài",
                    val: chapters.reduce(
                      (sum, chapter) =>
                        sum +
                        chapter.topics.reduce(
                          (topicSum, topic) => topicSum + (topic.problemTypes?.length || 0),
                          0,
                        ),
                      0,
                    ),
                    icon: Tag,
                  },
                  {
                    label: "Cập nhật",
                    val: taxonomy?.version || "1.0.0",
                    icon: TrendingUp,
                  },
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
