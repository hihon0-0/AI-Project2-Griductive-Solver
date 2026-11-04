# Griductive Solver — AI Project 2

> **Môn học**: Nhập môn Trí tuệ Nhân tạo (CSC14003) — Khoa Công nghệ Thông tin, Trường ĐH Khoa học Tự nhiên, ĐHQG-HCM.  
> **Mục tiêu**: Xây dựng thuật toán giải trò chơi logic **Griductive** hoàn toàn không đoán mò (**No-Guess Solver**) sử dụng Logic Mệnh đề, Mã hóa CNF và Thuật toán DPLL tự cài đặt.

---

## 📂 Cấu trúc Thư mục Repository

```text
AI-Project2-Griductive-Solver/
├── docs/                                 # Tài liệu đề bài và kế hoạch nhóm
│   ├── AI - Project 2.pdf                # Đề bài chính thức
│   ├── Griductive_Project_Plan_5Members.docx # File kế hoạch chi tiết (mở bằng Word / Google Docs)
│   └── create_plan_docx.py
├── schemas/                              # Định dạng chuẩn dữ liệu
│   └── puzzle_schema.json                # JSON Schema (Draft 2020-12) cho câu đố
├── data/                                 # Bộ dữ liệu 6 câu đố (2x 3x3, 2x 4x4, 2x 5x5)
│   ├── sample_3x3.json                   # File mẫu 3x3 hợp lệ
│   └── validate_sample.py                # Script kiểm tra hợp lệ với schema
├── Source/                               # Mã nguồn chính của đồ án
│   ├── main.py                           # Điểm khởi chạy chương trình (Entry point)
│   ├── core/                             # Module thuật toán logic (TV1 & TV2)
│   │   ├── dpll.py                       # [TV1] Bộ giải DPLL SAT Solver thuần Python
│   │   ├── solver_metrics.py             # [TV1] Bộ đo đạc chỉ số (decisions, backtracks, runtime)
│   │   ├── encoder.py                    # [TV2] Bộ mã hóa CNF cho 6 Clue cốt lõi & 2 Extensions
│   │   ├── clue_types.py                 # [TV2] Định nghĩa kiểu dữ liệu Clue & Region
│   │   └── semantics.py                  # [TV2] Direct Semantic Evaluators (kiểm tra trực tiếp)
│   ├── engine/                           # Module quản lý game & dữ liệu (TV3)
│   │   ├── models.py                     # [TV3] Các thực thể: Cell, Character, Board, GameState
│   │   ├── engine.py                     # [TV3] Game Engine (bảo mật nghiệm ẩn)
│   │   ├── region_helper.py              # [TV3] Xử lý tọa độ & các loại vùng
│   │   └── puzzle_io.py                  # [TV3] Đọc/ghi và kiểm tra file JSON câu đố
│   ├── agent/                            # Module tác tử suy diễn logic (TV4)
│   │   ├── agent.py                      # [TV4] Deductive Logic Agent (suy diễn phản chứng)
│   │   ├── deduction_trace.py            # [TV4] Nhật ký vết suy diễn (Deduction trace)
│   │   ├── uniqueness.py                 # [TV4] Kiểm tra tính duy nhất của nghiệm (Uniqueness check)
│   │   └── hint.py                       # [TV4] Bộ sinh gợi ý (Hint Engine)
│   ├── gui/                              # Module giao diện đồ họa & hoạt cảnh (TV5)
│   │   ├── app.py                        # [TV5] Ứng dụng GUI chính
│   │   └── components.py                 # [TV5] Renderer bàn cờ, thẻ lật/úp, highlight clue
│   └── tests/                            # Unit tests tự động cho từng module
│       ├── test_dpll.py
│       └── test_encoder.py
├── requirements.txt                      # Các thư viện phụ trợ
└── README.md
```

---

## 👥 Phân công Nhiệm vụ Nhóm 5 Người

| Thành viên | Phụ trách | Trách nhiệm chính |
| :--- | :--- | :--- |
| **Thành viên 1** | **Core DPLL Solver** | Cài đặt DPLL thuần Python, Unit Prop, Backtracking, Assumptions, đo đạc Metrics (`dpll.py`, `solver_metrics.py`). |
| **Thành viên 2** | **CNF & Semantics** | Mã hóa 6 Clue cơ bản + 2 Extensions sang CNF; viết 8 hàm Semantic Evaluator trực tiếp (`encoder.py`, `semantics.py`). |
| **Thành viên 3** | **Game Engine & Data** | Thiết kế JSON Schema, cấu trúc Board/Cell, Game Engine bảo mật nghiệm ẩn, xử lý `NOT_PROVABLE` / `CONTRADICTED` (`engine.py`, `puzzle_io.py`). |
| **Thành viên 4** | **Deductive Agent** | Tác tử suy diễn No-Guess (Entailment via Refutation), Deduction Trace, Uniqueness Check, Hint Engine (`agent.py`). |
| **Thành viên 5** | **GUI & Animation** | Giao diện đồ họa, Level Selector (6 màn), Chơi bằng tay (Manual Play), Highlight vùng clue, Hoạt cảnh Auto-Solve từng bước (`gui/app.py`). |

---

## 🚀 Hướng dẫn Cài đặt & Chạy Thử

1. **Cài đặt môi trường:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Kiểm tra tính hợp lệ của file JSON mẫu:**
   ```bash
   python data/validate_sample.py
   ```

3. **Chạy chương trình:**
   ```bash
   python Source/main.py
   ```
