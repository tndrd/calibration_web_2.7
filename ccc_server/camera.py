import cv2
import numpy as np
import urllib2
import yaml
from config import SAVING_PATH
import time

class CalibrationCamera(object):
    def __init__(self):
        self.width = None
        self.length = None
        self.sq_size = None
        self.processing_image = None

        self.criteria = None
        self.objp = None
        self.objpoints = []
        self.imgpoints = []
        self.corners = None

    def start(self, width, length, square_size):
        self.width = width
        self.length = length
        self.sq_size = square_size
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, square_size, 0.001)
        self.objp = np.zeros((length * width, 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:width, 0:length].T.reshape(-1, 2)
        self.processing_image = None
        self.objpoints = []
        self.imgpoints = []
        self.corners = None

    def get_raw(self):
        request = urllib2.Request('http://192.168.11.1:8080/snapshot?topic=/main_camera/image_raw')
        raw = []
        try:
            arr = np.asarray(bytearray(urllib2.urlopen(request).read()), dtype=np.uint8)
        except:
            time.sleep(0.5)
            raw = self.get_raw()
        else:
            raw = cv2.imdecode(arr, -1)
        return raw

    def get_frame(self):
        raw = self.get_raw()
        ret, jpg = cv2.imencode('.jpg', raw)
        return jpg.tobytes()

    def get_preview(self):
        ret, gray, img = self.chessboard()
        self.processing_image = gray
        height, width, depth = img.shape
        coef_x = 640 / width
        coef_y = 480 / height
        self.corners = cv2.cornerSubPix(self.processing_image, self.corners, (11, 11), (-1, -1), self.criteria)
        cv2.drawChessboardCorners(img, (self.width, self.length), self.corners, ret)
        img = cv2.resize(img, (0, 0), fx=coef_x, fy=coef_y)
        ret, jpg = cv2.imencode('.jpg', img)
        return jpg.tobytes()

    def chessboard(self):
        img = self.get_raw()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, self.corners = cv2.findChessboardCorners(gray, (self.width, self.length), None)
        return ret, gray, img

    def exists(self):
        ret, gray, img = self.chessboard()
        return ret

    def add_pic(self):
        self.objpoints.append(self.objp)
        self.imgpoints.append(self.corners)

    def finish(self):
        if len(self.objpoints) >= 25:
            try:
                ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints,
                                                                self.processing_image.shape[::-1], None,
                                                                None, None, None, cv2.CALIB_RATIONAL_MODEL)
            except:
		print("Calibration failed")
                return False, 0, ""
            else:
                name = self.__yaml_save(mtx, dist, rvecs, tvecs, self.processing_image.shape)
                return True, self.reproj_error(rvecs, tvecs, mtx, dist), name
        else:
            print("Not enough photos")	
	    return False, 0, ""

    def amount_left(self):
        if len(self.objpoints) < 25:
            return 25 - len(self.objpoints) - 1
        else:
            return len(self.objpoints)

    def __yaml_save(self, mtx, dist, rvecs, tvecs, resolution):
        h, w, = tuple(map(int, resolution))
        pmatrix = self.__compute_proj_mat(mtx, rvecs, tvecs)
        rm_data = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        mat_data = []
        for i in mtx:
            for x in i: mat_data.append(x)
        mat_data = list(map(float, mat_data))

        dst_data = list(map(float, dist[0]))

        pm_data = []
        for i in pmatrix:
            for x in i: pm_data.append(x)
        pm_data = list(map(float, pm_data))

        data = {"image_width": w,
                "image_height": h,
                "distortion_model": "plumb_bob",
                "camera_name": "raspicam",
                "camera_matrix": {"rows": 3, "cols": 3, "data": mat_data},
                "distortion_coefficients": {"rows": 1, "cols": 8, "data": dst_data},
                "rectification_matrix": {"rows": 3, "cols": 3, "data": rm_data},
                "projection_matrix": {"rows": 3, "cols": 4, "data": pm_data}}
        name = SAVING_PATH + "camera_info_" + str(w) + "x" + str(h) + ".yaml"
        file = open(name, "w")
        for key in data:
            if type(key) == dict:
                for key2 in key: file.write(yaml.dump({key2: key[key2]}))
            else:
                file.write(yaml.dump({key: data[key]}, default_flow_style=False))
        return name

    def __compute_proj_mat(self, mtx, rvecs, tvecs):
        cam_mtx = np.zeros((3, 4), np.float64)
        cam_mtx[:, :-1] = mtx
        rmat = np.zeros((3, 3), np.float64)
        r_t_mat = np.zeros((3, 4), np.float64)
        cv2.Rodrigues(rvecs[0], rmat)
        r_t_mat = cv2.hconcat([rmat, tvecs[0]], r_t_mat)
        return (cam_mtx * r_t_mat)

    def reproj_error(self, rvecs, tvecs, mtx, dist):
        mean_error = 0
        for i in xrange(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(self.objpoints[i], rvecs[i], tvecs[i], mtx, dist)
            error = cv2.norm(self.imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            mean_error += error
        return float(mean_error / len(self.objpoints))
