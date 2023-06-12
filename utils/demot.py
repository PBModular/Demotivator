# SOURCE: https://github.com/nesclass/demotivator-bot/blob/master/bot/utils/degenerator.py

import os
import cv2
import numpy as np

from PIL import ImageFont, ImageDraw, Image

class Demotivator:
    def __init__(self):
        self.update_params(512, 512)

    def update_params(self, MEDIA_WIDTH: int, MEDIA_HEIGHT: int):
        self.FRAME_MARGIN_X = int(MEDIA_WIDTH * 0.1)   # отступ до окантовки фрейма по Ox
        self.FRAME_MARGIN_Y = int(MEDIA_HEIGHT * 0.04)  # отступ до окантовки фрейма по Oy
        self.FRAME_THICKNESS = 1  # размер окантовки
        self.FRAME_INNER_PADDING = 3  # внутренний отступ до медиа (без учёта толщины)

        self.TEXT_AREA_HEIGHT = int(MEDIA_WIDTH * 0.15)
        self.TEXT_CONTAINER_PADDING = 15  # отступы контейнера

        # margin - padding - media - padding - margin
        self.WIDTH = 2 * self.FRAME_MARGIN_X + 2 * self.FRAME_INNER_PADDING + MEDIA_WIDTH
        # margin - padding - media - padding - text
        self.HEIGHT = self.FRAME_MARGIN_Y + 2 * self.FRAME_INNER_PADDING + MEDIA_HEIGHT + self.TEXT_AREA_HEIGHT

        if self.WIDTH < self.HEIGHT:
            self.TEXT_DEFAULT_FONT_SIZE = int(self.HEIGHT * 0.06)   # высота области для текста
        else:
            self.TEXT_DEFAULT_FONT_SIZE = int(self.WIDTH * 0.1)   # высота области для текста

        # margin - padding - media - padding - text
        self.MEDIA_TOP = self.FRAME_MARGIN_Y + self.FRAME_INNER_PADDING
        self.MEDIA_BOTTOM = self.HEIGHT - self.TEXT_AREA_HEIGHT - self.FRAME_INNER_PADDING

        # margin - padding - media - padding - margin
        self.MEDIA_LEFT = self.FRAME_MARGIN_X + self.FRAME_INNER_PADDING
        self.MEDIA_RIGHT = self.WIDTH - self.FRAME_MARGIN_X - self.FRAME_INNER_PADDING

        # margin - padding - container[text] - padding - margin
        self.MAX_TEXT_LENGTH = self.WIDTH - 2 * self.FRAME_MARGIN_X - 2 * self.TEXT_CONTAINER_PADDING

        # Черная штука эта
        self.TEMPLATE = cv2.rectangle(
            # чёрный фон по размерам медиа
            img=np.zeros(
                (self.HEIGHT, self.WIDTH, 3),
                dtype=np.uint8
            ),

            # верхний левый угол окантовки
            pt1=(self.FRAME_MARGIN_X,
                self.FRAME_MARGIN_Y),

            # нижний правый угол окантовки
            pt2=(self.WIDTH - self.FRAME_MARGIN_X - 1,
                self.HEIGHT - self.TEXT_AREA_HEIGHT - 1),

            color=(255, 255, 255),
            thickness=self.FRAME_THICKNESS
        )

    # кэш для сгенерированных размеров шрифтов
    # TODO: пре-генерация? возможно целесообразнее
    cached_sizes: dict[int, ImageFont] = {}


    # достать шрифт из кэша, либо сгенерировать новый
    def get_font_by_size(self, size: int) -> ImageFont:
        if size in self.cached_sizes:
            return self.cached_sizes[size]

        font = ImageFont.truetype(os.path.abspath(__file__).replace("demot.py", "../font.ttf"), size)
        self.cached_sizes[size] = font

        return font


    # подобрать шрифт по (размеру) текста
    def generate_font_from_text(self, text: str) -> ImageFont:
        font = self.get_font_by_size(self.TEXT_DEFAULT_FONT_SIZE)
        text_length = font.getlength(text)

        # если текст больше дозволенного
        if text_length > self.MAX_TEXT_LENGTH:
            # изменение размера шрифта пропорционально превышению
            ratio = self.MAX_TEXT_LENGTH / text_length
            font_size = int(self.TEXT_DEFAULT_FONT_SIZE * ratio)
            font_size += font_size % 2  # 23 -> 24, 25 -> 26
            font = self.get_font_by_size(int(font_size))

        return font


    # Запихиваем изображение с демотиватор
    # TODO: mp & frame-division: https://stackoverflow.com/a/55259105/20949821
    def modify_template_by_frame(self, template: np.ndarray, frame: np.ndarray, MEDIA_WIDTH: int, MEDIA_HEIGHT: int):
        frame = cv2.resize(
            frame,
            (MEDIA_WIDTH, MEDIA_HEIGHT),

            # лучшее соотношение задержки к качеству
            # чёткое изображение ценой +100-200мс оверхэда
            interpolation=cv2.INTER_CUBIC
        )

        # замена пикселей в области y:x на фрейм
        template[self.MEDIA_TOP:self.MEDIA_BOTTOM, self.MEDIA_LEFT:self.MEDIA_RIGHT] = frame


    # запись видео демика
    def write_video(self, input_file: str, output_file: str, template: np.ndarray):
        stream = cv2.VideoCapture(input_file)

        out = cv2.VideoWriter(
            output_file,
            cv2.VideoWriter_fourcc(*'mp4v'),
            stream.get(cv2.CAP_PROP_FPS),
            (self.WIDTH, self.HEIGHT)
        )

        while stream.isOpened():
            flag, frame = stream.read()
            if not flag:
                break

            self.modify_template_by_frame(template, frame, int(stream.get(3)), int(stream.get(4)))
            out.write(template)

        stream.release()
        out.release()


    # запись фото демика
    def write_image(self, input_file: str, output_file: str, template: np.ndarray):
        image = cv2.imread(input_file)
        self.modify_template_by_frame(template, image, image.shape[1], image.shape[0])
        cv2.imwrite(output_file, template)


    def generate_demotivator(self, input_file: str, output_file: str, text: str = "зачем"):
        font = self.generate_font_from_text(text)

        _, _, text_width, text_height = font.getbbox(text)

        imread = cv2.imread(input_file)
        if type(imread) == "numpy.ndarray":
            self.update_params(imread.shape[1], imread.shape[0])
        else:
            imread = cv2.VideoCapture(input_file)
            self.update_params(int(imread.get(3)), int(imread.get(4)))

        text_x = self.WIDTH - self.FRAME_MARGIN_X - self.TEXT_CONTAINER_PADDING - self.MAX_TEXT_LENGTH / 2
        text_y = self.HEIGHT - self.TEXT_AREA_HEIGHT / 2 - 1

        # opencv image (numpy matrix) -> pil image
        image = Image.fromarray(self.TEMPLATE)

        draw = ImageDraw.Draw(image)
        draw.text(
            (text_x, text_y),
            text=text,
            font=font,
            fill="#fff",
            anchor="mm"
        )

        # pil image -> opencv image (numpy matrix)
        template = np.array(image)  # noqa

        if input_file.endswith((".mp4", ".MP4")):  # если видео
            return self.write_video(input_file, output_file, template)
        elif input_file.endswith(".jpg"):  # если изображение
            return self.write_image(input_file, output_file, template)
        elif input_file.endswith(".png"):  # если изображение
            return self.write_image(input_file, output_file, template)

        # что это за херня?
        raise NotImplementedError

# generate_demotivator("/home/cakestwix/Pictures/video_2023-04-19_10-13-03.mp4", "deg.mp4")
