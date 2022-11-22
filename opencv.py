#!/usr/bin/python3
import math
import time
from argparse import ArgumentParser
import numpy as np
import cv2

import ht301_hacklib

class FrameProcessor:
    def __init__(self, width, height, scale, color_map, temp_range):
        self.width = width * scale
        self.height = height * scale
        self.scale = scale
        self.color_map = color_map
        if temp_range:
            self.min_temp = temp_range[0]
            self.max_temp = temp_range[1]
        else:
            self.min_temp = None
            self.max_temp = None

        self.legend_width = 55 * scale
        self.bar_hspace = 15 * scale
        self.text_vspace = 20 * scale

        if scale >= 2:
            self.font = cv2.FONT_HERSHEY_DUPLEX
        else:
            self.font = cv2.FONT_HERSHEY_PLAIN


    def getWidth(self, withLegend):
        if withLegend:
            return self.width + self.legend_width
        else:
            return self.width


    def getHeight(self):
        return self.height


    def processImage(self, frame, info):
        if self.min_temp or self.max_temp:
            fmin = frame.min()
            fmax = frame.max()
            d = (fmax - fmin) / (info['Tmax_C'] - info['Tmin_C'])
            vmin = fmin + (self.min_temp - info['Tmin_C']) * d
            vmax = fmax + (self.max_temp - info['Tmax_C']) * d
        else:
            vmin = frame.min()
            vmax = frame.max()

        # Sketchy auto-exposure
        frame = frame.astype(np.float32)
        frame -= vmin
        frame /= (vmax - vmin)

        frame = (np.clip(frame, 0, 1)*255).astype(np.uint8)

        if self.scale != 1:
            frame = cv2.resize(frame, dsize=(self.width, self.height), interpolation=cv2.INTER_CUBIC)

        return cv2.applyColorMap(frame, self.color_map)


    def _generateGradient(self):
        color_lut = cv2.applyColorMap(np.array(range(256), dtype=np.uint8), self.color_map)
        self.gradient = np.zeros((self.height, self.legend_width, 3), dtype=np.uint8)
        gradient_height = self.height - 2 * self.text_vspace
        y_start = self.bar_hspace
        y_end = self.legend_width - self.bar_hspace

        for index in range(gradient_height):
            color = color_lut[int(0xff - (index * 0x100 / gradient_height))][0]
            self.gradient[index + self.text_vspace][y_start:y_end] = color


    def _drawTemperatureCentered(self, img, point, dims, T, font, color = (0,0,0)):
        (x, y) = point
        (width, height) = dims
        t = f"{round(T)}C"
        dsize = 1

        (text_length, text_height) = cv2.getTextSize(t, font, 1, dsize)[0]
        text_x = x + round((width - text_length) / 2)
        text_y = y + height - round((height - text_height) / 2)
        cv2.putText(img, t, (text_x, text_y), font, 1, color, dsize, cv2.LINE_8)


    def addLegend(self, frame, info):
        if not hasattr(self, "gradient"):
            self._generateGradient()

        legend = np.copy(self.gradient)
        max_temp = self.max_temp if self.max_temp != None else info['Tmax_C']
        min_temp = self.min_temp if self.min_temp != None else info['Tmin_C']
        self._drawTemperatureCentered(legend, (0, 0), (self.legend_width, self.text_vspace), max_temp, self.font, (255,255,255))
        self._drawTemperatureCentered(legend, (0, self.height - self.text_vspace), (self.legend_width, self.text_vspace), min_temp, self.font, (255,255,255))
        return np.concatenate((frame, legend), axis=1)


    def _scalePoint(self, point, scale):
        (x, y) = point
        return (scale * x, scale * y)


    def _drawMarker(self, img, point, T, font, color = (0,0,0)):
        d1, d2 = 2, 5
        dsize = 1
        (x, y) = point
        t = '%.1fC' % T
        cv2.line(img,(x+d1, y),(x+d2,y),color, dsize)
        cv2.line(img,(x-d1, y),(x-d2,y),color, dsize)
        cv2.line(img,(x, y+d1),(x,y+d2),color, dsize)
        cv2.line(img,(x, y-d1),(x,y-d2),color, dsize)

        text_size = cv2.getTextSize(t, font, 1, dsize)[0]
        tx, ty = x+d1, y+d1+text_size[1]
        if tx + text_size[0] > img.shape[1]: tx = x-d1-text_size[0]
        if ty                > img.shape[0]: ty = y-d1

        cv2.putText(img, t, (tx,ty), font, 1, color, dsize, cv2.LINE_8)


    def addMarkers(self, frame, info):
        self._drawMarker(frame, self._scalePoint(info['Tmin_point'], self.scale), info['Tmin_C'], self.font, (55,0,0))
        self._drawMarker(frame, self._scalePoint(info['Tmax_point'], self.scale), info['Tmax_C'], self.font, (0,0,85))
        self._drawMarker(frame, self._scalePoint(info['Tcenter_point'], self.scale), info['Tcenter_C'], self.font, (0,255,255))
        return frame


def main():
    parser = ArgumentParser()
    parser.add_argument("-c", "--colormap",
        dest="colormap", default="inferno",
        type=lambda s:getattr(cv2, "COLORMAP_" + s.upper()),
        help="color map used for thermal gradient (bone, inferno, jet, turbo, ...)"
    )
    parser.add_argument("-s", "--scale",
        dest="scale", default=2, choices=[1, 2, 3], type=int,
        help="scaling factor for video size (default 2)"
    )
    parser.add_argument("-r", "--range",
        dest="range",  type=int, nargs=2, metavar=('FROM', 'TO'),
        help="specify visualized temperature range (default auto)"
    )
    parser.add_argument("-nl", "--no-legend",
        action="store_false", dest="legend", default=True,
        help="hide color map legend"
    )
    parser.add_argument("-nm", "--no-markers",
        action="store_false", dest="markers", default=True,
        help="hide min/max/center temperature markers"
    )
    args = parser.parse_args()

    with ht301_hacklib.HT301() as cap:
        processor = FrameProcessor(cap.FRAME_WIDTH, cap.FRAME_HEIGHT, args.scale, args.colormap, args.range)
        try:
            window_name = 'HT301'
            cv2.namedWindow(window_name, cv2.WINDOW_KEEPRATIO)
            cv2.resizeWindow(window_name, processor.getWidth(args.legend), processor.getHeight())

            while(True):
                ret, frame = cap.read()
                info, lut = cap.info()

                frame = processor.processImage(frame, info)
                if args.markers:
                    frame = processor.addMarkers(frame, info)
                if args.legend:
                    frame = processor.addLegend(frame, info)

                cv2.imshow(window_name, frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                if key == ord('u'):
                    cap.calibrate()
                if key == ord('s'):
                    cv2.imwrite(time.strftime("%Y-%m-%d_%H:%M:%S") + '.png', frame)

        finally:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
