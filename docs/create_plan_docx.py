import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_document():
    doc = docx.Document()
    
    # Page setup - Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Styles
    styles = doc.styles
    normal_style = styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Calibri'
    normal_font.size = Pt(11)
    normal_font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("KẾ HOẠCH TRIỂN KHAI DỰ ÁN CODE (PROJECT 2)\nGRIDUCTIVE SOLVER")
    run_title.font.name = 'Calibri'
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79) # Deep Blue

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(18)
    run_sub = p_sub.add_run("Môn: Nhập môn Trí tuệ Nhân tạo (CSC14003) — FIT - HCMUS\nPhân bổ nhiệm vụ nhóm 5 người & Thiết kế JSON Schema chuẩn")
    run_sub.font.name = 'Calibri'
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    def add_heading_1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        run = h.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(15)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        return h

    def add_heading_2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        run = h.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(12.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)
        return h

    # Section 1
    add_heading_1("1. NGUYÊN TẮC CỐT LÕI & MỤC TIÊU PHẦN CODE")
    doc.add_paragraph(
        "Kế hoạch này chỉ tập trung vào giai đoạn phát triển phần mềm (Code implementation) "
        "dành cho nhóm 5 sinh viên trong thời gian 3 tuần. Mục tiêu là xây dựng một hệ thống hoàn chỉnh "
        "đáp ứng 100% các tiêu chí kỹ thuật trong rubric chấm điểm của môn học:"
    )
    
    bullets = [
        ("No-guess Deduction: ", "Hệ thống chỉ được phép lật thẻ khi trạng thái nhân vật đã được chứng minh là hệ quả logic tất yếu (entailed by refutation) từ tập tri thức công khai KBt."),
        ("Độc lập kiến trúc (Separation of Concerns): ", "Logic Agent tuyệt đối không được đọc nghiệm ẩn hoặc manh mối chưa mở của Game Engine."),
        ("Tự xây dựng 100% Core Algorithms: ", "Bộ giải DPLL và CNF Encoder phải được lập trình thuần Python, không sử dụng các thư viện SAT ngoài (như PySAT, Z3,...)."),
        ("Bộ dữ liệu thử nghiệm chuẩn (FAQ): ", "Thiết kế và xác thực đúng 6 câu đố chuẩn JSON (2 map 3x3, 2 map 4x4, 2 map 5x5) có nghiệm duy nhất (Unique Solution)."),
        ("Trực quan hóa sinh động: ", "Giao diện GUI có tính năng highlight vùng ảnh hưởng của Clue và hiệu ứng chạy từng bước (Animation Auto-Solve) theo phản hồi FAQ của Giảng viên.")
    ]
    for b_title, b_desc in bullets:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        r_bold = p.add_run(b_title)
        r_bold.font.bold = True
        p.add_run(b_desc)

    # Section 2
    add_heading_1("2. BẢNG PHÂN BỔ NHIỆM VỤ CHI TIẾT (5 THÀNH VIÊN)")
    doc.add_paragraph(
        "Công việc được chia thành 5 module độc lập tương ứng với 5 tầng kiến trúc phần mềm, "
        "giúp mỗi thành viên có trách nhiệm cụ thể, code song song không xung đột:"
    )

    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    headers = ["Thành viên", "Phụ trách Module", "Nhiệm vụ Coding Cụ thể", "File / Deliverables"]
    col_widths = [Inches(1.0), Inches(1.5), Inches(3.0), Inches(1.3)]
    
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1F4E79")
        set_cell_margins(hdr_cells[i], top=120, bottom=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            r.font.size = Pt(10)

    members_data = [
        ("Thành viên 1\n(Algorithms Lead)", 
         "Core DPLL SAT Solver & Metrics", 
         "• Cài đặt thuật toán DPLL thuần Python (Unit Propagation, Conflict Detection, Backtracking).\n"
         "• Cơ chế chọn biến phân nhánh tiền định (Deterministic branching).\n"
         "• Hỗ trợ giải với giả định tạm thời (Assumptions) phục vụ bài toán phản chứng.\n"
         "• Bộ đo đếm số liệu: decisions, propagations, backtracks, runtime.\n"
         "• Viết unit tests kiểm thử độc lập cho DPLL.",
         "dpll.py\nsolver_metrics.py\ntest_dpll.py"),
         
        ("Thành viên 2\n(Logic & Math Lead)", 
         "CNF Encoder & Semantic Evaluators", 
         "• Variable Mapper: Ánh xạ 2 chiều Cell/Tên <-> ID biến logic.\n"
         "• Mã hóa CNF cho 6 Clue cơ bản (FACT, SAME, DIFFERENT, EXACTLY, AT_LEAST, AT_MOST) dùng Combinatorial Encoding.\n"
         "• Thiết kế & mã hóa CNF cho 2 Clue mở rộng (Parity & Count Compare).\n"
         "• Viết 8 hàm Direct Semantic Evaluator kiểm tra độc lập không qua CNF.\n"
         "• Báo cáo thống kê số biến chính, biến phụ và số clause.",
         "encoder.py\nclue_types.py\nsemantics.py\ntest_encoder.py"),

        ("Thành viên 3\n(Data & Engine Lead)", 
         "Game Engine & Puzzle Data", 
         "• Định nghĩa cấu trúc dữ liệu: Cell, Character, Clue, Region, Board.\n"
         "• Quản lý JSON Schema: Trình đọc, kiểm tra tính hợp lệ của file puzzle.\n"
         "• Region Helper: Xử lý chính xác danh sách ô cho Row, Col, Neighbors (8 hướng), Explicit List.\n"
         "• Game Engine: Quản lý trạng thái, giấu nghiệm ẩn.\n"
         "• Xử lý kiểm tra phán quyết: Trả về NOT_PROVABLE hoặc CONTRADICTED nếu người chơi gọi sai.",
         "models.py\nengine.py\nregion_helper.py\npuzzle_io.py"),

        ("Thành viên 4\n(Agent Lead)", 
         "Deductive Logic Agent & Pipeline", 
         "• Xây dựng Logic Agent tích hợp Encoder và DPLL.\n"
         "• Cơ chế phản chứng kiểm tra hệ quả logic: KB ∧ ¬C_i UNSAT -> CRIMINAL, KB ∧ C_i UNSAT -> INNOCENT.\n"
         "• Vòng lặp suy diễn No-Guess (Deduction Loop): Tìm ô bị ép buộc theo row-major order, lật thẻ tuần tự.\n"
         "• Module ghi nhận vết suy diễn (Deduction Trace logger).\n"
         "• Thuật toán Uniqueness Check (kiểm tra nghiệm duy nhất) & Hint Engine.",
         "agent.py\ndeduction_trace.py\nuniqueness.py\nhint.py"),

        ("Thành viên 5\n(Frontend / GUI Lead)", 
         "GUI Application & Animation", 
         "• Dựng giao diện đồ họa (Pygame / PyQt / Tkinter) chuẩn thẩm mỹ.\n"
         "• Hiển thị bàn cờ N x N, tọa độ A1.., thẻ úp/ngửa, tên, nghề nghiệp.\n"
         "• Tính năng Interactive Clue Highlight: Click vào clue thì đổi màu sáng vùng ô liên quan.\n"
         "• Menu chọn nhanh 6 màn chơi (Level Selector) và nút Restart.\n"
         "• Chế độ chơi bằng tay (Manual Play) có bắt lỗi.\n"
         "• Chế độ Auto-Solve có hoạt cảnh (Step-by-step Animation) từng bước lật thẻ.",
         "gui.py\nrenderer.py\nui_components.py\nassets/")
    ]

    for row_idx, data in enumerate(members_data):
        row = table.add_row()
        for c_idx, text in enumerate(data):
            cell = row.cells[c_idx]
            cell.text = text
            set_cell_margins(cell, top=100, bottom=100)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F2F2F2")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.size = Pt(9.5)

    for row in table.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = w

    # Section 3
    add_heading_1("3. CÔNG VIỆC PHỐI HỢP LIÊN THÀNH VIÊN (CROSS-FUNCTIONAL TASKS)")
    p_collab = doc.add_paragraph(
        "Ngoài nhiệm vụ độc lập, có 2 đầu việc quan trọng yêu cầu sự phối hợp chặt chẽ:"
    )
    collab_items = [
        ("Thiết kế & Thẩm định 6 Test Cases JSON (TV3 + TV4): ", 
         "TV3 soạn thảo cấu trúc 6 file JSON (2 bài 3x3, 2 bài 4x4, 2 bài 5x5). TV4 dùng module Uniqueness Check và Deduction Loop để chạy tự động, bảo đảm 100% cả 6 file đều có nghiệm duy nhất và giải được hoàn toàn bằng No-Guess."),
        ("Benchmark & Thu thập số liệu Thực nghiệm (TV1 + TV4): ", 
         "TV1 và TV4 phối hợp viết script benchmark.py để chạy toàn bộ 6 test cases, đo đếm 6 chỉ số bắt buộc (số biến, clauses, số lần gọi SAT, decisions, propagations, backtracks, reveal steps, runtime) và xuất kết quả ra file bảng biểu CSV/JSON.")
    ]
    for c_title, c_desc in collab_items:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        r_b = p.add_run(c_title)
        r_b.font.bold = True
        p.add_run(c_desc)

    # Section 4
    add_heading_1("4. HỢP ĐỒNG GIAO DIỆN & DỮ LIỆU (INTERFACE CONTRACTS)")
    doc.add_paragraph(
        "Để cả 5 thành viên lập trình song song mà không xung đột khi ghép nối, "
        "các hàm và kiểu dữ liệu sau đây được quy định là chuẩn bắt buộc:"
    )

    contracts = [
        ("1. Interface giữa TV1 (DPLL) và Hệ thống:",
         "def solve(clauses: list[list[int]], assumptions: list[int] = []) -> tuple[bool, dict[int, bool] | None, SolverMetrics]\n"
         "• Đầu vào: Danh sách các clause (mỗi clause là list các số nguyên khác 0), kèm list literal giả định.\n"
         "• Đầu ra: Tuple gồm (is_sat, model, metrics)."),

        ("2. Interface giữa TV2 (Encoder) và TV4 (Agent):",
         "def encode_clue(clue: Clue, var_map: VariableMapper) -> list[list[int]]:\n"
         "def evaluate_semantics(clue: Clue, assignment: dict[str, bool], region_cells: list[str]) -> bool:\n"
         "• Đảm bảo độc lập: Hàm evaluate_semantics không dùng bất kỳ logic CNF nào."),

        ("3. Interface giữa TV3 (Engine) và TV4 (Agent):",
         "class PublicState:\n"
         "    grid_size: int\n"
         "    revealed_verdicts: dict[str, str]   # {'A1': 'CRIMINAL', ...}\n"
         "    revealed_clues: list[Clue]\n"
         "    unsolved_cells: list[str]\n"
         "• Game Engine chỉ truyền PublicState cho Agent. Thuộc tính hidden_solution nằm trong phạm vi private của Engine."),

        ("4. Interface giữa TV4 (Agent) và TV5 (GUI):",
         "class DeductionStep:\n"
         "    step_number: int\n"
         "    cell_id: str\n"
         "    verdict: str                        # 'CRIMINAL' hoặc 'INNOCENT'\n"
         "    forced_by_clue_ids: list[str]\n"
         "    new_clue: Clue\n"
         "def get_solution_stream() -> Iterator[DeductionStep]:\n"
         "• Cho phép GUI lặp qua từng bước với hàm delay (timer) để tạo hoạt cảnh mượt mà.")
    ]

    for title, code_block in contracts:
        add_heading_2(title)
        p_code = doc.add_paragraph()
        p_code.paragraph_format.left_indent = Inches(0.2)
        p_code.paragraph_format.space_before = Pt(2)
        p_code.paragraph_format.space_after = Pt(6)
        r_c = p_code.add_run(code_block)
        r_c.font.name = 'Consolas'
        r_c.font.size = Pt(9.5)
        r_c.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    # Section 5
    add_heading_1("5. LỘ TRÌNH THỰC HIỆN THEO TUẦN (3-WEEK SPRINT)")
    
    sprints = [
        ("Tuần 1: Xây dựng Nền tảng Độc lập & Unit Tests", [
            "Cả nhóm: Thống nhất chuẩn JSON Schema và Interface Contracts.",
            "TV1: Hoàn thành lõi DPLL (Unit prop, conflict detection, backtrack) + viết unit test SAT/UNSAT.",
            "TV2: Hoàn thành Variable Mapper + mã hóa 6 Clue cơ bản + 6 Semantic Evaluator.",
            "TV3: Hoàn thành JSON Loader + Region Helper + cấu trúc Game State.",
            "TV4: Viết khung sườn Logic Agent và logic phản chứng trên dữ liệu giả lập (mock).",
            "TV5: Dựng cửa sổ GUI, hiển thị được lưới N x N tĩnh và tọa độ A1..C3."
        ]),
        ("Tuần 2: Tích hợp Logic, Mở rộng & Hoàn thiện Game Engine", [
            "TV1 + TV2: Ghép DPLL với CNF Encoder; triển khai 2 Clue mở rộng (Parity, Count Compare); tích hợp Metrics.",
            "TV3 + TV4: Ghép Game Engine với Logic Agent; hoàn thiện Deduction Loop (No-Guess) trên terminal.",
            "TV4: Cài đặt thuật toán Uniqueness Check và Hint Engine.",
            "TV3 + TV4: Tạo đủ 6 file test case JSON (2 map 3x3, 2 map 4x4, 2 map 5x5) và chạy verify nghiệm.",
            "TV5: Kết nối GUI với Game Engine: Chơi bằng tay (Manual Play), highlight vùng clue, cảnh báo lỗi NOT_PROVABLE / CONTRADICTED."
        ]),
        ("Tuần 3: Hoạt cảnh Animation, Benchmark, Tối ưu & Đóng gói", [
            "TV4 + TV5: Tích hợp chế độ Auto-Solve có hoạt cảnh (Step-by-step Animation) mượt mà trên GUI.",
            "TV5: Hoàn thiện thanh Level Selector (6 màn chơi) và nút Restart.",
            "TV1 + TV4: Chạy script benchmark.py trên 6 test cases, trích xuất toàn bộ bảng số liệu thực nghiệm.",
            "Cả nhóm: Kiểm thử chéo toàn diện, rà soát tránh lộ nghiệm ẩn (data leakage), đóng gói mã nguồn theo đúng cấu trúc thư mục quy định."
        ])
    ]

    for s_title, s_tasks in sprints:
        add_heading_2(s_title)
        for t in s_tasks:
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            p.add_run(t)

    # Section 6
    add_heading_1("6. THIẾT KẾ JSON SCHEMA CHO CÂU ĐỐ (PUZZLE SCHEMA)")
    doc.add_paragraph(
        "Mỗi câu đố được lưu dưới dạng một file JSON độc lập. "
        "File này bao gồm thông tin kích thước, tọa độ, nhân vật, trạng thái ẩn, "
        "manh mối sở hữu và danh sách các ô được lật sẵn ban đầu:"
    )

    sample_json_text = '''{
  "puzzle_id": "puzzle_3x3_01",
  "name": "Market Mystery",
  "size": 3,
  "initial_revealed": ["A1"],
  "grid": [
    {
      "id": "A1",
      "row": 1,
      "col": "A",
      "character": {"name": "Abel", "occupation": "Baker"},
      "hidden_status": "INNOCENT",
      "clue": {
        "id": "clue_A1",
        "type": "SAME",
        "params": {"target1": "B1", "target2": "C1"},
        "description": "Bea and Clara have the same status."
      }
    },
    {
      "id": "B1",
      "row": 1,
      "col": "B",
      "character": {"name": "Bea", "occupation": "Cook"},
      "hidden_status": "INNOCENT",
      "clue": {
        "id": "clue_B1",
        "type": "EXACTLY",
        "params": {
          "count": 1,
          "region": {"type": "NEIGHBORS", "cell": "B1"}
        },
        "description": "Exactly 1 neighbor of Bea is a Criminal."
      }
    }
  ]
}'''
    p_json = doc.add_paragraph()
    p_json.paragraph_format.left_indent = Inches(0.2)
    p_json.paragraph_format.space_after = Pt(8)
    r_j = p_json.add_run(sample_json_text)
    r_j.font.name = 'Consolas'
    r_j.font.size = Pt(9)
    r_j.font.color.rgb = RGBColor(0x22, 0x55, 0x22)

    doc.add_paragraph(
        "Chi tiết đầy đủ về toàn bộ các trường và cú pháp kiểm tra hợp lệ được đặc tả chi tiết "
        "trong file formal schema: puzzle_schema.json."
    )

    doc.save("Griductive_Project_Plan_5Members.docx")
    print("Document successfully created: Griductive_Project_Plan_5Members.docx")

if __name__ == '__main__':
    create_document()
