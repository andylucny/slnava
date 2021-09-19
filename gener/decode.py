import cv2

img=cv2.imread("qrcode.png")

det=cv2.QRCodeDetector()
val, pts, st_code=det.detectAndDecode(img)

val2, st_code2 = det.decode(img,points=pts)

print(val)
