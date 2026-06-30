import argparse
import os
import time
from datetime import datetime

import cv2
from ultralytics import YOLO

import lichsu  

CHI_SO_CAMERA = 1

CHIEU_RONG_KHUNG_HINH = 1280
CHIEU_CAO_KHUNG_HINH = 720

DUONG_DAN_MODEL = "best.pt"

CHI_LOC_CLASS_LIEN_QUAN = False
CAC_CLASS_BIEN_BAO_LIEN_QUAN = {
    "stop sign",
    "traffic light",  
}

NGUONG_TIN_CAY = 0.5  
THU_MUC_LUU_ANH = "anh_lichsu"
LUU_CA_KHUNG_HINH = False  



def chuan_bi_thu_muc_luu_anh(thu_muc):
    if not os.path.exists(thu_muc):
        os.makedirs(thu_muc)
        print(f"[nhandien] Đã tạo thư mục lưu ảnh: '{thu_muc}/'")


def tai_model(duong_dan_model):
    print(f"[nhandien] Đang tải model: {duong_dan_model} ...")
    model = YOLO(duong_dan_model)
    print("[nhandien] Tải model thành công!")
    print(f"[nhandien] Danh sách class của model: {list(model.names.values())}")
    return model


def mo_webcam(nguon_camera, chieu_rong, chieu_cao):
    if isinstance(nguon_camera, str) and nguon_camera.isdigit():
        nguon_camera = int(nguon_camera)

    la_camera_mang = isinstance(nguon_camera, str)

    if la_camera_mang:
        print(f"[nhandien] Đang kết nối camera qua mạng: {nguon_camera}")
        cap = cv2.VideoCapture(nguon_camera, cv2.CAP_FFMPEG)
    else:
        print(f"[nhandien] Đang kết nối camera USB/laptop, index={nguon_camera}")
        cap = cv2.VideoCapture(nguon_camera)

    if not cap.isOpened():
        if la_camera_mang:
            print(f"[LỖI] Không thể mở luồng video từ URL: {nguon_camera}")
            print("      -> Kiểm tra lại các điều sau:")
            print("         1. Điện thoại/camera và máy tính có đang cùng mạng WiFi không?")
            print("         2. App IP Webcam trên điện thoại đã bấm 'Start server' chưa?")
            print("         3. URL có đúng định dạng không, vd: http://192.168.1.6:8080/video")
            print("            (chú ý phải có '/video' ở cuối đối với app IP Webcam).")
            print("         4. Thử mở thẳng URL đó bằng trình duyệt trên máy tính xem có ra hình không.")
        else:
            print(f"[LỖI] Không thể mở camera với index = {nguon_camera}.")
            print("      -> Hãy thử đổi --camera (hoặc CHI_SO_CAMERA trong file) thành 0, 1, 2...")
        return None

    if not la_camera_mang:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, chieu_rong)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, chieu_cao)

    print(f"[nhandien] Đã kết nối camera thành công: {nguon_camera}")
    return cap


def la_class_lien_quan(ten_class):
    if not CHI_LOC_CLASS_LIEN_QUAN:
        return True
    return ten_class.lower() in CAC_CLASS_BIEN_BAO_LIEN_QUAN


def ve_bounding_box(khung_hinh, x1, y1, x2, y2, ten_class, do_tin_cay):
    mau_xanh_la = (0, 200, 0)
    mau_trang = (255, 255, 255)
    cv2.rectangle(khung_hinh, (x1, y1), (x2, y2), mau_xanh_la, 2)

    nhan = f"{ten_class}: {do_tin_cay:.2f}"
    (chu_rong, chu_cao), _ = cv2.getTextSize(nhan, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(
        khung_hinh,
        (x1, max(0, y1 - chu_cao - 10)),
        (x1 + chu_rong + 6, y1),
        mau_xanh_la,
        -1,  
    )
    cv2.putText(
        khung_hinh,
        nhan,
        (x1 + 3, max(15, y1 - 5)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        mau_trang,
        2,
    )


def luu_ket_qua_nhan_dien(khung_hinh, x1, y1, x2, y2, ten_class, do_tin_cay, thu_muc_luu):
    thoi_gian_hien_tai = datetime.now()
    chuoi_thoi_gian_file = thoi_gian_hien_tai.strftime("%Y%m%d_%H%M%S_%f")[:-3]

    ten_file_an_toan = ten_class.replace(" ", "_")

    ten_file = f"{ten_file_an_toan}_{chuoi_thoi_gian_file}.jpg"
    duong_dan_anh = os.path.join(thu_muc_luu, ten_file)

    if LUU_CA_KHUNG_HINH:
        anh_de_luu = khung_hinh
    else:
        anh_de_luu = khung_hinh[y1:y2, x1:x2]
        if anh_de_luu is None or anh_de_luu.size == 0:
            anh_de_luu = khung_hinh
    da_luu_thanh_cong = lichsu.them_lich_su(
        ten=ten_class,
        do_tin_cay=do_tin_cay,
        duong_dan_anh=duong_dan_anh,
        thoi_gian=thoi_gian_hien_tai,
    )

    if da_luu_thanh_cong:
        cv2.imwrite(duong_dan_anh, anh_de_luu)
        print(
            f"[GHI NHẬN] '{ten_class}' | confidence={do_tin_cay:.2f} "
            f"| lúc {thoi_gian_hien_tai.strftime('%H:%M:%S')} | ảnh: {duong_dan_anh}"
        )

    return da_luu_thanh_cong


def xu_ly_mot_khung_hinh(model, khung_hinh, thu_muc_luu_anh):
    ket_qua = model(khung_hinh, verbose=False)[0]

    for box in ket_qua.boxes:
        chi_so_class = int(box.cls[0])
        do_tin_cay = float(box.conf[0])
        ten_class = model.names[chi_so_class]
        if not la_class_lien_quan(ten_class):
            continue
        if do_tin_cay < NGUONG_TIN_CAY:
            continue
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        ve_bounding_box(khung_hinh, x1, y1, x2, y2, ten_class, do_tin_cay)

        luu_ket_qua_nhan_dien(
            khung_hinh, x1, y1, x2, y2, ten_class, do_tin_cay, thu_muc_luu_anh
        )

    return khung_hinh


def phan_tich_tham_so_dong_lenh():
    bo_phan_tich = argparse.ArgumentParser(
        description="Hệ thống nhận diện biển báo giao thông real-time"
    )
    bo_phan_tich.add_argument(
        "--camera",
        type=str,
        default=None,
        help=(
            "Nguồn camera: số index camera USB/laptop (vd 0, 1) hoặc "
            "URL luồng video mạng (vd http://192.168.1.6:8080/video)."
        ),
    )
    tham_so, _ = bo_phan_tich.parse_known_args()
    return tham_so.camera


def chay_chuong_trinh():

    print("=" * 70)
    print("HỆ THỐNG NHẬN DIỆN BIỂN BÁO GIAO THÔNG REAL-TIME")
    print("=" * 70)
    chuan_bi_thu_muc_luu_anh(THU_MUC_LUU_ANH)
    lichsu.doc_tu_file()
    model = tai_model(DUONG_DAN_MODEL)
    nguon_camera_tu_dong_lenh = phan_tich_tham_so_dong_lenh()
    nguon_camera = (
        nguon_camera_tu_dong_lenh if nguon_camera_tu_dong_lenh is not None else CHI_SO_CAMERA
    )

    cap = mo_webcam(nguon_camera, CHIEU_RONG_KHUNG_HINH, CHIEU_CAO_KHUNG_HINH)
    if cap is None:
        return  

    print("\n[HƯỚNG DẪN] Nhấn phím 'q' trên cửa sổ video để THOÁT chương trình.\n")
    thoi_diem_truoc = time.time()
    fps_hien_thi = 0.0

    try:
        while True:
            doc_thanh_cong, khung_hinh = cap.read()
            if not doc_thanh_cong:
                print("[LỖI] Không đọc được khung hình từ camera. Dừng chương trình.")
                break
            khung_hinh = xu_ly_mot_khung_hinh(model, khung_hinh, THU_MUC_LUU_ANH)
            thoi_diem_hien_tai = time.time()
            khoang_thoi_gian = thoi_diem_hien_tai - thoi_diem_truoc
            if khoang_thoi_gian > 0:
                fps_hien_thi = 1.0 / khoang_thoi_gian
            thoi_diem_truoc = thoi_diem_hien_tai

            cv2.putText(
                khung_hinh,
                f"FPS: {fps_hien_thi:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )
            cv2.putText(
                khung_hinh,
                "Nhan 'q' de thoat",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )

            cv2.imshow("He thong nhan dien bien bao giao thong", khung_hinh)

            phim_bam = cv2.waitKey(1) & 0xFF
            if phim_bam == ord("q"):
                print("\n[nhandien] Người dùng nhấn 'q' -> đang thoát chương trình...")
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

        print("\n[nhandien] Đang lưu lịch sử ra file JSON...")
        lichsu.luu_ra_file()

        print("\n[nhandien] Tổng kết phiên làm việc:")
        lichsu.in_lich_su()

        print("\n[nhandien] Đã thoát chương trình an toàn. Tạm biệt!")


if __name__ == "__main__":
    chay_chuong_trinh()