from captcha.image import ImageCaptcha
import random
import string
import io
from pathlib import Path
from typing import List


class CaptchaUtils:
    @staticmethod
    def random_text() -> str:
        chars: str = string.ascii_uppercase + string.digits
        return "".join(random.choice(chars) for _ in range(6))

    @staticmethod
    def captcha_image(text: str) -> bytes:
        fonts: list[str] = [
            str(p) for p in Path("src/Commands/Chat/Captcha/CaptchaFont").glob("*.ttf")
        ]

        image: ImageCaptcha = ImageCaptcha(
            width=280,
            height=90,
            fonts=[random.choice(fonts)],
        )

        buf: io.BytesIO = io.BytesIO()
        image.write(text, buf)
        return buf.getvalue()
    
    @classmethod
    def captcha_options(self, answer: str) -> List[str]:
        opts: set[str] = {answer}
        while len(opts) < 4:
            opts.add(self.random_text())
        options: List[str] = list(opts)
        random.shuffle(options)
        return options

