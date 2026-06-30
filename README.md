# Hệ thống nhận diện biển báo giao thông real-time

Hệ thống dùng webcam + YOLOv8 (ultralytics) để nhận diện biển báo giao thông
theo thời gian thực, hiển thị bounding box + tên + độ tin cậy, và tự động
lưu lại lịch sử nhận diện (ảnh + thông tin) ra thư mục `anh_lichsu/` và file
`lich_su_bien_bao.json`.

## Cấu trúc thư mục

```
he_thong_bien_bao/
├── best.pt                  # File training 
├── nhandien.py              # File chính: chạy webcam + YOLOv8 + hiển thị
├── lichsu.py                # Module quản lý lịch sử (thêm/lấy/in/lưu/đọc)
├── requirements.txt         # Danh sách thư viện cần cài
├── anh_lichsu/               # Thư mục tự động lưu ảnh biển báo đã nhận diện
└── lich_su_bien_bao.json     # File JSON lưu lịch sử (tự tạo khi chạy/khi thoát)
```

## 1. Cài đặt

Khuyến nghị tạo môi trường ảo (virtual environment) trước:

```bash
python -m venv venv
source venv/bin/activate        # Trên Windows: venv\Scripts\activate
```

Cài các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

> Lần chạy đầu tiên, `ultralytics` sẽ **tự động tải** file trọng số
> `yolov8n.pt` (~6MB) từ Internet, nên cần có kết nối mạng ở lần chạy đầu.

## 2. Chạy chương trình

```bash
python nhandien.py
```

- Cửa sổ video sẽ hiện lên, hiển thị hình ảnh từ webcam kèm bounding box
  cho các biển báo nhận diện được.
- Nhấn phím **`q`** để thoát chương trình. Khi thoát, lịch sử sẽ tự động
  được lưu vào `lich_su_bien_bao.json`.

### Đổi camera (nếu dùng webcam ngoài / USB)

Mở `nhandien.py`, tìm dòng:

```python
CHI_SO_CAMERA = 0
```

Đổi thành `1`, `2`,... tùy theo camera bạn muốn dùng (thử lần lượt nếu
không chắc index nào đúng).

## 3. Về model nhận diện (RẤT QUAN TRỌNG)

Mặc định, code dùng model YOLOv8 tổng quát (`yolov8n.pt`, huấn luyện trên
bộ dữ liệu COCO) để **chạy được ngay** mà không cần chuẩn bị gì thêm. Tuy
nhiên COCO **chỉ có 1 lớp liên quan tới biển báo** là `"stop sign"` (biển
STOP) — không có các lớp như biển giới hạn tốc độ, biển cấm, biển chỉ dẫn...

### Để nhận diện đầy đủ các loại biển báo giao thông, bạn nên:

1. **Tìm model có sẵn trên Roboflow Universe** (khuyến nghị nhanh nhất):
   - Truy cập https://universe.roboflow.com và tìm từ khóa
     `"traffic sign detection yolov8"`.
   - Nhiều project công khai cho phép tải về file trọng số `.pt` đã train
     sẵn theo định dạng YOLOv8 (qua nút "Download Dataset" → chọn format
     "YOLOv8" → có hướng dẫn deploy/tải weights).
   - Tải file `.pt` về, đặt vào thư mục `models/`, ví dụ
     `models/bien_bao_vn.pt`.

2. **Hoặc tự huấn luyện (fine-tune)** từ dataset như:
   - GTSRB (German Traffic Sign Recognition Benchmark)
   - Các bộ dữ liệu biển báo Việt Nam tự gắn nhãn bằng Roboflow/CVAT/LabelImg
lúc này chỉ cần đổi file ghi tên file đã huấn luyện được đưa vào 
DUONG_DAN_MODEL = "best.pt" 
ví dụ tên file đã huấn luyện tên là nhan_dien.pt
chỉ cần đổi trong đây thành DUONG_DAN_MODEL = "nhan_dien.pt"

## 4. Cấu hình có thể chỉnh trong `nhandien.py`

| Biến                      | Ý nghĩa                                              | Mặc định |
|---------------------------|-------------------------------------------------------|----------|
| `CHI_SO_CAMERA`           | Index webcam (0, 1, 2...)                              | `0`      |
| `CHIEU_RONG_KHUNG_HINH`   | Độ rộng khung hình webcam                              | `1280`   |
| `CHIEU_CAO_KHUNG_HINH`    | Độ cao khung hình webcam                               | `720`    |
| `DUONG_DAN_MODEL`         | Đường dẫn / tên model YOLOv8                           | `"yolov8n.pt"` |
| `CHI_LOC_CLASS_LIEN_QUAN` | Có lọc theo danh sách class liên quan hay không        | `True`   |
| `NGUONG_TIN_CAY`          | Ngưỡng confidence tối thiểu để lưu lại                 | `0.5`    |
| `THU_MUC_LUU_ANH`         | Thư mục lưu ảnh biển báo đã nhận diện                   | `"anh_lichsu"` |
| `LUU_CA_KHUNG_HINH`       | `True`: lưu cả khung hình; `False`: chỉ crop biển báo  | `False`  |

## 5. Module `lichsu.py` — dùng độc lập

```python
import lichsu

# Thêm 1 bản ghi mới
lichsu.them_lich_su("Biển báo dừng (Stop)", 0.92, "anh_lichsu/stop_001.jpg")

# Lấy toàn bộ lịch sử (list[dict])
ds = lichsu.lay_lich_su()

# In lịch sử ra console dạng bảng dễ đọc
lichsu.in_lich_su()

# Lưu / đọc lịch sử ra/từ file JSON
lichsu.luu_ra_file("lich_su_bien_bao.json")
lichsu.doc_tu_file("lich_su_bien_bao.json")
```

Cơ chế chống trùng lặp: nếu cùng một `ten_bien_bao` được thêm lại trong
vòng **3 giây** kể từ lần lưu trước đó, bản ghi mới sẽ **không** được lưu
(hàm `them_lich_su` trả về `False`). Có thể chỉnh hằng số
`KHOANG_CACH_TOI_THIEU_GIAY` ở đầu file `lichsu.py` nếu muốn thay đổi.

## 6. Một số lỗi thường gặp

- **"Không thể mở camera với index = 0"**: thử đổi `CHI_SO_CAMERA` sang
  giá trị khác (1, 2...), hoặc kiểm tra webcam có bị ứng dụng khác chiếm
  dụng không (Zoom, Teams, OBS...).
- **Chạy chậm / giật (FPS thấp)**: model `yolov8n.pt` đã là bản nhẹ nhất;
  nếu máy yếu, có thể giảm `CHIEU_RONG_KHUNG_HINH`/`CHIEU_CAO_KHUNG_HINH`
  xuống thấp hơn (vd 640x480).
- **Không nhận diện được biển báo nào ngoài "stop sign"**: đây là giới hạn
  của model COCO mặc định — xem mục 3 ở trên để dùng model chuyên biệt.


## Gợi ý thêm nếu không thể chạy và kết nối được với camera laptop, có thể sử dụng app IPwebcam 
Sau khi tải xong app mở app lên và sẽ nhìn thấy 3 chấm ở góc trên bên phải
Bấm vào sẽ thấy start server
Nhấn vào start server, sau khi mở cam lên nhìn xuống góc dưới sẽ thấy địa chỉ web ví dụ như (http://192.168.1.100:8080), đó là địa chỉ để kết nối tới webcam
Và quay lại hệ thống để mở và kết nối với wedcam từ vscode nhập dòng lệnh sau:
  - python nhandien.py --camera http://192.168.1.100:8080/video
còn nếu như sau khi dùng lệnh này vẫn không kết nối được thì có thể đổi sang lệnh khác
  - python nhandien.py --camera rtsp://192.168.1.6:8080/h264.sdp để biết được rõ cái này nằm ở đâu có thể rõ link lúc đầu của camera lên web sẽ thấy RTSP và link này nằm trong đấy