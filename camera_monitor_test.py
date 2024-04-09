from datetime import datetime

import cv2


def __get_area_px(image) -> float:

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    largest_countour = max(contours, key=cv2.contourArea)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 100_000:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            image, str(area), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
        )

    area = cv2.contourArea(largest_countour)
    return area


video_capture = cv2.VideoCapture(4)

while True:
    result, video_frame = video_capture.read()
    if result is False:
        break

    area = __get_area_px(video_frame)
    print(f"Area: {area}")

    cv2.imshow("My Face Detection Project", video_frame)

    if area > 140_000:
        print("Possible Fish Detected")
        print("Send notification")
        print("Do something useful")
        print("Took a photo")
        cv2.imwrite(f"sized_{datetime.now()}.png", video_frame)
        break

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
