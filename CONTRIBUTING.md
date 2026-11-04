# Quy định Đóng góp & Chuẩn Git Commit (Conventional Commits)

Để đảm bảo lịch sử Git chuyên nghiệp, dễ theo dõi tiến độ và minh chứng rõ ràng đóng góp của từng thành viên trong Báo cáo (Report), toàn bộ nhóm thống nhất tuân thủ quy chuẩn **Conventional Commits**.

---

## 1. Cấu trúc một Commit Message

```text
<type>(<scope>): <mô tả ngắn gọn bằng tiếng Anh hoặc tiếng Việt không dấu>

[optional body: mô tả chi tiết lý do và thay đổi nếu cần]

[optional footer: liên kết issue hoặc ghi chú]
```

Ví dụ:
```text
feat(dpll): implement unit propagation and conflict detection
fix(engine): prevent data leakage of hidden solution to public state
test(encoder): add unit tests for EXACTLY and AT_LEAST clues
```

---

## 2. Các Loại Commit (`<type>`)

| Type | Ý nghĩa | Khi nào dùng? |
| :--- | :--- | :--- |
| **`feat`** | Tính năng mới (Feature) | Khi viết xong một hàm, một class, một chức năng mới |
| **`fix`** | Sửa lỗi (Bug fix) | Khi sửa một lỗi sai logic, thuật toán chạy sai kết quả |
| **`refactor`**| Tái cấu trúc mã nguồn | Khi dọn dẹp code, đổi tên hàm/biến, tối ưu cấu trúc mà không đổi logic |
| **`test`** | Kiểm thử (Testing) | Khi viết thêm hoặc sửa unit tests trong thư mục `tests/` |
| **`docs`** | Tài liệu (Documentation) | Khi sửa `README.md`, cập nhật file kế hoạch `.docx`, ghi chú hướng dẫn |
| **`perf`** | Tối ưu hiệu năng | Khi cải thiện tốc độ giải DPLL, giảm số lần phân nhánh |
| **`chore`** | Công việc phụ trợ | Khi thêm thư viện vào `requirements.txt`, sửa `.gitignore` |

---

## 3. Phạm vi Áp dụng (`<scope>`) theo Từng Thành viên

Mỗi thành viên khi commit module của mình nên gắn kèm scope tương ứng:

| Thành viên | Phụ trách | `<scope>` khuyến nghị |
| :--- | :--- | :--- |
| **TV1** | DPLL Solver & Metrics | `dpll`, `metrics`, `solver` |
| **TV2** | CNF Encoder & Semantics | `encoder`, `semantics`, `clues` |
| **TV3** | Game Engine & JSON Data | `engine`, `models`, `puzzle-io` |
| **TV4** | Logic Agent & Pipeline | `agent`, `uniqueness`, `trace`, `hint` |
| **TV5** | GUI & Animation | `gui`, `ui`, `animation` |
| **Cả nhóm** | Chung | `docs`, `config`, `tests`, `benchmark` |

---

## 4. Bảng Ví dụ Tham khảo Mẫu cho Nhóm

### Thành viên 1 (DPLL Solver):
* `feat(dpll): implement recursive backtracking with deterministic branching`
* `feat(metrics): track decisions, propagations and backtracks count`
* `fix(dpll): handle empty clause conflict during unit propagation`

### Thành viên 2 (CNF Encoder):
* `feat(encoder): add combinatorial CNF encoding for EXACTLY and AT_MOST`
* `feat(semantics): implement direct semantic evaluators for all 8 clue types`
* `test(encoder): verify equivalence between CNF clauses and semantic checks`

### Thành viên 3 (Game Engine):
* `feat(puzzle-io): implement schema validator for puzzle json files`
* `feat(engine): implement submit_verdict with NOT_PROVABLE and CONTRADICTED checks`
* `fix(engine): strictly isolate hidden_solution from get_public_state`

### Thành viên 4 (Deductive Agent):
* `feat(agent): implement refutation-based entailment check KB and not Ci`
* `feat(agent): add automated no-guess deduction loop`
* `feat(uniqueness): implement separate uniqueness check for full puzzle`

### Thành viên 5 (GUI & Animation):
* `feat(gui): render N x N grid with character cards and status colors`
* `feat(gui): implement interactive clue highlight on click`
* `feat(animation): add step-by-step delay animation for auto-solve mode`

---

## 5. Quy trình Làm việc với Nhánh (Git Workflow)

1. **Luôn kéo code mới nhất từ `main` trước khi làm**:
   ```bash
   git checkout main
   git pull origin main
   ```
2. **Tạo nhánh chức năng của mình**:
   ```bash
   git checkout -b feature/<tên-task>
   # Ví dụ: git checkout -b feature/dpll-unit-prop
   ```
3. **Commit đúng chuẩn**:
   ```bash
   git add .
   git commit -m "feat(dpll): implement unit propagation"
   ```
4. **Push nhánh lên GitHub và tạo Pull Request (PR)**:
   ```bash
   git push origin feature/<tên-task>
   ```
   *Nhóm duyệt PR xong mới merge vào `main`.*
