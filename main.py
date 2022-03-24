import random
import logging

import maya.cmds as cmds
import json

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from PySide2.QtCore import QFile, QObject
from PySide2 import QtGui, QtWidgets, QtCore

logger = logging.getLogger("camera_plane_manager")
logger.setLevel(logging.WARNING)

# create console handler with debug log level
c_handler = logging.StreamHandler()

# create file handler with debug log level
# log_path = "/Users/sanazsanayei/Library/Preferences/Autodesk/maya/2022/scripts/CameraPlaneManager/log.log"
# f_handler = logging.FileHandler(filename=log_path)

# create formatter and add it to handlers
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
c_handler.setFormatter(formatter)
# f_handler.setFormatter(formatter)

# add handlers to logger
logger.addHandler(c_handler)
# logger.addHandler(f_handler)



def select_cameras():
    # Get all cameras
    cameras = cmds.ls(type='camera')
    return cameras


def create_image_plane(file_path, selected_camera):
    image_plane = cmds.imagePlane(camera=selected_camera)
    cmds.setAttr(image_plane[1] + ".imageName", file_path, type="string")
    return image_plane[1]


class CameraPlaneManager(QObject):
    def __init__(self, ui_file, parent=None):
        super(CameraPlaneManager, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        self.FILE_FILTERS = "Images (*.png *.jpeg *.jpg)"
        self.window.imageplane_pb.setIcon(QtGui.QIcon(":fileOpen.png"))



        #connection:
        self.window.imageplane_pb.clicked.connect(self.image_plane_selection)

        self.window.listWidget.itemClicked.connect(self.update_image_plane_attribute)

        self.window.offsetx_slider.sliderMoved.connect(self.image_plane_set_offset_x_slider)
        self.window.offsetx_sb.valueChanged.connect(self.image_plane_set_offset_x_sb)

        self.window.offsety_slider.sliderMoved.connect(self.image_plane_set_offset_y_slider)
        self.window.offsety_sb.valueChanged.connect(self.image_plane_set_offset_y_sb)

        self.window.lookthrough_pb.clicked.connect(self.image_plane_lookthrough)

        self.window.deleteip_btn.clicked.connect(self.delete_image_plane)

        self.window.deleteca_btn.clicked.connect(self.delete_camera)

        self.window.depth_sb.valueChanged.connect(self.image_plane_depth_sb)
        self.window.depth_slider.sliderMoved.connect(self.image_plane_depth_slider)

        self.window.scalex_sb.valueChanged.connect(self.set_scalex_sb)
        self.window.scalex_slider.sliderMoved.connect(self.set_scalex_slider)

        self.window.save_btn.clicked.connect(self.save_file)

        self.window.load_btn.clicked.connect(self.load_file)

        self.scene_cameras = select_cameras()

        for camera in self.scene_cameras:
            self.window.selectcame_cb.addItem(camera)

    def update_image_plane_attribute(self, item):
        self.window.offsetx_sb.setValue(cmds.getAttr(item.text() + ".offsetX"))
        self.window.offsety_sb.setValue(cmds.getAttr(item.text() + ".offsetY"))

    def image_plane_selection(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(None, "Select File", "",
                                                          self.FILE_FILTERS)[0]
        self.window.imagePlaneLineEdit.setText(file_path)

        if file_path:
            selected_camera = self.window.selectcame_cb.currentText()
            image_plane = create_image_plane(file_path, selected_camera)
            self.window.listWidget.addItem(image_plane)

    # by changing the slider of offset X the related double spinbar and maya in changed
    def image_plane_set_offset_x_slider(self, current_value):
        item = self.window.listWidget.currentItem()
        if not item:
            return
        cmds.setAttr(item.text() + ".offsetX", current_value)
        self.window.offsetx_sb.setValue(current_value)

    # by changing the spinbar of offset X the related slider bar and maya in changed
    def image_plane_set_offset_x_sb(self, current_value):
        item = self.window.listWidget.currentItem()
        if not item:
            return
        cmds.setAttr(item.text() + ".offsetX", current_value)
        self.window.offsetx_slider.setSliderPosition(current_value*100)

    # by changing the slider of offset Y the related double spinbar and maya in changed
    def image_plane_set_offset_y_slider(self, current_value):
        item = self.window.listWidget.currentItem()
        if not item:
            return
        cmds.setAttr(item.text() + ".offsetY", current_value)
        self.window.offsety_sb.setValue(current_value)

    # by changing the spinbar of offset Y the related slider bar and maya in changed
    def image_plane_set_offset_y_sb(self, current_value):
        item = self.window.listWidget.currentItem()
        if not item:
            return
        cmds.setAttr(item.text() + ".offsetY", current_value)
        self.window.offsety_slider.setSliderPosition(current_value*100)

    # changing the depth of image plane with spinbox
    def image_plane_depth_sb(self, current_value):
        item = self.window.listWidget.currentItem()
        if not item:
            return
        cmds.setAttr(item.text() + ".depth", current_value)
        self.window.depth_slider.setSliderPosition(current_value)

    # changing the depth of image plane with slider
    def image_plane_depth_slider(self, current_value):
        item = self.window.listWidget.currentItem()
        if not item:
            return
        cmds.setAttr(item.text() + ".depth", current_value)
        self.window.depth_sb.setValue(current_value)

    def set_scalex_sb(self, current_value):
        item = self.window.listWidget.currentItem()
        if not item:
            return
        cmds.setAttr(item.text() + ".sizeX", current_value)
        self.window.scalex_slider.setSliderPosition(current_value*100)

    def set_scalex_slider(self, current_value):
        item = self.window.listWidget.currentItem()
        if not item:
            return
        cmds.setAttr(item.text() + ".sizeX", current_value)
        self.window.scalex_sb.setValue(current_value)

    def image_plane_lookthrough(self):
        selected_camera = self.window.selectcame_cb.currentText()
        cmds.lookThru(selected_camera)

    def delete_image_plane(self):
        item = self.window.listWidget.currentItem()
        if not item:
            return
        deleted_item = cmds.listRelatives(item.text(), parent=True)
        cmds.delete(deleted_item)
        logger.warning("{} is deleted".format(item.text()))
        current_row = self.window.listWidget.row(item)
        self.window.listWidget.takeItem(current_row)

    def delete_camera(self):
        selected_camera = self.window.selectcame_cb.currentText()
        camera_transform = cmds.listRelatives(selected_camera, parent=True)
        cmds.delete(camera_transform)
        logger.warning("{} is deleted".format(selected_camera))
        current_index = self.window.selectcame_cb.currentIndex()
        self.window.selectcame_cb.removeItem(current_index)

    def save_file(self, file_name):

        image_planes = {}

        for index in range(self.window.listWidget.count()):
            item = self.window.listWidget.item(index)
            image_plane_name = item.text()
            image_planes[index] = {"file_path": cmds.getAttr(image_plane_name + ".imageName"),
                                  "offsetX": cmds.getAttr(image_plane_name + ".offsetX"),
                                  "offsetY": cmds.getAttr(image_plane_name + ".offsetY"),
                                  "scale": cmds.getAttr(image_plane_name + ".sizeX"),
                                  "depth": cmds.getAttr(image_plane_name + ".depth")}
        file_name = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", "",
                                                          "JSON (*.json)",
                                                          )
        with open(file_name[0], "w") as f:
            json.dump(image_planes, f, indent=4)

    def load_file(self, file_name):

        file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Select File", "","JSON (*.json)")
        if file_name[0] == "":
            return
        with open(file_name[0], "r") as f:
            data = json.load(f)
            print(data)
        for key, value in data.items():
            image_plane = create_image_plane(value["file_path"],self.window.selectcame_cb.currentText())
            cmds.setAttr(image_plane + ".offsetX", value["offsetX"])
            cmds.setAttr(image_plane + ".offsetY", value["offsetY"])
            cmds.setAttr(image_plane + ".sizeX", value["scale"])
            cmds.setAttr(image_plane + ".depth", value["depth"])
            self.window.listWidget.addItem(image_plane)


def launch():
    print("launch application")

    form = CameraPlaneManager('/Users/sanazsanayei/Library/Preferences/Autodesk/maya/2022/scripts/'
                              'CameraPlaneManager/camera_plane_manager.ui')
    form.window.exec_()
