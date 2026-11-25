A. YÊU CẦU CỦA THẦY & TIÊU CHÍ CHẤM ĐIỂM

Video 10 điểm, tải lên GOOGLE DRIVE, cài đặt quyền CÔNG KHAI (Bất kỳ ai có liên kết đều có thể xem) dán link vào báo cáo.
LƯU Ý ĐẶC BIỆT TỪ ĐỀ BÀI (Trang 8): TUYỆT ĐỐI KHÔNG nộp link YouTube ("Do NOT submit a YouTube link").

1. Giao diện (5 điểm) - phải cho thấy RÕ:
   - Bàn cờ lưới N x N với tọa độ hàng/cột (A, B, C... 1, 2, 3...).
   - Thẻ bài ở 2 trạng thái: Thẻ úp (tên nhân vật, nghề nghiệp, avatar) và Thẻ ngửa (Criminal/Innocent, icon khiên/còng, manh mối).
   - Tô màu vùng của clue (Highlight): phân biệt rõ ô mục tiêu (target) và các vùng lân cận (region, region2).
   - Thanh trạng thái StatusBar phản hồi động các thông báo logic.
   - Các nút điều khiển: Hint, Step, Auto (chuyển Stop), Restart, Load, nút tròn '?' (How to Play), dãy 6 viên thuốc chọn nhanh màn 1..6.
   - Panel bên phải gồm 3 tab chuyển đổi: Clue (chi tiết clue), Trace (vết suy diễn), Metrics (chỉ số đo đạc).

2. Trình diễn tính năng (5 điểm):
   - Chơi tay (Manual Play): Gọi phán quyết Criminal / Innocent; Lật thẻ đúng; THỬ ĐOÁN MÒ bị chặn (phân biệt rõ NOT_PROVABLE và CONTRADICTED qua hoạt cảnh rung thẻ và nhãn dán).
   - Gợi ý (Hint Engine): Gợi ý 2 tầng theo đúng FAQ (sáng thẻ có thể suy luận được + viền hồng các thẻ chứa clue làm cơ sở).
   - Chạy Tác tử tự giải (Deductive Agent):
     * Giải từng bước (Step): nháy viền clue tiền đề -> lật thẻ -> ghi nhận vào Tab Trace.
     * Tự động giải (Auto-Solve): lật tuần tự nhịp nhàng tới khi hoàn thành -> hiện banner Solved.
     * Bảng đo đạc Tab Metrics: cập nhật thời gian thực số biến, số mệnh đề CNF, số lần gọi SAT, decisions, propagations, backtracks, runtime.
   - Chạy trên đủ 6 test cases chuẩn (2x 3x3, 2x 4x4, 2x 5x5); nạp file JSON tùy chọn bằng nút Load.
   - Thể hiện 2 Clue mở rộng (Extensions): PARITY (chẵn/lẻ) và COUNT_COMPARE (so sánh 2 vùng).
   - Demo trường hợp câu đố bị kẹt (STUCK): chứng minh Agent không đoán mò (theo đúng FAQ 13).

3. Bắt buộc có PHỤ ĐỀ hoặc THUYẾT MINH (tiếng Việt hoặc tiếng Anh).
4. FAQ: Thầy cho phép dùng mã nguồn game Clues By Sam thay thế (nhóm có trích dẫn); giải thích thuật toán chỉ cần liệt kê ngắn gọn; 6 test cases có nghiệm duy nhất; nút Load chọn file JSON; hỗ trợ map kẹt (STUCK) để demo.

Thời lượng: Đề quy định 5-10 phút. Đề xuất: 6-7 phút (đủ ý, súc tích, thầy không phải tua). Mục tiêu: 6.5 phút.

---

B. KỊCH BẢN TỪNG CẢNH

CẢNH 1 - Mở đầu
  Hình: Mở đầu ở màn 01 (puzzle_3x3_01). Di chuột nhẹ qua logo thám tử, tên câu đố, thanh Level Pills 1..6 và panel bên phải.
  Thuyết minh: "Kính chào thầy và các bạn! Đây là đồ án Griductive No-Guess Solver của nhóm, môn Nhập môn Trí tuệ Nhân tạo. Giao diện được xây dựng bằng Pygame, bộ giải SAT DPLL thuần Python kết hợp bộ mã hóa CNF tự động. Hệ thống phân tách độc lập giữa Game Engine giữ nghiệm ẩn và Deductive Agent chỉ nhìn thấy tri thức công khai, tuyệt đối không đoán mò. Nhóm có đủ 6 test case chuẩn chia 3 kích thước: 3x3, 4x4 và 5x5."

CẢNH 2 - Giới thiệu giao diện  [Giao diện - 5đ]
  Hình: Giữ màn 01. Bấm nút tròn '?' góc trên phải mở popup How to Play (để 2 giây rồi bấm đóng).
  Chỉ lần lượt: Tọa độ cột A-B-C, hàng 1-2-3; thẻ mở sẵn ban đầu A1 (Innocent); các thẻ úp còn lại (hiện tên, nghề nghiệp); thanh trạng thái StatusBar bên dưới; dãy nút Hint, Step, Auto, Restart, Load; và 3 tab Clue, Trace, Metrics ở panel bên phải.
  Thuyết minh: "Giao diện hiển thị rõ tọa độ hàng cột, thẻ mở sẵn mang manh mối công khai, và các thẻ úp mang danh tính nhân vật. Dưới lưới là thanh trạng thái và các nút điều khiển. Bên phải là bảng điều khiển 3 tab: xem chi tiết Clue, theo dõi vết suy luận Trace, và các chỉ số hiệu năng Metrics."

CẢNH 3 - Chơi tay: gọi phán quyết đúng và lật thẻ  [Tính năng - Manual Play]
  Hình: Click vào ô B1 -> popover hiện 2 nút Criminal và Innocent. Bấm chọn Innocent (hoặc phím I).
  Thẻ B1 thực hiện hoạt cảnh lật 3D (flip), chuyển sang màu xanh Innocent kèm icon khiên, mở ra clue mới của Bea. StatusBar báo CORRECT màu xanh.
  Thuyết minh: "Ở chế độ chơi tay, người chơi chọn thẻ để đưa ra phán quyết Criminal hoặc Innocent. Khi phán quyết được chứng minh đúng từ tri thức hiện tại, thẻ thực hiện hoạt ảnh lật 3D, ghi nhận kết quả và mở ra manh mối mới nạp vào Knowledge Base."

CẢNH 4 - Chơi tay: bắt lỗi đoán mò NOT_PROVABLE  [Tính năng - Không đoán mò]
  Hình: Click vào ô C3 (ô chưa đủ dữ kiện chứng minh). Popover hiện lên, bấm chọn Criminal (hoặc phím C).
  Thẻ C3 rung lắc sang hai bên (shake animation), xuất hiện nhãn cam 'Not provable'. Thẻ vẫn úp nguyên vẹn. StatusBar báo: 'NOT PROVABLE: Neither verdict is logically forced yet.'
  Thuyết minh: "Quy tắc cốt lõi của game là Không đoán mò. Khi em phán đoán một ô chưa đủ dữ kiện suy luận như C3, thẻ sẽ rung lắc cảnh báo, dán nhãn Not Provable và từ chối tiết lộ thông tin ẩn."

CẢNH 5 - Chơi tay: bắt lỗi mâu thuẫn CONTRADICTED  [Tính năng - Bắt mâu thuẫn]
  Hình: Click vào ô mà logic bắt buộc phải là Innocent, nhưng cố tình bấm chọn Criminal.
  Thẻ rung lắc, dán nhãn đỏ 'Contradicted'. StatusBar báo: 'CONTRADICTED: cannot be Criminal (the opposite is logically forced).'
  Thuyết minh: "Tương tự, nếu phán quyết đi ngược lại logic đã bị ép buộc, hệ thống lập tức bắt lỗi Contradicted với nhãn đỏ. Hệ thống phân biệt hoàn hảo giữa Not Provable và Contradicted đúng theo yêu cầu đề bài."

CẢNH 6 - Gợi ý Hint & Highlight vùng manh mối  [Tính năng - Hint & Clue Inspector]
  Hình: Bấm nút HINT (hoặc phím H). Ô tiếp theo có thể suy ra phát sáng viền ngọc kèm quầng sáng nhịp thở (pulse glow); các thẻ chứa clue làm cơ sở suy luận được viền màu hồng (hint_clue). StatusBar hướng dẫn rõ ràng.
  Sau đó, click vào một thẻ đã lật: Tab Clue bên phải hiện cấu trúc manh mối; trên bàn cờ tự động tô viền các ô mục tiêu (target) và ô vùng lân cận (region, region2), các ô không liên quan mờ nhẹ.
  Thuyết minh: "Bộ máy Hint gợi ý thông minh 2 tầng đúng chuẩn FAQ: vừa làm sáng thẻ có thể chứng minh tiếp theo bằng hiệu ứng nhịp thở viền ngọc, vừa viền hồng các thẻ chứa manh mối nguồn. Khi nhấp vào từng thẻ đã lật, Tab Clue hiển thị chi tiết câu nói, đồng thời bàn cờ tự động khoanh vùng trực quan các ô bị ảnh hưởng."
  (Dừng chuột 1-2 giây cho thầy nhìn rõ hiệu ứng viền hồng và viền ngọc nha Quang).

CẢNH 7 - Tác tử giải từng bước (Step) và Bảng vết Trace  [Tính năng - Step & Trace]
  Hình: Bấm nút STEP (hoặc phím Space) 2 đến 3 lần. Mỗi lần bấm: viền clue tiền đề nháy sáng xác nhận 0.35s -> thẻ lật mở 3D.
  Chuyển sang xem Tab TRACE ở cột phải: cuộn nhẹ cho thấy từng dòng: Step t, ô, phán quyết, based on clue_*, số truy vấn SAT.
  Thuyết minh: "Ở chế độ tự giải từng bước, mỗi lần bấm Step, Agent lập luận trên tri thức hiện có qua bộ giải DPLL phản chứng, nháy viền manh mối gốc và lật thẻ. Tab Deduction Trace ghi lại vết suy diễn minh bạch: bước mấy, ô nào, phán quyết gì, dựa vào clue nào và tốn bao nhiêu truy vấn SAT."

CẢNH 8 - Auto-Solve, Hoàn thành màn & Bảng Metrics  [Tính năng - Auto & Metrics]
  Hình: Bấm nút AUTO (nút chuyển sang Stop màu vàng). Các thẻ tự động giải và lật tuần tự nhịp nhàng (1.25s/thẻ).
  Khi ô cuối cùng lật xong -> banner SOLVED lướt vào giữa bàn cờ! Viên thuốc số 1 trên thanh tiêu đề đổi màu xanh hoàn thành.
  Chuyển sang Tab METRICS: chỉ chuột vào các dòng Primary vars, Aux vars, CNF clauses, SAT calls, Decisions, Propagations, Backtracks, Runtime.
  Thuyết minh: "Bấm Auto để Agent tự động giải toàn bộ bàn cờ. Tốc độ chuyển cảnh mượt mà giúp thầy dễ dàng kiểm chứng. Khi hoàn thành, banner Solved xuất hiện báo chiến thắng. Tab Metrics hiển thị đầy đủ các chỉ số thực nghiệm của thuật toán DPLL: biến chính, biến phụ, mệnh đề CNF, số lần phân nhánh, lan truyền đơn vị và thời gian chạy."

CẢNH 9 - Bộ 6 test cases, Nút Load & 2 Clue mở rộng  [Tính năng - 4x4, 5x5, Extensions]
  Hình: Bấm viên thuốc số 3 (chuyển sang màn 4x4: puzzle_4x4_01). Bấm Auto chạy vài bước lật nhanh.
  Bấm tiếp viên thuốc số 5 (chuyển sang màn 5x5: puzzle_5x5_01 - stress test 25 biến). Chỉ vào thẻ chứa clue mở rộng: PARITY (chẵn/lẻ) và COUNT_COMPARE (so sánh 2 vùng). Bấm Auto giải mượt mà trong vài giây.
  Sau đó, bấm nút LOAD (hoặc phím L) -> hộp thoại Windows mở ra thư mục data/ -> chọn puzzle_5x5_02 -> bấm Open để nạp. Bấm nút RESTART màu đỏ để đặt lại màn chơi về trạng thái ban đầu.
  Thuyết minh: "Nhóm chuẩn bị đủ 6 test case chuẩn có nghiệm duy nhất cho các kích thước 3x3, 4x4 và 5x5. Ở các màn lớn, nhóm tích hợp 2 Clue mở rộng là PARITY ràng buộc tính chẵn lẻ, và COUNT_COMPARE so sánh tương quan giữa 2 vùng. Màn 5x5 đóng vai trò kiểm thử áp lực stress test, thuật toán DPLL giải trọn vẹn 25 ô rất nhanh. Nút Load hỗ trợ nạp bất kỳ file JSON nào từ ổ đĩa và nút Restart cho phép chơi lại tức thì."

CẢNH 10 - Xử lý câu đố bị kẹt (STUCK) theo FAQ 13  [Tính năng - Điểm nhấn học thuật]
  Hình: Bấm Load, chọn file sample_3x3.json. Bấm Step 1-2 lần lật các ô suy luận được. Đến khi hết ô suy ra được, bấm tiếp Step.
  StatusBar đổi màu vàng cảnh báo: 'STUCK: Solver reached fixpoint; no further verdict is entailed.' Agent dừng lại, không lật bừa.
  Thuyết minh: "Bám sát câu hỏi 13 trong FAQ của thầy về trường hợp câu đố bị kẹt giữa chừng, nhóm nạp file sample_3x3. Khi tập tri thức đạt điểm bất động fixpoint và không còn ô nào bị ép buộc logic, Agent kiên quyết dừng lại và báo STUCK thay vì đoán mò. Điều này chứng minh tác tử tuân thủ 100% nguyên tắc No-Guess trung thực."

CẢNH 11 - Kết thúc
  Hình: Mở slide hoặc quay về toàn cảnh bàn cờ hoàn thành. Hiện thông tin nhóm, GitHub repo, file Report.
  Thuyết minh: "Tóm lại, hệ thống đã hoàn thành trọn vẹn cả 5 điểm giao diện và 5 điểm tính năng theo đúng yêu cầu đề bài và giải đáp FAQ của thầy. Chi tiết mã nguồn và bảng số liệu thực nghiệm đã được trình bày đầy đủ trong file Báo cáo. Nhóm chúng em xin cảm ơn thầy và quý thầy cô trợ giảng đã theo dõi!"
