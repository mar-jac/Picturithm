import math
import os
import random
import time

import cv2
import numpy
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

"""
Each block in the slicing has an id
id:   where a piece should be in sorted state
imid: Where a piece actually is

"""

import sys

sys.stdout = open('output.txt', 'w')
sys.stderr = open('error.txt', 'w')


class cvutil:
    @staticmethod
    def piltocv(pil_image):
        numpyarr = numpy.array(pil_image.convert('RGB'))
        return cv2.cvtColor(numpyarr, cv2.COLOR_RGB2BGR)

    @staticmethod
    def crop(img, coords):
        # Returns reference from original image
        x1, y1, x2, y2 = coords
        return img[y1:y2, x1:x2]

    @staticmethod
    def paste(dest, position, source, max_x, max_y):
        # Copies source image to destination image
        srows = source.shape[0]
        scols = source.shape[1]
        x, y = position
        if x + scols <= max_x and y + srows <= max_y:
            dest[y: y + srows, x: x + scols] = source
        else:
            dest[y: max_y, x: max_x] = source[0: y + srows - max_y, 0: x + scols - max_x]


class SortBox:
    _lengthx = 0
    _lengthy = 0
    _divsx = 0
    _divsy = 0
    gif_frames = []
    _blocklen = 0
    _blocklenx = 0
    _blockleny = 0
    _impieces = []

    @staticmethod
    def ready(divsx, divsy, duration, img, gif_frames=[]):
        size = img.size
        lengthx = (size[0] // divsx) * divsx
        lengthy = (size[1] // divsy) * divsy
        blocklenx = lengthx // divsx
        blockleny = lengthy // divsy

        img = img.convert("RGB")
        # img = SortBox.make_square(img)
        img = img.resize((lengthx, lengthy))
        img = cvutil.piltocv(img)
        SortBox._lengthx = lengthx
        SortBox._divsx = divsx
        SortBox._divsy = divsy
        SortBox._lengthy = lengthy
        SortBox._blocklenx = blocklenx
        SortBox._blockleny = blockleny
        SortBox._duration = duration
        SortBox.gif_frames = gif_frames

        for i in range(divsy):
            for j in range(divsx):
                piece = cvutil.crop(img, (j * blocklenx, i * blockleny, (j + 1) * blocklenx, (i + 1) * blockleny))
                SortBox._impieces.append(piece)

    def _reposition(self, id, imid):
        """
        Repositions a piece using its id to another imid

        """
        imX = (imid % self._divsx) * self._blocklenx
        imY = (imid // self._divsx) * self._blockleny
        cvutil.paste(self._img, (imX, imY), SortBox._impieces[id], SortBox._lengthx, SortBox._lengthy)

        self._imidarr[id] = imid
        self._idarr[imid] = id

    def _swap(self, imid1, imid2):
        """
        Swap piece of imid1 with piece of imid2

        """
        id1 = self._idarr[imid1]
        id2 = self._idarr[imid2]
        self._reposition(id1, imid2)
        self._reposition(id2, imid1)

    def _shuffle(self):
        divsx = SortBox._divsx
        divsy = SortBox._divsy

        # Shuffle Arrays
        random.shuffle(self._imidarr)

        for i in range(divsx * divsy):
            self._idarr[self._imidarr[i]] = i

        # Create Image
        for piece in range(divsx * divsy):
            self._reposition(piece, self._imidarr[piece])

    def __init__(self):
        self._imidarr = list(range(divsx*divsy))
        self._idarr = list(range(divsx*divsy))

        lengthx = SortBox._lengthx
        lengthy = SortBox._lengthy
        duration = SortBox._duration

        self._img = numpy.zeros((lengthy, lengthx, 3), numpy.uint8)
        self.anim = Anim(lengthx, lengthy, duration)

        self._shuffle()

    def applyalgo(self, sort):
        steps = sort(self._idarr[:])
        self.anim.addframe(self._img)
        for step in steps:
            self._swap(step[0], step[1])
            self.anim.addframe(self._img)
        self.anim.normalize()
        for gif_frame in self.gif_frames:
            self.anim.addframe(gif_frame)


class Algo:
    @staticmethod
    def bubble(arr):
        steps = []
        for i in range(0, len(arr)):
            for j in range(1, len(arr) - i):
                if (arr[j - 1] > arr[j]):
                    arr[j - 1], arr[j] = arr[j], arr[j - 1]
                    steps.append([j - 1, j])
        return steps

    @staticmethod
    def selection(arr):
        steps = []
        for i in range(0, len(arr) - 1):
            minimum = i
            for j in range(i + 1, len(arr)):
                if (arr[j] < arr[minimum]):
                    minimum = j
            if (minimum != i):
                arr[minimum], arr[i] = arr[i], arr[minimum]
                steps.append([minimum, i])
        return steps

    @staticmethod
    def insertion(arr):
        steps = []
        for i in range(1, len(arr)):
            j = i
            while j > 0 and arr[j - 1] > arr[j]:
                arr[j - 1], arr[j] = arr[j], arr[j - 1]
                steps.append([j - 1, j])
                j = j - 1
        return steps

    @staticmethod
    def merge(arr):
        steps = []

        def x(arr, start, end):
            if end <= start:
                return

            pivot = (start + end) // 2

            x(arr, start, pivot)
            x(arr, pivot + 1, end)

            for i in range(start + 1, end + 1):
                j = i
                while j > start and arr[j - 1] > arr[j]:
                    arr[j - 1], arr[j] = arr[j], arr[j - 1]
                    steps.append([j - 1, j])
                    j = j - 1

        x(arr, 0, len(arr) - 1)
        return steps

    @staticmethod
    def shell(arr):
        steps = []
        part = 1
        while 3 * part + 1 < len(arr):
            part = 3 * part + 1

        while part > 0:
            for i in range(part, len(arr), part):
                j = i
                while j > 0 and arr[j - part] > arr[j]:
                    arr[j - part], arr[j] = arr[j], arr[j - part]
                    steps.append([j - part, j])
                    j = j - part

            part = (part - 1) // 3
        return steps

    @staticmethod
    def quick(arr):
        steps = []

        def x(arr, start, end):
            if end <= start:
                return

            pivot = arr[end]
            i = start

            for j in range(start, end):
                if arr[j] < pivot:
                    if i != j:
                        arr[i], arr[j] = arr[j], arr[i]
                        steps.append([i, j])
                    i = i + 1

            arr[i], arr[end] = arr[end], arr[i]
            steps.append([i, end])

            x(arr, start, i - 1)
            x(arr, i + 1, end)

        x(arr, 0, len(arr) - 1)
        return steps


class Anim:

    def normalize(self):
        """
        Normalization of frames
        This beautiful motherfucker took 4 hours to code

        """
        t = self._duration * self._fps  # Total Frames available
        n = len(self._frames)  # Number of Frames

        while (n < t):
            self._frames.extend(list(range(n)))
            for i in range(n - 1, -1, -1):
                self._frames[2 * i] = self._frames[i]
                self._frames[2 * i + 1] = self._frames[i]
            n = 2 * n

        assert (n >= t)

        while ((n - 2) // 2 >= t - 2):
            for i in range(1, ((n - 2) // 2) + 1):
                self._frames[i] = self._frames[2 * i]
            self._frames[((n - 2) // 2) + 1] = self._frames[-1]

            n = 2 + ((n - 2) // 2)

            for i in range(len(self._frames) - n):
                self._frames.pop()

        assert (n >= t)
        assert (n < t * 2 - 3)
        assert (t >= 2)

        if (n > t):
            diff = n - t
            for i in range(1, len(self._frames) - 1, n // diff):
                self._frames[i] = None
                n = n - 1
                if n == t:
                    break

            free = 0
            for i in range(0, len(self._frames)):
                if self._frames[i] is None:
                    if self._frames[free] is not None:
                        free = i
                else:
                    if self._frames[free] is None:
                        self._frames[free], self._frames[i] = self._frames[i], self._frames[free]
                    free = free + 1

            for i in range(len(self._frames) - n):
                self._frames.pop()

    def __init__(self, width, height, duration):
        self._height = height
        self._width = width
        self._duration = duration
        self._fps = 120
        self._frames = []
        self._pausein = 1
        self._pauseout = 1

    def addframe(self, frame):
        self._frames.append(numpy.copy(frame))

    def export(self):
        video = cv2.VideoWriter(sys.argv[2], cv2.VideoWriter_fourcc(*'mp4v'), self._fps, (self._width, self._height))

        for i in range(self._fps * self._pausein):
            firstframe = self._frames[0]
            video.write(firstframe)

        for frame in self._frames:
            video.write(frame)

        for i in range(self._fps * self._pauseout):
            lastframe = self._frames[-1]
            video.write(lastframe)

        cv2.destroyAllWindows()
        video.release()

    def frames(self):
        return self._frames


start_time = time.time()

img = Image.open(sys.argv[1])
size = img.size
lengthx = size[0]
lengthy = size[1]
divsx = int(sys.argv[3])
divsy = int(sys.argv[4])

_lengthx = (size[0] // divsx) * divsx
_lengthy = (size[1] // divsy) * divsy
duration = 6
padding = 0
lineheight = 15
boxes = []
vidheight = _lengthy + lineheight + padding
vidwidth = _lengthx + padding
gif_frames = []
if os.path.exists("%s.gif" % sys.argv[1]):
    gif = "%s.gif" % sys.argv[1]

    extra_duration = 0
    if gif is not None:
        im = Image.open(gif)
        mypalette = im.getpalette()
        prev = im.copy()
        try:
            while 1:
                im.seek(im.tell() + 1)
                extra_duration = im.info['duration']
                imt = im.convert("RGBA")
                imt = imt.resize((_lengthx, _lengthy))
                imt = cvutil.piltocv(imt)
                repeat = math.ceil(extra_duration / (1000 / 120))
                for i in range(repeat):
                    gif_frames.append(imt)
        except EOFError:
            pass  # end of sequence
video = Anim(vidwidth, vidheight, duration)
SortBox.ready(divsx, divsy, duration, img, gif_frames)
boxes.append(SortBox())
boxes[0].applyalgo(Algo.quick)

background = Image.new('RGB', (vidwidth, vidheight))
ImageDraw.Draw(background).text((padding + (_lengthx - 110) // 2, padding + _lengthy), "Quick Sort", (255, 255, 255), ImageFont.truetype("cour.ttf", 16))

background = cvutil.piltocv(background)

for i in range(len(boxes[0].anim.frames())):
    frame = numpy.copy(background)
    cvutil.paste(frame, (padding, padding), boxes[0].anim.frames()[i], lengthx, lengthy)
    video.addframe(frame)

frames_time = numpy.round(time.time() - start_time, 2)
print("Frames processing done in " + str(frames_time) + ", rendering now")
start_time = time.time()

f = open(sys.argv[1] + ".status", "w")
f.write("1")
f.close()

video.export()

rendering_time = numpy.round(time.time() - start_time, 2)
print("Rendering done in " + str(rendering_time))
print("Total time taken: " + str(frames_time + rendering_time))

f = open(sys.argv[1] + ".status", "w")
f.write("3")
f.close()
