import os
import cv2
import random
import numpy
import time
import sys
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

"""
Each block in the slicing has an id
id:   where a piece should be in sorted state
imid: Where a piece actually is

"""

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
    def paste(dest, position, source):
        # Copies source image to destination image
        sheight = source.shape[0]
        swidth = source.shape[1]
        x, y = position
        dest[y : y+sheight, x : x+swidth] = source

class SortBox:
    _length = 0
    _divs = 0
    _blocklen = 0
    _impieces = []
    
    @staticmethod
    def ready(length, divs, duration, img):
        length   = (length//divs)*divs
        blocklen = length//divs
        
        imlength = ((min(img.size))//divs)*divs
        img = img.convert("RGB");
        img = img.crop((0, 0, imlength, imlength))
        img = img.resize((length, length))
        img = cvutil.piltocv(img)
        
        SortBox._length   = length
        SortBox._divs     = divs
        SortBox._blocklen = blocklen
        SortBox._duration = duration
        
        for i in range(divs):
            for j in range(divs):
                piece = cvutil.crop(img, (j*blocklen, i*blocklen, (j+1)*blocklen, (i+1)*blocklen))
                SortBox._impieces.append(piece)
    
    def _reposition(self, id, imid):
        """
        Repositions a piece using its id to another imid
        
        """
        imX = (imid%self._divs)*self._blocklen
        imY = (imid//self._divs)*self._blocklen
        cvutil.paste(self._img, (imX, imY), SortBox._impieces[id])
        
        self._imidarr[id] = imid;
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
        divs = SortBox._divs
    
        #Shuffle Arrays
        random.shuffle(self._imidarr)
        
        for i in range(divs**2):
            self._idarr[self._imidarr[i]] = i;
        
        #Create Image
        for piece in range(divs**2):
            self._reposition(piece, self._imidarr[piece])
    
    def __init__(self):
        self._imidarr = list(range(divs**2))
        self._idarr   = list(range(divs**2))
        
        length   = SortBox._length
        duration = SortBox._duration
        
        self._img = numpy.zeros((length,length,3), numpy.uint8)
        self.anim = Anim(length, length, duration)
        
        self._shuffle()
        
    def applyalgo(self, sort):
        steps = sort(self._idarr[:])
        
        self.anim.addframe(self._img)
        
        for step in steps:
            self._swap(step[0], step[1])
            self.anim.addframe(self._img)
        
        self.anim.normalize()

class Algo:
    @staticmethod
    def bubble(arr):
        steps = []
        for i in range(0, len(arr)):
            for j in range(1, len(arr)-i):
                if(arr[j-1] > arr[j]):
                    arr[j-1], arr[j] = arr[j], arr[j-1];
                    steps.append([j-1, j]);
        return steps
    
    @staticmethod
    def selection(arr):
        steps = []
        for i in range(0, len(arr)-1):
            minimum = i
            for j in range(i+1, len(arr)):
                if(arr[j] < arr[minimum]):
                    minimum = j
            if(minimum != i):
                arr[minimum], arr[i] = arr[i], arr[minimum];
                steps.append([minimum, i]);
        return steps
    
    @staticmethod
    def insertion(arr):
        steps = []
        for i in range(1, len(arr)):
            j = i
            while j > 0 and arr[j-1] > arr[j]:
                arr[j-1], arr[j] = arr[j], arr[j-1];
                steps.append([j-1, j])
                j = j-1
        return steps
        
    @staticmethod
    def merge(arr):
        steps = []
        def x(arr, start, end):
            if end <= start:
                return
            
            pivot = (start+end)//2
            
            x(arr, start, pivot)
            x(arr, pivot+1, end)
            
            for i in range(start+1, end+1):
                j = i
                while j > start and arr[j-1] > arr[j]:
                    arr[j-1], arr[j] = arr[j], arr[j-1]
                    steps.append([j-1, j])
                    j = j-1
           
        x(arr, 0, len(arr)-1)
        return steps
    
    @staticmethod
    def shell(arr):
        steps = []
        part = 1
        while 3*part+1 < len(arr):
            part = 3*part+1
        
        while part>0:
            for i in range(part, len(arr), part):
                j = i
                while j > 0 and arr[j-part] > arr[j]:
                    arr[j-part], arr[j] = arr[j], arr[j-part]
                    steps.append([j-part, j])
                    j = j-part
                    
            part = (part-1)//3
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
                        steps.append([i,j])
                    i = i+1
            
            arr[i], arr[end] = arr[end], arr[i]
            steps.append([i, end])
            
            x(arr, start, i-1)
            x(arr, i+1, end)
            
        x(arr, 0, len(arr)-1)
        return steps
    
class Anim:
    
    def normalize(self):
        """
        Normalization of frames
        This beautiful motherfucker took 4 hours to code
        
        """
        t = self._duration * self._fps # Total Frames available
        n = len(self._frames) # Number of Frames
        
        while(n < t):
            self._frames.extend(list(range(n)))
            for i in range(n-1, -1, -1):
                self._frames[2*i] = self._frames[i]
                self._frames[2*i+1] = self._frames[i]
            n = 2*n
        
        assert(n >= t)
        
        while((n-2)//2 >= t-2):
            for i in range(1, ((n-2)//2)+1):
                self._frames[i] = self._frames[2*i]
            self._frames[((n-2)//2)+1] = self._frames[-1]
            
            n = 2+((n-2)//2)
            
            for i in range(len(self._frames)-n):
                self._frames.pop()
        
        assert(n >= t)
        assert(n < t*2 - 3)
        assert(t >= 2)
        
        if(n > t):
            diff = n - t
            for i in range(1, len(self._frames)-1, n//diff):
                self._frames[i] = None
                n = n-1
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
                    free = free+1
             
            for i in range(len(self._frames)-n):
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
length = 300
divs = 10
duration = 6
padding = 20
lineheight = 15
boxes = []
vidheight = 2*length+2*lineheight+3*padding
vidwidth = 3*length+4*padding
video = Anim(vidwidth, vidheight, duration)

SortBox.ready(length, divs, duration, img)

for i in range(6):
    boxes.append(SortBox())

boxes[0].applyalgo(Algo.bubble)
boxes[1].applyalgo(Algo.selection)
boxes[2].applyalgo(Algo.insertion)
boxes[3].applyalgo(Algo.merge)
boxes[4].applyalgo(Algo.shell)
boxes[5].applyalgo(Algo.quick)

background = Image.new('RGB', (vidwidth, vidheight))
ImageDraw.Draw(background).text((padding+(length-110)//2, padding+length), "Bubble Sort", (255,255,255), ImageFont.truetype("cour.ttf", 16))
ImageDraw.Draw(background).text((length+2*padding+(length-140)//2, padding+length), "Selection Sort", (255,255,255), ImageFont.truetype("cour.ttf", 16))
ImageDraw.Draw(background).text((2*length+3*padding+(length-140)//2, padding+length), "Insertion Sort", (255,255,255), ImageFont.truetype("cour.ttf", 16))
ImageDraw.Draw(background).text((padding+(length-210)//2, 2*length+lineheight+2*padding), "Merge Sort (in-place)", (255,255,255), ImageFont.truetype("cour.ttf", 16))
ImageDraw.Draw(background).text((length+2*padding+(length-280)//2, 2*length+lineheight+2*padding), "Shell Sort (Knuth's formula)", (255,255,255), ImageFont.truetype("cour.ttf", 16))
ImageDraw.Draw(background).text((2*length+3*padding+(length-100)//2, 2*length+lineheight+2*padding), "Quick Sort", (255,255,255), ImageFont.truetype("cour.ttf", 16))
background = cvutil.piltocv(background)

for i in range(len(boxes[0].anim.frames())):
    frame = numpy.copy(background)
    cvutil.paste(frame, (padding, padding), boxes[0].anim.frames()[i])
    cvutil.paste(frame, (length+2*padding, padding), boxes[1].anim.frames()[i])
    cvutil.paste(frame, (2*length+3*padding, padding), boxes[2].anim.frames()[i])
    cvutil.paste(frame, (padding, length+lineheight+2*padding), boxes[3].anim.frames()[i])
    cvutil.paste(frame, (length+2*padding, length+lineheight+2*padding), boxes[4].anim.frames()[i])
    cvutil.paste(frame, (2*length+3*padding, length+lineheight+2*padding), boxes[5].anim.frames()[i])
    video.addframe(frame)


frames_time = numpy.round(time.time() - start_time, 2)
print("Frames processing done in " + str(frames_time) + ", rendering now")
start_time = time.time()

f = open(sys.argv[1]+".status", "w")
f.write("1")
f.close()

video.export()

rendering_time = numpy.round(time.time() - start_time, 2)
print("Rendering done in " + str(rendering_time))
print("Total time taken: " + str(frames_time+rendering_time))

f = open(sys.argv[1]+".status", "w")
f.write("3")
f.close()