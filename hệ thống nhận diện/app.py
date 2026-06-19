import cv2
from ultralytics import YOLO

def main():
    model_path = "best.pt" 
    print(f"Đang tải mô hình từ: {model_path}...")
    model = YOLO(model_path)

    input_source = 0 

    cap = cv2.VideoCapture(input_source, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Lỗi: Không thể mở nguồn video hoặc Camera.")
        return

    print("Hệ thống đang chạy... Nhấn nút 'Q' trên bàn phím để THOÁT.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Đã kết thúc Video hoặc không nhận được dữ liệu từ Camera.")
            break
        results = model(frame, conf=0.5, verbose=False)
        for result in results:
            boxes = result.boxes 
            
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                cls_id = int(box.cls[0])
                label_name = model.names[cls_id]
                confidence = float(box.conf[0]) * 100 

                color = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                display_text = f"{label_name}: {confidence:.1f}%"

                (w, h), _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(frame, (x1, y1 - h - 10), (x1 + w, y1), color, -1)
                
                cv2.putText(frame, display_text, (x1, y1 - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("He Thong Nhan Biet Bien Bao Giao Thong Real-time", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Hệ thống đã đóng an toàn.")

if __name__ == "__main__":
    main()