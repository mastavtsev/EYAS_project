from enum import Enum


class ReportImageType(str, Enum):
    AV_SEGMENTATION = "av_segmentation"
    MAC_CONTOUR = "mac_contour"
    MAC_SEGMENTATION = "mac_segmentation"
    OD_CONTOUR = "od_contour"
    OD_SEGMENTATION = "od_segmentation"
    SOURCE = "source"

    def __str__(self) -> str:
        return str(self.value)
