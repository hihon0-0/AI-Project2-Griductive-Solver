# Griductive Solver — No-Guess Logic Deduction Game

> **Môn học**: Cơ sở Trí tuệ Nhân tạo (CSC14003) — Khoa Công nghệ Thông tin, Trường ĐH Khoa học Tự nhiên, ĐHQG-HCM.  
> **Đồ án 2 (Project 2)**: Propositional Logic, SAT Solver & Game Agent.  
> **Mục tiêu**: Xây dựng hệ thống hoàn chỉnh từ thuật toán **DPLL SAT Solver** thuần Python, bộ **Mã hóa Mệnh đề CNF** (Tseytin Transformation), **Game Engine** bảo mật nghiệm ẩn, **Tác tử suy luận No-Guess** (*Entailment via Refutation*), đến **Giao diện Đồ họa Pygame** tương tác với hoạt cảnh lật thẻ, gợi ý quầng sáng và cơ chế chống đoán mò.

---

## 📑 Bảng Mục lục
1. [Giới thiệu Dự án](#-giới-thiệu-dự-án)
2. [Cấu trúc Thư mục Repository](#-cấu-trúc-thư-mục-repository)
3. [Thành viên & Phân công Nhiệm vụ](#-thành-viên--phân-công-nhiệm-vụ)
4. [Nguyên lý Thuật toán & Điểm Nổi bật](#-nguyên-lý-thuật-toán--điểm-nổi-bật)
5. [Hướng dẫn Cài đặt & Khởi chạy](#-hướng-dẫn-cài-đặt--khởi-chạy)
6. [Hướng dẫn Chơi & Thao tác trên Giao diện GUI](#-hướng-dẫn-chơi--thao-tác-trên-giao-diện-gui)
7. [Kiểm thử Tự động (Automated Testing)](#-kiểm-thử-tự-động-automated-testing)

---

## 🌟 Giới thiệu Dự án

**Griductive** là trò chơi suy luận logic lấy cảm hứng từ *Clues by Sam*. Trên một bảng lưới kích thước $N \times N$ ($3\times3$, $4\times4$, $5\times5$), mỗi ô đại diện cho một nhân vật với thân phận bí mật là **Tội phạm (CRIMINAL)** hoặc **Vô tội (INNOCENT)**. 

* Khi một nhân vật được chứng minh thân phận chính xác, thẻ bài sẽ lật mở và tiết lộ một **Manh mối (Clue)**.
* **Nguyên lý Không đoán mò (No-Guess Principle)**: Người chơi hoặc Agent chỉ được phép đưa ra phán quyết khi và chỉ khi thân phận của nhân vật đó **được kéo theo một cách tất yếu về mặt logic** từ tập các manh mối đã biết. Mọi hành vi đoán mò đều bị hệ thống phát hiện và từ chối (`NOT_PROVABLE`).

---

## 📂 Cấu trúc Thư mục Repository

```text
AI-Project2-Griductive-Solver/
├── Source/                               # Toàn bộ mã nguồn chính của đồ án
│   ├── main.py                           # Điểm khởi chạy chính (Entry point)
│   ├── core/                             # Phân hệ Logic Mệnh đề & Solver
│   │   ├── dpll.py                       # [Trần Ngọc Thanh Tú] DPLL SAT Solver thuần Python
│   │   ├── solver_metrics.py             # [Trần Ngọc Thanh Tú] Bộ thu thập chỉ số hiệu năng
│   │   ├── encoder.py                    # [Phạm Nguyễn Quang Sáng] Bộ mã hóa CNF cho 8 loại Clue (Tseytin)
│   │   ├── clue_types.py                 # [Phạm Nguyễn Quang Sáng] Định nghĩa kiểu dữ liệu Clue & Region
│   │   └── semantics.py                  # [Phạm Nguyễn Quang Sáng] Hàm đánh giá chân trị trực tiếp
│   ├── engine/                           # Phân hệ Quản lý Trò chơi & Dữ liệu
│   │   ├── models.py                     # [Huỳnh Huy Hoàng] Data models: Cell, Character, Board, PublicState
│   │   ├── engine.py                     # [Huỳnh Huy Hoàng] GameEngine cách ly nghiệm ẩn, bắt lỗi NOT_PROVABLE
│   │   ├── region_helper.py              # [Huỳnh Huy Hoàng] Phân giải tọa độ các vùng: ROW, COL, NEIGHBORS
│   │   └── puzzle_io.py                  # [Huỳnh Huy Hoàng] Đọc/ghi và kiểm thực file JSON theo Schema
│   ├── agent/                            # Phân hệ Tác tử Suy luận Logic
│   │   ├── agent.py                      # [Trần Công Quang] DeductiveAgent: suy luận phản chứng KB ∧ ¬C ⊨ ⊥
│   │   ├── deduction_trace.py            # [Trần Công Quang] DeductionStep & vết suy diễn logic cho từng bước
│   │   ├── hint.py                       # [Trần Công Quang] Bộ sinh gợi ý (Hint Engine) tìm ô ép buộc kế tiếp
│   │   └── uniqueness.py                 # [Trần Công Quang] Kiểm tra nghiệm duy nhất qua Blocking Clause
│   ├── gui/                              # Phân hệ Giao diện Đồ họa & Hoạt cảnh
│   │   ├── app.py                        # [Trịnh Kim Mai] Ứng dụng Pygame chính (event loop, render, layout)
│   │   ├── session.py                    # [Trịnh Kim Mai] GameSession Facade kết nối GUI với Engine & Agent
│   │   ├── components.py                 # [Trịnh Kim Mai] Render bàn cờ, thẻ bài lật 3D, Popover, Side Panel
│   │   ├── theme.py                      # [Trịnh Kim Mai] Bảng màu chuẩn giao diện và typography
│   │   ├── avatars.py                    # [Trịnh Kim Mai] Trình sinh avatar đồ họa theo thuộc tính nhân vật
│   │   ├── clue_text.py                  # [Trịnh Kim Mai] Định dạng câu manh mối có màu nổi bật trực quan
│   │   ├── clue_utils.py                 # [Trịnh Kim Mai] Trích xuất vai trò các ô trong manh mối để highlight
│   │   └── assets/fonts/                 # Bộ phông chữ chuẩn mở OFL (Inter, Merriweather, JetBrains Mono)
│   └── tests/                            # Bộ kiểm thử tự động toàn diện (87 tests PASS)
│       ├── test_dpll.py                  # Test DPLL solver, đơn vị, quay lui, giả định (45 tests)
│       ├── test_encoder.py               # Test bộ mã hóa CNF cho các dạng manh mối (15 tests)
│       ├── test_semantics.py             # Test đánh giá chân trị các manh mối (4 tests)
│       ├── test_engine.py                # Test vòng đời GameEngine và verifier (4 tests)
│       ├── test_region_helper.py         # Test phân giải vùng không gian bàn cờ (6 tests)
│       ├── test_puzzle_io.py             # Test đọc/ghi và xác thực schema file JSON (3 tests)
│       ├── test_agent.py                 # Test Agent phân loại phản chứng, hint, uniqueness (10 tests)
│       ├── fakes.py                      # Mocks/Stubs độc lập dùng cho unit test
│       ├── smoke_session.py              # Smoke test tích hợp GameSession không cần mở cửa sổ
│       └── gui_test.py                   # Test kiểm thử headless toàn bộ flow GUI
├── data/                                 # Bộ dữ liệu 6 màn chơi chuẩn đồ án + màn mẫu
│   ├── puzzle_3x3_01.json                # Màn 3x3 #1 (Đạt Unique solution, 8 bước giải)
│   ├── puzzle_3x3_02.json                # Màn 3x3 #2 (Đạt Unique solution, 8 bước giải)
│   ├── puzzle_4x4_01.json                # Màn 4x4 #1 (Đạt Unique solution, 14 bước giải)
│   ├── puzzle_4x4_02.json                # Màn 4x4 #2 (Đạt Unique solution, 14 bước giải)
│   ├── puzzle_5x5_01.json                # Màn 5x5 #1 (Đạt Unique solution, 22 bước giải)
│   ├── puzzle_5x5_02.json                # Màn 5x5 #2 (Đạt Unique solution, 23 bước giải)
│   ├── sample_3x3.json                   # Màn mẫu 3x3 ban đầu
│   └── generate_all_puzzles.py           # Script sinh và chuẩn hóa bộ câu đố
├── schemas/                              # Định dạng chuẩn kiểm thực dữ liệu
│   └── puzzle_schema.json                # JSON Schema (Draft 2020-12)
├── tools/                                # Công cụ hỗ trợ phát triển
│   └── gen_puzzle.py                     # Thuật toán ngẫu nhiên sinh câu đố mới kèm kiểm tra Unique & Solvable
├── docs/                                 # Tài liệu đồ án và kế hoạch nhóm
│   ├── AI - Project 2.pdf                # Đề bài chính thức
│   ├── Report_Griductive_Solver.docx     # Báo cáo Word chuẩn thẻ tương tác Google Docs
│   └── generate_report_docx.py           # Script tự động tạo báo cáo Word
├── requirements.txt                      # Danh sách thư viện phụ thuộc
└── README.md                             # Tài liệu hướng dẫn sử dụng đồ án
```

---

## 👥 Thành viên & Phân công Nhiệm vụ

*(Danh sách được sắp xếp theo thứ tự **tăng dần MSSV**)*

| STT | MSSV | Họ và tên | Vai trò Kỹ thuật | Phân hệ phụ trách | Trách nhiệm chính |
| :---: | :---: | :--- | :--- | :--- | :--- |
| **1** | **24120132** | **Phạm Nguyễn Quang Sáng** | **CNF Encoder & Semantics** | `Source/core/encoder.py`<br>`Source/core/semantics.py` | Áp dụng biến đổi Tseytin mã hóa 8 loại Clue (6 cốt lõi + 2 mở rộng `PARITY`, `COUNT_COMPARE`) sang dạng chuẩn hội CNF. Ánh xạ biến `VariableMapper`. Xây dựng hàm đánh giá chân trị thực tế. |
| **2** | **24120152** | **Trần Ngọc Thanh Tú** | **Core DPLL Solver** | `Source/core/dpll.py`<br>`Source/core/solver_metrics.py` | Cài đặt thuật toán giải SAT DPLL thuần Python. Lan truyền đơn vị (Unit Propagation), triệt tiêu biến đơn cực (Pure Literal), quay lui (Backtracking) có hỗ trợ Assumptions. Đo đạc bộ chỉ số hiệu năng `SolverMetrics`. |
| **3** | **24120181** | **Huỳnh Huy Hoàng** *(Nhóm trưởng)* | **Game Engine & Datasets** | `Source/engine/*`<br>`data/*` | Thiết kế JSON Schema, phân giải vùng tọa độ `RegionHelper`, xây dựng `GameEngine` cách ly nghiệm ẩn, cơ chế chặn đoán mò. Thiết kế và thẩm định bộ 6 màn chơi chuẩn ($3\times3, 4\times4, 5\times5$). |
| **4** | **24120199** | **Trịnh Kim Mai** | **GUI & User Experience** | `Source/gui/*` | Giao diện đồ họa Pygame hoàn chỉnh. Cầu nối `GameSession`. Hiệu ứng lật thẻ bài 3D giả lập. Gợi ý quầng sáng ngọc đa lớp. Hoạt cảnh tự động giải từng bước. Bảng phụ Side Panel (Clue, Trace, Metrics). Dãy nút chọn nhanh màn chơi. |
| **5** | **24120221** | **Trần Công Quang** | **Deductive Logic Agent** | `Source/agent/*` | Tác tử suy diễn logic dựa trên phản chứng ($KB \land \neg C \models \bot$). Vòng lặp suy luận No-Guess. Ghi nhận vết suy luận `DeductionStep`. Kiểm tra nghiệm duy nhất `uniqueness.py`. Bộ sinh gợi ý `hint.py`. |

---

## 🧠 Nguyên lý Thuật toán & Điểm Nổi bật

### 1. Nguyên lý Suy diễn Phản chứng (Proof by Refutation)
Agent phân loại thân phận một ô $C_i$ bằng cách truy vấn Solver trên cơ sở tri thức công khai $\text{KB}_t$ kết hợp với giả định:
$$\text{KB}_t \land \neg C_i \models \bot \iff \text{DPLL}(\text{KB}_t \cup \{[\neg C_i]\}) = \text{UNSAT} \implies C_i = \text{CRIMINAL}$$
$$\text{KB}_t \land C_i \models \bot \iff \text{DPLL}(\text{KB}_t \cup \{[C_i]\}) = \text{UNSAT} \implies C_i = \text{INNOCENT}$$
$$\text{Cả hai đều SAT} \implies C_i = \text{UNKNOWN} \quad (\text{Chưa đủ cơ sở logic, kiên quyết KHÔNG đoán mò})$$

### 2. Biến đổi Tseytin & Bộ nhớ đệm Biến phụ (Auxiliary Variables Cache)
Để tránh bùng nổ cấp số nhân khi biến đổi các mệnh đề phức tạp (như đếm số lượng `EXACTLY`, `AT_LEAST`, `AT_MOST`, `PARITY`, so sánh vùng `COUNT_COMPARE`), bộ mã hóa sinh các biến phụ đại diện cho từng biểu thức con. Module Agent cài đặt `_clue_cache` theo `clue_id` nhằm đảm bảo các biến phụ không bị sinh lặp lại giữa các chu kỳ suy luận.

### 3. Kiểm tra Tính Duy nhất của Nghiệm (Uniqueness Check)
Sử dụng kỹ thuật **Mệnh đề chặn (Blocking Clause)**:
1. Giải bài toán với toàn bộ manh mối ban đầu, thu được mô hình nghiệm $M$. Nếu vô nghiệm ($\text{UNSAT}$) $\rightarrow$ Không có nghiệm.
2. Thêm mệnh đề chặn phủ định mô hình nghiệm nguyên thủy:
   $$\text{Blocking Clause} = \bigvee_{v \in \text{Primary}} (\neg M(v))$$
3. Giải lại hệ thức mới. Nếu kết quả là **UNSAT** $\rightarrow$ Bài toán chứng minh có **nghiệm duy nhất (UNIQUE)**. Nếu SAT $\rightarrow$ Tồn tại đa nghiệm (không đạt yêu cầu đồ án).
*Toàn bộ 6 màn chơi chính thức của nhóm đều đạt chứng nhận nghiệm duy nhất 100%.*

---

## 🚀 Hướng dẫn Cài đặt & Khởi chạy

### 1. Yêu cầu Hệ thống
* **Python**: Phiên bản 3.10 trở lên (Hỗ trợ tốt trên Python 3.10, 3.11, 3.12, 3.13, 3.14 trên Windows, Linux và macOS).

### 2. Cài đặt Thư viện Phụ thuộc
Mở terminal tại thư mục gốc của đồ án và thực thi:
```bash
pip install -r requirements.txt
```

> [!TIP]
> **Lưu ý dành cho Python 3.13 / 3.14 trên Windows**:  
> Nếu gặp khó khăn khi cài đặt gói `pygame` nguyên bản (do môi trường thiếu trình biên dịch C++ SDL), bạn có thể cài đặt gói thay thế hoàn toàn tương thích:
> ```bash
> pip install pygame-ce
> ```
> Gói `pygame-ce` cung cấp mã nhị phân có sẵn, tương thích 100% với toàn bộ mã nguồn của dự án mà không cần chỉnh sửa bất kỳ dòng lệnh nào.

### 3. Khởi chạy Trò chơi (GUI Game)
Khởi động ứng dụng đồ họa chính:
```bash
python Source/main.py
```
*(hoặc chạy trực tiếp `python Source/gui/app.py`)*

---

## 🎮 Hướng dẫn Chơi & Thao tác trên Giao diện GUI

```text
+-----------------------------------------------------------------------------------------+
| [LOGO] GRIDUCTIVE SOLVER       Level: (1) (2) (3) (4) (5) (6)           [?] How to play |
+------------------------------------------------------+----------------------------------+
|                                                      | [ Clue ] [ Trace ] [ Metrics ]   |
|                 BÀN CỜ LƯỚI THẺ BÀI                  | -------------------------------- |
|               (3x3, 4x4 hoặc 5x5)                    | Thẻ bên phải hiển thị chi tiết:  |
|                                                      | - Nội dung manh mối đang xem     |
|   - Thẻ úp: Màu xám đậm, avatar nhân vật mờ          | - Lịch sử từng bước suy luận     |
|   - CRIMINAL: Thẻ viền đỏ, nền hồng nhạt             | - Số liệu đo đạc SAT Solver:     |
|   - INNOCENT: Thẻ viền xanh lá, nền ngọc nhạt        |   + Biến chính & biến phụ Tseytin|
|   - Gợi ý (Hint): Quầng sáng xanh ngọc nhấp nháy     |   + Số mệnh đề CNF               |
|   - Căn cứ gợi ý: Viền hồng ở các thẻ liên quan      |   + Số lần gọi SAT               |
|                                                      |   + Propagations, Backtracks     |
|                                                      |   + Thời gian thực thi (ms)      |
+------------------------------------------------------+----------------------------------+
|  Thanh thông báo trạng thái: Thông báo lỗi, kết quả suy luận logic và gợi ý             |
+-----------------------------------------------------------------------------------------+
|   [ Hint ]       [ Step ]       [ Auto ]       [ Restart ]       [ Load JSON... ]       |
+-----------------------------------------------------------------------------------------+
```

* **Chơi bằng tay (Manual Play)**:
  * Click chuột trái vào một thẻ bài đang úp $\rightarrow$ Menu nhỏ (Popover) hiện lên.
  * Chọn **Criminal** hoặc **Innocent** theo suy đoán của bạn.
  * *Nếu lựa chọn có căn cứ chứng minh*: Thẻ lật mở, manh mối mới được tiết lộ.
  * *Nếu lựa chọn là đoán mò*: Thẻ bài rung lắc nhẹ, hiện nhãn đỏ `NOT PROVABLE` và hệ thống kiên quyết không lật thẻ.
* **Xem lại manh mối**: Click chuột trái vào bất kỳ thẻ bài nào đã lật để xem toàn văn manh mối ở tab **Clue** bên phải. Vùng ô liên quan trên bàn cờ sẽ được tô màu trực quan.
* **Nút Gợi ý (Hint)**: Giúp bạn tìm ra nước đi hợp lệ kế tiếp mà không làm mất tính thử thách của ván chơi.
* **Nút Bước kế tiếp (Step)**: Yêu cầu Agent thực hiện đúng 1 bước suy luận logic kế tiếp.
* **Nút Tự động giải (Auto)**: Agent tự động suy luận và mở từng thẻ cho đến khi phá đảo. Bấm lại để tạm dừng (**Stop**).
* **Nút Chơi lại (Restart)**: Khôi phục bàn cờ về trạng thái mở thẻ ban đầu.

---

## 🧪 Kiểm thử Tự động (Automated Testing)

Toàn bộ dự án được bảo vệ bằng hệ thống unit test và regression test nghiêm ngặt với **87 test case**:

```bash
python -m pytest Source/tests/ -v
```

Kết quả thực nghiệm chuẩn:
```text
============================= 87 passed in ~5.60s =============================
- Source/tests/test_agent.py          : 10/10 PASSED (Refutation, Trace, Hint, Uniqueness)
- Source/tests/test_dpll.py           : 45/45 PASSED (SAT/UNSAT, UnitProp, Backtrack, Metrics)
- Source/tests/test_encoder.py        : 15/15 PASSED (Tseytin CNF Transformation for 8 Clues)
- Source/tests/test_engine.py         :  4/4  PASSED (Game cycle, Entailment verifier)
- Source/tests/test_puzzle_io.py      :  3/3  PASSED (JSON IO & Schema validation)
- Source/tests/test_region_helper.py  :  6/6  PASSED (Row, Col, Neighbors, Explicit)
- Source/tests/test_semantics.py      :  4/4  PASSED (Direct evaluation verification)
```

Bạn cũng có thể chạy thử nghiệm headless kiểm thử luồng hoạt ảnh GUI:
```bash
python Source/tests/gui_test.py
```
Script sẽ tự động khởi chạy app không cần màn hình đồ họa và xuất hình ảnh kiểm chứng vào thư mục `shots/`.

---

## 📄 Bản quyền & Tài liệu Tham khảo
* **Trường**: Đại học Khoa học Tự nhiên, Đại học Quốc gia TP. Hồ Chí Minh.
* **Khoa**: Công nghệ Thông tin — Bộ môn Khoa học Máy tính.
* **Phông chữ đính kèm**: Cung cấp theo giấy phép chuẩn mở SIL Open Font License (OFL) bao gồm *Inter*, *Merriweather*, và *JetBrains Mono*.
