import json
import os
from datetime import datetime

DINH_DANG_THOI_GIAN = "%Y-%m-%d %H:%M:%S"

FILE_LICH_SU_MAC_DINH = "lich_su_bien_bao.json"

KHOANG_CACH_TOI_THIEU_GIAY = 3.0


class QuanLyLichSu:

    def __init__(self, duong_dan_file=FILE_LICH_SU_MAC_DINH):

        self.danh_sach_lich_su = []

        self._thoi_diem_luu_gan_nhat = {}

        self.duong_dan_file = duong_dan_file

    def them_lich_su(self, ten, do_tin_cay, duong_dan_anh, thoi_gian=None):
        
        thoi_gian_hien_tai = thoi_gian if thoi_gian is not None else datetime.now()

        thoi_diem_truoc = self._thoi_diem_luu_gan_nhat.get(ten)
        if thoi_diem_truoc is not None:
            so_giay_da_troi_qua = (thoi_gian_hien_tai - thoi_diem_truoc).total_seconds()
            if so_giay_da_troi_qua < KHOANG_CACH_TOI_THIEU_GIAY:
                return False

        ban_ghi_moi = {
            "ten_bien_bao": ten,
            "thoi_gian": thoi_gian_hien_tai.strftime(DINH_DANG_THOI_GIAN),
            "do_tin_cay": round(float(do_tin_cay), 4),
            "duong_dan_anh": duong_dan_anh,
        }

        self.danh_sach_lich_su.append(ban_ghi_moi)

        self._thoi_diem_luu_gan_nhat[ten] = thoi_gian_hien_tai

        return True

    def lay_lich_su(self):
        return self.danh_sach_lich_su

    def in_lich_su(self):
        if not self.danh_sach_lich_su:
            print("Lịch sử trống, chưa có biển báo nào được ghi nhận.")
            return

        print("=" * 70)
        print(f"{'STT':<5}{'Tên biển báo':<25}{'Thời gian':<22}{'Độ tin cậy':<10}")
        print("-" * 70)
        for idx, ban_ghi in enumerate(self.danh_sach_lich_su, start=1):
            print(
                f"{idx:<5}"
                f"{ban_ghi['ten_bien_bao']:<25}"
                f"{ban_ghi['thoi_gian']:<22}"
                f"{ban_ghi['do_tin_cay']:<10}"
            )
            print(f"     -> Ảnh: {ban_ghi['duong_dan_anh']}")
        print("=" * 70)
        print(f"Tổng cộng: {len(self.danh_sach_lich_su)} bản ghi")
    def luu_ra_file(self, duong_dan_file=None):
        
        duong_dan = duong_dan_file or self.duong_dan_file
        try:
            with open(duong_dan, "w", encoding="utf-8") as f:
                json.dump(self.danh_sach_lich_su, f, ensure_ascii=False, indent=4)
            print(f"[lichsu] Đã lưu {len(self.danh_sach_lich_su)} bản ghi vào '{duong_dan}'")
        except Exception as loi:
            print(f"[lichsu] Lỗi khi lưu file JSON: {loi}")

    def doc_tu_file(self, duong_dan_file=None):
        duong_dan = duong_dan_file or self.duong_dan_file

        if not os.path.exists(duong_dan):
            print(f"[lichsu] Không tìm thấy file '{duong_dan}', bắt đầu lịch sử mới.")
            return

        try:
            with open(duong_dan, "r", encoding="utf-8") as f:
                du_lieu = json.load(f)
            self.danh_sach_lich_su = du_lieu
            print(f"[lichsu] Đã đọc {len(du_lieu)} bản ghi từ '{duong_dan}'")
        except Exception as loi:
            print(f"[lichsu] Lỗi khi đọc file JSON: {loi}")



_instance_dung_chung = QuanLyLichSu()


def them_lich_su(ten, do_tin_cay, duong_dan_anh, thoi_gian=None):
    """Hàm cấp module: thêm bản ghi mới (xem QuanLyLichSu.them_lich_su)."""
    return _instance_dung_chung.them_lich_su(ten, do_tin_cay, duong_dan_anh, thoi_gian)


def lay_lich_su():
    """Hàm cấp module: lấy toàn bộ lịch sử (xem QuanLyLichSu.lay_lich_su)."""
    return _instance_dung_chung.lay_lich_su()


def in_lich_su():
    """Hàm cấp module: in lịch sử ra console (xem QuanLyLichSu.in_lich_su)."""
    return _instance_dung_chung.in_lich_su()


def luu_ra_file(duong_dan_file=None):
    """Hàm cấp module: lưu lịch sử ra file JSON."""
    return _instance_dung_chung.luu_ra_file(duong_dan_file)


def doc_tu_file(duong_dan_file=None):
    """Hàm cấp module: đọc lịch sử từ file JSON."""
    return _instance_dung_chung.doc_tu_file(duong_dan_file)


if __name__ == "__main__":
    print("Đang chạy thử module lichsu.py ...")

    them_lich_su("Biển báo dừng (Stop)", 0.92, "anh_lichsu/stop_001.jpg")
    them_lich_su("Biển báo giới hạn tốc độ 60", 0.81, "anh_lichsu/toc_do_001.jpg")

    da_them = them_lich_su("Biển báo dừng (Stop)", 0.95, "anh_lichsu/stop_002.jpg")
    print("Lần thêm thứ 2 (cùng biển, ngay sau đó) có được lưu không?", da_them)

    in_lich_su()
    luu_ra_file("test_lich_su.json")
