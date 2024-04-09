from reader import Camera

camera = Camera()
image = camera.capture_image()
open("imgs/temp_test_out.png", "wb").write(image)  # pyright: ignore
